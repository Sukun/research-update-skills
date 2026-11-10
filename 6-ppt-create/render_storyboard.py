#!/usr/bin/env python3
"""Render one approved storyboard with the bundled static postprocessor."""
import argparse
import ast
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path
from urllib.parse import unquote

SKILL = Path(__file__).resolve().parent
LAYOUTS = {'text-only', 'single', 'figure-dominant', 'annotated', 'vstack-2',
           'hstack-2', 'vstack-3', 'hstack-3', 'focus-context', 'grid-2x2',
           'figure-right-text-left', 'figure-pair-right-text-left',
           'vertical-balanced-text', 'large-text-summary', 'table'}
VARIANTS = {'short-keep', 'short-only', 'full-only', 'backup'}


def parse_storyboard(path):
    path = Path(path).resolve()
    lines = path.read_text().splitlines(keepends=True)
    headings, separators, markers = [], [], []
    fenced = None
    comment = False
    notes = False
    yaml = bool(lines and lines[0].strip() == '---')
    for i, line in enumerate(lines):
        strip = line.strip()
        if yaml:
            if i and strip in ('---', '...'):
                yaml = False
            continue
        if comment:
            if '-->' in line:
                comment = False
            continue
        if strip.startswith('<!--'):
            comment = '-->' not in line
            if re.match(r'<!--\s*Slide\s+\d+\s*-->', strip):
                markers.append(i)
            continue
        fence = re.match(r'^\s*(`{3,}|~{3,})', line)
        if fence:
            token = fence.group(1)
            if fenced is None:
                fenced = token
            elif token[0] == fenced[0] and len(token) >= len(fenced):
                fenced = None
            continue
        if fenced:
            continue
        if re.match(r'^::: ?(?:notes|\{\.notes\})\s*$', strip):
            notes = True
            continue
        if notes:
            if re.fullmatch(r':{3,}', strip):
                notes = False
            continue
        if line.startswith('## '):
            headings.append(i)
        if strip == '---':
            separators.append(i)
    if not headings:
        raise ValueError('No level-2 slide headings')
    starts = []
    for pos, h in enumerate(headings):
        prev = headings[pos-1] if pos else -1
        candidates = [x for x in markers if prev < x < h]
        if candidates:
            start = candidates[-1]
        else:
            seps = [x for x in separators if prev < x < h]
            start = seps[-1] + 1 if seps else h
            if not seps:
                while start > prev+1 and (not lines[start-1].strip() or
                                         re.fullmatch(r'\s*<!--.*-->\s*\n?', lines[start-1])):
                    start -= 1
        starts.append(start)
    slides = []
    index_file = path.with_suffix('.index.json')
    prior = json.loads(index_file.read_text()) if index_file.is_file() else []
    if isinstance(prior, dict):
        prior = prior.get('slides', [])
    for i, h in enumerate(headings):
        block = ''.join(lines[starts[i]:starts[i+1] if i+1 < len(starts) else len(lines)])
        title = lines[h][3:].strip()
        prior_slide = next((x for x in prior if x.get('title') == title), {})
        metadata_block = re.sub(r'(?ms)^::: ?(?:notes|\{\.notes\})\s*\n.*?^:::\s*$', '', block)
        metadata_block = re.sub(r'(?ms)^(`{3,}|~{3,})[^\n]*\n.*?^\1[^\n]*$', '', metadata_block)
        def annotation(name):
            values = re.findall(r'<!--\s*' + re.escape(name) + r':\s*(.*?)\s*-->', metadata_block)
            if len(values) > 1:
                raise ValueError('Duplicate {} on {}'.format(name, title))
            return values[0] if values else None
        sid = annotation('slide-id')
        variant = annotation('variant')
        if variant and variant not in VARIANTS:
            raise ValueError('Unknown variant: ' + variant)
        # Speaker notes never count as visible images or bullets.
        visible = re.sub(r'::: ?(?:notes|\{\.notes\})\s*\n.*?\n:::','',block,flags=re.S)
        declared = annotation('figures')
        paths = ([x.strip() for x in declared.split(',')] if declared else
                 re.findall(r'!\[[^\]]*\]\((?:<([^>]+)>|([^\s)]+))\)',visible))
        if not declared:
            paths = [a or b for a,b in paths]
        resolved = []
        for name in paths:
            if re.match(r'\w+://',name):
                raise ValueError('Use an existing local figure: ' + name)
            source = (path.parent / unquote(name)).resolve()
            if not source.is_file():
                raise FileNotFoundError(source)
            resolved.append(str(source))
        layout = annotation('layout') or prior_slide.get('layout')
        if not layout:
            layout = ('hstack-3' if len(resolved)==3 and declared else
                      'figure-dominant' if len(resolved)==1 else
                      'text-only' if not resolved else 'hstack-2' if len(resolved)==2 else 'grid-2x2')
        if layout == 'annotated':
            layout = 'figure-dominant'
        if layout not in LAYOUTS:
            raise ValueError('Unsupported layout: ' + layout)
        tag = annotation('section-tag')
        match = re.fullmatch(r'"(.*?)"\s+color="([^"]+)"',tag) if tag else None
        if tag and not match:
            raise ValueError('Invalid section-tag on ' + title)
        height = annotation('figure-height')
        if height:
            terms = height.split('/')
            if len(terms)>2:
                raise ValueError('Invalid figure-height')
            height = float(terms[0]) / (float(terms[1]) if len(terms)==2 else 1)
            if not 0<height<=1:
                raise ValueError('figure-height must be in (0,1]')
        known = {'slide-id','variant','figures','layout','section-tag','figure-height','layout-options','original-title'}
        for key in re.findall(r'<!--\s*([\w-]+):',metadata_block):
            if key not in known:
                print('WARNING: annotation has no renderer effect: {} ({})'.format(key,sid or title))
        options = json.loads(annotation('layout-options') or '{}')
        if not isinstance(options,dict):
            raise ValueError('layout-options must be a JSON object')
        if len(title)>65:
            print('WARNING: long title retained: ' + title)
        slides.append(dict(index=i,id=sid,title=title,variant=variant,layout=layout,
                           tag=list(match.groups()) if match else None, paths=resolved,
                           override=height,options=options,block=block))
    explicit = [x['id'] for x in slides if x['id']]
    if len(explicit)!=len(set(explicit)):
        raise ValueError('Duplicate slide-id')
    # Mint render-local IDs only for legacy decks; variants require authored stable IDs.
    taken=set(explicit)
    for i,s in enumerate(slides):
        if not s['id']:
            sid='S{:03d}'.format(i+1)
            if sid in taken:
                raise ValueError('Generated ID conflicts with authored ID; add explicit IDs')
            s['id']=sid;taken.add(sid);s['generated_id']=True
    return slides


