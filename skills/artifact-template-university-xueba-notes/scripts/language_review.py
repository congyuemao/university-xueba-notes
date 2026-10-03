"""Editorial candidates, not automatic judgements of language quality."""
import re
from content_schema import walk_blocks, TEXT_TYPES, PROBLEM_PAGES

DEPENDENCIES=('沿用','接上','如前','前述','上一轮','继续')

def plain_text(value):
    if isinstance(value,str):return value
    if isinstance(value,list):
        return '\n'.join(str(b.get('text',b.get('formula',''))) for b in walk_blocks(value))
    return ''

def language_findings(data):
    findings=[]
    def check_problem(value,where,continuation=False):
        found=[word for word in DEPENDENCIES if word in plain_text(value)]
        if found and not continuation:
            findings.append(dict(code='context_dependency',severity='manual_review',block_id=where,terms=found))
    for page in data.get('pages',[]):
        if page.get('type') in PROBLEM_PAGES and page.get('problem'):
            check_problem(page['problem'],page['id'])
        for block in walk_blocks(page.get('blocks',[])):
            if block['type']=='worked_example':check_problem(block['problem'],block['id'],bool(block.get('continuation_of')))
            if block['type'] in TEXT_TYPES:
                for i,paragraph in enumerate(re.split(r'\n\s*\n',block['text'])):
                    markers=re.findall(r'先|再|然后|接着|最后',paragraph)
                    if len(markers)>=3:
                        findings.append(dict(code='compressed_steps',severity='manual_review',block_id=block['id'],paragraph=i+1,markers=markers))
    return findings

def paragraph_finding(block_id,paragraph,lines,row,level=None):
    if lines<=4:return None
    return dict(code='long_paragraph',severity='manual_review' if lines>=6 else 'warning',block_id=block_id,paragraph=paragraph,line_count=lines,row=row,language_level=level)
