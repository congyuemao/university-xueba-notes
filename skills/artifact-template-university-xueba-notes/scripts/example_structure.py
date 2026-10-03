"""Lower a complete example into measured, independently paginated sections."""
from copy import deepcopy

def example_parts(example):
    e=deepcopy(example);parts=[]
    def part(key,title,value,identifier=None):
        pid=identifier or e['id']+'::'+key
        if isinstance(value,str):
            value=[dict(id=pid+'::text',type='paragraph',text=value,source_kind=e['source_kind'],language_level='L3')]
        # The section owns the vertical gap; do not add it again per child.
        for child in value:
            if child['type'] in {'paragraph','formula_step'}:child['space_after']=False
        parts.append(dict(id=pid,type='_example_part',part=key,title=title,content=value,
            example_id=e['id'],problem_number=e['problem_number'],source_kind=e['source_kind'],language_level='L3'))
    suffix=' 续' if e.get('continuation_of') else ''
    part('problem','典例 '+str(e['problem_number']).zfill(2)+suffix+' · 题目',e['problem'],e['id'])
    part('analysis','分析',e['analysis'])
    for step in e['steps']:part('step',str(step['label']).zfill(2)+' '+step['title'],step['content'],e['id']+'::step-'+str(step['label']))
    part('result','结果',e['result']);part('method','方法',e['method'])
    parts[0]['outline_ids']=e.get('outline_ids',[])
    parts[0]['keep_with_next']=True
    # Keep the result with its transferable method, while allowing steps to flow.
    parts[-2]['keep_with_next']=True
    return parts