def fill_template(template, values):
    source=Path(template).read_text(); lines=source.splitlines(keepends=True)
    edits=[]
    for node in ast.parse(source).body:
        if isinstance(node,ast.Assign) and len(node.targets)==1 and isinstance(node.targets[0],ast.Name):
            name=node.targets[0].id
            if name in values:
                edits.append((node.lineno-1,node.end_lineno,name+' = '+repr(values[name])+'\n'))
    if {name for name in values} - {re.match(r'(\w+)',e[2]).group(1) for e in edits}:
        raise ValueError('Template DATA BLOCK is missing a required field')
    for start,end,text in reversed(edits):
        lines[start:end]=[text]
    return ''.join(lines)


def derive_variant(source, slides, variant, output, backup='exclude'):
    from pptx import Presentation
    if any(s.get('generated_id') for s in slides):
        raise ValueError('Variants require explicit stable slide-id comments on every slide')
    if variant not in ('short','full') or backup not in ('exclude','append','hidden'):
        raise ValueError('Unknown variant/backup mode')
    # Select by ID; physical indices are used only to locate the stamped slide part.
    selected={s['id'] for s in slides if
              (s['variant'] in ('short-keep','short-only') if variant=='short' else s['variant'] not in ('short-only','backup'))}
    backups={s['id'] for s in slides if s['variant']=='backup'} if backup!='exclude' else set()
    prs=Presentation(source); ids=[]
    for slide in prs.slides:
        found=set()
        for sh in slide.shapes:
            try:
                payload=json.loads(sh._element._nvXxPr.cNvPr.get('descr','{}'))
                if payload.get('sid'):found.add(payload['sid'])
            except (ValueError,AttributeError,TypeError):pass
        if len(found)!=1:
            raise ValueError('Expected one stable identity per slide')
        ids.append(found.pop())
    if len(ids)!=len(set(ids)) or set(ids)!={s['id'] for s in slides}:
        raise ValueError('Deck and storyboard IDs differ')
    kept=[]; appended=[]
    for element,sid in list(zip(prs.slides._sldIdLst,ids)):
        if sid not in selected|backups:
            prs.part.drop_rel(element.rId);prs.slides._sldIdLst.remove(element)
        elif sid in backups:
            appended.append(element)
        else:kept.append(element)
    for el in appended:
        prs.slides._sldIdLst.remove(el);prs.slides._sldIdLst.append(el)
    for slide in prs.slides:
        sid=next(json.loads(sh._element._nvXxPr.cNvPr.get('descr','{}')).get('sid')
                 for sh in slide.shapes if sh.has_text_frame and '"sid"' in sh._element._nvXxPr.cNvPr.get('descr',''))
        slide._element.set('show','0' if sid in backups and backup=='hidden' else '1')
    if not len(prs.slides):raise ValueError('Variant selection is empty')
    prs.save(output)
    return [sid for sid in ids if sid in selected]+[sid for sid in ids if sid in backups]


