"""Observable language structure, pagination and printed output regressions."""
import json,os,sys,tempfile,unittest
from copy import deepcopy
from pathlib import Path
from types import SimpleNamespace
from io import BytesIO

SKILL=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(SKILL/'scripts'))
from build_calibration import build
from content_schema import validate_v2,walk_blocks
from language_review import language_findings,paragraph_finding
from example_structure import example_parts
from book_compositor import balanced_pages

def example(data):return next(b for p in data['pages'] for b in p['blocks'] if b['type']=='worked_example')

class LanguageSchemaTests(unittest.TestCase):
    def test_incomplete_example_and_formula_fail_before_rendering(self):
        for field in ('problem','analysis','steps','result','method'):
            d=build();example(d).pop(field)
            with self.subTest(field=field),self.assertRaises(ValueError):validate_v2(d)
        d=build();e=example(d);e['steps'][0]['content']=[dict(id='missing-reason',type='formula_step',source_kind='authored_example',formula='x=2')]
        with self.assertRaisesRegex(ValueError,'reason required'):validate_v2(d)

    def test_steps_require_titles_and_distinct_labels(self):
        d=build();e=example(d);e['steps'][0].pop('title')
        with self.assertRaisesRegex(ValueError,'each step needs'):validate_v2(d)
        d=build();e=example(d);e['steps'][1]['label']=e['steps'][0]['label']
        with self.assertRaisesRegex(ValueError,'unique'):validate_v2(d)
        d=build();example(d)['steps']=['compressed string']
        with self.assertRaisesRegex(ValueError,'object'):validate_v2(d)

    def test_continuation_cannot_reference_itself(self):
        d=build();e=example(d);e['continuation_of']=e['id']
        with self.assertRaisesRegex(ValueError,'earlier example'):validate_v2(d)

    def test_new_example_dependency_is_reviewed_but_valid_continuation_is_exempt(self):
        d=build();e=example(d);e['problem']='沿用上一轮数据，继续计算。'
        self.assertTrue(any(f['code']=='context_dependency' for f in language_findings(d)))
        e2=deepcopy(e);e2.update(id='explicit-continuation',continuation_of=e['id'])
        # Give every copied child a unique ID.
        for child in walk_blocks([e2]):
            if child is not e2:child['id']='copy-'+child['id']
        d['pages'].append({**deepcopy(d['pages'][0]),'id':'continuation-page','blocks':[e2],'handwritten_layer':[],'handwriting_reason':'Test continuation','sidebar':{'items':[]}})
        validate_v2(d)
        self.assertFalse(any(f['block_id']==e2['id'] for f in language_findings(d)))
        e2['problem_number']='different'
        with self.assertRaisesRegex(ValueError,'same problem_number'):validate_v2(d)

    def test_long_paragraph_and_multi_action_reviews_are_candidates(self):
        self.assertIsNone(paragraph_finding('p',1,4,2))
        self.assertEqual(paragraph_finding('p',1,5,2)['severity'],'warning')
        self.assertEqual(paragraph_finding('p',1,6,2)['severity'],'manual_review')
        d=build();d['pages'][0]['blocks'].append(dict(id='crowded',type='paragraph',text='先确定变量，再代入，然后比较，最后核验。',source_kind='authored_example'))
        self.assertTrue(any(f['code']=='compressed_steps' and f['block_id']=='crowded' for f in language_findings(d)))

    def test_standalone_maps_require_all_four_editorial_conditions(self):
        d=build();page=deepcopy(d['pages'][0]);page.update(id='requested-map',type='chapter_map',blocks=[dict(id='map',type='knowledge_map',source_kind='editorial_synthesis',height_rows=20,tree=dict(label='复习',children=[dict(label='已学内容')]))],handwritten_layer=[],handwriting_reason='Map',sidebar={'items':[]})
        d['pages'].append(page)
        with self.assertRaisesRegex(ValueError,'disabled by default'):validate_v2(d)
        d['standalone_map_policy']={k:True for k in d['standalone_map_policy']};validate_v2(d)

    def test_balanced_pagination_keeps_order_without_a_tiny_tail(self):
        groups=[[{'id':i}] for i in range(5)]
        pages=balanced_pages(groups,[8,8,8,8,3],30)
        self.assertEqual([[b['id'] for b in page] for page in pages],[[0,1],[2,3,4]])
        with self.assertRaises(ValueError):balanced_pages(groups, [31,1,1,1,1],30)

