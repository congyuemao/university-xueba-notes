"""Measured, composable knowledge blocks. Measurement and drawing share one path."""
import math
import re
from html import escape
from pathlib import Path
from pdf_template_layout import *
from context_highlights import contextual_highlight_lines
from content_schema import TEXT_TYPES
from knowledge_map import layout_tree,svg_text
from example_structure import example_parts
from language_review import paragraph_finding

LABELS={'definition':'定义','property':'性质','rule':'法则','condition':'条件','example_inline':'例','common_error':'易错','memory_note':'记忆','diagram_explanation':'读图','method_card':'方法'}

def drawing_svg(items,x,y,w,h):
    out=[f'<g transform="translate({x},{y}) scale({w/100},{h/100})">']
    for p in items:
        color=p.get('color',BLUE);kind=p['kind']
        if kind in {'line','arrow','polyline','polygon'}:
            pts=' '.join(f'{a},{b}' for a,b in p['points']);tag='polygon' if kind=='polygon' else 'polyline'
            out.append(f'<{tag} points="{pts}" fill="{p.get("fill","none")}" stroke="{color}" stroke-width="0.6"/>')
        elif kind=='circle':out.append(f'<circle cx="{p["x"]}" cy="{p["y"]}" r="{p.get("r",2)}" fill="{p.get("fill","white")}" stroke="{color}" stroke-width="0.6"/>')
        elif kind=='label':out.append(f'<text x="{p["x"]}" y="{p["y"]}" font-size="4" fill="{color}">{escape(p["text"])}</text>')
    out.append('</g>');return ''.join(out)

