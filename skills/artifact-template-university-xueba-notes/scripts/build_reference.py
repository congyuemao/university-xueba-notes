from pathlib import Path
from html import escape
import json
from reportlab.pdfgen import canvas
from reportlab.lib.units import mm
from reportlab.lib.colors import HexColor, Color, white
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import Paragraph
from reportlab.lib.styles import ParagraphStyle

import argparse

SKILL_ROOT = Path(__file__).resolve().parents[1]
parser = argparse.ArgumentParser(description="Build the University Xueba Notes reference examples.")
parser.add_argument('--legacy-geometry-demo', action='store_true', help='Explicitly reproduce the archived 3.0 geometry demo; not a current book generator.')
parser.add_argument('--edition', choices=('print','digital'), required=True)
parser.add_argument('--font-dir', type=Path, required=True)
parser.add_argument('--output', type=Path, required=True)
args = parser.parse_args()
if not args.legacy_geometry_demo:
    parser.error("This builder is archived. Supply --legacy-geometry-demo only to reproduce the historical layout; use the active series and sidebar-comics references for new books.")
EDITION = args.edition
PATH = args.output.resolve()
PATH.parent.mkdir(parents=True, exist_ok=True)
FONT_DIR = args.font_dir.resolve()

def font_path(file):
    candidates=[FONT_DIR/file,Path('/usr/share/fonts/truetype/dejavu')/file]
    for candidate in candidates:
        if candidate.is_file(): return str(candidate)
    raise FileNotFoundError(f"Missing {file}. Run prepare_fonts.py or supply --font-dir.")

for name,file in [('Kai','WenKai.ttf'),('Sans','Sans.ttf'),('SansBold','SansBold.ttf'),
                  ('Mono','DejaVuSansMono.ttf'),('Math','DejaVuSans.ttf')]:
    pdfmetrics.registerFont(TTFont(name,font_path(file)))
pdfmetrics.registerFontFamily('Sans',normal='Sans',bold='SansBold',italic='Sans',boldItalic='SansBold')
pdfmetrics.registerFontFamily('Kai',normal='Kai',bold='SansBold',italic='Kai',boldItalic='SansBold')
W,H = 210*mm,297*mm
GREEN='#0A9D53'; BLUE='#007FA5'; RED='#C63734'; INK='#262722'; GREY='#737C75'
LINE='#E7EFEA'; YELLOW='#FFF178'; LIGHTGREEN='#EDF5D8'; ORANGE='#D47827'
CX,CW,AX,AW=20,128,153,45
PL,PR,PW,BODYTOP=20,198,178,35
LX=RX=AX;LW=RW=AW
C=canvas.Canvas(str(PATH),pagesize=(W,H),pageCompression=1)
C.setTitle('大学学霸笔记版式规范 3.0 · '+('打印版' if EDITION=='print' else '电子批注版'))
C.setAuthor('University Xueba Notes')
PAGES=[]; BLOCKS=[]; FOOTER_ROWS=[]; PAGE_DECOR=[]; PAGE=0; ANNOTATIONS=[]

def rect(x,y,w,h,fill=None,stroke=None,lw=.4):
    C.setLineWidth(lw)
    if fill: C.setFillColor(HexColor(fill))
    if stroke: C.setStrokeColor(HexColor(stroke))
    C.rect(x*mm,H-(y+h)*mm,w*mm,h*mm,fill=bool(fill),stroke=bool(stroke))

def line(x1,y1,x2,y2,color=LINE,width=.4):
    C.setStrokeColor(HexColor(color)); C.setLineWidth(width)
    C.line(x1*mm,H-y1*mm,x2*mm,H-y2*mm)

def label(txt,x,y,size=10,font='Sans',color=INK,align='left'):
    C.setFont(font,size); C.setFillColor(HexColor(color))
    if align=='center': C.drawCentredString(x*mm,H-y*mm,txt)
    elif align=='right': C.drawRightString(x*mm,H-y*mm,txt)
    else: C.drawString(x*mm,H-y*mm,txt)

def para(txt,y,x=None,w=CW,size=10.5,leading=14.4,font='Kai',color=INK,gap=2.2):
    if x is None: x=CX
    st=ParagraphStyle('p',fontName=font,fontSize=size,leading=leading,textColor=HexColor(color),
        wordWrap='CJK',spaceAfter=0,allowWidows=0,allowOrphans=0)
    p=Paragraph(txt,st)
    _,h=p.wrap(w*mm,1000*mm)
    bottom=y+h/mm
    if bottom>268 and y<275: raise ValueError(f'page {PAGE} text overflow: {bottom:.1f} {txt[:45]}')
    p.drawOn(C,x*mm,H-y*mm-h)
    BLOCKS.append({'page':PAGE,'x':x,'y':y,'w':w,'h':h/mm,'text':txt})
    return bottom+gap

def heading(n,txt,y,color=BLUE):
    rect(CX,y,5.5,5.8,color)
    label(str(n),CX+2.75,y+4.5,11,'SansBold','#FFFFFF','center')
    label(txt,CX+7.4,y+4.7,12,'SansBold')
    return y+8.2

def smallhead(txt,y,color=BLUE):
    label(txt,CX,y+4,10.5,'SansBold',color)
    return y+6.5

def note(title,body,y,side='right',colour=BLUE):
    ANNOTATIONS.append({'kind':'note','title':title,'body':body,'anchor':y,'colour':colour,'side':side})
    return y

def blank(y=185,side='right',height=80):
    # The combined outer column receives one continuous writing area at page close.
    return None

def flush_annotations():
    from PIL import Image
    columns=[('outer',AX,AW)] if EDITION=='print' else [('left',LX,LW),('right',RX,RW)]
    positions=[]; writing=[]
    for side,x,w in columns:
        y=BODYTOP+4
        items=ANNOTATIONS if side=='outer' else [a for a in ANNOTATIONS if a['side']==side]
        for item in sorted(items,key=lambda a:a['anchor']):
            top=y
            if item['kind']=='image':
                with Image.open(COMIC) as im:
                    iw=min(34,w);ih=iw*im.height/im.width
                C.drawImage(str(COMIC),(x+(w-iw)/2)*mm,H-(y+ih)*mm,iw*mm,ih*mm,mask='auto')
                y+=ih
            else:
                colour=item.get('colour',BLUE)
                rect(x,y,1.6,5,colour)
                y=para(item['title'],y,x+2.4,w-2.4,size=8.5,leading=11.8,font='SansBold',color=colour,gap=2.3)
                if item['kind']=='bilingual':
                    y=en(item['term'].replace('<br/>',' '),y,x,w,size=8.7,leading=11.8,font='SansBold',gap=1.2)
                    y=en(item['definition'],y,x,w,size=8.4,leading=11.7,gap=1.2)
                    y=para(item['cn'],y,x,w,size=8.5,leading=11.8,gap=0)
                else:
                    y=para(item['body'],y,x,w,size=8.5,leading=11.8,gap=0)
            positions.append({'kind':item['kind'],'side':side,'x':x,'y':top,'w':w,'h':y-top})
            y+=6
        if y+10>250: raise ValueError(f'Annotation {side} column {PAGE} leaves too little writing space: {y:.1f}')
        blank_top=y+5
        label('我的批注',x,blank_top,8.2,'Kai','#A3B4A6')
        writing.append({'side':side,'x':x,'width':w,'start':blank_top+5,'end':268})
    PAGE_DECOR[-1]['annotation_blocks']=positions
    PAGE_DECOR[-1]['writing_areas']=writing