@unittest.skipUnless(os.environ.get('XUEBA_TEST_FONTS'),'Set XUEBA_TEST_FONTS for PDF integration')
class LanguageRenderingTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        from pdf_template_layout import register_fonts
        cls.fonts=Path(os.environ['XUEBA_TEST_FONTS']);register_fonts(cls.fonts)

    def engine(self):
        from reportlab.pdfgen.canvas import Canvas
        from teaching_blocks import BlockEngine
        book=SimpleNamespace(pitch=7.2,y=lambda r:28.8+r*7.2,say=lambda *args:None,c=Canvas(BytesIO()))
        return BlockEngine(book)

    def test_semantic_paragraph_gap_and_measured_review(self):
        e=self.engine();b=dict(id='p',type='paragraph',text='第一段完整说明。\n\n第二段说明另一个任务。')
        self.assertEqual(e.block(b,2,10,128)-2,4) # 2 lines + semantic gap + trailing gap
        long=dict(id='long',type='paragraph',text='这是一个很长的解释段落，需要查看是否包含多个教学动作。'*8)
        e.block(long,2,10,128)
        self.assertEqual(e.language_findings[-1]['severity'],'manual_review')

    def test_formula_reason_and_formula_occupy_separate_baselines(self):
        e=self.engine();calls=[];e.b.say=lambda *args:calls.append(args)
        b=dict(id='f',type='formula_step',reason='由第二条约束解出x：',formula='x=3−0.5y−0.5s₂')
        height=e.measure(b,128);self.assertEqual(height,e.block(b,2,10,128)-2)
        self.assertGreater(calls[1][2],calls[0][2])
        self.assertEqual(calls[1][3],'Math')

    def test_highlight_crossing_semantic_paragraph_break_is_not_lost(self):
        e=self.engine();marks=[];e.rectangle=lambda *args:marks.append(args)
        text='先解释含义。\n\n再说明条件。'
        b=dict(id='marked',type='paragraph',text=text,highlights=[dict(start=0,end=len(text),text=text,reason='Both statements selected')])
        e.block(b,2,10,128)
        self.assertEqual(len(marks),2)
        self.assertGreater(marks[1][1]-marks[0][1],e.b.pitch)

    def test_complete_examples_repaginate_with_sections_and_correct_anchors(self):
        from fill_template import Book
        import fitz
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp);out=root/'review.pdf'
            args=SimpleNamespace(content=SKILL/'Resources/content/operations-research-calibration.json',templates=SKILL/'Resources/templates',fonts=self.fonts,assets=SKILL/'Resources/illustrations',edition='digital',output=out,fun_mode='content',fun_seed=None,foldout_only=False)
            book=Book(args);book.run()
            compiled=book.content['pages'];continuations=[p for p in compiled if p.get('continuation_of')]
            self.assertTrue(continuations)
            self.assertTrue(all('续' in p['title'] for p in continuations))
            doc=fitz.open(out);text='\n'.join(p.get_text() for p in doc)
            for title in ('题目','分析','结果','方法','01 定义变量','02 建立模型'):self.assertIn(title,text)
            self.assertNotIn('运筹学知识地图',text);self.assertNotIn('动态规划方法图',text)
            ids=[p['id'] for p in compiled];self.assertEqual(len(ids),len(set(ids)))
            parts=[b for p in compiled for b in p['blocks'] if b['type']=='_example_part']
            for number in ('01','02','03','04'):
                subset=[p for p in parts if p['problem_number']==number]
                self.assertEqual([p['part'] for p in subset].count('problem'),1)
                self.assertEqual([p['part'] for p in subset].count('result'),1)
                self.assertEqual([p['part'] for p in subset].count('method'),1)
            self.assertIn('sx-specials',book.body_targets)
            for page in book.logs:
                for note in page.get('annotations',[]):self.assertIn(note['anchor'],page['blocks'])
            doc.close();book.doc.close();book.master.close()

if __name__=='__main__':unittest.main()