class BlockEngine:
    def __init__(self,book,draw=True):self.b=book;self.draw=draw;self.boxes={};self.types=[];self.vectors=[];self.language_findings=[]
    def say(self,s,x,y,font='Body',size=11.6,color=INK,align='left',grid=True):
        if self.draw:self.b.say(s,x,y,font,size,color,align,grid)
    def rectangle(self,x,y,w,h,fill,stroke=None):
        if self.draw:rect(self.b.c,x,y,w,h,fill,stroke)
    def line(self,x1,y1,x2,y2,color=RULE,lw=.4):
        if self.draw:line(self.b.c,x1,y1,x2,y2,color,lw)
    def lines(self,s,x,row,w,font='Body',size=11.6,color=INK,highlights=None):
        ls=wrap(str(s),w,font,size)
        for i,(t,fragments) in enumerate(contextual_highlight_lines(str(s),ls,highlights or [])):
            for start,end in fragments:self.rectangle(x+width(t[:start],font,size),self.b.y(row+i)-3.05,width(t[start:end],font,size),3.4,'#FBE77A')
            self.say(t,x,self.b.y(row+i),font,size,color)
        return row+len(ls)
    def many(self,blocks,row,x,w):
        for block in blocks:row=self.block(block,row,x,w)
        return row
    def prose(self,s,x,row,w,b,font='Body',size=11.6,color=INK):
        s=clean(s)
        offset=0
        for i,paragraph in enumerate(re.split(r'\n\s*\n',s)):
            start=s.index(paragraph,offset);offset=start+len(paragraph)
            if i:row+=1
            highlights=[]
            for mark in b.get('highlights',[]):
                left=max(start,mark['start']);right=min(offset,mark['end'])
                if left<right:highlights.append({**mark,'start':left-start,'end':right-start,'text':s[left:right]})
            count=len(wrap(paragraph,w,font,size))
            finding=paragraph_finding(b.get('id'),i+1,count,row,b.get('language_level'))
            if finding and self.draw:self.language_findings.append(finding)
            row=self.lines(paragraph,x,row,w,font,size,color,highlights)
        return row
    def measure(self,block,w):return BlockEngine(self.b,False).block(block,0,0,w)
    def block(self,b,row,x,w):
        start=row;t=b['type'];self.types.append(t);bid=b.get('id');title=b.get('title')
        if t=='group':row=self.many(b['blocks'],row,x,w)
        elif t=='worked_example':row=self.many(example_parts(b),row,x,w)
        elif t=='_example_part':
            color=RED if b['part']=='problem' else BLUE
            self.line(x,self.b.y(row)-4.8,x+w,self.b.y(row)-4.8,color,.45)
            row=self.lines(b['title'],x,row,w,'Head',11.6,color)
            row=self.many(b['content'],row,x,w)
            row+=1
        elif t=='paired':
            ratio=b.get('ratio',.52);gap=5;left=(w-gap)*ratio;right=w-gap-left
            row=max(self.many(b['left'],row,x,left),self.many(b['right'],row,x+left+gap,right))
        elif t=='heading':
            self.rectangle(x,self.b.y(row)-4.4,4.7,5,BLUE);self.say(b.get('number',''),x+2.35,self.b.y(row)-.2,'Head',9,'#FFFFFF','center')
            row=self.lines(b['text'],x+6,row,w-6,'Head',11.8,BLUE)
        elif t in TEXT_TYPES:
            if t!='paragraph':
                label=(title or LABELS[t])+(' '+b['symbol'] if b.get('symbol') else '')
                if t=='condition' and b.get('boundary_level')=='C':label='扩展 · '+label
                color=RED if t in {'common_error','memory_note'} else BLUE
                font='Hand' if t=='memory_note' else 'Head'
                if t=='method_card':self.line(x,self.b.y(row)-5,x+w,self.b.y(row)-5,BLUE,.65)
                row=self.lines(label,x,row,w,font,11,color)
            row=self.prose(b['text'],x,row,w,b,'Latin' if b.get('language')=='en' else 'Body',11 if b.get('language')=='en' else 11.6)
            if t=='paragraph' and b.get('space_after',True):row+=1
        elif t=='formula_step':
            row=self.prose(b['reason'],x,row,w,b)
            for s in wrap(b['formula'],w,'Math',10.4):self.say(s,x+w/2,self.b.y(row),'Math',10.4,INK,'center');row+=1
            if b.get('space_after',True):row+=1
        elif t=='formula':
            for s in wrap(b['text'],w,'Math',10.4):self.say(s,x+w/2,self.b.y(row),'Math',10.4,INK,'center');row+=1
        elif t in {'formula_group','formula_relation','property_list'}:
            if title:row=self.lines(title,x,row,w,'Head',11,BLUE)
            for i,item in enumerate(b['items']):
                item={'text':item} if isinstance(item,str) else item
                if t=='property_list':
                    self.say(str(i+1),x,self.b.y(row),'Head',10,BLUE)
                    row=self.lines((item.get('label','')+'　'+item['text']).strip(),x+5,row,w-5)
                else:
                    self.line(x,self.b.y(row)-4,x,self.b.y(row)+1,BLUE,.8)
                    row=self.lines(item.get('formula',item.get('text','')),x+3,row,w-3,'Math',10.4)
                    if item.get('reason'):row=self.lines(item['reason'],x+3,row,w-3,'Body',10.5)
        elif t in {'process_steps','worked_micro_example'}:
            if title:row=self.lines(title,x,row,w,'Head',11,BLUE)
            if t=='worked_micro_example':
                self.say('例',x,self.b.y(row),'Head',11,RED);row=self.lines(b['problem'],x+6,row,w-6)
            for i,step in enumerate(b['steps']):
                step={'text':step} if isinstance(step,str) else step
                self.say(f'{i+1:02}',x,self.b.y(row),'Latin',10,BLUE)
                row=self.lines((step.get('label','')+' '+step['text']).strip(),x+7,row,w-7)
            if t=='worked_micro_example':
                row=self.lines('结果　'+b['answer'],x,row,w,'Body',11.6)
                if b.get('note'):row=self.lines(b['note'],x,row,w,'Hand',12,RED)
        elif t in {'table','comparison','comparison_table'}:row=self.table(b,row,x,w)
        elif t=='concept_diagram':
            h=b['height_rows']*self.b.pitch;top=self.b.y(row)-5
            self.rectangle(x,top,w,h,'#FFFFFF')
            if b.get('drawing'):self.drawing(b['drawing'],x+2,top+2,w-4,h-4)
            elif self.draw:
                f=self.b.assets/b['asset']
                if f.suffix.lower() in {'.pdf','.svg'}:self.vectors.append((str(f),[x,top,x+w,top+h]))
                else:self.b.image(b['asset'],x,top,w,h)
            row+=b['height_rows'];row=self.lines(b['caption'],x,row,w,'Body',10,BLUE)
        elif t=='knowledge_map':
            h=b.get('height_rows',24)*self.b.pitch;top=self.b.y(row)-5
            layout=layout_tree(b['tree'],w,h);self.rectangle(x,top,w,h,'#FFFFFF')
            if self.draw:
                c=self.b.c
                for e in layout['edges']:
                    xx1,yy1,xx2,yy2=x+e['x1'],top+e['y1'],x+e['x2'],top+e['y2'];dx=(xx2-xx1)*.55
                    p=c.beginPath();p.moveTo(xx1*MM,(297-yy1)*MM);p.curveTo((xx1+dx)*MM,(297-yy1)*MM,(xx2-dx)*MM,(297-yy2)*MM,xx2*MM,(297-yy2)*MM)
                    c.setStrokeColor(e['color']);c.setLineWidth(e['width']*MM);c.drawPath(p)
                for n in layout['nodes']:
                    for i,s in enumerate(n['lines']):
                        font='Head' if n['depth']==0 else 'Body' if i<n['label_lines'] else 'Math'
                        self.say(s,x+n['x'],top+n['y']-(len(n['lines'])-1)*2.5+i*5,font,11.5 if n['depth']==0 else 10 if font=='Body' else 9,n['color'],grid=False)
                    self.line(x+n['x'],top+n['branch_y'],x+n['x']+n['extent']+1,top+n['branch_y'],n['color'],.55)
                    if n.get('drawing'):self.drawing(n['drawing'],x+n['x'],top+n['y']+5,n['max_w'],12)
                out=Path(self.b.a.output).with_suffix('.assets');out.mkdir(parents=True,exist_ok=True)
                (out/(bid+'.svg')).write_text(svg_text(layout),encoding='utf-8')
            row+=b.get('height_rows',24)
            if b.get('caption'):row=self.lines(b['caption'],x,row,w,'Body',10,BLUE)
        elif t=='handwritten_annotation':
            # In-flow note gets its own row(s); overlay marks use handwritten_layer.
            row=self.lines(b.get('text',''),x,row,w,'Hand',12,RED)
        elif t=='comparison_bars':
            for prior,post in b['values']:
                self.say(format(prior,'.2f'),x,self.b.y(row),'Math',9)
                self.rectangle(x+18,self.b.y(row)-4,prior*(w-45),1.5,'#9FC8D6');self.rectangle(x+18,self.b.y(row)-1.8,post*(w-45),1.5,'#81AF51')
                self.say(format(post*100,'.2f')+'%',x+w,self.b.y(row),'Math',9,align='right');row+=1
        else:raise ValueError('Unsupported block '+t)
        if bid:self.boxes[bid]={'x':x,'row':start,'end':row,'w':w,'type':t}
        return row
    def table(self,b,row,x,w):
        if b.get('title'):row=self.lines(b['title'],x,row,w,'Head',11,BLUE)
        data=[b.get('headers',b.get('columns'))]+b['rows'];n=len(data[0]);size=b.get('font_size',9.5)
        natural=[max(width(str(r[k]),'Head' if i==0 else 'Body',size) for i,r in enumerate(data))+4 for k in range(n)]
        weights=b.get('widths_mm',natural);total=min(w,sum(natural))
        if len(weights)!=n or any(z<=0 for z in weights):raise ValueError('Table widths must be positive and match its columns')
        # A short column must retain at least one glyph plus padding when a
        # neighbouring explanation wraps. Proportional scaling alone can
        # otherwise shrink a one-character heading to less than its glyph.
        minimum=[max(7,max((width(token.lstrip(),'Head' if i==0 else 'Body',size) for i,r in enumerate(data) for token in wrap_tokens(str(r[k]))),default=0)+3.5) for k in range(n)]
        if sum(minimum)>w:raise ValueError('Table too narrow for its columns; split or widen it')
        total=min(w,sum(max(a,b) for a,b in zip(natural,minimum)))
        ws=[0]*n;active=set(range(n));available=total
        while active:
            weight_sum=sum(weights[k] for k in active)
            small={k for k in active if available*weights[k]/weight_sum<minimum[k]}
            if not small:
                for k in active:ws[k]=available*weights[k]/weight_sum
                break
            for k in small:ws[k]=minimum[k];available-=ws[k]
            active-=small
        marks={(a['row'],a['col']):a.get('color','#FBE77A') for a in b.get('cell_marks',[])}
        for i,values in enumerate(data):
            ls=[wrap(str(s),ws[k]-3,'Head' if i==0 else 'Body',size) for k,s in enumerate(values)];nr=max(map(len,ls));xx=x;top=self.b.y(row)-5
            for k,lines in enumerate(ls):
                self.rectangle(xx,top,ws[k],nr*self.b.pitch,marks.get((i,k),'#F0F5DE' if i==0 else '#FFFFFF'),BLUE)
                for j,s in enumerate(lines):self.say(s,xx+1.5,self.b.y(row+j),'Head' if i==0 else 'Body',size)
                if b.get('id'):self.boxes[f'{b["id"]}@{i},{k}']={'x':xx,'row':row,'end':row+nr,'w':ws[k],'type':'cell'}
                xx+=ws[k]
            row+=nr
        return row
    def drawing(self,items,x,y,w,h):
        if not self.draw:return
        c=self.b.c
        for obj in items:
            kind=obj['kind'];color=obj.get('color',BLUE)
            if kind in {'line','polyline','polygon','arrow'}:
                pts=[(x+a*w/100,y+b*h/100) for a,b in obj['points']];p=c.beginPath();p.moveTo(pts[0][0]*MM,(297-pts[0][1])*MM)
                for xx,yy in pts[1:]:p.lineTo(xx*MM,(297-yy)*MM)
                if kind=='polygon':p.close()
                c.setStrokeColor(color);c.setLineWidth(obj.get('width',.7));c.setFillColor(obj.get('fill','#FFFFFF'));c.drawPath(p,stroke=1,fill=int(kind=='polygon'))
                if kind=='arrow':
                    (a,b),(u,v)=pts[-2:];ang=math.atan2(v-b,u-a)
                    for turn in (-.48,.48):self.line(u,v,u-2*math.cos(ang+turn),v-2*math.sin(ang+turn),color,.7)
            elif kind=='circle':
                c.setStrokeColor(color);c.setLineWidth(.7);c.setFillColor(obj.get('fill','#FFFFFF'));c.circle((x+obj['x']*w/100)*MM,(297-y-obj['y']*h/100)*MM,obj.get('r',2)*min(w,h)/100*MM,stroke=1,fill=1)
            elif kind=='label':
                xx=x+obj['x']*w/100;yy=y+obj['y']*h/100;size=obj.get('size',9)
                label_w=width(obj['text'],obj.get('font','Body'),size)
                if xx+label_w>x+w+.01:raise ValueError('Diagram label extends outside slot: '+obj['text'])
                self.say(obj['text'],xx,yy,obj.get('font','Body'),size,color,grid=False)
            else:raise ValueError('Unknown drawing primitive '+kind)