def start(title,tag='版式规范',color=GREEN,section_number=None):
    global PAGE,CX,AX,LX,RX,LW,RW,PL,PR,PW,BODYTOP,ANNOTATIONS
    if PAGE:
        flush_annotations();C.showPage()
    PAGE+=1; PAGES.append(title)
    odd=PAGE%2==1
    if EDITION=='print':
        CX,AX,PL,PR=(20,153,20,198) if odd else (62,12,12,190)
        LX=RX=AX;LW=RW=AW
    else:
        CX,LX,LW,RX,RW,PL,PR=38,12,22,170,28,12,198
    PW=PR-PL;ANNOTATIONS=[]
    body_top=35 if section_number is not None else 16
    BODYTOP=body_top
    yy=body_top+5
    while yy<=268:
        line(PL,yy,PR,yy,LINE,.3);yy+=5.2
    splits=[150.5 if odd else 59.5] if EDITION=='print' else [36,168]
    for split in splits: line(split,body_top,split,268,'#E1EACD',.5)
    subject='算法与数据结构' if PAGE>=9 else '学习笔记版式规范'
    label(subject,PL,11,8.6,'SansBold',GREEN)
    label('渐近分析' if PAGE>=9 else ('规范 3.0 · '+('打印版' if EDITION=='print' else '电子批注版')),PR,11,8.2,'Sans',GREY,'right')
    if section_number is not None:
        rect(PL,16,PW,13,color)
        p=C.beginPath(); p.moveTo(PL*mm,H-16*mm);p.lineTo((PL+7)*mm,H-16*mm);p.lineTo(PL*mm,H-23*mm);p.close()
        C.setFillColor(HexColor('#E1F1E5'));C.drawPath(p,fill=1,stroke=0)
        label(str(section_number),PL+4.5,25.2,15,'SansBold','#FFFFFF')
        label(title,PL+17,25.1,13,'SansBold','#FFFFFF')
        label(tag,PR-5,24.5,8.2,'Sans','#FFFFFF','right')
    label(str(PAGE),PR if odd else PL,292,9,'SansBold',GREEN,'right' if odd else 'left')
    if PAGE>=9:
        label('算法与数据结构 · 渐近分析',PL if odd else PR,292,8,'Sans',GREY,'left' if odd else 'right')
    PAGE_DECOR.append({'page':PAGE,'edition':EDITION,'page_number_side':'right' if odd else 'left',
        'section_number':section_number,'subject':subject,'body_top':body_top,
        'body_x':CX,'body_width':CW,'annotation_columns':
            [{'side':'right' if odd else 'left','x':AX,'width':AW}] if EDITION=='print' else
            [{'side':'left','x':LX,'width':LW},{'side':'right','x':RX,'width':RW}],
        'inner_margin':20 if EDITION=='print' else 12,'outer_margin':12,
        'content_left':PL,'content_right':PR})
    C.bookmarkPage(f'p{PAGE}');C.addOutlineEntry(title,f'p{PAGE}',level=0)
    footer(PAGE)
    return body_top

def table(headers,rows,y,widths=None,x=None,w=CW,size=9.1):
    if x is None: x=CX
    if widths is None: widths=[w/len(headers)]*len(headers)
    st=ParagraphStyle('cell',fontName='Kai',fontSize=size,leading=size*1.36,
        wordWrap='CJK',textColor=HexColor(INK))
    for rid,row in enumerate([headers]+rows):
        ps=[]; hs=[]
        for txt,ww in zip(row,widths):
            style=ParagraphStyle('cellh',parent=st,fontName='SansBold') if rid==0 else st
            p=Paragraph(str(txt),style);_,hh=p.wrap((ww-3.4)*mm,1000*mm)
            ps.append(p); hs.append(hh/mm)
        rh=max(hs)+4.0
        if y+rh>268: raise ValueError(f'page {PAGE} table overflow')
        xx=x
        for p,ww,hh in zip(ps,widths,hs):
            rect(xx,y,ww,rh,'#E6F2CF' if rid==0 else ('#FFFFFF' if rid%2 else '#F7F9F2'),'#C0CBC0',.4)
            p.drawOn(C,(xx+1.7)*mm,H-(y+(rh-hh)/2+hh)*mm)
            xx+=ww
        y+=rh
    return y+4

def claim(text,y):
    return para(f'<span backColor="{YELLOW}">{text}</span>',y)

def math(text,y,size=11):
    label(text,CX+CW/2,y+5.2,size,'Math',INK,'center')
    return y+10

pdfmetrics.registerFont(TTFont('Latin',font_path('DejaVuSerif.ttf')))
pdfmetrics.registerFont(TTFont('LatinBold',font_path('DejaVuSerif-Bold.ttf')))
pdfmetrics.registerFontFamily('Latin',normal='Latin',bold='LatinBold',italic='Latin',boldItalic='LatinBold')
COMIC=SKILL_ROOT/'assets/illustrations/asymptotic-upper-bound.png'
STYLE_CN='荒诞短漫画、冷笑话、极简小人物；脸部与服装主动做减法，依靠清楚轮廓、眼口和少量关键形状建立人物辨识度；表情偏冷脸、尴尬或突然夸张，姿态要有明确喜剧节奏，避免统一的可爱微笑。'
STYLE_EN='Absurd short-gag cartoons, deadpan humour and minimalist little figures. Simplify faces and clothing; build recognisable figures through clear silhouettes, eyes, mouths and a few key shapes. Use deadpan, awkward or suddenly exaggerated expressions, with poses that establish a clear comic beat.'

