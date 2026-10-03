"""Page composition, anchored annotation allocation and balanced contents."""
from copy import deepcopy
import math
import warnings
from pdf_template_layout import *
from teaching_blocks import BlockEngine,LABELS
from content_schema import PAGE_PROFILES,PROBLEM_PAGES,MAP_PAGES,validate_v2,walk_blocks
from context_highlights import contextual_highlight_lines
from example_structure import example_parts
from language_review import language_findings

def balanced_pages(groups,heights,capacity):
    """Minimise page count, then uneven whitespace, at authored unit boundaries."""
    best={0:((0,0),[])}
    for end in range(1,len(groups)+1):
        used=0;candidates=[]
        for start in range(end-1,-1,-1):
            used+=heights[start]
            if used>capacity:break
            if start in best:
                (count,cost),parts=best[start]
                candidates.append(((count+1,cost+(capacity-used)**2),parts+[(start,end)]))
        if candidates:best[end]=min(candidates,key=lambda candidate:candidate[0])
    if len(groups) not in best:raise ValueError('Indivisible teaching unit exceeds page; split at an explained step')
    return [[block for group in groups[start:end] for block in group] for start,end in best[len(groups)][1]]

def balanced_columns(items,capacity):
    """Contiguous DP partition; keep-with-next chains cannot straddle columns.

    Find the fewest sheets, then balance all columns, including the last sheet.
    Entries store measured row heights; no invisible padding or fake entries.
    """
    if not items:return [[]]
    groups=[];group=[]
    for item in items:
        group.append(item)
        if not item.get('keep_next'):groups.append(group);group=[]
    if group:groups.append(group)
    hs=[sum(i['height'] for i in g) for g in groups]
    if max(hs)>capacity:raise ValueError('Contents parent/first-child chain exceeds one column')
    total=sum(hs)
    for sheets in range(1,len(groups)+1):
        k=min(sheets*2,len(groups));target=total/k;prefix=[0]
        for h in hs:prefix.append(prefix[-1]+h)
        dp={(0,0):(0,[])}
        for col in range(1,k+1):
            for end in range(col,len(groups)+1):
                candidates=[]
                for start in range(end-1,col-2,-1):
                    height=prefix[end]-prefix[start]
                    if height>capacity:break
                    if (col-1,start) in dp:
                        score,cuts=dp[col-1,start];candidates.append((score+(height-target)**2,cuts+[(start,end)]))
                if candidates:dp[col,end]=min(candidates,key=lambda v:v[0])
        if (k,len(groups)) in dp:
            cuts=dp[k,len(groups)][1]
            return [[i for g in groups[a:b] for i in g] for a,b in cuts]
    raise ValueError('Cannot paginate contents')

