"""Behavioral regressions for v2 teaching blocks and the three-chapter sample.

Set XUEBA_TEST_FONTS to a prepared font directory for the rendering tests.
Pure schema, pagination and independent arithmetic tests need no font files.
"""
from copy import deepcopy
from fractions import Fraction
from io import BytesIO
import json
import os
from pathlib import Path
import sys
import tempfile
from types import SimpleNamespace
import unittest

SKILL=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(SKILL/'scripts'))
from build_calibration import build
from content_schema import validate_v2,walk_blocks,PAGE_PROFILES
from book_compositor import balanced_columns

def find_block(data,identifier):
    return next(b for p in data['pages'] for b in walk_blocks(p['blocks']) if b['id']==identifier)

def find_note(data,key):
    return next(n for p in data['pages'] for n in p['handwritten_layer'] if key in n)

class SchemaTests(unittest.TestCase):
    def setUp(self):self.data=build()
    def test_calibration_fields_and_all_body_types(self):
        validate_v2(self.data)
        self.assertEqual({p['type'] for p in self.data['pages']},set(PAGE_PROFILES)-{'glossary','foldout','chapter_map','volume_map'})
    def test_rejects_bad_block_table_source_and_problem(self):
        mutations=[
            lambda d:find_block(d,'lp-vars').update(type='unknown'),
            lambda d:find_block(d,'lp-data')['rows'][0].append('extra'),
            lambda d:find_block(d,'lp-vars').update(source_id='missing'),
            lambda d:find_block(d,'lp-app-steps').pop('analysis'),
            lambda d:d['pages'][1]['handwritten_layer'][0].update(anchor_block_id='absent'),
        ]
        for mutate in mutations:
            with self.subTest(mutation=mutate):
                data=deepcopy(self.data);mutate(data)
                with self.assertRaises(ValueError):validate_v2(data)
    def test_advanced_boundaries_need_explicit_scope(self):
        condition=next(b for p in self.data['pages'] for b in walk_blocks(p['blocks']) if b['type']=='condition')
        condition['boundary_level']='C'
        with self.assertRaisesRegex(ValueError,'advanced boundary'):validate_v2(self.data)
        condition['course_required']=True;validate_v2(self.data)
    def test_introduced_is_not_taught(self):
        concept=self.data['concepts'][0];concept['first_use_role']='introduced';concept.pop('teaching_refs')
        validate_v2(self.data)
        concept['first_use_role']='taught'
        with self.assertRaisesRegex(ValueError,'no definition evidence'):validate_v2(self.data)
    def test_rejects_stale_circle_and_invalid_cell(self):
        circle=find_note(self.data,'target_span')
        self.assertEqual(circle['target_span']['text'],'交集')
        circle['target_span']['text']='旧稿'
        with self.assertRaises(ValueError):validate_v2(self.data)
        data=build();find_note(data,'target_cell')['target_cell']=[9,9]
        with self.assertRaisesRegex(ValueError,'target_cell'):validate_v2(data)
    def test_authored_chapter_cannot_claim_textbook_number(self):
        self.data['outline'][0]['textbook_chapter_number']='22'
        self.data['outline'][0]['source_kind']='editorial_synthesis'
        with self.assertRaisesRegex(ValueError,'authored material'):validate_v2(self.data)
    def test_prerequisite_cycles_and_outline_order(self):
        a,b=self.data['concepts'][:2];a['prerequisite_ids']=[b['id']];b['prerequisite_ids']=[a['id']]
        with self.assertRaisesRegex(ValueError,'cyclic'):validate_v2(self.data)
        data=build();data['outline'][0],data['outline'][1]=data['outline'][1],data['outline'][0]
        with self.assertRaisesRegex(ValueError,'parent must precede'):validate_v2(data)
    def test_drawing_bounds_and_missing_map_height(self):
        find_block(self.data,'lp-figure').pop('height_rows')
        with self.assertRaisesRegex(ValueError,'height_rows'):validate_v2(self.data)
        data=build();find_block(data,'lp-figure')['drawing'][5]['x']=101
        with self.assertRaisesRegex(ValueError,'normalized slot'):validate_v2(data)