FOOTERS=[
 ('小笑话','待办事项写得特别整齐，感觉事情已经做完一半了。'),
 ('冷知识','A4 的长宽比接近 √2。沿长边对折后，纸张依然保持相同的长宽比例。'),
 ('名言','“One man\'s constant is another man\'s variable.” 一个人的常数，可能是另一个人的变量。Alan J. Perlis · Epigram 1'),
 ('小笑话','闹钟每天都很准时，准时被我关掉。'),
 ('小笑话','我问冰箱有什么吃的，它给了我一盏灯。'),
 ('冷知识','金星自转一周约需 243 个地球日，绕太阳一周约需 225 个地球日。NASA · Venus Facts'),
 ('冷知识','二分查找反复缩小一半的搜索区间；它在有序数组上的比较次数随输入规模呈对数增长。NIST DADS · Binary search'),
 ('名言','“To understand a program you must become both the machine and the program.” 理解程序时，可以逐步模拟机器执行与程序逻辑。Alan J. Perlis · Epigram 23'),
 ('小笑话','n：“我还可以继续长大。”c：“没关系，我的工作合同写着：固定常数。”'),
 ('小笑话','Threshold 对学生说：“从这里开始，每一个 n 都要参加检查。”'),
 ('冷知识','同一个函数可以有多个有效上界。3n＋2 同时属于 O(n) 和 O(n²)，线性上界提供了更具体的增长信息。'),
 ('小笑话','n² 想钻进 cn 的雨伞。c 说：“我已经固定好了，你怎么还在长高？”'),
 ('冷知识','对固定底数 a、b＞1，<font name="Math">log<sub>a</sub> n</font> 与 <font name="Math">log<sub>b</sub> n</font> 相差固定倍数，因此具有相同的 Θ 增长阶。'),
 ('小笑话','天气预报说适合出门，我决定让它先出去。'),
]

def footer(index):
    kind,txt=FOOTERS[index-1]
    size,leading=8.5,11.2
    st=ParagraphStyle('footer-measure',fontName='Kai',fontSize=size,leading=leading,
        wordWrap='CJK',textColor=HexColor(INK))
    text_x,text_w=PL+25,PW-29
    p=Paragraph(txt,st);_,h=p.wrap(text_w*mm,100*mm)
    rows=round(h/leading)
    if rows>2: raise ValueError(f'Footer {index} exceeds two lines')
    FOOTER_ROWS.append(rows)
    rect(PL,275,PW,10,'#F5F7DF')
    label(kind,PL+3,280.9,8.2,'SansBold',GREEN)
    y=275+(10-h/mm)/2
    end=para(txt,y,x=text_x,w=text_w,size=size,leading=leading,font='Kai',gap=0)
    if end>284.1: raise ValueError(f'Footer {index} overflow {end}')

def en(txt,y,x=None,w=CW,size=10.0,leading=14.4,gap=2.3,font='Latin'):
    if x is None: x=CX
    st=ParagraphStyle('en',fontName=font,fontSize=size,leading=leading,textColor=HexColor(INK),
        wordWrap=None,splitLongWords=False,allowWidows=0,allowOrphans=0)
    p=Paragraph(txt,st);_,h=p.wrap(w*mm,1000*mm)
    if y+h/mm>268: raise ValueError(f'English page {PAGE} overflow {y+h/mm:.1f}: {txt[:50]}')
    p.drawOn(C,x*mm,H-y*mm-h)
    BLOCKS.append({'page':PAGE,'x':x,'y':y,'w':w,'h':h/mm,'text':txt,'language':'English'})
    return y+h/mm+gap

def bilingual_note(title,term,definition,cn,y,side='right'):
    ANNOTATIONS.append({'kind':'bilingual','title':title,'term':term,'definition':definition,'cn':cn,'anchor':y,'side':side})
    return y

def comic(x,y,w=28):
    ANNOTATIONS.append({'kind':'image','anchor':y,'side':'right'})
    return y

EXAM_SENTENCES = {
 'Input size': 'Let n denote the number of elements in the input array.',
 'Asymptotic analysis': 'We compare the growth of the functions for sufficiently large n.',
 'Fixed constant': 'Choose c = 5 independently of the input size n.',
 'Threshold': 'For every integer n ≥ n₀, the inequality holds.',
 'Upper bound': 'The function 5n is an upper bound for 3n + 2 when n ≥ 1.',
 'Lower bound': 'For every n ≥ 1, we have 3n ≤ 3n + 2.',
 'Tight bound': 'The bounds 3n ≤ 3n + 2 ≤ 5n establish Θ(n) for n ≥ 1.',
 'Counterexample': 'Choosing n > max{c, n₀} violates the proposed inequality n² ≤ cn.'
}

def glossary(entries,y):
    y=table(['English term  中文术语','Definition  定义与理解'],[],y,[37,91],size=9.2)-4
    for term,cn,definition,explanation in entries:
        st=ParagraphStyle('gd',fontName='Latin',fontSize=9.2,leading=12.4,wordWrap=None,splitLongWords=False)
        sc=ParagraphStyle('gc',fontName='Kai',fontSize=9.3,leading=12.7,wordWrap='CJK')
        sn=ParagraphStyle('gt',fontName='LatinBold',fontSize=9.2,leading=12.2,wordWrap=None,splitLongWords=False)
        p1=Paragraph(term,sn);_,h1=p1.wrap(33.6*mm,1000*mm)
        p2=Paragraph(cn,sc);_,h2=p2.wrap(33.6*mm,1000*mm)
        p3=Paragraph(definition+'<br/><b>Exam:</b> '+EXAM_SENTENCES[term],st);_,h3=p3.wrap(87.6*mm,1000*mm)
        p4=Paragraph(explanation,sc);_,h4=p4.wrap(87.6*mm,1000*mm)
        rh=max((h1+h2)/mm+1.2,(h3+h4)/mm+1.2)+3.5
        if y+rh>268: raise ValueError(f'Glossary page {PAGE} overflow {y+rh}')
        rect(CX,y,37,rh,'#FFFFFF','#C0CBC0');rect(CX+37,y,91,rh,'#FBFCF6','#C0CBC0')
        for p,xx,yy,hh in [(p1,CX+1.7,y+1.7,h1),(p2,CX+1.7,y+1.7+h1/mm+1.2,h2),
            (p3,CX+38.7,y+1.7,h3),(p4,CX+38.7,y+1.7+h3/mm+1.2,h4)]:
            p.drawOn(C,xx*mm,H-yy*mm-hh)
        BLOCKS.append({'page':PAGE,'x':CX,'y':y,'w':CW,'h':rh,'text':term+' '+cn+' '+definition+' '+EXAM_SENTENCES[term]+' '+explanation,'language':'Bilingual'})
        y+=rh
    return y+4

