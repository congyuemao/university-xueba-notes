#!/usr/bin/env python3
"""Create fixed masters once; normal book runs use fill_template.py."""
import argparse,json
from pathlib import Path
from reportlab.pdfgen import canvas
from pdf_template_layout import *
p=argparse.ArgumentParser();p.add_argument('--fonts',required=True);p.add_argument('--output',required=True);a=p.parse_args()
register_fonts(a.fonts);out=Path(a.output);out.mkdir(parents=True,exist_ok=True)
manifest={'version':5,'paper':'#FFFFFF','page_mm':[210,297],'grid':{'first_baseline_mm':28.8,'pitch_mm':7.2,'rows':34,'rule_offset_mm':1},'fonts':{'body':['Body',11.6],'body_file':'WenKai.ttf','body_family':'LXGW WenKai Regular','english':['Latin',11],'sidebar':['Hand',10],'table':['Body',9.5]},'humour_strip':{'position':'page-bottom','top_mm':275,'height_mm':10,'background':'#F3F7E0','foreground':'#252823','font':'Hand','size_pt':10,'padding_mm':3,'max_lines':2,'line_pitch_mm':4.2,'single_baseline_mm':281.3,'double_baselines_mm':[279.2,283.4]},'roles':{'cover':0,'odd':1,'even':2,'opening_odd':3,'opening_even':4,'foldout':5,'blank':6},'editions':{}}
for edition in ('print','digital'):
    dest=out/(edition+'-master.pdf');c=canvas.Canvas(str(dest),pagesize=(210*MM,297*MM));c.setTitle('学霸笔记 '+edition+' PDF母版')
    # Cover fixed layer. No slogan, no variable subject text.
    rect(c,20,24,170,29,'#191919');text(c,'学霸笔记',28,44,'Head',31,'#FFFFFF')
    line(c,20,73,190,73,BLUE,.7);line(c,20,234,190,234,BLUE,.7)
    for yy in (184,191.2,198.4,205.6,212.8,220):line(c,20,yy,190,yy)
    c.bookmarkPage('cover');c.addOutlineEntry('封面', 'cover');c.showPage()
    manifest['editions'][edition]={}
    for role,even,opening in [('odd',False,False),('even',True,False),('opening_odd',False,True),('opening_even',True,True)]:
        g=page_geo(edition,even);manifest['editions'][edition][role]=g
        # Humour is fixed page furniture, below the notebook body.
        strip=manifest['humour_strip']
        rect(c,g['start'],strip['top_mm'],g['end']-g['start'],strip['height_mm'],strip['background'])
        for row in range(34):
            yy=manifest['grid']['first_baseline_mm']+row*manifest['grid']['pitch_mm']+manifest['grid']['rule_offset_mm']
            line(c,g['start'],yy,g['end'],yy)
        for x in g['dividers']:line(c,x,22,x,270,'#DDC683',.5)
        yy=manifest['grid']['first_baseline_mm']+(manifest['grid']['pitch_mm'] if opening else 0)-5.8
        # A restrained brush-shaped strip on the title grid slot.
        path=c.beginPath();path.moveTo((g['main_x']+.5)*MM,(297-yy)*MM)
        for x,y in [(g['main_x']+g['main_w']-1,yy+.35),(g['main_x']+g['main_w'],yy+6),(g['main_x'],yy+6.2)]:path.lineTo(x*MM,(297-y)*MM)
        path.close();c.setFillColor(GREEN);c.drawPath(path,fill=1,stroke=0)
        c.bookmarkPage(role);c.addOutlineEntry(('章首'if opening else'知识页')+(' 偶数页'if even else' 奇数页'),role);c.showPage()
    c.setPageSize((594*MM,210*MM));line(c,14,30,580,30,BLUE,.6,page_h=210)
    for yy in [39+7.2*i for i in range(22)]:line(c,14,yy,580,yy,page_h=210)
    for xx in [155.5,297,438.5]:line(c,xx,34,xx,198,'#DDC683',.5,page_h=210)
    c.bookmarkPage('foldout');c.addOutlineEntry('超宽知识速查','foldout');c.showPage()
    c.setPageSize((210*MM,297*MM));c.bookmarkPage('blank');c.addOutlineEntry('空白背页','blank');c.showPage();c.save()
(out/'template-manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2))
print('Created fixed print and digital masters and coordinate manifest.')
