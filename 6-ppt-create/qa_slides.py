#!/usr/bin/env python3
"""Structural QA, optional office previews, and clearly labelled geometry diagrams."""
import argparse
import io
import json
import math
import shutil
import subprocess
import tempfile
from pathlib import Path
from pptx import Presentation
from PIL import Image, ImageDraw, ImageFont, ImageOps


def metadata(shape):
    try:return json.loads(shape._element._nvXxPr.cNvPr.get('descr','{}'))
    except (ValueError,AttributeError,TypeError):return {}


def slide_id(slide,idx):
    ids={metadata(sh).get('sid') for sh in slide.shapes if metadata(sh).get('sid')}
    return next(iter(ids)) if len(ids)==1 else 'slide-{}'.format(idx+1)


def overlap(a,b):
    return min(a.left+a.width,b.left+b.width)>max(a.left,b.left) and min(a.top+a.height,b.top+b.height)>max(a.top,b.top)


def structural_checks(prs):
    issues=[];tag_boxes=[];ids=[]
    for idx,slide in enumerate(prs.slides):
        sid=slide_id(slide,idx);ids.append(sid)
        def flag(kind,shape=None,detail='',severity='warning'):
            issues.append(dict(slide_id=sid,kind=kind,shape=shape.name if shape is not None else None,detail=detail,severity=severity))
        pics=[s for s in slide.shapes if s.shape_type==13]
        texts=[s for s in slide.shapes if s.has_text_frame and s.text.strip()]
        tags=[s for s in texts if metadata(s).get('role')=='section']
        body=[s for s in texts if s not in tags and s!=slide.shapes.title]
        for shape in pics+texts:
            if shape.width<=0 or shape.height<=0 or shape.left<0 or shape.top<0 or shape.left+shape.width>prs.slide_width+2 or shape.top+shape.height>prs.slide_height+2:
                flag('bounds',shape,severity='error')
        for pic in pics:
            w,h=pic.image.size
            aspect=w*(1-pic.crop_left-pic.crop_right)/(h*(1-pic.crop_top-pic.crop_bottom))
            if abs(pic.width/pic.height/aspect-1)>.003:
                flag('aspect-ratio',pic,severity='error')
            if pic.width*pic.height/(prs.slide_width*prs.slide_height)<.045:
                flag('small-figure',pic,'Check axes and legend legibility in an office-rendered preview.')
            if not all(metadata(pic).get(k) for k in ('sha','fid','src')):
                flag('provenance',pic,'Missing source, hash or figure ID.')
        for sh in body:
            fonts=[r.font.size.pt for p in sh.text_frame.paragraphs for r in p.runs if r.font.size]
            font=max(fonts or [20]);width=max(sh.width-sh.text_frame.margin_left-sh.text_frame.margin_right,1)
            chars=max(width/914400*72/font/.55,1)
            lines=sum(max(1,math.ceil(len(p.text)/chars)) for p in sh.text_frame.paragraphs if p.text.strip())
            estimated=lines*font*1.35*12700+sh.text_frame.margin_top+sh.text_frame.margin_bottom
            if estimated>sh.height:
                flag('possible-text-overflow',sh,'Font-metric estimate only; inspect the rendered slide.')
            for pic in pics:
                if overlap(sh,pic):flag('text-picture-overlap',sh,severity='error')
        for i,a in enumerate(body):
            for b in body[i+1:]:
                if overlap(a,b):flag('text-text-overlap',a,severity='error')
        for tag in tags:
            tag_boxes.append((sid,tuple(int(getattr(tag,a)) for a in ('left','top','width','height'))))
            for p in tag.text_frame.paragraphs:
                for r in p.runs:
                    try:
                        white = str(r.font.color.rgb) == 'FFFFFF'
                    except (AttributeError, ValueError):
                        white = False
                    if r.font.size is None or abs(r.font.size.pt-24)>.01 or r.font.bold is not True or not white:
                        flag('section-style',tag,'Expected 24 pt bold white tag.',severity='error')
        content=pics+body
        if content:
            occupied=sum(1 for y in range(30) for x in range(50)
                         if any(s.left<=(x+.5)*prs.slide_width/50<=s.left+s.width and s.top<=(y+.5)*prs.slide_height/30<=s.top+s.height for s in content))/1500
            if occupied<.25:
                cx=sum(s.left+s.width/2 for s in content)/len(content)/prs.slide_width
                cy=sum(s.top+s.height/2 for s in content)/len(content)/prs.slide_height
                if abs(cx-.5)>.18 or abs(cy-.5)>.22:
                    flag('corner-concentration',detail='Sparse content concentrated away from the centre; review whitespace.')
        if sid.startswith('slide-'):flag('slide-identity',detail='Stable slide identity is missing.',severity='error')
    if len(ids)!=len(set(ids)):issues.append(dict(slide_id='deck',kind='duplicate-slide-identity',severity='error'))
    if tag_boxes:
        standard=tag_boxes[0][1]
        for sid,box in tag_boxes[1:]:
            if any(abs(a-b)>12700*2 for a,b in zip(standard,box)):
                issues.append(dict(slide_id=sid,kind='tag-alignment',severity='warning'))
    return issues