# 01
y=start('阅读结构与新增栏目',section_number='01')
y=para('大学学霸笔记以完整基础知识为正文，配合淡横线、彩色知识编号、荧光划线、可选择的批注布局和手绘漫画。打印版使用奇右偶左的外侧宽栏和装订留白；电子批注版每页保留左右两栏。中文解释帮助理解，英文术语、例题解答和自测答案支持英语考试。每页底部安排一则名言、冷知识或小笑话。',y)
y=heading(1,'中央正文保持连续完整',y)
y=para('章节从需要解决的问题进入定义、条件、直觉、推导与例题，逐步联系后续知识。读者沿中央正文就能理解每个基础概念，再借助边栏恢复英文术语与常用答题表达。整册适合初次学习，也适合一遍又一遍地通读。',y)
y=table(['页面组成','内容与阅读作用'],[
 ['中央正文','定义、假设、推导、知识联系与代表性应用。'],
 ['双语术语','英文名称、中文含义、英文定义与考试表达。'],
 ['英文例题解答','完整英文题目、方法、步骤、理由与结论。'],
 ['自测与完整答案','题号一一对应；给出全部推理与结果。'],
 ['两种批注布局','打印后手写：外侧单栏；电脑或平板：左右双栏。'],
 ['每页底部','名言、冷知识、小笑话轮换，保持轻松的阅读节奏。']
],y,[35,93])
y=heading(2,'稳定地重复阅读',y)
y=para('同一概念的名称、符号、英文译法与主要定义句在全书中保持一致。后续章节再次使用旧知识时，恢复必要定义，再解释它在新情境中的用途。章末再读用完整段落恢复知识联系，英文答案展示如何把理解写成可评分的推理。',y)
y=heading(3,'选择使用方式与页面连接',y)
y=para('生成前选择：打印后手写批注，或在电脑、平板上批注。一个概念可以跨数页展开，术语页和例题页沿用相同符号与编号；正文依次连接定义、解释、应用、自测与完整答案。两种版式共用这些知识内容。',y)
note('语言安排','中文帮助理解；英文承担术语、答题与完整解答。',45,'left')
note('新版重点','每页底部一则趣味内容；每项自测一份完整答案。',45)
blank(128,'left',129);blank(133,'right',124)

# 02
y=start('页面坐标与底部空间')
if EDITION=='print':
    description='A4 页面为 210×297 毫米。正文宽 128，外侧批注宽 45，栏间距 5。内侧装订留白 20，外侧页边距 12 毫米。批注与页码在奇数页右侧、偶数页左侧。'
    schemes=[('奇数页：左侧装订，右侧批注',[(20,'装订','20 mm','#F4F1EB'),(128,'正文','128 mm','#EAF5EE'),(5,'','','#FFFFFF'),(45,'批注','45 mm','#F4F7E9'),(12,'外','12 mm','#FFFFFF')]),
             ('偶数页：左侧批注，右侧装订',[(12,'外','12 mm','#FFFFFF'),(45,'批注','45 mm','#F4F7E9'),(5,'','','#FFFFFF'),(128,'正文','128 mm','#EAF5EE'),(20,'装订','20 mm','#F4F1EB')])]
    rows=[['正文','奇数 x＝20；偶数 x＝62；宽 128 毫米。'],['批注','奇数 x＝153；偶数 x＝12；宽 45 毫米。'],['装订空隙','内侧 20 毫米：奇数左，偶数右，完全留白。'],['章首页绿条','起点 x＝20 奇／12 偶；宽 178，高 13 毫米。']]
else:
    description='A4 页面宽 210、高 297 毫米。正文固定宽 128，左批注宽 22，右批注宽 28，两个栏间距各 4 毫米。左右页边距各 12 毫米。每页都提供两块独立批注区。'
    schemes=[('电子版：每页固定左右双栏',[(12,'外','12 mm','#FFFFFF'),(22,'左栏','22 mm','#F4F7E9'),(4,'','','#FFFFFF'),(128,'正文','128 mm','#EAF5EE'),(4,'','','#FFFFFF'),(28,'右栏','28 mm','#F4F7E9'),(12,'外','12 mm','#FFFFFF')])]
    rows=[['正文','每页 x＝38；宽 128 毫米，左右位置固定。'],['左批注','每页 x＝12；宽 22 毫米。'],['右批注','每页 x＝170；宽 28 毫米。'],['章首页绿条','x＝12；宽 186，高 13 毫米。']]
y=para(description,y)
scale=CW/210
for title,segments in schemes:
    label(title,CX,y+3.2,8,'SansBold',BLUE);y+=5;xx=CX
    for ww,t,d,fill in segments:
        dw=ww*scale;rect(xx,y,dw,12,fill,'#8B9F91',.4)
        if t:
            label(t,xx+dw/2,y+4.7,6.6,'SansBold',INK,'center')
            label(d,xx+dw/2,y+9.3,5.4,'Sans',GREY,'center')
        xx+=dw
    y+=15
rows += [['正文上下缘','章首页 y＝35；续页 y＝16；下缘 y＝268 毫米。'],['底部趣味栏目','y＝275，高 10 毫米；一则内容，最长两行。'],['页码','基线 y＝292；奇数右，偶数左。']]
y=table(['区域','位置与尺寸'],rows,y,[30,98],size=8.8)
y=heading(1,'正文与页底之间的距离',y)
y=para('正文下缘位于 268 毫米，趣味栏目从 275 毫米开始，中间保留 7 毫米。趣味栏目高 10 毫米，每页一项，一行优先，最长两行。短笑话通常为 15 至 45 个汉字；名言、冷知识与署名一起控制在两行内。',y)
y=heading(2,'横线与批注带',y)
y=para('淡横线间距约 5.2 毫米。打印版合并外侧宽栏，电子版保留左右两栏；术语提示和插图之后留出连续书写区。较长的英文定义进入正文术语专页，边栏保留简短提示与个人批注。',y)
y=heading(3,'页眉 页脚与章节编号',y)
y=para('页眉使用科目名，页脚可用科目与章名或省略。长绿条、大号数字与章节标题仅在新章节首页出现，编号依次递增。续页从 y＝16 毫米开始，正文与批注向上补满原标题区。蓝色小编号标示知识点。',y)
y=heading(4,'打印装订与电子书写',y)
y=para('打印版按左右页镜像，书脊侧完全留白；单独手绘封面背面留空，正文第 1 页位于右手页。电子版两边批注区保持固定位置，导出可用 PDF 批注工具书写的文件。两版共用知识内容与完整答案。',y,size=9.8,leading=13.7)
blank(112,'left',145);blank(128,'right',129)

