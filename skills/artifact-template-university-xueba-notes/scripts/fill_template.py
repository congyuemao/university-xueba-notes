#!/usr/bin/env python3
"""Fill retained PDF masters with searchable chapter text and compact assets."""
import argparse,json,hashlib,math
from pathlib import Path
from io import BytesIO
import fitz
from PIL import Image
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from pdf_template_layout import *
from context_highlights import validate_content_highlights,contextual_highlight_lines
from pick_fun_content import DEFAULT_CATALOG,KINDS,FunPicker,UsageHistory,load_catalog,display_text,write_json
from book_compositor import BookCompositor
class Book(BookCompositor):
    def __init__(self,a,history=None):
        self.a=a;self.content=json.loads(Path(a.content).read_text(encoding='utf-8'));self.man=json.loads((Path(a.templates)/'template-manifest.json').read_text(encoding='utf-8'));self.src=Path(a.templates)/(a.edition+'-master.pdf');self.hash=hashlib.sha256(self.src.read_bytes()).hexdigest();self.master=fitz.open(self.src);self.doc=fitz.open();self.toc=[];self.logs=[];self.g=None;self.contents_links=[];self.body_targets={};self.contents_pdf_page=None;register_fonts(a.fonts)
        self.validate_schema()
        validate_content_highlights(self.content)
        grid=self.man['grid'];self.first=grid['first_baseline_mm'];self.pitch=grid['pitch_mm'];self.maxrows=grid['rows'];self.assets=Path(a.assets)
        self.history=history;self.fun_picker=None;self.fun_item=None;self.fun_lines_cache={}
        if a.fun_mode=='random' and not a.foldout_only:
            self.fun_picker=FunPicker(load_catalog(a.fun_catalog),seed=a.fun_seed,subjects=a.fun_subject,
                kinds=a.fun_types,include_general=a.fun_include_general,max_lines=a.fun_max_lines,history=history)
        self.prepare_v2()
    def validate_schema(self):
        legacy=[key for key in ('terminology_extended','answer_vocabulary') if key in self.content]
        if legacy:raise ValueError('Remove legacy fields: '+', '.join(legacy))
        front=self.content.get('frontmatter') or {}
        if 'glossary' in front:raise ValueError('frontmatter.glossary is no longer supported; use chapter_glossary at the end')
        outline=self.content.get('outline')
        if not isinstance(outline,list) or not outline:raise ValueError('outline must be a non-empty independent knowledge hierarchy')
        ids=set()
        for node in outline:
            if not isinstance(node,dict) or not isinstance(node.get('id'),str) or not node['id'].strip():raise ValueError('Every outline node needs an id')
            if node['id'] in ids:raise ValueError('Duplicate outline id '+node['id'])
            ids.add(node['id'])
            if not isinstance(node.get('title'),str) or not node['title'].strip():raise ValueError(node['id']+': outline title is required')
            if node.get('level') not in (1,2,3,4):raise ValueError(node['id']+': outline level must be 1–4')
        for node in outline:
            parent=node.get('parent_id')
            if parent and parent not in ids:raise ValueError(node['id']+': unknown outline parent '+str(parent))
        for page in self.content.get('pages') or []:
            for oid in page.get('outline_ids') or []:
                if oid not in ids:raise ValueError(f"Page {page.get('number')}: unknown outline id {oid}")
            sidebar=page.get('sidebar') or {}
            if 'english_terms' in sidebar or 'term_limit' in sidebar:raise ValueError(f"Page {page.get('number')}: sidebar English term lists were removed")
        glossary=self.content.get('chapter_glossary')
        if not isinstance(glossary,list) or not glossary:raise ValueError('chapter_glossary must contain the final chapter-grouped specialist glossary')
        seen=set()
        for group in glossary:
            if not isinstance(group,dict) or not group.get('chapter_id') or not group.get('chapter_title'):raise ValueError('Each glossary group needs chapter_id and chapter_title')
            if group['chapter_id'] not in ids:raise ValueError('Glossary group references unknown outline id '+str(group['chapter_id']))
            entries=group.get('entries')
            if not isinstance(entries,list) or not entries:raise ValueError(str(group.get('chapter_id'))+': glossary entries are required')
            for entry in entries:
                if not isinstance(entry,dict) or set(entry)!={'term_en','meaning_zh'}:raise ValueError('Glossary entries may contain only term_en and meaning_zh')
                term=entry.get('term_en');meaning=entry.get('meaning_zh')
                if not isinstance(term,str) or not term.strip() or not isinstance(meaning,str) or not meaning.strip():raise ValueError('Glossary term_en and meaning_zh must be non-empty')
                key=term.strip().casefold()
                if key in seen:raise ValueError('Duplicate glossary term '+term)
                seen.add(key)
    def y(self,row):return self.first+row*self.pitch
    def start(self,role,number=None):
        self.page_extra={};self.vector_assets=[]
        self.role=role;self.no=number;self.buf=BytesIO();self.h=210 if role=='foldout' else 297;self.w=594 if role=='foldout' else 210;self.c=canvas.Canvas(self.buf,pagesize=(self.w*MM,self.h*MM));LOG.clear()
        self.g=self.man['editions'][self.a.edition].get(role);self.fun_item=None
    def finish(self):
        self.c.showPage();self.c.save();overlay=fitz.open(stream=self.buf.getvalue(),filetype='pdf');p=self.doc.new_page(width=self.w*MM,height=self.h*MM);p.show_pdf_page(p.rect,self.master,self.man['roles'][self.role]);p.show_pdf_page(p.rect,overlay,0)
        for asset,box in self.vector_assets:
            source=fitz.open(asset)
            if not source.is_pdf:source=fitz.open(stream=source.convert_to_pdf(),filetype='pdf')
            p.show_pdf_page(fitz.Rect(*(v*MM for v in box)),source,0)
        self.logs.append({'pdf_page':len(self.doc),'logical_page':self.no,'role':self.role,'texts':list(LOG),'fun_content':self.fun_item,**self.page_extra})
    def say(self,s,x,y,font='Body',size=11.6,color=INK,align='left',grid=False):
        if s is not None and str(s):return text(self.c,str(s),x,y,font,size,color,align,self.h,grid)
    def furniture(self,title,joke,logical=None,opening=False):
        g=self.g;header=self.content.get('running_header') or {};self.say(header.get('left',self.content.get('subject','')),g['start'],11,'Head',9,BLUE);self.say(header.get('right',self.content.get('chapter','')),g['end'],11,'Body',9,INK,'right')
        strip=self.man['humour_strip'];available=g['end']-g['start']-2*strip['padding_mm']
        if self.fun_picker:
            def line_count(value):
                key=(value,available,strip['font'],strip['size_pt'])
                if key not in self.fun_lines_cache:
                    try:self.fun_lines_cache[key]=len(wrap(value,available,strip['font'],strip['size_pt']))
                    except ValueError:self.fun_lines_cache[key]=3
                return self.fun_lines_cache[key]
            self.fun_item=self.fun_picker.pick(line_count);joke=display_text(self.fun_item)
        lines=wrap(joke,available,strip['font'],strip['size_pt'])
        if len(lines)>strip['max_lines']:raise ValueError('Humour exceeds the two-line bottom strip')
        baselines=[strip['single_baseline_mm']] if len(lines)<2 else strip['double_baselines_mm']
        for humour_line,baseline in zip(lines,baselines):self.say(humour_line,g['start']+strip['padding_mm'],baseline,strip['font'],strip['size_pt'],strip['foreground'])
        if opening:self.say(self.content.get('chapter_heading',self.content.get('chapter','')),g['main_x'],self.y(0),'Head',13.8,INK,grid=True)
        self.say(title,g['main_x']+2,self.y(1 if opening else 0),'Head',13,INK,grid=True)
        if logical is not None:self.say(str(logical),g['start'] if logical%2==0 else g['end'],291,'Latin',9,INK,'left'if logical%2==0 else'right')
    def blocks(self,blocks,startrow=1):
        row=startrow;g=self.g;x=g['main_x'];w=g['main_w']
        for b in blocks:
            typ=b['type']
            if typ=='table':row=self.table(b,row);continue
            if typ=='comparison_bars':
                self.fit(row,3,'comparison bars')
                for j,(prior,post) in enumerate(b['values']):
                    yy=self.y(row+j);rect(self.c,x,yy-5,128,7.2,'#FFFFFF')
                    self.say(b.get('parameter_label','')+format(prior,'.2f'),x,yy,'Math',9,grid=True)
                    rect(self.c,x+20,yy-4.1,prior*62,1.5,'#9FC8D6')
                    rect(self.c,x+20,yy-1.8,post*62,1.5,'#81AF51')
                    self.say(format(post*100,'.2f')+'%',x+87,yy,'Math',9,grid=True)
                    if j==0:self.say(b.get('legend',''),x+104,yy,'Hand',8,grid=True)
                row+=3;continue
            if typ=='heading':
                self.fit(row,1,b['text']);rect(self.c,x,self.y(row)-4.3,4.7,4.9,BLUE);self.say(b.get('number',''),x+2.35,self.y(row)-.35,'Head',9.1,'#FFFFFF','center');self.say(b['text'],x+6,self.y(row),'Head',11.8,BLUE,grid=True);row+=1;continue
            font='Latin' if b.get('language')=='en' else'Body';size=11 if font=='Latin' else 11.6
            if typ=='formula':font='Math';size=10.4
            lines=wrap(b['text'],w-.5,font,size);self.fit(row,len(lines),b['text'])
            for t,fragments in contextual_highlight_lines(b['text'],lines,b.get('highlights',[])):
                for start,end in fragments:
                    left=x+width(t[:start],font,size)
                    rect(self.c,left,self.y(row)-3.05,width(t[start:end],font,size),3.4,'#FBE77A')
                self.say(t,x+w/2 if typ=='formula' else x,self.y(row),font,size,INK,'center' if typ=='formula' else'left',grid=True);row+=1
        return row
    def fit(self,row,n,txt):
        if row+n>self.maxrows:raise ValueError(f'Page {self.no}: needs {row+n} rows, capacity {self.maxrows}: {txt[:90]}')
    def table(self,b,row):
        x=self.g['main_x'];limit=self.g['main_w'];data=[b['headers']]+b['rows'];cols=len(data[0]);size=9.5
        # Natural widths with small padding: no blanket full-column expansion.
        natural=[max(width(str(r[k]),'Body',size)for r in data)+4 for k in range(cols)]
        total=sum(natural)
        if total>limit:
            weights=b.get('widths_mm',natural);ws=[limit*z/sum(weights)for z in weights]
        else:ws=natural
        rows=[]
        for r in data:
            ls=[wrap(str(t),ws[k]-3,'Body',size)for k,t in enumerate(r)];n=max(map(len,ls));rows.append((ls,n))
        needed=sum(n for ls,n in rows);self.fit(row,needed,'table');top=self.y(row)-5.05;h=needed*self.pitch
        rect(self.c,x,top,sum(ws),h,'#FFFFFF');rect(self.c,x,top,sum(ws),rows[0][1]*self.pitch,'#F0F5DE')
        yy=top;line(self.c,x,yy,x+sum(ws),yy,INK,.4)
        offset=0
        for i,(ls,n)in enumerate(rows):
            xx=x
            for k,lines in enumerate(ls):
                for j,t in enumerate(lines):self.say(t,xx+1.5,self.y(row+offset+j),'Body',size,INK,grid=True)
                xx+=ws[k]
            offset+=n;line(self.c,x,top+offset*self.pitch,x+sum(ws),top+offset*self.pitch,INK,.4)
        xx=x
        for z in [0]+ws:
            xx+=z;line(self.c,xx,top,xx,top+h,INK,.4)
        return row+needed
    def image(self,name,x,y,w,maxh):
        f=self.assets/name
        im=Image.open(f);iw,ih=im.size;hh=w*ih/iw
        if hh>maxh:w*=maxh/hh;hh=maxh
        self.c.drawImage(ImageReader(im),x*MM,(self.h-y-hh)*MM,width=w*MM,height=hh*MM,mask='auto')
        return hh
    def sidebar(self,page):
        s=page.get('sidebar') or {};g=self.g;x=g['side_x'];w=g['side_w'];r=2
        if s.get('title'):self.say(s['title'],x,self.y(r),'Hand',10.5,BLUE,grid=True);r+=1
        # All sidebar content comes from this page's data, independent of its number.
        if s.get('text'):
            for t in wrap(s['text'],w,'Hand',10):self.say(t,x,self.y(r),'Hand',10,INK,grid=True);r+=1
        comic=s.get('comic') or {}
        if comic.get('asset'):
            yy=self.y(r)+4;ww=min(w,34);hh=self.image(comic['asset'],x,yy,ww,27);r=math.ceil((yy+hh+5-self.first)/self.pitch)
        if comic.get('speech'):
            for t in wrap(comic['speech'],w,'Hand',10):self.say(t,x,self.y(r),'Hand',10,RED,grid=True);r+=1
        calculation=s.get('calculation') or {}
        if any(calculation.get(key) for key in ('title','lines','note')):
            r+=1
            if calculation.get('title'):self.say(calculation['title'],x,self.y(r),'Hand',10,BLUE,grid=True);r+=1
            for label in calculation.get('lines') or []:
                self.say(label,x,self.y(r),'Math',7.7,INK,grid=True);r+=1
            if calculation.get('note'):
                for t in wrap(calculation['note'],w,'Hand',10):self.say(t,x,self.y(r),'Hand',10,RED,grid=True);r+=1
        keywords=s.get('keywords') or []
        if self.a.edition=='digital' and keywords:
            self.say(s.get('keywords_title','关键词'),g['left_x'],self.y(2),'Hand',9.5,BLUE,grid=True)
            for j,t in enumerate(keywords):self.say(t,g['left_x'],self.y(3+j),'Hand'if any(ord(z)>127 for z in t)else'Latin',8.8,INK,grid=True)
    def cover(self):
        cover=self.content.get('cover') or {}
        self.start('cover');self.say(cover.get('subject',self.content.get('subject','')),20,109,'Head',38);self.say(cover.get('chapter',self.content.get('chapter','')),20,135,'Body',22);self.say(cover.get('subtitle',''),20,159,'Hand',15,BLUE)
        if cover.get('image'):self.image(cover['image'],123,181,50,34)
        self.say(cover.get('note',''),20,244,'Body',11);self.say((cover.get('edition_labels') or {}).get(self.a.edition,''),20,254,'Body',11);self.finish();self.toc.append([1,'封面',1])
    def outline_numbers(self):
        numbers={}
        for page in self.content.get('pages') or []:
            for oid in page.get('outline_ids') or []:numbers.setdefault(oid,page['number'])
        first_glossary=max((p['number'] for p in self.content.get('pages') or []),default=0)+1
        for node in self.content.get('outline') or []:
            if node.get('kind') in {'glossary','appendix'}:numbers.setdefault(node['id'],first_glossary)
        return numbers
    def legacy_frontmatter(self):
        contents=((self.content.get('frontmatter') or {}).get('contents') or {});title=contents.get('title','目录');numbers=self.outline_numbers();r=3
        def begin():
            role='contents_odd' if (len(self.doc)+1)%2 else 'contents_even'
            self.start(role);self.furniture(title,contents.get('humour',''))
            if self.contents_pdf_page is None:self.contents_pdf_page=len(self.doc)
        begin()
        for node in self.content.get('outline') or []:
            if node.get('include_in_toc',True) is False:continue
            if node['id'] not in numbers:raise ValueError(node['id']+': outline node has no page anchor')
            level=node['level'];indent=(level-1)*7;font='Head' if level==1 else 'Body';size=12.2 if level==1 else 11.4 if level==2 else 10.7
            lines=wrap(node['title'],self.g['main_w']-indent-20,font,size)
            needed=len(lines)+(1 if level==1 else 0)
            if r+needed>self.maxrows:
                self.finish();begin();r=3
            if level==1 and r>3:r+=1
            page_index=len(self.doc);top=self.y(r)-5
            for line_text in lines:
                self.say(line_text,self.g['main_x']+indent,self.y(r),font,size,BLUE if level==1 else INK,grid=True);r+=1
            dots='·'*100
            number_text=str(numbers[node['id']]);right=self.g['main_x']+self.g['main_w']
            dot_start=self.g['main_x']+indent+min(self.g['main_w']-24,width(lines[-1],font,size)+3)
            dot_width=max(0,right-14-dot_start)
            if dot_width>2:self.say(dots[:max(1,int(dot_width/2.2))],dot_start,self.y(r-1),'Body',8,'#7D8B8E',grid=True)
            self.say(number_text,right,self.y(r-1),'Latin',10.5,INK,'right',grid=True)
            self.contents_links.append((page_index,node['id'],[self.g['main_x']+indent,top,right,self.y(r-1)+1]))
            r+=1
        self.finish()
    def legacy_chapter(self):
        jokes=self.content.get('humour') or []
        for index,page in enumerate(self.content.get('pages') or []):
            n=page['number'];opening=n==1;role=('opening_'if opening else'')+('odd'if n%2 else'even')
            for oid in page.get('outline_ids') or []:self.body_targets.setdefault(oid,len(self.doc))
            self.start(role,n);self.furniture(page['title'],page.get('humour',jokes[index] if index<len(jokes) else ''),n,opening);end=self.blocks(page['blocks'],2 if opening else 1);self.sidebar(page);self.finish();print(f'{self.a.edition} page {n}: {end}/{self.maxrows} rows')
    def glossary_pages(self):
        groups=self.content.get('chapter_glossary') or [];settings=self.content.get('glossary_settings') or {};title=settings.get('title','分章专有词汇表');number=max((p['number'] for p in self.content.get('pages') or []),default=0)+1
        glossary_nodes=[n for n in self.content.get('outline') or [] if n.get('kind') in {'glossary','appendix'}]
        if not glossary_nodes:raise ValueError('outline needs one glossary or appendix node')
        for node in glossary_nodes:self.body_targets.setdefault(node['id'],len(self.doc))
        col=0;r=3;started=False
        def begin():
            nonlocal col,r,started
            role='glossary_odd' if number%2 else 'glossary_even';self.start(role,number);self.furniture(title,settings.get('humour',''),number);col=0;r=3;started=True
        def advance():
            nonlocal col,r,number
            if col==0:col=1;r=3;return
            self.finish();number+=1;begin()
        def put(lines):
            nonlocal r
            if len(lines)>self.maxrows-3:raise ValueError('Glossary entry is too long for one column')
            if r+len(lines)>self.maxrows:advance()
            gap=8;cw=(self.g['main_w']-gap)/2;x=self.g['main_x']+col*(cw+gap)
            for label,font,size,color in lines:self.say(label,x,self.y(r),font,size,color,grid=True);r+=1
        begin()
        gap=8;cw=(self.g['main_w']-gap)/2
        for group in groups:
            header=[(line,'Head',11.2,BLUE) for line in wrap(group['chapter_title'],cw,'Head',11.2)]
            if r+len(header)>self.maxrows:advance()
            put(header);r+=1
            for entry in group['entries']:
                term_lines=wrap(entry['term_en'],cw-2,'Latin',9.8);meaning_lines=wrap(entry['meaning_zh'],cw-2,'Body',10)
                lines=[(line,'Latin',9.8,BLUE) for line in term_lines]+[(line,'Body',10,INK) for line in meaning_lines]
                if r+len(lines)>self.maxrows:
                    advance();put([(line,'Head',10.5,BLUE) for line in wrap(group['chapter_title']+'（续）',cw,'Head',10.5)]);r+=1
                put(lines)
            r+=1
        if started:self.finish()
    def build_toc(self,has_foldout=False):
        toc=[[1,'封面',1]]
        if self.contents_pdf_page is not None:toc.append([1,((self.content.get('frontmatter') or {}).get('contents') or {}).get('title','目录'),self.contents_pdf_page+1])
        for node in self.content.get('outline') or []:
            if node.get('include_in_toc',True) is False:continue
            target=self.body_targets.get(node['id'])
            if target is not None:toc.append([node['level'],node['title'],target+1])
        if has_foldout:toc.append([1,'知识速查',len(self.doc)])
        self.toc=toc
    def foldout(self):
        wide=self.content.get('wide_reference') or {};self.start('foldout');self.say(wide.get('title',self.content.get('chapter','')),14,21,'Head',23);self.say(wide.get('label','知识速查'),580,21,'Hand',14,BLUE,'right')
        cols=wide.get('columns') or []
        if len(cols)>4:raise ValueError('Foldout supports at most four columns')
        for i,col in enumerate(cols):
            x=14+141.5*i;r=0;self.say(col['title'],x+2,38,'Head',14,BLUE);y=49.8
            for t in col.get('formulas') or []:
                for s in wrap(t,131,'Math',11):self.say(s,x+2,y,'Math',11);y+=7.2
            y+=7.2
            for k,t in enumerate(col.get('notes') or [],1):
                for s in wrap(str(k)+'  '+t,131,'Body',12):self.say(s,x+2,y,'Body',12);y+=7.2
            example=col.get('example') or {}
            if example.get('title') or example.get('lines'):
                y=max(y+7.2,136.2)
                if example.get('title'):self.say(example['title'],x+2,y,'Head',12,BLUE);y+=7.2
                for t in example.get('lines') or []:
                    for s in wrap(t,131,'Body',11.5):self.say(s,x+2,y,'Body',11.5);y+=7.2
            if y>202:raise ValueError(f'Foldout column {i+1} exceeds available height; shorten or split the reference')
        self.finish()
    def run(self):
        if self.a.foldout_only:self.foldout()
        else:
            self.cover()
            if self.a.edition=='print':self.start('blank');self.finish()
            self.frontmatter()
            if self.a.edition=='print' and len(self.doc)%2:self.start('blank');self.finish()
            self.chapter()
            self.glossary_pages()
            self.build_toc(False)
        if self.toc:self.doc.set_toc(self.toc)
        for src,outline_id,box in self.contents_links:
            self.doc[src].insert_link({'kind':fitz.LINK_GOTO,'from':fitz.Rect(*(z*MM for z in box)),'page':self.body_targets[outline_id]})
        metadata=self.content.get('metadata') or {};self.doc.set_metadata({key:metadata.get(key,'') for key in ('title','author','subject','keywords')})
        self.doc.rewrite_images(dpi_threshold=450,dpi_target=300,quality=94,bitonal=False)
        self.doc.save(self.a.output,garbage=4,deflate=True)
        write_json(Path(self.a.output).with_suffix('.layout.json'),{'master_sha256':self.hash,'content_schema_version':self.content.get('content_schema_version',1),'fun_mode':self.a.fun_mode,'fun_seed':self.a.fun_seed,'pages':self.logs,'chapters':self.layout_metrics,'warnings':self.composition_warnings,'language_findings':getattr(self,'language_review',[]),'review_status':{'automatic_structure':'passed','automatic_fields':'passed','human_content':'not_run','human_visual':'not_run'}})
        if self.compiled:write_json(Path(self.a.output).with_suffix('.compiled.json'),self.content)
        assert hashlib.sha256(self.src.read_bytes()).hexdigest()==self.hash,'Master was modified'
        if self.fun_picker and self.history:self.history.commit(self.fun_picker.selected)
