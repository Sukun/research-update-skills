"""Run: python -m unittest discover -s tests -v (python-pptx and Pillow required)."""
import importlib.util
import json
import os
import hashlib
import tempfile
import unittest
from pathlib import Path
from pptx import Presentation
from pptx.util import Inches, Pt
from PIL import Image
from lxml import etree

SKILL=Path(__file__).resolve().parents[1]
def load(name,path):
    spec=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
renderer=load('renderer',SKILL/'render_storyboard.py')
qa=load('qa',SKILL/'qa_slides.py')

class RendererTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.root=Path(self.temp.name)
        self.figures=[]
        for i,size in enumerate([(300,600),(360,600),(420,600)]):
            path=self.root/('fig{}.png'.format(i));Image.new('RGB',size,(100+i*30,120,160)).save(path);self.figures.append(str(path))
        self.m=load('postprocess',SKILL/'postprocess_template.py')
        self.m.BULLET_PLACEHOLDERS=False;self.m.REFORMAT_NOTES=False
    def tearDown(self):self.temp.cleanup()
    def deck(self,layout,pics=3,bullets=2):
        p=Presentation();p.slide_width=Inches(13.33);p.slide_height=Inches(7.5)
        s=p.slides.add_slide(p.slide_layouts[1]);s.shapes.title.text='Section'
        tf=s.placeholders[1].text_frame
        for i in range(bullets):
            para=tf.paragraphs[0] if i==0 else tf.add_paragraph()
            run=para.add_run();run.text='Authored statement {}'.format(i+1);run.font.bold=i==0;run.font.italic=i==1
        for f in self.figures[:pics]:s.shapes.add_picture(f,Inches(.2),Inches(2),height=Inches(4))
        s.notes_slide.notes_text_frame.text='Original speaker notes. Keep these paragraphs.\nSecond paragraph.'
        path=self.root/'deck.pptx';p.save(path)
        self.m.PPTX_PATH=str(path);self.m.SECTION_TAGS={0:('Section','teal')};self.m.LAYOUT_MAP={layout:[0]}
        self.m.FIGURES={0:self.figures[:pics] if pics!=1 else self.figures[0]};self.m.SLIDE_IDS={0:'TEST-A'}
        self.m.PROJECT_ROOT=str(self.root);return path
    def test_three_picture_rebuild_retains_bullets_notes_and_emphasis(self):
        for layout in ('hstack-3','vstack-3'):
            path=self.deck(layout);before=Presentation(path).slides[0].notes_slide._element.xml
            self.m.main();after=Presentation(path);s=after.slides[0]
            self.assertEqual(before,s.notes_slide._element.xml)
            text='\n'.join(sh.text for sh in s.shapes if sh.has_text_frame)
            self.assertIn('Authored statement 1',text);self.assertIn('Authored statement 2',text)
            runs=[r for sh in s.shapes if sh.has_text_frame for p in sh.text_frame.paragraphs for r in p.runs]
            self.assertTrue(next(r for r in runs if r.text=='Authored statement 1').font.bold)
            self.assertTrue(next(r for r in runs if r.text=='Authored statement 2').font.italic)
            self.assertEqual(len([sh for sh in s.shapes if sh.shape_type==13]),3)
            self.assertFalse([x for x in qa.structural_checks(after) if x['severity']=='error'])
    def test_tag_style_preserved_but_other_text_boxes_formatted(self):
        p=Presentation();s=p.slides.add_slide(p.slide_layouts[6]);m=self.m
        chip=m.add_section_tag(s,'Tag','teal',p.slide_width)
        run=chip.text_frame.paragraphs[0].runs[0];before=etree.tostring(chip._element)
        box=s.shapes.add_textbox(0,Inches(1),Inches(4),Inches(1));box.text='Ordinary text';box.text_frame.paragraphs[0].runs[0].font.size=Pt(9)
        m.set_body_font(s)
        self.assertEqual(before,etree.tostring(chip._element));self.assertEqual(box.text_frame.paragraphs[0].runs[0].font.size.pt,20)
    def test_side_layouts_text_is_centred_18pt_bullets(self):
        from pptx.enum.text import MSO_ANCHOR
        from pptx.oxml.ns import qn
        for layout,count in [('figure-right-text-left',1),('figure-left-text-right',1),('figure-pair-left-text-right',2)]:
            path=self.deck(layout,count,2);self.m.main();p=Presentation(path);s=p.slides[0]
            box=self.m.body_text_shapes(s)[0];pics=[x for x in s.shapes if x.shape_type==13]
            self.assertEqual(box.text_frame.vertical_anchor,MSO_ANCHOR.MIDDLE,layout)
            self.assertEqual(box.text_frame.paragraphs[0].runs[0].font.size.pt,18,layout)
            self.assertTrue(all(q._p.pPr.find(qn('a:buChar')) is not None for q in box.text_frame.paragraphs if q.text.strip()),layout)
            self.assertEqual(box.top+box.height/2,pics[0].top+pics[0].height/2 if len(pics)==1 else box.top+box.height/2)
            if layout=='figure-right-text-left':self.assertTrue(all(x.left>=box.left+box.width for x in pics))
            else:self.assertTrue(all(x.left+x.width<=box.left for x in pics),layout)
    def test_new_balanced_layouts_and_summary(self):
        for layout,count in [('figure-right-text-left',1),('figure-pair-right-text-left',2),('figure-left-text-right',1),('figure-pair-left-text-right',2),('vertical-balanced-text',1),('large-text-summary',0)]:
            path=self.deck(layout,count,3 if count==0 else 2);self.m.main();p=Presentation(path)
            self.assertFalse([x for x in qa.structural_checks(p) if x['severity']=='error'],layout)
            if layout=='large-text-summary':
                shapes=self.m.body_text_shapes(p.slides[0]);self.assertEqual(len(shapes),1)
                self.assertEqual(len(shapes[0].text_frame.paragraphs),3)
                self.assertTrue(all(p.space_after.pt>0 for p in shapes[0].text_frame.paragraphs))
                self.assertTrue(all(sh.text_frame.paragraphs[0].runs[0].font.size.pt==28 for sh in shapes))
    def test_legacy_render_is_repeatable_and_provenance_survives(self):
        path=self.deck('figure-dominant',1);self.m.main();one=Presentation(path)
        def snapshot(p):
            return [(sh.text if sh.has_text_frame else '',tuple(int(getattr(sh,a)) for a in ['left','top','width','height']),qa.metadata(sh)) for sh in p.slides[0].shapes]
        before=snapshot(one);self.m.main();self.assertEqual(before,snapshot(Presentation(path)))
        pic=next(sh for sh in Presentation(path).slides[0].shapes if sh.shape_type==13)
        self.assertEqual(qa.metadata(pic)['src'],'fig0.png')
        self.assertEqual(qa.slide_id(Presentation(path).slides[0],0),'TEST-A')
    def test_variants_select_stable_ids_after_reordering_and_preserve_notes(self):
        path=self.deck('single',1);self.m.main();p=Presentation(path)
        # Each added slide has a stable anchor and notes, independent of ordering.
        variants=['short-keep','full-only','short-only','backup']
        first=p.slides[0];sids=['TEST-A','TEST-B','TEST-C','TEST-D']
        for sid in sids[1:]:
            s=p.slides.add_slide(p.slide_layouts[6]);sh=s.shapes.add_textbox(0,0,Inches(4),Inches(1));sh.text=sid
            self.m._set_meta(sh,'sb:role=title|slide='+sid,{'role':'title','sid':sid})
            s.notes_slide.notes_text_frame.text='Notes for '+sid
        first_id=p.slides._sldIdLst[0];p.slides._sldIdLst.remove(first_id);p.slides._sldIdLst.insert(2,first_id)
        p.save(path)
        manifest=[{'id':sid,'variant':v} for sid,v in zip(sids,variants)]
        for variant,expected in [('short',['TEST-C','TEST-A','TEST-D']),('full',['TEST-B','TEST-A','TEST-D'])]:
            out=self.root/(variant+'.pptx');renderer.derive_variant(path,manifest,variant,out,'hidden');derived=Presentation(out)
            self.assertEqual([qa.slide_id(s,i) for i,s in enumerate(derived.slides)],expected)
            self.assertEqual(derived.slides[-1]._element.get('show'),'0')
            self.assertEqual(derived.slides[-1].notes_slide.notes_text_frame.text,'Notes for TEST-D')
            self.assertTrue(any(qa.metadata(sh).get('sha') for sh in derived.slides[1].shapes))
    def test_parse_frontmatter_comments_and_explicit_ids(self):
        text='---\n---\n\n<!-- introductory comment -->\n<!-- Slide 1 -->\n<!-- slide-id: A -->\n<!-- variant: short-keep -->\n## Cover\n\n::: notes\n## Not a slide\n:::\n---\n<!-- Slide 2 -->\n<!-- slide-id: B -->\n<!-- layout: large-text-summary -->\n## Summary\n- One\n- Two\n- Three\n'
        path=self.root/'story.md';path.write_text(text);slides=renderer.parse_storyboard(path)
        self.assertEqual([s['id'] for s in slides],['A','B']);self.assertEqual(slides[1]['layout'],'large-text-summary')
    def test_recorded_geometry_overrides_layout_only_for_unique_matching_figures(self):
        path=self.deck('figure-dominant',1);self.m.main()
        p=Presentation(path); slide=p.slides[0]; pic=next(sh for sh in slide.shapes if sh.shape_type==13)
        sha=hashlib.sha256(pic.image.blob).hexdigest()
        notes=slide.notes_slide.notes_text_frame.text
        deck={'schema_version':1,'slides':[{'slide_id':'TEST-A','figures':[{'figure_id':'F','sha256':sha,'x':.12,'y':.25,'w':.3,'h':.4,'crop':[.1,.05,.02,.03]}]}]}
        recorded=self.root/'source.deck.json';recorded.write_text(json.dumps(deck))
        self.assertEqual(renderer.restore_recorded_geometry(path,[{'id':'TEST-A'}],recorded),1)
        result=Presentation(path); pic=next(sh for sh in result.slides[0].shapes if sh.shape_type==13)
        self.assertAlmostEqual(pic.left/result.slide_width,.12,places=4)
        self.assertAlmostEqual(pic.height/result.slide_height,.4,places=4)
        self.assertAlmostEqual(pic.crop_left,.1,places=4)
        self.assertEqual(result.slides[0].notes_slide.notes_text_frame.text,notes)
        deck['slides'][0]['figures'].append(dict(deck['slides'][0]['figures'][0]))
        recorded.write_text(json.dumps(deck)); self.assertEqual(renderer.restore_recorded_geometry(path,[{'id':'TEST-A'}],recorded),0)
        self.assertEqual(renderer.restore_recorded_geometry(path,[{'id':'TEST-A','generated_id':True}],recorded),0)
    def test_deck_json_discovery(self):
        source=self.root/'slides.pptx.md';source.write_text('')
        sibling=self.root/'slides.deck.json';sibling.write_text('{}')
        self.assertEqual(renderer.find_deck_json(source),sibling.resolve())
        other=self.root/'slides.pptx.deck.json';other.write_text('{}')
        with self.assertRaises(ValueError):renderer.find_deck_json(source)
        self.assertEqual(renderer.find_deck_json(source,sibling),sibling.resolve())
    def test_invalid_geometry_rejected(self):
        path=self.deck('figure-right-text-left',1);self.m.LAYOUT_OPTIONS={'TEST-A':{'text_fraction':.9}}
        with self.assertRaises(ValueError):self.m.main()
        self.m.LAYOUT_OPTIONS={};self.m.FIGURE_HEIGHT_OVERRIDE={0:1.5}
        with self.assertRaises(ValueError):self.m.main()