# 03
y=start('字体 颜色与重点标记')
y=para('中文正文使用具有书写感的字形，英文答案使用适合连续阅读的英文正文字体。中文标题采用黑体，代码采用等宽字体，数学符号与上下标保持规范字形。全书沿用同一组字体与颜色。',y)
y=table(['用途','字号与行距','排版要求'],[
 ['中文正文','10.5 pt；约 14.4 pt','完整段落，按知识关系连接。'],
 ['英文解答','10 至 10.5 pt；约 14.4 pt','按英文单词换行，完整句子。'],
 ['知识标题','12 pt','黑色标题配蓝色知识点编号。'],
 ['双语术语','9.2 至 10 pt','英文名称、中文名与定义相邻。'],
 ['侧栏解释','8.5 至 9 pt','短段落与准确术语，适当换行。'],
 ['页底栏目','8.5 pt；约 11.2 pt','一至两行，高 10 毫米。']
],y,[29,44,55])
y=heading(1,'色彩的固定含义',y)
y=table(['用途','颜色','表现方式'],[
 ['章节与页码','绿 #0A9D53','章首页绿条；页码在左右外侧交替。'],
 ['编号与术语','蓝 #007FA5','知识编号、术语标签、图题。'],
 ['定义与结论','黄 #FFF178','局部荧光划线。'],
 ['易错条件','红 #C63734','短提醒与限制条件。'],
 ['表头与页底','浅绿与淡黄','低对比背景，黑色正文。']
],y,[34,42,52])
y=heading(2,'强调完整条件',y)
y=para('定义中的变量范围、固定常数和阈值与结论一起呈现。普通说明段以少量局部标记突出要点，正式定义可以完整标记必要条件。中英术语使用一致的名称，英文答案中的公式与中文正文保持相同符号。',y)
y=para('英文长词按单词边界换行，必要时调整术语栏宽。关键公式单独排版，推导中的主要关系符号对齐。横线保持浅淡，黑白打印时仍然能通过编号、字重与文字辨认知识层级。',y)
note('英文字体','完整答案使用连贯的英文段落，保留冠词、量词与连接词。',47,'left')
note('高亮对象','成立条件与核心结论一起突出，便于再次阅读。',47)
blank(137,'left',120);blank(148,'right',109)

# 04
y=start('基础知识与双语学习')
y=heading(1,'每个概念的理解路径',y)
y=para('一个基础概念从它解决的问题开始，随后给出中文解释、英文术语、正式定义和适用条件。简单例子帮助读者理解符号，再展开推导、代表性应用、边界情形与相关知识。正文形成连续解释，读者能够反复沿同一条路径重建理解。',y)
y=para('数学内容写明变量范围、量词与每一步依据。算法内容写明输入、输出、计算模型、正确性与复杂度。统计内容区分总体、样本、随机变量、估计量与使用条件。知识所需篇幅由完整解释决定。',y)
y=heading(2,'扩展术语条目的内容',y)
y=table(['条目部分','应当包含的内容'],[
 ['英文名称','标准术语、常用缩写与相关表达。'],
 ['中文含义','对应概念和它在当前课程中的用途。'],
 ['英文定义','一至两句完整定义，保留关键条件。'],
 ['理解提示','说明相近概念之间的关系或差别。'],
 ['考试表达','一条能体现该术语用法的完整英文句子。']
],y,[31,97])
y=para('术语首次出现时紧邻正文，随后在例题中保持一致。每个核心主题可设置六至十二个扩展条目，较长条目集中成一页双语术语，边栏继续保留重点术语与个人批注。全书末尾设置术语索引，便于按英语考试用词返回知识位置。',y)
y=heading(3,'中文理解与英文作答',y)
y=para('中文正文解释概念如何成立，英文定义展示标准表述，英文例题解答展示论证如何展开。答案中的每一步包含必要理由与结果含义。读者能把中文建立的理解，转化为包含前提、连接词和结论的完整英文回答。',y)
y=para('章末再读采用连贯段落恢复基础知识。自测问题随后出现，每题附完整答案，包含依据、中间过程和最终结果。答案可以在下一页或章末答案区集中安排，题号保持一一对应。',y)
note('阅读路径','中文概念 → 英文定义 → 英文解答 → 自测与完整答案。',45,'left')
note('术语长度','核心词条扩展到定义与用法，让英文名称与知识一起熟悉。',45)
blank(145,'left',112);blank(158,'right',99)

# 05
y=start('103号插图与生图提示词')
y=para('全书手绘插图采用 handraw-style 仓库的第 103 个条目。生成插图后嵌入相应知识位置，配上清晰排版的术语、对白、图题与公式。角色和情景围绕本页知识展开，同一章保持一致的线条与表达。',y)
y=table(['条目','固定内容'],[
 ['编号','103'],['风格名称','Minimal Absurd Short-Gag Cartoon'],['参考作者','YAGI']
],y,[32,96],size=9.4)
y=smallhead('仓库原始风格特征',y)
y=para(STYLE_CN,y,size=9.8,leading=13.7)
y=smallhead('中文生图提示词模板',y)
y=para('风格名称：Minimal Absurd Short-Gag Cartoon。参考作者／风格名称：YAGI。核心风格特征：'+STYLE_CN+'主题：当前知识点对应的角色、动作和情景。配图用途：大学教辅笔记插图。背景透明，术语、对白和公式在页面中排版。',y,size=9.5,leading=13.1)
y=smallhead('English prompt template',y)
y=en('Style name: Minimal Absurd Short-Gag Cartoon. Reference author/style name: YAGI. Core style traits: '+STYLE_EN+' Theme: the characters, actions and scene that illustrate the current concept. Asset type: a university workbook illustration. Transparent background; labels and formulas are typeset on the page.',y,size=9.0,leading=12.5)
y=smallhead('从提示词到页面',y)
y=para('每幅插图确定一个知识点和一个具体情景，使用上述风格提示词调用生图功能。完成后检查动作与知识关系，再按比例嵌入。图题与英文术语紧邻插图，便于把视觉记忆接回正式定义。',y,size=9.8,leading=13.7)
note('画风要点','极简小人物、清楚轮廓、尴尬表情与荒诞短漫画。',45,'left')
comic(RX,95,28)
note('配图主题','雨伞表示上界；旁边的文字给出固定倍数与阈值。',143)
blank(132,'left',125);blank(196,'right',61)

# 06
y=start('英文例题与完整自测答案')
y=heading(1,'英文解答包含全部推理',y)
y=para('每道例题使用英文写出完整题目与解答。题目说明输入、条件与所求结果；解答说明使用的定义或方法，展开中间步骤，解释关键操作的理由，最后给出结论与含义。中文直觉解释安排在题目前后或对应边栏。',y)
y=para('证明题使用完整量词与逻辑连接。计算题保留代入、中间结果和单位。算法题说明前提、正确性、终止性和复杂度。英文答案从前提自然推进到结果，读者能直接学习相应的答题表达。',y)
y=heading(2,'常用考试表达',y)
y=table(['English expression','含义与用途'],[
 ['Let n denote ...','引入变量的含义。'],
 ['By the definition of ...','说明采用的定义或定理。'],
 ['Choose c = ... and n₀ = ...','给出固定常数与阈值。'],
 ['For every n ≥ n₀, ...','说明结论覆盖全部指定输入。'],
 ['Suppose, for contradiction, that ...','开始反证，并指出暂时假设。'],
 ['This contradicts ... Therefore, ...','说明矛盾位置并给出结论。']
],y,[64,64],size=9.0)
y=heading(3,'自测问题与答案一一对应',y)
y=para('每项自测都有独立编号和完整答案。概念题给出完整定义与条件；计算题给出全部计算；证明题给出论证；解释题写出关系与原因。答案安排在紧随其后的页面或统一答案区，读者可以闭书作答后逐项核对。',y)
y=para('一个问题包含数个小问时，答案按相同小问顺序呈现。关键步骤附理由，最终结论明确。答案中出现的新术语同时进入双语术语区，整章的符号与英文表达保持一致。',y)
note('英文作答','题目与全部解答用英语；中文批注补充理解。',45,'left')
note('答案完整性','定义、依据、中间过程、理由与结果都在答案中。',45)
blank(136,'left',121);blank(148,'right',109)