class MathematicsTests(unittest.TestCase):
    def test_lp_vertices_and_drawn_constraints(self):
        data=build();blocks={b['id']:b for p in data['pages'] for b in walk_blocks(p['blocks'])}
        graph=blocks['lp-figure']['drawing']
        vertices=[((X-10)/16,(88-Y)/17.5) for X,Y in graph[0]['points']]
        self.assertEqual(max((3*x+2*y,x,y) for x,y in vertices),(10,2,2))
        for x,y in vertices:self.assertTrue(x>=0 and y>=0 and x+y<=4 and 2*x+y<=6)
        for primitive,a,limit in [(graph[3],1,4),(graph[4],2,6)]:
            for X,Y in primitive['points']:self.assertAlmostEqual(a*(X-10)/16+(88-Y)/17.5,limit)
        new_graph=blocks['lp-order-figure']['drawing']
        self.assertTrue(all((X-10)/16>=1 for X,Y in new_graph[0]['points']))
    def test_simplex_pivot_matches_final_table(self):
        blocks={b['id']:b for p in build()['pages'] for b in walk_blocks(p['blocks'])}
        def number(value):return Fraction(str(value).replace('−','-'))
        matrix=[[number(x) for x in row[1:]] for row in blocks['sx-pivot-table']['rows']]
        pivot=matrix[0][1];matrix[0]=[x/pivot for x in matrix[0]]
        for i in (1,2):
            factor=matrix[i][1];matrix[i]=[x-factor*y for x,y in zip(matrix[i],matrix[0])]
        expected=[[number(x) for x in row[1:]] for row in blocks['sx-final-table']['rows']]
        self.assertEqual(matrix,expected)
    def test_knapsack_table_matches_exhaustive_search(self):
        blocks={b['id']:b for p in build()['pages'] for b in walk_blocks(p['blocks'])}
        for i,row in enumerate(blocks['dp-values']['rows']):
            expected=[max(3*a+4*b for a in range(cap//2+1) for b in range(cap//3+1) if 2*a+3*b<=cap and (i>=1 or a==0) and (i>=2 or b==0)) for cap in range(8)]
            self.assertEqual(row[1:],expected)
    def test_resource_allocation_by_enumeration(self):
        blocks={b['id']:b for p in build()['pages'] for b in walk_blocks(p['blocks'])}
        a,b=[row[1:] for row in blocks['dp-return']['rows']]
        self.assertEqual(max((a[x]+b[y],x,y) for x in range(4) for y in range(4) if x+y<=3),(10,2,1))

class ContentsTests(unittest.TestCase):
    def test_long_contents_balances_tail_and_keeps_parent_child(self):
        items=[dict(id=i,height=3,keep_next=i%5==0) for i in range(21)]
        columns=balanced_columns(items,20)
        self.assertEqual(len(columns),4)
        self.assertEqual([i['id'] for col in columns for i in col],list(range(21)))
        heights=[sum(i['height'] for i in col) for col in columns]
        self.assertLessEqual(max(heights),20);self.assertLessEqual(max(heights)-min(heights),3)
        for col in columns[:-1]:self.assertFalse(col[-1]['keep_next'])
    def test_oversized_parent_chain_fails(self):
        with self.assertRaisesRegex(ValueError,'parent/first-child'):balanced_columns([dict(height=15,keep_next=True),dict(height=15)],20)

@unittest.skipUnless(os.environ.get('XUEBA_TEST_FONTS'),'Set XUEBA_TEST_FONTS for actual rendering regressions')
class RenderingTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        from pdf_template_layout import register_fonts
        cls.fonts=Path(os.environ['XUEBA_TEST_FONTS']);register_fonts(cls.fonts)
    def test_body_hand_fonts_are_distinct(self):
        from reportlab.pdfbase import pdfmetrics
        self.assertNotEqual(pdfmetrics.getFont('Body').face.charWidths,pdfmetrics.getFont('Hand').face.charWidths)
    def test_measured_table_and_pair_equal_drawn_height(self):
        from teaching_blocks import BlockEngine
        from reportlab.pdfgen.canvas import Canvas
        book=SimpleNamespace(pitch=7.2,y=lambda r:28.8+r*7.2,say=lambda *args:None,c=Canvas(BytesIO()))
        table=dict(id='t',type='table',headers=['量','解释较长的列'],rows=[['x','一段需要换行的中文解释，逐行测量。'],['y','短句']])
        block=dict(id='pair',type='paired',left=[table],right=[dict(id='p',type='paragraph',text='先看左侧数据，再比较。')])
        measure=BlockEngine(book,False).measure(block,80);engine=BlockEngine(book)
        self.assertEqual(engine.block(block,3,10,80)-3,measure)
        self.assertIn('t@1,1',engine.boxes)
        # Enough page width must preserve short labels such as 甲乙 and the
        # DP header on one row even when numeric columns need minimum widths.
        dp=next(b for p in build()['pages'] for b in walk_blocks(p['blocks']) if b['id']=='dp-values')
        self.assertEqual(BlockEngine(book,False).measure(dp,128),4)
    def test_tree_exports_connected_curves_and_checks_crowding(self):
        from knowledge_map import layout_tree,svg_text
        tree=dict(label='中心',children=[dict(label='第一类',children=[dict(label='子概念',formula='x+y=4')]),dict(label='第二类')])
        layout=layout_tree(tree,128,100);svg=svg_text(layout)
        self.assertIn(' C',svg);self.assertIn('x+y=4',svg)
        self.assertTrue(all(e['x1']<e['x2'] for e in layout['edges']))
        with self.assertRaisesRegex(ValueError,'crowded'):layout_tree(tree,128,10)
    def test_actual_repagination_preserves_outline_and_hand_anchor(self):
        from fill_template import Book
        data=build();data['concepts']=[];data['frontmatter']={}
        data['outline']=[dict(id='chapter',title='章',kind='chapter',level=1,parent_id=None),dict(id='one',title='前段',kind='section',level=2,parent_id='chapter'),dict(id='two',title='后段',kind='section',level=2,parent_id='chapter'),dict(id='glossary',title='词汇',kind='glossary',level=1,parent_id=None)]
        data['chapter_glossary']=[dict(chapter_id='chapter',chapter_title='章',entries=[dict(term_en='Basis',meaning_zh='基')])]
        data['pages']=[]
        for name,count in [('one',10),('two',6)]:
            blocks=[dict(id=f'{name}-{i}',type='definition',text='简短解释。',source_kind='authored_example') for i in range(count)]
            data['pages'].append(dict(id=name,title=name,chapter_id='chapter',type='knowledge_dense',outline_ids=(['chapter'] if name=='one' else [])+[name],blocks=[dict(id=name+'-group',type='group',blocks=blocks,source_kind='authored_example')],handwritten_layer=[],handwriting_reason='测试完整单元分页。'))
        data['pages'][1]['handwritten_layer']=[dict(anchor_block_id='two-0',kind='text',text='与首个知识块对应。',source_kind='editorial_synthesis')]
        with tempfile.TemporaryDirectory() as temp:
            path=Path(temp);(path/'input.json').write_text(json.dumps(data,ensure_ascii=False),encoding='utf-8')
            args=SimpleNamespace(content=path/'input.json',templates=SKILL/'Resources/templates',fonts=self.fonts,assets=SKILL/'Resources/illustrations',edition='print',output=path/'result.pdf',fun_mode='content',fun_seed=None,foldout_only=False)
            book=Book(args)
            self.assertEqual(len(book.content['pages']),2)
            self.assertNotIn('two',book.content['pages'][0]['outline_ids'])
            self.assertIn('two',book.content['pages'][1]['outline_ids'])
            self.assertEqual(book.content['pages'][1]['handwritten_layer'][0]['anchor_block_id'],'two-0')
            book.run()
            self.assertEqual(book.body_targets['two'],book.body_targets['one']+1)
            log=json.loads((path/'result.layout.json').read_text(encoding='utf-8'))
            self.assertEqual(log['review_status']['human_visual'],'not_run')
            self.assertEqual(log['review_status']['human_content'],'not_run')
            book.doc.close();book.master.close()

if __name__=='__main__':unittest.main()