def render(storyboard, output, pandoc, reference=None, project_root=None, variants=(), backup='exclude'):
    from pptx import Presentation
    storyboard=Path(storyboard).resolve();output=Path(output).resolve()
    if output==storyboard or output.suffix.lower()!='.pptx':
        raise ValueError('Output must be a separate PPTX file')
    slides=parse_storyboard(storyboard)
    if variants and any(s.get("generated_id") for s in slides):
        raise ValueError("Variants require explicit stable slide-id comments before rendering")
    if reference is None:
        local_reference = storyboard.parent / "reference.pptx"
        if local_reference.is_file():
            reference = local_reference
    output.parent.mkdir(parents=True,exist_ok=True)
    formatted=output.with_suffix('.render.md')
    blocks=[]
    for s in slides:
        block=s['block']
        # Single Pandoc anchor; the template rebuilds only the picture region.
        if s['layout'] in ('hstack-3','vstack-3','figure-pair-right-text-left'):
            matches=list(re.finditer(r'!\[[^\]]*\]\([^\n]+?\)(?:\{[^}]*\})?',block))
            for m in reversed(matches[1:]):block=block[:m.start()]+block[m.end():]
        block=re.sub(r'(?m)^Note:\s*\n(.*?)(?=\n---|\Z)',r'::: notes\n\1\n:::\n',block,flags=re.S)
        blocks.append(re.sub(r'(?m)^---\s*$', '', block).strip())
    formatted.write_text('\n\n---\n\n'.join(blocks)+'\n')
    cmd=[str(pandoc),str(formatted),'--slide-level=2','--resource-path='+str(storyboard.parent),'-o',str(output)]
    if reference:cmd.extend(['--reference-doc',str(Path(reference).resolve())])
    subprocess.run(cmd,check=True,cwd=str(storyboard.parent))
    prs=Presentation(output)
    if len(prs.slides)!=len(slides):raise ValueError('Pandoc slide count differs from heading count')
    for slide,expected in zip(prs.slides,slides):
        if slide.shapes.title is None or slide.shapes.title.text.strip()!=expected['title']:
            raise ValueError('Pandoc title/index mismatch on '+expected['id'])
    layout_map={}
    for s in slides:layout_map.setdefault(s['layout'],[]).append(s['index'])
    values=dict(PPTX_PATH=str(output),SECTION_TAGS={s['index']:tuple(s['tag']) for s in slides if s['tag']},
                LAYOUT_MAP=layout_map,FIGURES={s['index']:(s['paths'][0] if len(s['paths'])==1 else s['paths']) for s in slides if s['paths']},
                FIGURE_HEIGHT_OVERRIDE={s['index']:s['override'] for s in slides if s['override'] is not None},
                SLIDE_IDS={s['index']:s['id'] for s in slides},LAYOUT_OPTIONS={s['id']:s['options'] for s in slides if s['options']},
                PROJECT_ROOT=str(Path(project_root).resolve()) if project_root else str(storyboard.parent),
                BULLET_PLACEHOLDERS=False,STAMP_IDS=True,REFORMAT_NOTES=False)
    processor=output.with_suffix('.postprocess.py')
    processor.write_text(fill_template(SKILL/'postprocess_template.py',values))
    subprocess.run([sys.executable,str(processor)],check=True)
    manifest=output.with_suffix('.slides.json')
    manifest.write_text(json.dumps([{k:v for k,v in s.items() if k!='block'} for s in slides],indent=2)+'\n')
    outputs=[output]
    for variant in variants:
        target=output.with_name(output.stem+'.'+variant+'.pptx')
        derive_variant(output,slides,variant,target,backup);outputs.append(target)
    return outputs,slides


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('storyboard',type=Path)
    parser.add_argument('-o','--output',type=Path)
    parser.add_argument('--pandoc',default=shutil.which('pandoc'))
    parser.add_argument('--reference',type=Path)
    parser.add_argument('--project-root',type=Path)
    parser.add_argument('--variants',nargs='+',choices=['short','full'],default=[])
    parser.add_argument('--backup',choices=['exclude','append','hidden'],default='exclude')
    args=parser.parse_args()
    if not args.pandoc:parser.error('Pandoc unavailable; pass --pandoc /path/to/pandoc')
    outputs,_=render(args.storyboard,args.output or args.storyboard.with_suffix('.pptx'),args.pandoc,args.reference,args.project_root,args.variants,args.backup)
    print('Outputs: '+', '.join(str(p) for p in outputs))

if __name__=='__main__':main()
