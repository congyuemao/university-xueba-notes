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
class Book:
    def __init__(self,a,history=None):
        self.a=a;self.content=json.loads(Path(a.content).read_text(encoding='utf-8'));self.man=json.loads((Path(a.templates)/'template-manifest.json').read_text(encoding='utf-8'));self.src=Path(a.templates)/(a.edition+'-master.pdf');self.hash=hashlib.sha256(self.src.read_bytes()).hexdigest();self.master=fitz.open(self.src);self.doc=fitz.open();self.toc=[];self.logs=[];self.g=None;self.contents_links=[];self.body_targets={};register_fonts(a.fonts)
        validate_content_highlights(self.content)
        grid=self.man['grid'];self.first=grid['first_baseline_mm'];self.pitch=grid['pitch_mm'];self.maxrows=grid['rows'];self.assets=Path(a.assets)
        self.history=history;self.fun_picker=None;self.fun_item=None;self.fun_lines_cache={}
        if a.fun_mode=='random' and not a.foldout_only:
            self.fun_picker=FunPicker(load_catalog(a.fun_catalog),seed=a.fun_seed,subjects=a.fun_subject,
                kinds=a.fun_types,include_general=a.fun_include_general,max_lines=a.fun_max_lines,history=history)
    def y(self,row):return self.first+row*self.pitch
    def start(self,role,number=None):
        self.role=role;self.no=number;self.buf=BytesIO();self.h=210 if role=='foldout' else 297;self.w=594 if role=='foldout' else 210;self.c=canvas.Canvas(self.buf,pagesize=(self.w*MM,self.h*MM));LOG.clear()
        self.g=self.man['editions'][self.a.edition].get(role);self.fun_item=None
    def finish(self):
        self.c.showPage();self.c.save();overlay=fitz.open(stream=self.buf.getvalue(),filetype='pdf');p=self.doc.new_page(width=self.w*MM,height=self.h*MM);p.show_pdf_page(p.rect,self.master,self.man['roles'][self.role]);p.show_pdf_page(p.rect,overlay,0)
        self.logs.append({'pdf_page':len(self.doc),'logical_page':self.no,'role':self.role,'texts':list(LOG),'fun_content':self.fun_item})
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
        terms=s.get('english_terms') or []
        if terms:
            r+=1
            for term in terms[:s.get('term_limit',len(terms))]:
                if term.get('term'):
                    for t in wrap(term['term'],w,'Latin',8.5):self.say(t,x,self.y(r),'Latin',8.5,BLUE,grid=True);r+=1
                if term.get('meaning'):
                    for t in wrap(term['meaning'],w,'Hand',9.8):self.say(t,x,self.y(r),'Hand',9.8,INK,grid=True);r+=1
        keywords=s.get('keywords') or []
        if self.a.edition=='digital' and keywords:
            self.say(s.get('keywords_title','关键词'),g['left_x'],self.y(2),'Hand',9.5,BLUE,grid=True)
            for j,t in enumerate(keywords):self.say(t,g['left_x'],self.y(3+j),'Hand'if any(ord(z)>127 for z in t)else'Latin',8.8,INK,grid=True)
    def cover(self):
        cover=self.content.get('cover') or {}
        self.start('cover');self.say(cover.get('subject',self.content.get('subject','')),20,109,'Head',38);self.say(cover.get('chapter',self.content.get('chapter','')),20,135,'Body',22);self.say(cover.get('subtitle',''),20,159,'Hand',15,BLUE)
        if cover.get('image'):self.image(cover['image'],123,181,50,34)
        self.say(cover.get('note',''),20,244,'Body',11);self.say((cover.get('edition_labels') or {}).get(self.a.edition,''),20,254,'Body',11);self.finish();self.toc.append([1,'封面',1])
    def frontmatter(self):
        front=self.content.get('frontmatter') or {};contents=front.get('contents') or {};glossary=front.get('glossary') or {}
        title=contents.get('title','目录');self.start('odd');self.furniture(title,contents.get('humour',''));x=self.g['main_x'];r=3
        for p in self.content.get('pages') or []:
            self.fit(r,1,p['title']);self.contents_links.append((len(self.doc),p['number'],[x,self.y(r)-5,x+128,self.y(r)+1]));self.say(p['title'],x,self.y(r),'Body',12,grid=True);self.say(str(p['number']),x+121,self.y(r),'Latin',11,grid=True);r+=2
        vocabulary=self.content.get('answer_vocabulary') or {}
        if vocabulary.get('entries'):
            self.fit(r,1,'答案词汇');self.contents_links.append((len(self.doc),'answer_vocabulary',[x,self.y(r)-5,x+128,self.y(r)+1]))
            self.say(vocabulary.get('title','答案词汇'),x,self.y(r),'Body',12,grid=True)
            self.say(str(max((p['number'] for p in self.content.get('pages') or []),default=0)+1),x+121,self.y(r),'Latin',11,grid=True);r+=2
        if contents.get('summary_title'):self.say(contents['summary_title'],x,self.y(r),'Head',11.8,BLUE,grid=True);r+=1
        if contents.get('summary'):
            for t in wrap(contents['summary'],128,'Body',11.6):self.say(t,x,self.y(r),grid=True);r+=1
        self.toc.append([1,title,len(self.doc)+1]);self.finish()
        self.term_pages(self.content.get('terminology_extended') or [],glossary,'术语索引')
    def term_pages(self,entries,settings,default_title,first_number=None):
        """Paginate complete CN/EN/CN entries without shrinking or dropping content."""
        if not entries:return
        title=settings.get('title',default_title);r=1;page_index=0;number=first_number
        def begin():
            role=('odd' if number%2 else 'even') if number is not None else ('odd' if (len(self.doc)+1)%2 else 'even')
            self.start(role,number);self.furniture(title,settings.get('humour',''),number)
        begin();self.toc.append([1,title,len(self.doc)+1])
        for entry in entries:
            for key in ('zh','term','definition_zh'):
                if not isinstance(entry.get(key),str) or not entry[key].strip():
                    raise ValueError(f'{default_title}: entry requires {key}; replace legacy definition/sentence with definition_zh/usage_en')
            if not any('\u3400'<=ch<='\u9fff' for ch in entry['definition_zh']):
                raise ValueError(f"{default_title}: {entry['term']} needs a Chinese explanation")
            if first_number is not None and (not entry.get('usage_en') or not entry.get('question_ids')):
                raise ValueError(f"{default_title}: {entry['term']} needs usage_en and question_ids")
            parts=[('  '.join((entry['zh'],entry['term'])),'Head',10.5,BLUE),
                   (entry['definition_zh'],'Body',11.6,INK)]
            if entry.get('note_zh'):parts.append((entry['note_zh'],'Body',11.6,INK))
            if entry.get('usage_en'):parts.append((entry['usage_en'],'Latin',10.2,INK))
            if entry.get('question_ids'):parts.append(('对应题目  '+'、'.join(str(q) for q in entry['question_ids']),'Body',10.2,BLUE))
            lines=[(line,font,size,color) for label,font,size,color in parts for line in wrap(label,self.g['main_w']-.5,font,size)]
            if len(lines)>self.maxrows-1:raise ValueError(f"{default_title}: entry too long for a page: {entry['term']}")
            if r+len(lines)>self.maxrows:
                self.finish();page_index+=1
                if first_number is not None:number=first_number+page_index
                begin();r=1
            for label,font,size,color in lines:
                self.say(label,self.g['main_x'],self.y(r),font,size,color,grid=True);r+=1
        self.finish()
    def answer_vocabulary(self):
        vocabulary=self.content.get('answer_vocabulary') or {}
        if vocabulary.get('entries'):
            self.body_targets['answer_vocabulary']=len(self.doc)
            first_number=max((p['number'] for p in self.content.get('pages') or []),default=0)+1
            self.term_pages(vocabulary['entries'],vocabulary,'答案词汇',first_number)
    def chapter(self):
        jokes=self.content.get('humour') or []
        for index,page in enumerate(self.content.get('pages') or []):
            n=page['number'];self.body_targets[n]=len(self.doc);opening=n==1;role=('opening_'if opening else'')+('odd'if n%2 else'even');self.start(role,n);self.furniture(page['title'],page.get('humour',jokes[index] if index<len(jokes) else ''),n,opening);end=self.blocks(page['blocks'],2 if opening else 1);self.sidebar(page);self.toc.append([1,page['title'],len(self.doc)+1]);self.finish();print(f'{self.a.edition} page {n}: {end}/{self.maxrows} rows')
    def foldout(self):
        wide=self.content.get('wide_reference') or {};self.start('foldout');self.say(wide.get('title',self.content.get('chapter','')),14,21,'Head',23);self.say(wide.get('label','知识速查'),580,21,'Hand',14,BLUE,'right')
        cols=wide.get('columns') or []
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
        self.finish()
    def run(self):
        if self.a.foldout_only:self.foldout()
        else:
            self.cover()
            if self.a.edition=='print':self.start('blank');self.finish()
            self.frontmatter()
            if self.a.edition=='print' and len(self.doc)%2:self.start('blank');self.finish()
            self.chapter()
            self.answer_vocabulary()
            if self.a.edition=='digital' and (self.content.get('wide_reference') or {}).get('columns'):self.toc.append([1,'知识速查',len(self.doc)+1]);self.foldout()
        if self.toc:self.doc.set_toc(self.toc)
        for src,number,box in self.contents_links:
            self.doc[src].insert_link({'kind':fitz.LINK_GOTO,'from':fitz.Rect(*(z*MM for z in box)),'page':self.body_targets[number]})
        metadata=self.content.get('metadata') or {};self.doc.set_metadata({key:metadata.get(key,'') for key in ('title','author','subject','keywords')})
        self.doc.rewrite_images(dpi_threshold=450,dpi_target=300,quality=94,bitonal=False)
        self.doc.save(self.a.output,garbage=4,deflate=True)
        write_json(Path(self.a.output).with_suffix('.layout.json'),{'master_sha256':self.hash,'fun_mode':self.a.fun_mode,'fun_seed':self.a.fun_seed,'pages':self.logs})
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
