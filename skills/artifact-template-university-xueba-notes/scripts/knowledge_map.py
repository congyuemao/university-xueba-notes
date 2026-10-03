"""Organic, measured trees shared by searchable PDF drawing and SVG export."""
from html import escape
from pdf_template_layout import wrap, width
COLORS=['#287E69','#B86A29','#477BA9','#945E91','#B75B65','#7F852D']

def layout_tree(tree,w,h):
    def depth(n):return 1+max((depth(c) for c in n.get('children',[])),default=0)
    levels=depth(tree)
    if levels>4:raise ValueError('Knowledge map supports at most four levels; split the map')
    col=w/levels;nodes=[];edges=[]
    def weight(n):return sum(weight(c) for c in n.get('children',[])) or 1
    def visit(n,d,top,bottom,color):
        x=2+d*col;mid=(top+bottom)/2
        labels=wrap(n['label'],col-7,'Head' if d==0 else 'Body',11.5 if d==0 else 10)
        if n.get('formula'):labels+=wrap(n['formula'],col-7,'Math',9)
        needed=len(labels)*5+ (14 if n.get('drawing') else 0)
        if needed>bottom-top-3:raise ValueError('Knowledge map node is crowded: '+n['label'])
        label_lines=len(wrap(n['label'],col-7,'Head' if d==0 else 'Body',11.5 if d==0 else 10))
        extent=max(width(s,'Head' if d==0 else 'Body' if j<label_lines else 'Math',11.5 if d==0 else 10 if j<label_lines else 9) for j,s in enumerate(labels))
        node={'x':x,'y':mid,'lines':labels,'color':color,'depth':d,'max_w':col-7,'drawing':n.get('drawing'),'label_lines':label_lines,'extent':extent,'branch_y':mid+(len(labels)-1)*2.5+1}
        nodes.append(node);offset=top
        for i,c in enumerate(n.get('children',[])):
            span=(bottom-top)*weight(c)/weight(n);child_color=COLORS[i%len(COLORS)] if d==0 else color
            child=visit(c,d+1,offset,offset+span,child_color);offset+=span
            edges.append({'x1':x+extent+1,'y1':node['branch_y'],'x2':child['x'],'y2':child['branch_y'],'color':child_color,'width':max(.45,1.4-.4*d)})
        return node
    visit(tree,0,3,h-3,COLORS[0]);return {'width':w,'height':h,'nodes':nodes,'edges':edges}

def svg_text(layout):
    w,h=layout['width'],layout['height'];out=[f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}mm" height="{h}mm">','<rect width="100%" height="100%" fill="white"/>']
    for e in layout['edges']:
        x1,y1,x2,y2=(e[k] for k in ('x1','y1','x2','y2'));dx=(x2-x1)*.55
        out.append(f'<path d="M{x1},{y1} C{x1+dx},{y1} {x2-dx},{y2} {x2},{y2}" stroke="{e["color"]}" stroke-width="{e["width"]}" fill="none" stroke-linecap="round"/>')
    for n in layout['nodes']:
        for i,s in enumerate(n['lines']):
            out.append(f'<text x="{n["x"]}" y="{n["y"]-(len(n["lines"])-1)*2.5+i*5}" font-family="LXGW WenKai, sans-serif" font-size="3.5" fill="{n["color"]}">{escape(s)}</text>')
        out.append(f'<path d="M{n["x"]},{n["branch_y"]} h{n["extent"]+1}" stroke="{n["color"]}" stroke-width="0.4"/>')
        if n.get('drawing'):
            # Drawings are referenced by a descriptive accessible node; PDF uses the exact primitives.
            from teaching_blocks import drawing_svg
            out.append(drawing_svg(n['drawing'],n['x'],n['y']+5,n['max_w'],12))
    out.append('</svg>');return '\n'.join(out)