# 07
y=start('页底内容与整册组织')
y=heading(1,'每页底部固定一则内容',y)
y=para('名言、冷知识和小笑话在每页底部轮换，选材自由，可以使用生活、自然、历史、艺术等题材，也可以联系当前知识。名言写明作者，冷知识写清事实，笑话保持简短。整章逐页核对，确保每页都有内容，并让同一则材料保持一次出现。',y)
y=para('页底内容优先排成一行，最长两行；作者署名也计入行数。栏目高 10 毫米，正文与栏目之间保留 7 毫米。短句配浅色背景和小标签，翻到页底时轻松读完，正文与手写批注获得更多空间。',y)
y=heading(2,'整册按知识依赖展开',y)
y=para('课程大纲形成基础知识覆盖表，章节按必要前提展开。正文依次安排完整解释、扩展术语、英文例题、基础知识再读、自测问题与完整答案。材料较多时分卷制作，各卷沿用相同编号、术语、字体、插图风格与页底规则。',y)
y=heading(3,'学习文字直接说明知识',y)
y=para('笔记正文直接解释定义、条件、原因、推导与应用。数学成立条件、算法前提和事实之间的差异，在相关知识位置清楚说明。课程材料用于确定范围和术语，正文按章节组织，书末集中列出参考书、论文或网页来源。',y)
y=para('页内引用以学者、著作或概念名称为主。课程 PPT 的具体页码留在制作记录中。读者在成书页面看到的是知识本身、相关术语和推理过程。插图提示词与排版规则集中保留在规范文件，课程正文保持学习内容。',y)
y=smallhead('本册页底材料与风格来源',y)
y=para('Alan J. Perlis，Epigrams in Programming，1982，条目 1 与 23。NIST，Dictionary of Algorithms and Data Structures，Binary search。NASA，Venus Facts。手绘风格来自 yang0／handraw-style 的 103 号条目，固定版本 3737026e。',y,size=9.4,leading=13.1)
y=para('https://cs.yale.edu/homes/perlis-alan/quotes.html<br/>https://xlinux.nist.gov/dads/HTML/binarySearch.html<br/>https://science.nasa.gov/venus/venus-facts/<br/>https://github.com/yang0/handraw-style',y,size=8.7,leading=12.2,font='Sans')
note('每页栏目','名言、冷知识、小笑话轮换；题材自由，一至两行。',45,'left')
note('写作原则','正文直接推进理解；条件与理由贴近对应结论。',45)
blank(139,'left',118);blank(153,'right',104)

# 08
y=start('验收项目与连续样稿')
y=heading(1,'内容检查',y)
y=table(['检查项目','完成条件'],[
 ['完整基础知识','每个基础概念都有定义、条件与解释。'],
 ['双语术语','英文名称、中文名、英文定义与用法齐全。'],
 ['英文例题','题目与完整解答为英语，步骤与理由清楚。'],
 ['自测答案','每一题、每一小问都有完整答案。'],
 ['知识连贯','术语、符号、章节与题号一致。']
],y,[35,93])
y=heading(2,'页面检查',y)
y=table(['检查项目','完成条件'],[
 ['页底栏目','每页一则，最多两行；高 10 毫米，与正文保持间距。'],
 ['生成插图','采用 103 号提示词生成，再嵌入知识位置。'],
 ['批注空间','打印版外侧宽 45，内侧空 20；电子版两栏宽 22 与 28 毫米。'],
 ['文字与公式','中英文清晰，公式与上下标完整。'],
 ['分页与图表','文字、侧栏、图题与表格排列完整。']
 ,['页码与名称','奇数右、偶数左；科目名作页眉；章首页用绿条与大数字，续页正文与批注补满。']
],y,[35,93])
y=heading(3,'六页连续样稿',y)
y=para('第 9 页讲解函数增长与渐近上界；第 10 页展开八项中英术语；第 11 页用完整英文证明线性上界；第 12 页用完整英文反证平方函数的线性上界；第 13 页连续回顾基础知识并提出四项自测；第 14 页逐题给出完整英文答案。',y)
y=para('各页沿用相同的函数、符号和术语，知识、英语表达、图解和题目形成连续关系。页底逐页轮换名言、冷知识和小笑话，按所选方式留下个人批注区域：打印版外侧单栏与装订留白；电子版左右双栏。',y)
blank(73,'left',184);blank(91,'right',166)

# 09
y=start('函数增长与渐近上界','知识详解',section_number='02')
y=heading(1,'从输入规模到工作量',y)
y=para('输入规模 input size 通常用 n 表示，例如数组中的元素个数。设 f(n) 表示算法执行某项基本操作的次数。输入继续扩大时，比较工作量函数的增长速度，可以帮助我们理解需要的操作怎样增加。',y)
y=para('例如 f(n)＝3n＋2 随 n 线性增长，而 h(n)＝n² 随 n 平方增长。较小输入上可能出现不同的大小关系；渐近分析 asymptotic analysis 关注规模足够大之后持续成立的关系。',y)
y=heading(2,'大 O 的完整定义',y)
y=para('设 f(n) 在所讨论的输入上非负，g(n) 为正。<span backColor="#FFF178">存在固定常数 c＞0 与阈值 n₀，使所有 n≥n₀ 都满足 f(n)≤c·g(n)</span> 时，称 f 属于 g 的渐近上界，记为 f∈O(g)。n 在这里取正整数。',y)
y=en('<b>English definition.</b> We write f ∈ O(g) if there exist constants c &gt; 0 and n₀ such that f(n) ≤ c g(n) for every integer n ≥ n₀.',y,size=9.8,leading=14.0)
y=math('∃ c > 0, ∃ n₀, ∀ n ≥ n₀ :  f(n) ≤ c · g(n)',y,size=10)
y=para('常数 c 选定后保持固定，阈值 n₀ 指定比较从哪里开始。所有阈值之后的输入都满足不等式。有限个较小输入的表现，可以通过选择阈值处理；较大输入则需要被同一个常数倍持续控制。',y)
y=heading(3,'一次完整的理解',y)
y=para('令 f(n)＝3n＋2，比较函数取 g(n)＝n。对于 n≥1，有 2≤2n，从而 3n＋2≤5n。选择 c＝5、n₀＝1，定义中的全部条件都满足，得到 f∈O(n)。',y)
y=para('同一个函数可以拥有多个有效上界。对于 n≥1，n≤n²，因此 3n＋2≤5n²，也得到 f∈O(n²)。线性上界提供更具体的增长信息；紧确界 tight bound 则从上下两个方向刻画增长阶。',y)
y=heading(4,'分析的是哪个工作量函数',y)
y=para('最坏情况 worst-case、最好情况 best-case 与平均情况 average-case，分别决定我们正在分析哪个工作量函数。大 O 记号表达这个函数的上界。说明算法复杂度时，把输入规模、所统计的操作与所分析的情况一起写清。',y)
bilingual_note('规模','Input size','The number of elements or the size of an instance.','规模描述输入大小，例如数组元素个数。',45,'left')
bilingual_note('固定常数','Fixed constant','A value independent of the input size n.','选定后保持同一个值，覆盖全部较大输入。',122,'left')
comic(RX,63,28)
note('上界图解','雨伞对应 c·g(n)，较小角色对应 f(n)，阈值之后始终被同一上界覆盖。',103)
bilingual_note('考试表达','For every ...','For every n ≥ n₀, the inequality holds.','覆盖阈值之后的全部输入。',163)
blank(198,'left',59);blank(235,'right',22)

