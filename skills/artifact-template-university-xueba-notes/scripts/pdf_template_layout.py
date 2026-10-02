"""Shared text metrics for fixed PDF masters and their content overlays."""
from pathlib import Path
from io import BytesIO
import re
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from fontTools.ttLib import TTFont as Font
MM=72/25.4
INK='#16191A'; BLUE='#135B82'; GREEN='#BBD76E'; RULE='#9ED5DE'; RED='#B64930'
MAP={}; LOG=[]
def register_fonts(folder):
    for name,fn in [('Body','WenKai.ttf'),('Head','SansBold.ttf'),('Hand','WenKai.ttf'),('Latin','DejaVuSerif.ttf'),('Math','DejaVuSans.ttf')]:
        f=Font(str(Path(folder)/fn)); MAP[name]=set(f.getBestCmap())
        for n in f['name'].names:
            if n.nameID in (1,3,4,6):
                try:n.string=('Xueba'+name).encode(n.getEncoding())
                except Exception:pass
        b=BytesIO();f.save(b);b.seek(0);pdfmetrics.registerFont(TTFont(name,b))
def clean(s):return s.replace('^c','ᶜ').replace('ₘ','ₘ')
def face(ch,base):
    if ord(ch) in MAP[base]:return base
    for alt in ['Math','Body','Hand']:
        if ord(ch) in MAP[alt]:return alt
    raise ValueError('Missing glyph '+repr(ch))
def runs(s,base):
    out=[]
    for ch in clean(s):
        f=face(ch,base)
        if out and out[-1][0]==f:out[-1]=(f,out[-1][1]+ch)
        else:out.append((f,ch))
    return out
def width(s,base,size):return sum(pdfmetrics.stringWidth(t,f,size) for f,t in runs(s,base))/MM
def wrap(s,w,base='Body',size=11.6):
    tokens=re.findall(r"P\([^)]*\)|\([a-z]\)|[0-9]+(?:\.[0-9]+)?/[0-9]+(?:\.[0-9]+)?|[A-Za-z0-9ᵢ₁₂₃ₖₘᶜ²³]+(?:['’.-][A-Za-z0-9]+)*|\s+|.",clean(s))
    # Keep closing punctuation with its preceding token before line breaking.
    # Letting punctuation overhang can put ink in the blank print binding margin.
    closers='，。；：、？！）】》,.;:?!)]}'
    grouped=[]
    for token in tokens:
        if token in closers and grouped:grouped[-1]+=token
        else:grouped.append(token)
    lines=[];line=''
    for t in grouped:
        if not line and t.isspace():continue
        if width(t.lstrip(),base,size)>w:
            raise ValueError(f'Unbreakable text exceeds {w} mm: {t!r}; revise the text or its allocated slot')
        if width(line+t,base,size)<=w:
            line+=t
        else:lines.append(line.rstrip());line=t.lstrip()
    if line:lines.append(line.rstrip())
    return lines
def text(c,s,x,y,base='Body',size=11.6,color=INK,align='left',page_h=297,log=False):
    s=clean(s); w=width(s,base,size)
    if align=='center':x-=w/2
    if align=='right':x-=w
    c.setFillColor(color)
    xx=x*MM
    for f,t in runs(s,base):
        c.setFont(f,size);c.drawString(xx,(page_h-y)*MM,t);xx+=pdfmetrics.stringWidth(t,f,size)
    if log:LOG.append({'text':s,'x_mm':round(x,3),'baseline_mm':round(y,3),'width_mm':round(w,3),'font':base,'size':size})
    return w
def rect(c,x,y,w,h,fill,stroke=None,page_h=297):
    c.setFillColor(fill)
    if stroke:c.setStrokeColor(stroke)
    c.rect(x*MM,(page_h-y-h)*MM,w*MM,h*MM,fill=1,stroke=int(bool(stroke)))
def line(c,x1,y1,x2,y2,color=RULE,lw=.4,page_h=297):
    c.setStrokeColor(color);c.setLineWidth(lw);c.line(x1*MM,(page_h-y1)*MM,x2*MM,(page_h-y2)*MM)
def page_geo(edition,even=False):
    if edition=='digital':return {'main_x':38,'main_w':128,'side_x':171,'side_w':27,'left_x':12,'left_w':21,'start':12,'end':198,'dividers':[35,168]}
    if even:return {'main_x':62,'main_w':128,'side_x':12,'side_w':45,'start':12,'end':190,'dividers':[59]}
    return {'main_x':20,'main_w':128,'side_x':153,'side_w':45,'start':20,'end':198,'dividers':[150]}