class BookCompositor:
    def prepare_v2(self):
        self.layout_metrics=[];self.composition_warnings=[];self.compiled=False
        self.v2=self.content.get('content_schema_version',1)==2
        if not self.v2:return
        validate_v2(self.content,self.assets)
        self.language_review=language_findings(self.content)
        if self.man.get('version',0)<7:raise ValueError('Schema v2 requires version 7 masters; rebuild templates')
        self.original_content=deepcopy(self.content);compiled=[];pending=[]
        # Adjacent knowledge sections of the same type flow together by default.
        for page in self.content['pages']:
            page=deepcopy(page)
            if page['blocks']:page['blocks'][0]['outline_ids']=list(dict.fromkeys(page['blocks'][0].get('outline_ids',[])+page.get('outline_ids',[])))
            if any(b['type']=='worked_example' for b in page['blocks']):
                page['_structured_example']=True
                page['blocks']=[part for b in page['blocks'] for part in (example_parts(b) if b['type']=='worked_example' else [b])]
            if pending and not page.get('page_break',False) and page['type']==pending[-1]['type'] and page['chapter_id']==pending[-1]['chapter_id'] and page['type'] not in PROBLEM_PAGES|MAP_PAGES:
                old=pending[-1];old['blocks']+=page['blocks'];old['handwritten_layer']+=page['handwritten_layer'];old.setdefault('sidebar',{}).setdefault('items',[]).extend(page.get('sidebar',{}).get('items',[]))
                old['outline_ids']=list(dict.fromkeys(old.get('outline_ids',[])+page.get('outline_ids',[])))
            else:pending.append(page)
        for page in pending:
            profile=PAGE_PROFILES[page['type']];limit=profile['rows'];self.g=self.man['editions'][self.a.edition][page['type']+'_odd']
            groups=[];current=[]
            for block in page['blocks']:
                current.append(block)
                if not block.get('keep_with_next') and block['type']!='heading':groups.append(current);current=[]
            if current:groups.append(current)
            row=2;chunks=[];chunk=[]
            if page['type'] in PROBLEM_PAGES and not page.get('_structured_example'):
                row=self.problem_header(page,BlockEngine(self,False),self.g['main_x'],self.g['main_w'])
                footer=len(wrap('结论　'+page['solution'],self.g['main_w'],'Body',11.6))+len(wrap('方法　'+page['method'],self.g['main_w'],'Body',11))
                limit-=footer
            for group in groups:
                size=sum(BlockEngine(self,False).measure(b,self.g['main_w']) for b in group)
                if size>limit-row and chunk:
                    chunks.append(chunk);chunk=[];row=2
                if size>limit-row:raise ValueError(page['id']+': indivisible teaching unit exceeds page; split at an explained step')
                chunk+=group;row+=size
            if chunk:chunks.append(chunk)
            if not (page['type'] in PROBLEM_PAGES and not page.get('_structured_example')):
                heights=[sum(BlockEngine(self,False).measure(b,self.g['main_w']) for b in group) for group in groups]
                chunks=balanced_pages(groups,heights,limit-2)
            if page['type'] in PROBLEM_PAGES and not page.get('_structured_example') and len(chunks)>1:raise ValueError(page['id']+': complete problem page overflow; use worked_example with structured steps')
            for i,blocks in enumerate(chunks):
                p=deepcopy(page);p['blocks']=blocks;p['id']=page['id']+(f'-cont-{i}' if i else '');p['number']=len(compiled)+1
                ids={b['id'] for b in walk_blocks(blocks)}
                p['handwritten_layer']=[a for a in page['handwritten_layer'] if a['anchor_block_id'] in ids]
                p['sidebar']={'items':[a for a in page.get('sidebar',{}).get('items',[]) if a['anchor_block_id'] in ids]}
                p['outline_ids']=list(dict.fromkeys(oid for b in walk_blocks(blocks) for oid in b.get('outline_ids',[])))
                if i:
                    first=blocks[0]
                    if first.get('example_id') and first.get('part')!='problem':
                        p['title']='典例 '+str(first['problem_number']).zfill(2)+' 续 · '+page['title']
                        p['continuation_of']=first['example_id']
                    else:p['title']=page['title']+'（续）'
                compiled.append(p)
        # Never silently discard annotations pointing to a different input page.
        expected=sum(len(p.get('handwritten_layer',[]))+len(p.get('sidebar',{}).get('items',[])) for p in pending)
        actual=sum(len(p['handwritten_layer'])+len(p['sidebar']['items']) for p in compiled)
        if expected!=actual:raise ValueError('Annotation anchor must belong to its input page/flow group')
        self.content['pages']=compiled;self.compiled=True

    def problem_header(self,page,engine,x,w):
        engine.say(str(page['problem_number']).zfill(2),x,self.y(2),'Latin',25,RED)
        row=2
        row=engine.lines(page['problem'],x+14,row,w-14,'Body',11.6)
        row=engine.lines('分析　'+page['analysis'],x,row+1,w,'Body',11.6)
        return row

    def frontmatter(self):
        if not self.v2:return self.legacy_frontmatter()
        settings=self.content.get('frontmatter',{}).get('contents',{});numbers=self.outline_numbers()
        geo=self.man['editions'][self.a.edition]['contents_odd'];gap=9;cw=(geo['main_w']-gap)/2
        visuals={v['outline_id']:v for v in settings.get('visuals',[])};items=[]
        nodes=[n for n in self.content['outline'] if n.get('include_in_toc',True)]
        styles={'part':('Head',11.4,BLUE),'chapter':('Head',11,RED),'unit':('Head',11,RED),'feature':('Head',10.1,BLUE),'chapter_map':('Head',10.1,BLUE),'volume_map':('Head',10.1,BLUE),'appendix':('Head',10.5,BLUE),'glossary':('Head',10.5,BLUE)}
        for index,n in enumerate(nodes):
            font,size,color=styles.get(n['kind'],('Body',10.6,INK));indent=max(0,n['level']-1)*3
            title=(str(n.get('ordinal_label',''))+' '+n['title']).strip();ls=wrap(title,cw-indent-13,font,size)
            visual=visuals.get(n['id']);height=len(ls)+(.8 if n['kind'] in {'part','chapter','appendix'} else .25)+(visual.get('height_rows',5) if visual else 0)
            keep=index+1<len(nodes) and nodes[index+1].get('parent_id')==n['id']
            items.append({'node':n,'lines':ls,'height':height,'font':font,'size':size,'color':color,'indent':indent,'keep_next':keep,'visual':visual})
        columns=balanced_columns(items,30)
        for i in range(0,len(columns),2):
            role='contents_odd' if (len(self.doc)+1)%2 else 'contents_even';self.start(role)
            title=settings.get('title','知识目录')+('续' if i else '')
            self.furniture(title,settings.get('humour',''));self.contents_pdf_page=self.contents_pdf_page if self.contents_pdf_page is not None else len(self.doc)
            heights=[]
            for j,column in enumerate(columns[i:i+2]):
                row=3;x=self.g['main_x']+j*(cw+gap)
                for entry in column:
                    n=entry['node'];indent=entry['indent'];top=self.y(row)-5;right=x+cw
                    if n['id'] not in numbers:raise ValueError(n['id']+': outline has no page anchor')
                    if n['kind'] in {'part','appendix','feature','chapter_map','volume_map'}:rect(self.c,x,top,cw,len(entry['lines'])*self.pitch,'#EDF3D8' if n['kind'] in {'part','appendix'} else '#EDF6F7')
                    for s in entry['lines']:self.say(s,x+indent,self.y(row),entry['font'],entry['size'],entry['color'],grid=True);row+=1
                    last=entry['lines'][-1];left=x+indent+width(last,entry['font'],entry['size'])+2
                    if left<right-10:
                        self.c.setDash(1,2);line(self.c,left,self.y(row-1)-.7,right-9,self.y(row-1)-.7,'#9AABAD',.35);self.c.setDash()
                    self.say(str(numbers[n['id']]),right,self.y(row-1),'Latin',10,entry['color'],'right',grid=True)
                    self.contents_links.append((len(self.doc),n['id'],[x,top,right,self.y(row-1)+1]))
                    if entry['visual']:
                        v=entry['visual'];hh=v.get('height_rows',5)*self.pitch
                        if v.get('drawing'):BlockEngine(self).drawing(v['drawing'],x+2,self.y(row)-3,cw-4,hh-6)
                        elif v.get('asset'):self.image(v['asset'],x+2,self.y(row)-3,cw-4,hh-6)
                        row+=v.get('height_rows',5)
                    row+=entry['height']-len(entry['lines'])-(entry['visual'].get('height_rows',5) if entry['visual'] else 0)
                heights.append(row-3)
            self.page_extra={'contents_column_rows':heights,'contents_density':sum(heights)/60}
            if i+2>=len(columns) and sum(heights)/60<settings.get('last_page_min_density',.35):self.composition_warnings.append('Last contents page is sparse; edit groups or add a relevant toc visual')
            self.finish()

    def chapter(self):
        if not self.v2:return self.legacy_chapter()
        chapters={n['id']:n['title'] for n in self.content['outline']};metrics=[];last_type=None;run=0
        for page in self.content['pages']:
            n=page['number'];ptype=page['type'];role=ptype+('_odd' if n%2 else '_even')
            self.start(role,n);self.content['chapter']=chapters[page['chapter_id']]
            for oid in page.get('outline_ids',[]):self.body_targets.setdefault(oid,len(self.doc))
            self.furniture(page['title'],page.get('humour',''),n)
            self.engine=BlockEngine(self);row=2
            if ptype in PROBLEM_PAGES and not page.get('_structured_example'):row=self.problem_header(page,self.engine,self.g['main_x'],self.g['main_w'])
            end=self.engine.many(page['blocks'],row,self.g['main_x'],self.g['main_w'])
            if ptype in PROBLEM_PAGES and not page.get('_structured_example'):
                end=self.engine.lines('结论　'+page['solution'],self.g['main_x'],end,self.g['main_w'])
                end=self.engine.lines('方法　'+page['method'],self.g['main_x'],end,self.g['main_w'],'Body',11,BLUE)
            if end>PAGE_PROFILES[ptype]['rows']:raise ValueError(f'{page["id"]}: {end} rows exceed capacity')
            self.sidebar_occupancy={};self.annotation_records=[]
            notes=[(item,False) for item in page.get('sidebar',{}).get('items',[])]+[(item,True) for item in page['handwritten_layer']]
            # Allocate by the rendered anchor, not by whether it was authored
            # as a sidebar or handwriting. A late sidebar must not push an
            # earlier handwritten note to the foot of the page.
            notes.sort(key=lambda pair:self.engine.boxes[pair[0]['anchor_block_id']]['end' if pair[0].get('after_anchor',True) else 'row'])
            for item,hand in notes:self.anchored_note(item,hand)
            side_widths=[self.g['side_w']]+([self.g['left_w']] if self.a.edition=='digital' else [])
            total=sum(side_widths)*32*self.pitch;used=sum(a['w']*(a['end']-a['row'])*self.pitch for entries in self.sidebar_occupancy.values() for a in entries)
            m={'page_id':page['id'],'chapter_id':page['chapter_id'],'type':ptype,'body_rows':end-2,'body_density':(end-2)/(PAGE_PROFILES[ptype]['rows']-2),'annotation_total_mm2':total,'annotation_used_mm2':used,'working_diagrams':sum(t in {'concept_diagram','knowledge_map'} for t in self.engine.types),'tables':self.engine.types.count('table')+self.engine.types.count('comparison_table'),'comics':sum(bool(i.get('comic')) for i in page.get('sidebar',{}).get('items',[])),'handwritten_items':len(page['handwritten_layer']),'block_types':self.engine.types}
            run=run+1 if ptype==last_type else 1;last_type=ptype
            if run==3:self.composition_warnings.append(page['id']+': review three repeated page structures')
            if m['body_density']<PAGE_PROFILES[ptype]['min_density'] and used/total<.25:self.composition_warnings.append(page['id']+': body and sidebar are both sparse')
            self.vector_assets=self.engine.vectors;self.page_extra={'composition':m,'blocks':self.engine.boxes,'annotations':self.annotation_records,'language_findings':self.engine.language_findings};metrics.append(m);self.finish()
        for cid in {m['chapter_id'] for m in metrics}:
            subset=[m for m in metrics if m['chapter_id']==cid];free=1-sum(m['annotation_used_mm2'] for m in subset)/sum(m['annotation_total_mm2'] for m in subset)
            target=self.content.get('annotation_policy',{}).get('chapter_min_free_fraction',.35)
            if free<target:raise ValueError(f'{cid}: measured chapter annotation free fraction {free:.3f} < {target}')
            if len(subset)>=3 and not any(m['type'] in PROBLEM_PAGES for m in subset):self.composition_warnings.append(cid+': assess an integrated application page')
            self.layout_metrics.append({'chapter_id':cid,'annotation_free_fraction':free,'pages':subset,'page_type_counts':{t:sum(m['type']==t for m in subset) for t in {m['type'] for m in subset}}})

    def anchored_note(self,item,hand):
        anchor=self.engine.boxes.get(item['anchor_block_id'])
        if anchor is None:raise ValueError('Annotation anchor not on rendered page: '+item['anchor_block_id'])
        kind=item.get('kind','text');side=item.get('side','outer')
        if side=='inline':
            if kind not in {'circle','underline','wave','bracket','strike'}:raise ValueError('Inline marks support circle, underline, wave, bracket or strike')
            if item.get('target_span'):
                block=next(b for p in self.content['pages'] for b in walk_blocks(p['blocks']) if b['id']==item['anchor_block_id'])
                if block['type'] not in {'paragraph','definition','property','rule','condition','example_inline','common_error','memory_note','diagram_explanation','method_card'}:raise ValueError('target_span requires a text-bearing block')
                span={**item['target_span'],'reason':'Author-selected handwriting target'}
                title_font='Hand' if block['type']=='memory_note' else 'Head'
                row=anchor['row']+(0 if block['type']=='paragraph' else len(wrap((block.get('title') or LABELS[block['type']])+(' '+block['symbol'] if block.get('symbol') else ''),anchor['w'],title_font,11)))
                font,size=('Latin',11) if block.get('language')=='en' else ('Body',11.6)
                for j,(s,fragments) in enumerate(contextual_highlight_lines(block['text'],wrap(block['text'],anchor['w'],font,size),[span])):
                    for start,end in fragments:
                        box=[anchor['x']+width(s[:start],font,size),self.y(row+j)-4.2,width(s[start:end],font,size),5]
                        self.mark(kind,box);self.annotation_records.append({'anchor':item['anchor_block_id'],'kind':kind,'side':'inline','box_mm':box,'text':s[start:end]})
                return
            if item.get('target_cell'):
                r,c=item['target_cell'];anchor=self.engine.boxes.get(f'{item["anchor_block_id"]}@{r},{c}')
                if anchor is None:raise ValueError('Invalid annotation target cell')
            box=[anchor['x'],self.y(anchor['row'])-4.5,anchor['w'],(anchor['end']-anchor['row'])*self.pitch-1]
            self.mark(kind,box)
            self.annotation_records.append({'anchor':item['anchor_block_id'],'kind':kind,'side':'inline','box_mm':box});return
        left=self.a.edition=='digital' and side=='left';x=self.g['left_x'] if left else self.g['side_x'];w=self.g['left_w'] if left else self.g['side_w']
        key='left' if left else 'outer';font='Hand' if hand else 'Body';size=12 if hand else 10.4
        ls=wrap(item.get('text',''),w-3,font,size);nr=len(ls)+(1 if item.get('title') else 0)+(item.get('height_rows',4) if item.get('drawing') or item.get('comic') or item.get('asset') else 0)
        row=max(2,anchor['end'] if item.get('after_anchor',True) else anchor['row']+1)
        intervals=self.sidebar_occupancy.setdefault(key,[])
        for old in intervals:
            if row<old['end']+.5 and row+nr>old['row']:row=old['end']+.5
        if row+nr>33:raise ValueError(f'Page {self.no}: annotation {item["anchor_block_id"]} overflows ({row}+{nr} rows); shorten, move its anchor or allocate another page')
        intervals.append({'row':row,'end':row+nr,'w':w})
        top=row
        if item.get('title'):self.say(item['title'],x,self.y(row),'Head',10,BLUE,grid=True);row+=1
        if hand and kind=='arrow_note':
            sx=x-1 if x>anchor['x'] else x+w+1;ex=anchor['x']+anchor['w']+1 if sx>anchor['x'] else anchor['x']-1
            self.curve_arrow(sx,self.y(row)-2,ex,self.y(anchor['end']-1)-1)
        for i,s in enumerate(ls):
            if hand:
                # Rotation stays inside its measured reservation; only handwriting deviates from the baseline.
                c=self.c;c.saveState();c.translate(x*MM,(297-self.y(row))*MM);c.rotate((-.7,.45,-.35)[i%3]);text(c,s,0,0,font,size,RED,page_h=0);c.restoreState()
            else:self.say(s,x,self.y(row),font,size,INK,grid=True)
            row+=1
        if item.get('drawing'):self.engine.drawing(item['drawing'],x,self.y(row)-4,w,item.get('height_rows',4)*self.pitch-3)
        if item.get('comic') or item.get('asset'):self.image(item.get('comic',item.get('asset')),x,self.y(row)-4,w,item.get('height_rows',4)*self.pitch-3)
        self.annotation_records.append({'anchor':item['anchor_block_id'],'kind':kind,'side':key,'row':top,'end':top+nr,'text':item.get('text','')})

    def curve_arrow(self,x1,y1,x2,y2):
        c=self.c;p=c.beginPath();p.moveTo(x1*MM,(297-y1)*MM);p.curveTo((x1+(x2-x1)*.5)*MM,(297-y1+2)*MM,(x2-1)*MM,(297-y2-1)*MM,x2*MM,(297-y2)*MM);c.setStrokeColor(RED);c.setLineWidth(.65);c.drawPath(p)
        sign=1 if x2>x1 else -1
        line(c,x2,y2,x2-sign*2,y2-1,RED,.65);line(c,x2,y2,x2-sign*2,y2+1,RED,.65)
    def mark(self,kind,box):
        x,y,w,h=box;c=self.c;c.setStrokeColor(RED);c.setLineWidth(.65)
        if kind=='circle':c.ellipse(x*MM,(297-y-h)*MM,(x+w)*MM,(297-y)*MM,stroke=1,fill=0)
        elif kind=='underline':line(c,x,y+h,x+w,y+h-.4,RED,.65)
        elif kind=='strike':line(c,x,y,x+w,y+h,RED,.65);line(c,x+w,y,x,y+h,RED,.65)
        elif kind=='bracket':
            line(c,x+2,y,x,y+1,RED,.65);line(c,x,y+1,x,y+h-1,RED,.65);line(c,x,y+h-1,x+2,y+h,RED,.65)
        else:
            for i in range(max(1,int(w/2))):line(c,x+i*2,y+h+(i%2)*.6,min(x+w,x+(i+1)*2),y+h+((i+1)%2)*.6,RED,.65)