class IntegrationTests(unittest.TestCase):
    @unittest.skipUnless(os.environ.get("PPT_TEST_AMOC") and os.environ.get("PPT_TEST_PANDOC"), "set AMOC storyboard and Pandoc paths")
    def test_amoc_source_without_project_repair_script(self):
        source=Path(os.environ["PPT_TEST_AMOC"])
        before=hashlib.sha256(source.read_bytes()).hexdigest()
        with tempfile.TemporaryDirectory() as directory:
            outputs,slides=renderer.render(source,Path(directory)/"amoc.pptx",os.environ["PPT_TEST_PANDOC"],variants=["short","full"])
            p=Presentation(outputs[0])
            index=json.loads(source.with_suffix(".index.json").read_text())
            self.assertEqual(len(p.slides),len(index))
            for slide,expected in zip(p.slides,index):
                text="\n".join(sh.text for sh in slide.shapes if sh.has_text_frame)
                for bullet in expected["bullets"]:
                    self.assertIn(bullet.replace("**",""),text)
                self.assertEqual(len([sh for sh in slide.shapes if sh.shape_type==13]),len(expected["paths"]))
                self.assertTrue(slide.notes_slide.notes_text_frame.text.strip())
            self.assertFalse([x for x in qa.structural_checks(p) if x["severity"]=="error"])
            for output,variant in zip(outputs[1:],["short","full"]):
                expected={s["id"] for s in slides if (s["variant"] in ("short-keep","short-only") if variant=="short" else s["variant"] not in ("short-only","backup"))}
                derived=Presentation(output)
                self.assertEqual({qa.slide_id(s,i) for i,s in enumerate(derived.slides)},expected)
        self.assertEqual(before,hashlib.sha256(source.read_bytes()).hexdigest())

if __name__=='__main__':unittest.main()
