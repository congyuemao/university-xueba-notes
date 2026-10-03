"""Version 2 executable content contract. Legacy v1 is read-only compatible.

This validates fields and references, never certifies teaching or visual quality.
"""
from pathlib import Path

PAGE_PROFILES = {
    'knowledge_dense': dict(rows=32, min_density=.65, slots=['knowledge','table','hand','sidebar']),
    'knowledge_visual': dict(rows=32, min_density=.60, slots=['figure','paired','hand','sidebar']),
    'comparison_page': dict(rows=32, min_density=.60, slots=['comparison','formula','hand','sidebar']),
    'worked_example_page': dict(rows=31, min_density=.60, slots=['problem_number','problem','analysis','solution','method','figure','hand','sidebar']),
    'application_page': dict(rows=31, min_density=.60, slots=['problem_number','problem','analysis','solution','method','table','hand','sidebar']),
    'core_problem_page': dict(rows=31, min_density=.60, slots=['problem_number','problem','analysis','solution','method','figure','hand','sidebar']),
    'chapter_map': dict(rows=32, min_density=.55, slots=['organic_map','formula_node','figure_node','hand','sidebar']),
    'volume_map': dict(rows=32, min_density=.55, slots=['organic_map','formula_node','figure_node','hand','sidebar']),
    'process_page': dict(rows=32, min_density=.60, slots=['steps','trace','table','hand','sidebar']),
    'formula_summary': dict(rows=32, min_density=.60, slots=['formula_group','conditions','table','hand','sidebar']),
    'glossary': dict(rows=31, min_density=.45, slots=['two_columns','chapter_labels']),
    'foldout': dict(rows=22, min_density=.55, slots=['four_columns','formula','notes','example']),
}
PROBLEM_PAGES={'worked_example_page','application_page','core_problem_page'}
MAP_PAGES={'chapter_map','volume_map'}
TEXT_TYPES={'paragraph','definition','property','rule','condition','example_inline','common_error','memory_note','diagram_explanation','method_card'}
BLOCK_TYPES=TEXT_TYPES|{'heading','formula','formula_relation','formula_group','property_list','worked_micro_example','comparison','comparison_table','table','process_steps','concept_diagram','knowledge_map','paired','group','handwritten_annotation','comparison_bars'}
SOURCE_KINDS={'textbook_core','course_core','authored_example','supplement','editorial_synthesis'}
HAND_KINDS={'text','arrow_note','circle','underline','wave','bracket','strike','sketch'}
OUTLINE_KINDS={'part','chapter','unit','section','lesson','feature','appendix','glossary','chapter_map','volume_map'}

def walk_blocks(blocks):
    for b in blocks:
        yield b
        if b.get('type')=='group':yield from walk_blocks(b.get('blocks',[]))
        if b.get('type')=='paired':
            yield from walk_blocks(b.get('left',[]));yield from walk_blocks(b.get('right',[]))