if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--content',required=True);p.add_argument('--templates',required=True);p.add_argument('--fonts',required=True);p.add_argument('--assets',required=True);p.add_argument('--edition',choices=['print','digital'],default='print');p.add_argument('--output',required=True);p.add_argument('--foldout-only',action='store_true')
    p.add_argument('--fun-mode',choices=['random','content'],default='random',help='random随机抽取；content使用内容JSON原有humour')
    p.add_argument('--fun-catalog',type=Path,default=DEFAULT_CATALOG)
    p.add_argument('--fun-seed',type=int,help='固定随机种子以复现本次抽取')
    p.add_argument('--fun-subject',action='append',help='按学科筛选，可重复使用，支持中文名')
    p.add_argument('--fun-include-general',action='store_true',help='学科筛选时同时纳入通用笑话和名句')
    p.add_argument('--fun-types',nargs='+',choices=KINDS)
    p.add_argument('--fun-max-lines',type=int,choices=[1,2],default=2)
    p.add_argument('--fun-used-file',type=Path,help='同一本书各章共用的已用语料记录')
    a=p.parse_args()
    try:
        output=Path(a.output)
        reserved={Path(a.content).resolve(),a.fun_catalog.resolve(),output.with_suffix('.layout.json').resolve()}
        if a.fun_used_file and a.fun_used_file.resolve() in reserved|{output.resolve()}:
            raise ValueError('趣味语料历史文件须与输入、输出及布局记录使用不同路径')
        if output.resolve() in {Path(a.content).resolve(),a.fun_catalog.resolve()}:
            raise ValueError('PDF输出路径不能覆盖输入内容或语料库')
        if a.fun_used_file and a.fun_mode=='content':
            raise ValueError('--fun-used-file用于random模式；content模式直接使用手写内容')
        output.parent.mkdir(parents=True,exist_ok=True)
        with UsageHistory(a.fun_used_file if not a.foldout_only else None) as history:Book(a,history).run()
    except (ValueError,OSError) as error:p.error(str(error))
