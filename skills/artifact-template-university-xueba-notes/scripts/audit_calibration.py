"""Audit bundled LP/simplex/DP calibration PDFs. Requires PyMuPDF, no fonts.

This verifies machine-observable geometry and navigation, not teaching quality.
Page counts come from actual composition, not an old fixed-length fixture.
"""
from pathlib import Path
import fitz,json,hashlib
import argparse
parser=argparse.ArgumentParser(description='Read-only checks of the three bundled calibration PDFs and their layout logs.')
parser.add_argument('--examples',type=Path,default=Path(__file__).resolve().parents[1]/'Resources/examples')
parser.add_argument('--output',type=Path)
args=parser.parse_args();root=args.examples;report={}
for name,edition in [('打印版','print'),('电子版','digital'),('知识折页','foldout')]:
 p=root/f'calibration-{edition}.pdf';doc=fitz.open(p);log=json.loads(p.with_suffix('.layout.json').read_text(encoding='utf-8'))
 compiled=json.loads(p.with_suffix('.compiled.json').read_text(encoding='utf-8'))
 assert len(doc)==len(log['pages'])
 if edition=='foldout':assert len(doc)==1
 else:assert len([page for page in log['pages'] if 'composition' in page])==len(compiled['pages'])
 errors=[];fonts=set();fun_ids=[]
 for page,entry in zip(doc,log['pages']):
  target=(594,210) if edition=='foldout' else (210,297)
  assert abs(page.rect.width-target[0]*72/25.4)<.1 and abs(page.rect.height-target[1]*72/25.4)<.1
  for block in page.get_text('dict')['blocks']:
   for line in block.get('lines',[]):
    for span in line['spans']:
     fonts.add(span['font']);x0,y0,x1,y1=span['bbox'];text=span['text']
     if '\ufffd' in text or '\x00' in text:errors.append((entry['pdf_page'],'missing glyph',text))
     if x0<-.2 or y0<-.2 or x1>page.rect.width+.2 or y1>page.rect.height+.2:errors.append((entry['pdf_page'],'page overflow',text))
     if edition=='print' and entry.get('logical_page'):
      odd=entry['logical_page']%2==1
      if (odd and x0<20*72/25.4-.7) or (not odd and x1>190*72/25.4+.7):errors.append((entry['pdf_page'],'binding margin',text))
  if entry.get('fun_content'):fun_ids.append(entry['fun_content']['id'])
  by_side={}
  for note in entry.get('annotations',[]):
   if note['side']=='inline':continue
   assert note['end']<=33
   by_side.setdefault(note['side'],[]).append((note['row'],note['end']))
  for intervals in by_side.values():
   intervals.sort()
   assert all(a[1]<=b[0] for a,b in zip(intervals,intervals[1:]))
  if 'composition' in entry:
   for box in entry['blocks'].values():assert box['end']<=32
   assert entry['composition']['body_density']<=1
 assert len(fun_ids)==len(set(fun_ids))
 assert not errors,errors
 if edition!='foldout':
  assert any('XuebaBody' in f for f in fonts) and any('XuebaHand' in f for f in fonts)
  assert len(doc.get_toc())>=len(compiled['outline'])
  links=[link for page in doc for link in page.get_links()]
  assert len(links)>=len([n for n in compiled['outline'] if n.get('include_in_toc',True)])
  for link in links:assert 0<=link['page']<len(doc)
 # Composition warnings are editorial candidates and require a separate review.
 # The audit reports them without treating them as geometric corruption.
 report[edition]={'pdf_pages':len(doc),'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'size_bytes':p.stat().st_size,'warnings':log['warnings'],'checks':['page size','text clipping/missing glyphs','print text binding margin','sidebar overlap and height','block vertical bounds','unique fun strips','embedded Body/Hand (books)','contents links (books)'],'chapters':[{k:c[k] for k in ('chapter_id','annotation_free_fraction','page_type_counts')} for c in log['chapters']],'body_pages':len([e for e in log['pages'] if 'composition' in e]),'contents_column_rows':[e['contents_column_rows'] for e in log['pages'] if 'contents_column_rows' in e]}
 report[edition]['language_findings']=log.get('language_findings',[])+[dict(pdf_page=page['pdf_page'],**f) for page in log['pages'] for f in page.get('language_findings',[])]
 print(name,len(doc),[(c['chapter_id'],round(c['annotation_free_fraction'],3)) for c in log['chapters']])
if args.output:
 args.output.parent.mkdir(parents=True,exist_ok=True)
 args.output.write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
print('PDF audit passed')