# 10
y=start('增长率的中英术语对照','扩展术语')
y=para('术语中的英文定义保留概念条件，中文解释连接本章的例子。答题时，输入规模、固定常数、阈值和量词共同决定论证的含义。',y)
y=glossary([
 ('Input size','输入规模','A measure of the amount of data in an input instance, usually denoted by n.','例如数组元素个数，决定工作量函数的自变量。'),
 ('Asymptotic analysis','渐近分析','The study of a function\'s growth as the input size becomes arbitrarily large.','比较输入持续扩大之后的增长关系。'),
 ('Fixed constant','固定常数','A constant chosen independently of n and kept unchanged for all inputs under consideration.','证明选定 c 后，后续输入使用相同的 c。'),
 ('Threshold','阈值','A starting value n₀ beyond which the stated relationship holds for every input size.','明确不等式从哪个规模开始持续成立。'),
 ('Upper bound','上界','A function that controls growth from above, up to a fixed positive multiplicative constant.','O 给出上方界限，同一函数可有多个上界。'),
 ('Lower bound','下界','A function that controls growth from below, up to a fixed positive multiplicative constant.','Ω 给出下方界限，使用固定正倍数。'),
 ('Tight bound','紧确界','A bound that describes the same growth rate using both upper and lower inequalities.','Θ 同时具有相应上界和下界。'),
 ('Counterexample','反例','An instance that violates a proposed universal statement and therefore shows that it is false.','一个违反全称结论的输入即可否定该结论。')
],y)
y=smallhead('量词在答题中的位置',y)
y=en('There exist constants ... such that, for every sufficiently large n, ...',y,size=9.6,leading=13.8)
y=para('存在 there exist 引入常数与阈值；所有 for every 说明不等式覆盖的输入范围。',y,size=9.8,leading=13.7)
bilingual_note('存在','There exists','At least one suitable choice can be made.','用来说明可以找到符合条件的常数。',48,'left')
bilingual_note('全称','For all','The claim applies to every element in the stated domain.','定义中 n≥n₀ 的每个输入都需要满足。',49)
blank(149,'left',108);blank(158,'right',99)

# 11
y=start('证明线性上界与紧确界','English worked example')
y=heading(1,'Example 1',y)
y=en('<b>Question.</b> Let f(n) = 3n + 2 for positive integers n. Prove that f ∈ O(n). Show that f ∈ Θ(n), and determine whether f ∈ O(n²).',y)
y=smallhead('Complete solution',y)
y=en('<b>Step 1: establish an upper bound.</b> By the definition of O(n), we must find fixed constants c &gt; 0 and n₀ such that f(n) ≤ cn for every n ≥ n₀. For every n ≥ 1, we have 2 ≤ 2n. Hence',y)
y=math('3n + 2 ≤ 3n + 2n = 5n.',y)
y=en('Choose c = 5 and n₀ = 1. These values are independent of n, and the required inequality holds for every n ≥ 1. Therefore, f ∈ O(n).',y)
y=en('<b>Step 2: establish a matching lower bound.</b> For every n ≥ 1, we also have 3n ≤ 3n + 2. Combining the two inequalities gives',y)
y=math('3n ≤ 3n + 2 ≤ 5n  for every n ≥ 1.',y)
y=en('Taking c₁ = 3, c₂ = 5 and n₀ = 1 satisfies the definition of Θ(n). Therefore, f ∈ Θ(n), so f has linear asymptotic growth.',y)
y=en('<b>Step 3: check the quadratic upper bound.</b> Since n ≤ n² for every n ≥ 1, the upper bound from Step 1 implies',y)
y=math('3n + 2 ≤ 5n ≤ 5n².',y)
y=en('The same constants c = 5 and n₀ = 1 establish f ∈ O(n²). This upper bound is valid but gives less precise growth information than Θ(n).',y)
y=smallhead('中文理解',y)
y=para('先找到上界，再找到同阶下界，就得到 Θ(n)。平方上界同样成立，因为它提供更宽松的上方范围。证明中的常数和阈值明确给出，每一步不等式说明相应依据。',y)
bilingual_note('选择常数','Choose ...','Choose c = 5 and n₀ = 1.','直接写出满足定义的具体数值。',44,'left')
bilingual_note('推出','Hence','Hence, the required inequality holds for every n ≥ 1.','连接依据与紧接着成立的结果。',44)
bilingual_note('结论','Therefore','Therefore, f has linear asymptotic growth.','给出证明完成后得到的正式结论。',136)
blank(140,'left',117);blank(218,'right',39)

# 12
y=start('反证平方函数的线性上界','English worked example')
y=heading(1,'Example 2',y)
y=en('<b>Question.</b> Let h(n) = n² for positive integers n. Prove that h ∉ O(n).',y)
y=smallhead('Complete solution',y)
y=en('<b>Step 1: assume the proposed bound.</b> Suppose, for contradiction, that h ∈ O(n). Then there exist fixed constants c &gt; 0 and n₀ such that n² ≤ cn for every integer n ≥ n₀.',y)
y=en('<b>Step 2: simplify the inequality.</b> Since n is positive, dividing both sides by n preserves the inequality. Therefore, the assumption requires',y)
y=math('n ≤ c  for every integer n ≥ n₀.',y)
y=en('<b>Step 3: choose a violating input.</b> Choose an integer n &gt; max{c, n₀}. Such an integer exists because the positive integers are unbounded. This choice satisfies n ≥ n₀ and n &gt; c, contradicting the inequality obtained in Step 2.',y)
y=en('<b>Conclusion.</b> No fixed positive constant and threshold can establish the proposed linear upper bound. Therefore, n² ∉ O(n).',y)
y=heading(2,'An unsuccessful choice of constants',y)
y=en('<b>Question.</b> Why does choosing c = 3 fail for f(n) = 3n + 2, even though f ∈ O(n)?',y)
y=en('<b>Complete answer.</b> Choosing c = 3 would require 3n + 2 ≤ 3n, which is false for every positive integer n. However, membership in O(n) requires the existence of at least one suitable constant and threshold. Choosing c = 5 and n₀ = 1 works because 3n + 2 ≤ 5n for every n ≥ 1. The failed choice c = 3 does not eliminate the successful choice c = 5.',y)
y=smallhead('中文理解',y)
y=para('反证需要覆盖任何固定常数。平方函数总能找到超过该常数的较大输入；线性函数则可以用另一组常数完成证明。两段论证所覆盖的选择范围决定了各自结论。',y)
bilingual_note('反证','Proof by<br/>contradiction','Assume the statement and derive a contradiction.','写明假设，再说明与哪一步发生矛盾。',45,'left')
bilingual_note('足够大','Sufficiently large','Large enough to exceed the stated threshold.','对应定义中的 n≥n₀，保留具体范围。',46)
comic(RX,158,28)
note('固定倍数','n 可以继续增大，c 在同一证明中保持固定。',196)
blank(155,'left',102);blank(237,'right',20)