def contact_sheet(paths,output,label):
    thumbs=[]
    for path in paths:
        im=Image.open(path).convert('RGB');im.thumbnail((480,270))
        tile=Image.new('RGB',(500,310),'white');tile.paste(im,((500-im.width)//2,28))
        ImageDraw.Draw(tile).text((10,6),path.stem,fill='black');thumbs.append(tile)
    columns=3;rows=math.ceil(len(thumbs)/columns)
    sheet=Image.new('RGB',(columns*500,rows*310+35),'#dddddd')
    ImageDraw.Draw(sheet).text((10,10),label,fill='black')
    for i,tile in enumerate(thumbs):sheet.paste(tile,((i%columns)*500,35+(i//columns)*310))
    sheet.save(output)


def geometry_previews(prs,out):
    out=Path(out);out.mkdir(parents=True,exist_ok=True);paths=[]
    try:font=ImageFont.truetype('DejaVuSans.ttf',14)
    except OSError:font=ImageFont.load_default()
    scale=960/prs.slide_width
    for idx,slide in enumerate(prs.slides):
        im=Image.new('RGB',(960,int(prs.slide_height*scale)+30),'white');draw=ImageDraw.Draw(im)
        draw.text((8,5),'GEOMETRY ONLY - not an office render | '+slide_id(slide,idx),fill='red',font=font)
        for shape in slide.shapes:
            x,y=int(shape.left*scale),int(shape.top*scale)+30
            w,h=max(1,int(shape.width*scale)),max(1,int(shape.height*scale))
            if shape.shape_type==13:
                pic=Image.open(io.BytesIO(shape.image.blob)).convert('RGB')
                pw,ph=pic.size
                pic=pic.crop((int(pw*shape.crop_left),int(ph*shape.crop_top),int(pw*(1-shape.crop_right)),int(ph*(1-shape.crop_bottom))))
                im.paste(pic.resize((w,h)),(x,y))
            elif shape.has_text_frame and shape.text.strip():
                tag=metadata(shape).get('role')=='section'
                draw.rectangle((x,y,x+w,y+h),outline='#4678a0' if tag else '#888888',width=1)
                # Diagram text is approximate and intentionally does not claim font QA.
                lines=[]
                for line in shape.text.splitlines():
                    import textwrap
                    lines+=textwrap.wrap(line,width=max(5,w//8))
                for j,line in enumerate(lines):draw.text((x+3,y+3+j*17),line,font=font,fill='black')
        path=out/('slide-{:03d}.png'.format(idx+1));im.save(path);paths.append(path)
    contact_sheet(paths,out/'contact-sheet.png','GEOMETRY ONLY - not an office render')
    return paths


def qa(path,out,preview=False,geometry=False):
    path=Path(path).resolve();out=Path(out).resolve();out.mkdir(parents=True,exist_ok=True)
    prs=Presentation(path);issues=structural_checks(prs)
    report=dict(deck=str(path),slides=len(prs.slides),issues=issues,
                visual_status='not-run',hidden_playback_status='not-verified-in-presentation-software')
    if geometry:geometry_previews(prs,out/'geometry')
    soffice=shutil.which('soffice') or shutil.which('libreoffice')
    pdftoppm=shutil.which('pdftoppm')
    if preview and soffice and pdftoppm:
        preview_dir=Path(tempfile.mkdtemp(prefix='office-',dir=str(out)))
        with tempfile.TemporaryDirectory(prefix='ppt-preview-profile-') as profile:
            try:
                subprocess.run([soffice,'-env:UserInstallation='+Path(profile).as_uri(),'--headless','--convert-to','pdf','--outdir',str(preview_dir),str(path)],check=True,timeout=90,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
                subprocess.run([pdftoppm,'-png','-scale-to','1280',str(preview_dir/(path.stem+'.pdf')),str(preview_dir/'preview')],check=True,timeout=90,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
                images=sorted(preview_dir.glob('preview-*.png'))
                if not images:raise RuntimeError('Renderer produced no slides')
                contact_sheet(images,out/'contact-sheet.png','Office-rendered previews - inspect every slide')
                report['visual_status']='previews-created-human-review-required'
                report['preview_directory']=str(preview_dir)
                report['preview_count']=len(images)
                if len(images)!=len(prs.slides):
                    report['preview_warning']='Rendered page count differs from slide count; check hidden-slide export and missing pages.' 
            except (subprocess.SubprocessError,RuntimeError,OSError) as error:
                report['visual_status']='renderer-failed';report['renderer_error']=str(error)
    elif preview:
        report['visual_status']='unavailable';report['renderer_error']='LibreOffice/soffice or pdftoppm not found. Geometry diagrams are not visual QA.'
    (out/'qa-report.json').write_text(json.dumps(report,indent=2)+'\n')
    print('{}: {} structural errors, {} warnings; visual: {}'.format(path.name,sum(x['severity']=='error' for x in issues),sum(x['severity']=='warning' for x in issues),report['visual_status']))
    return report

if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('pptx');parser.add_argument('--out',required=True)
    parser.add_argument('--preview',action='store_true');parser.add_argument('--geometry',action='store_true')
    args=parser.parse_args();result=qa(args.pptx,args.out,args.preview,args.geometry)
    raise SystemExit(1 if any(x['severity']=='error' for x in result['issues']) else 0)