def validate_v2(data, assets=None):
    """Fail before PDF creation on missing fields, orphan anchors or false sources."""
    if data.get('content_schema_version',1)==1:return
    if data.get('content_schema_version')!=2:raise ValueError('Unsupported content_schema_version')
    errors=[]
    def need(ok,msg):
        if not ok:errors.append(msg)
    def drawing(items,where):
        for p in items:
            kind=p.get('kind');need(kind in {'line','polyline','polygon','arrow','circle','label'},f'{where}: unknown drawing primitive')
            if kind in {'line','polyline','polygon','arrow'}:
                points=p.get('points',[])
                need(len(points)>=(3 if kind=='polygon' else 2),f'{where}: drawing needs points')
                for x,y in points:need(0<=x<=100 and 0<=y<=100,f'{where}: drawing outside normalized slot')
            if kind in {'circle','label'}:
                need(all(isinstance(p.get(a),(int,float)) and 0<=p[a]<=100 for a in ('x','y')),f'{where}: drawing outside normalized slot')
            if kind=='label':need(bool(p.get('text')),f'{where}: empty drawing label')
            if kind=='circle':need(isinstance(p.get('r',2),(int,float)) and p.get('r',2)>0,f'{where}: invalid circle radius')
    need(data.get('learning_mode','learning') in {'learning','revision'},'learning_mode must be learning or revision')
    sources={s['id']:s for s in data.get('sources',[])}
    need(len(sources)==len(data.get('sources',[])),'Duplicate source IDs')
    for sid,s in sources.items():
        need(bool(s.get('title')) and bool(s.get('locator')),f'{sid}: source title and locator required')
    outline={n['id']:n for n in data.get('outline',[])}
    need(len(outline)==len(data.get('outline',[])),'Duplicate outline IDs')
    for oid,n in outline.items():
        need(n.get('kind') in OUTLINE_KINDS,f'{oid}: unknown outline kind')
        parent=outline.get(n.get('parent_id'))
        need((parent and n['level']==parent['level']+1) or (not n.get('parent_id') and n['level']==1),f'{oid}: invalid hierarchy')
        if parent:need(list(outline).index(n['parent_id'])<list(outline).index(oid),f'{oid}: outline parent must precede child')
        if n.get('source_kind') in {'supplement','editorial_synthesis'}:
            need(not n.get('textbook_chapter_number'),f'{oid}: authored material cannot use a textbook chapter number')
        if n.get('textbook_chapter_number'):
            need(n.get('source_id') in sources and bool(n.get('source_section')),f'{oid}: textbook chapter needs source mapping')
    all_blocks={};page_ids=set();pending=[]
    need(isinstance(data.get('pages'),list) and bool(data['pages']),'pages must be nonempty')
    for page in data.get('pages',[]):
        pid=page.get('id');need(bool(pid) and pid not in page_ids,'Missing or duplicate page ID');page_ids.add(pid)
        need(page.get('type') in PAGE_PROFILES and page['type'] not in {'glossary','foldout'},f'{pid}: invalid body page type')
        need(page.get('chapter_id') in outline,f'{pid}: chapter_id required')
        need(bool(page.get('title')) and bool(page.get('blocks')),f'{pid}: title and blocks required')
        for ref in page.get('outline_ids',[]):need(ref in outline,f'{pid}: unknown outline anchor {ref}')
        need(isinstance(page.get('handwritten_layer'),list),f'{pid}: handwritten_layer assessment required (empty list is allowed with reason)')
        if not page.get('handwritten_layer'):need(bool(page.get('handwriting_reason')),f'{pid}: explain why handwriting is unnecessary')
        if page.get('type') in PROBLEM_PAGES:
            for key in ('problem_number','problem','analysis','solution','method'):
                need(bool(page.get(key)),f'{pid}: problem page requires {key}')
        blocks=list(walk_blocks(page.get('blocks',[])))
        if page.get('type') in MAP_PAGES:need(any(b.get('type')=='knowledge_map' for b in blocks),f'{pid}: map page needs organic knowledge_map')
        for b in blocks:
            bid=b.get('id');need(bool(bid) and bid not in all_blocks,f'{pid}: missing or duplicate block ID {bid}');all_blocks[bid]=b
            typ=b.get('type');need(typ in BLOCK_TYPES,f'{bid}: unknown block type {typ}')
            need(b.get('source_kind') in SOURCE_KINDS,f'{bid}: source_kind required')
            if b.get('source_kind') in {'textbook_core','course_core'}:
                need(b.get('source_id') in sources and bool(b.get('source_section')),f'{bid}: source_id and source_section required')
            if typ in TEXT_TYPES|{'heading','formula'}:need(isinstance(b.get('text'),str) and bool(b['text'].strip()),f'{bid}: text required')
            if typ in {'property_list','formula_group','formula_relation'}:need(bool(b.get('items')),f'{bid}: items required')
            if typ=='process_steps':need(bool(b.get('steps')),f'{bid}: steps required')
            if typ=='worked_micro_example':
                for key in ('problem','steps','answer'):need(bool(b.get(key)),f'{bid}: {key} required')
            if typ in {'table','comparison','comparison_table'}:
                headers=b.get('headers',b.get('columns',[]));rows=b.get('rows',[])
                need(bool(headers) and bool(rows),f'{bid}: table headers and rows required')
                need(all(len(r)==len(headers) for r in rows),f'{bid}: ragged table')
                for mark in b.get('cell_marks',[]):need(0<=mark['row']<=len(rows) and 0<=mark['col']<len(headers),f'{bid}: cell mark outside table')
            if typ=='concept_diagram':
                need(bool(b.get('caption')),f'{bid}: diagram needs explanation caption')
                need(bool(b.get('asset')) != bool(b.get('drawing')),f'{bid}: exactly one asset or drawing required')
                need(type(b.get('height_rows')) is int and 2<=b['height_rows']<=28,f'{bid}: height_rows 2..28 required')
                if b.get('asset') and assets is not None:need((Path(assets)/b['asset']).is_file(),f'{bid}: missing asset')
                drawing(b.get('drawing',[]),bid)
            if typ=='knowledge_map':
                need(bool(b.get('tree',{}).get('children')),f'{bid}: tree children required')
                need(type(b.get('height_rows')) is int and 2<=b['height_rows']<=28,f'{bid}: height_rows 2..28 required')
                def visit_tree(node,depth=1):
                    need(bool(node.get('label')),f'{bid}: map label required')
                    need(depth<=4,f'{bid}: map exceeds four levels')
                    drawing(node.get('drawing',[]),bid)
                    for child in node.get('children',[]):visit_tree(child,depth+1)
                visit_tree(b.get('tree',{}))
            if typ=='group':need(bool(b.get('blocks')),f'{bid}: group must be nonempty')
            if typ=='paired':
                need(bool(b.get('left')) and bool(b.get('right')),f'{bid}: paired requires both columns')
                need(.2<=b.get('ratio',.52)<=.8,f'{bid}: paired ratio must be .2..8')
            if typ=='condition':
                need(b.get('boundary_level') in {'A','B','C'},f'{bid}: boundary_level required')
                if b.get('boundary_level')=='C':need(bool(b.get('course_required')) or b.get('source_kind')=='supplement',f'{bid}: advanced boundary must be course-required or supplementary')
            if typ=='handwritten_annotation':pending.append((pid,b))
        pending.extend((pid,b) for b in page.get('handwritten_layer',[]))
        pending.extend((pid,b) for b in page.get('sidebar',{}).get('items',[]))
    for pid,b in pending:
        need(b.get('anchor_block_id') in all_blocks,f'{pid}: orphan annotation anchor {b.get("anchor_block_id")}')
        if b.get('type')=='handwritten_annotation' or b.get('kind') in HAND_KINDS:
            need(b.get('kind') in HAND_KINDS,f'{pid}: unknown handwritten kind')
        need(b.get('source_kind') in SOURCE_KINDS,f'{pid}: annotation source_kind required')
        if b.get('source_kind') in {'textbook_core','course_core'}:need(b.get('source_id') in sources and bool(b.get('source_section')),f'{pid}: annotation source mapping required')
        need(b.get('side','outer') in {'outer','left','inline'},f'{pid}: invalid annotation side')
        drawing(b.get('drawing',[]),pid)
        if b.get('drawing') or b.get('comic') or b.get('asset'):need(type(b.get('height_rows')) is int and 1<=b['height_rows']<=28,f'{pid}: annotation height_rows required')
        anchor=all_blocks.get(b.get('anchor_block_id'))
        if b.get('target_span') and anchor:
            need(anchor['type'] in TEXT_TYPES,f'{pid}: target_span needs a text-bearing anchor')
            if anchor['type'] in TEXT_TYPES:
                from context_highlights import validate_highlights
                try:validate_highlights(anchor['text'],[{**b['target_span'],'reason':'Author-selected handwriting target'}])
                except ValueError as err:errors.append(str(err))
        if b.get('target_cell') and anchor:
            cell=b['target_cell'];need(anchor['type'] in {'table','comparison','comparison_table'},f'{pid}: target_cell needs a table')
            need(len(cell)==2 and all(type(i) is int for i in cell) and 0<=cell[0]<=len(anchor.get('rows',[])) and 0<=cell[1]<len(anchor.get('headers',anchor.get('columns',[]))),f'{pid}: target_cell outside table')
    for v in data.get('frontmatter',{}).get('contents',{}).get('visuals',[]):
        need(v.get('outline_id') in outline,'Contents visual needs outline anchor')
        need(bool(v.get('asset')) != bool(v.get('drawing')),'Contents visual needs exactly one asset or drawing')
        need(type(v.get('height_rows')) is int and 1<=v['height_rows']<=28,'Contents visual height_rows required')
        drawing(v.get('drawing',[]),'contents')
    concept_ids={c['id'] for c in data.get('concepts',[])}
    need(len(concept_ids)==len(data.get('concepts',[])),'Duplicate concept IDs')
    for c in data.get('concepts',[]):
        cid=c.get('id','concept')
        for f in ('importance','first_use_role','preferred_representation','boundary_level','requires_worked_example','requires_visual'):need(f in c,f'{cid}: missing {f}')
        need(c.get('importance') in {'core','supporting','extension'},f'{cid}: importance')
        need(c.get('first_use_role') in {'introduced','taught','reused'},f'{cid}: first_use_role')
        need(c.get('boundary_level') in {'A','B','C'},f'{cid}: boundary_level')
        for flag in ('requires_visual','requires_worked_example'):need(isinstance(c.get(flag),bool),f'{cid}: {flag} must be boolean')
        need(isinstance(c.get('preferred_representation'),list) and bool(c['preferred_representation']),f'{cid}: preferred_representation must be nonempty list')
        for ref in c.get('prerequisite_ids',[]):need(ref in concept_ids and ref!=cid,f'{cid}: invalid prerequisite {ref}')
        for flag,field,types in [('requires_visual','visual_refs',{'concept_diagram','knowledge_map','table','comparison_table'}),('requires_worked_example','example_refs',{'worked_micro_example','process_steps'})]:
            if c.get(flag):
                need(bool(c.get(field)),f'{cid}: {field} required')
                for ref in c.get(field,[]):need(ref in all_blocks and all_blocks[ref]['type'] in types,f'{cid}: invalid {field} {ref}')
        for role,refs in c.get('teaching_refs',{}).items():
            need(isinstance(refs,list) and bool(refs),f'{cid}: {role} needs block IDs')
            for ref in refs:need(ref in all_blocks,f'{cid}: unknown teaching block {ref}')
        if c.get('first_use_role')=='taught':
            for role in ('definition','plain_explanation','canonical_example','example_mapping','boundary'):need(bool(c.get('teaching_refs',{}).get(role)),f'{cid}: no {role} evidence')
    target=data.get('annotation_policy',{}).get('chapter_min_free_fraction',.35)
    need(isinstance(target,(int,float)) and 0<=target<=1,'Invalid chapter writing-space target')
    concepts={c['id']:c for c in data.get('concepts',[])}
    done=set();active=set()
    def visit_concept(cid):
        if cid in done:return
        if cid in active:errors.append(f'{cid}: cyclic prerequisites');return
        active.add(cid)
        for ref in concepts[cid].get('prerequisite_ids',[]):
            if ref in concepts:visit_concept(ref)
        active.remove(cid);done.add(cid)
    for cid in concepts:visit_concept(cid)
    if errors:raise ValueError('\n'.join(errors))