# 13
y=start('增长率再读与闭书自测','章末再读')
y=heading(1,'把三个条件重新联系起来',y)
y=para('工作量函数 f(n) 描述选定模型下的操作次数。渐近关系比较输入足够大之后的增长。上界的证明选择固定正倍数 c 与阈值 n₀，再说明每个 n≥n₀ 都满足不等式。固定倍数、阈值和全部较大输入共同构成定义。',y)
y=para('3n＋2 的线性上界可由 c＝5、n₀＝1 建立。它也具有线性下界，因此属于 Θ(n)。平方函数 n² 相对于 n 的增长会超过任何固定倍数，所以无法得到线性上界。',y)
y=heading(2,'上界 下界与紧确界',y)
y=table(['记号','English term','条件与含义'],[
 ['O(g)','Asymptotic upper bound','存在 c＞0 与 n₀，使所有 n≥n₀ 时 f(n)≤c·g(n)。'],
 ['Ω(g)','Asymptotic lower bound','存在 c＞0 与 n₀，使所有 n≥n₀ 时 f(n)≥c·g(n)。'],
 ['Θ(g)','Asymptotically tight bound','存在 c₁、c₂＞0 与 n₀，使所有 n≥n₀ 时 c₁g(n)≤f(n)≤c₂g(n)。']
],y,[17,47,64],size=9.1)
y=para('这些定义在本章约定的非负工作量函数和正比较函数上使用。上下界可以选用不同常数，只要在同一个足够大的输入范围中持续成立。',y)
y=heading(3,'Self-test questions',y)
y=en('<b>Q1.</b> State the definition of f ∈ O(g), including the quantifiers and the roles of c and n₀.',y,size=9.8,leading=14)
y=en('<b>Q2.</b> Prove that 3n + 2 ∈ O(n) using c = 4. State a suitable threshold.',y,size=9.8,leading=14)
y=en('<b>Q3.</b> Explain why n² ∉ O(n), even if a very large fixed constant is allowed.',y,size=9.8,leading=14)
y=en('<b>Q4.</b> Explain the difference between O and Θ. Use f(n) = 3n + 2 to illustrate your answer.',y,size=9.8,leading=14)
y=para('下一页按 Q1 至 Q4 给出完整英文答案，包含全部定义、推导与结果。',y,size=9.8,leading=13.7)
bilingual_note('量词','Quantifier','A phrase specifying existence or universality.','例如存在 there exists 与所有 for every。',45,'left')
bilingual_note('增长阶','Order of growth','The rate at which work increases as n grows.','通过渐近关系比较输入增大后的工作量。',46)
blank(139,'left',118);blank(148,'right',109)

# 14
y=start('闭书自测的完整英文答案','Complete answers')
y=heading(1,'Answer to Q1',y)
y=en('For eventually non-negative f and eventually positive g, f ∈ O(g) means that there exist constants c &gt; 0 and n₀ such that f(n) ≤ c g(n) for every integer n ≥ n₀. The constant c is chosen independently of n and remains fixed. The threshold n₀ specifies where the inequality begins to hold for all subsequent input sizes.',y,size=9.8,leading=14)
y=heading(2,'Answer to Q2',y)
y=en('Choose c = 4 and n₀ = 2. For every n ≥ 2, we have 2 ≤ n. Therefore, 3n + 2 ≤ 3n + n = 4n. The constants are fixed, and the inequality holds for every integer n ≥ n₀. By the definition of O(n), 3n + 2 ∈ O(n).',y,size=9.8,leading=14)
y=heading(3,'Answer to Q3',y)
y=en('Suppose that fixed constants c &gt; 0 and n₀ establish n² ≤ cn for every n ≥ n₀. Dividing by positive n gives n ≤ c. Choose an integer n &gt; max{c, n₀}. This input lies beyond the threshold but violates n ≤ c. Thus every proposed fixed constant and threshold fail for some larger input, so n² ∉ O(n). Making c very large only moves the violating input further away.',y,size=9.8,leading=14)
y=heading(4,'Answer to Q4',y)
y=en('O gives an asymptotic upper bound. Θ gives both an upper and a lower bound of the same order. For every n ≥ 1, 3n ≤ 3n + 2 ≤ 5n. Hence f ∈ Θ(n), using c₁ = 3, c₂ = 5 and n₀ = 1. Since n ≤ n², we also have f(n) ≤ 5n², so f ∈ O(n²).',y,size=9.8,leading=14)
y=en('However, f ∉ Θ(n²). For any proposed lower-bound constant a &gt; 0 and threshold N, choose an integer n &gt; max{N, 1, 5/a}. Then f(n) ≤ 5n &lt; a n², so the quadratic lower bound fails. Thus the linear tight bound describes the growth more precisely than the quadratic upper bound.',y,size=9.8,leading=14)
y=smallhead('答案中的知识对应',y)
y=para('Q1 保留完整量词；Q2 给出常数、阈值与不等式；Q3 覆盖任何固定常数；Q4 同时说明上界与紧确界，并证明平方下界无法成立。',y,size=9.6,leading=13.3)
bilingual_note('由定义','By the definition','By the definition of O(n), the claim follows.','说明所用依据与正式结论的连接。',45,'left')
bilingual_note('任意给定','Any proposed ...','For any proposed constant and threshold, choose ...','说明论证覆盖全部候选常数与阈值。',47)
blank(136,'left',121);blank(152,'right',105)

flush_annotations()
C.save()
PATH.with_suffix('.layout.json').write_text(json.dumps({'pages':PAGES,'blocks':BLOCKS,'footer_rows':FOOTER_ROWS,'page_decor':PAGE_DECOR},ensure_ascii=False,indent=2))
print(json.dumps({'path':str(PATH),'pages':PAGE,'size_bytes':PATH.stat().st_size},ensure_ascii=False))
