"""Author-owned LP/simplex/DP calibration data; no source-book pages are copied."""
import argparse,json
from pathlib import Path

def build():
    seq=0
    def b(t,**kw):
        nonlocal seq;seq+=1
        return dict(id=kw.pop('id',f'b{seq:03}'),type=t,source_kind=kw.pop('source_kind','authored_example'),**kw)
    def core(t,section,**kw):return b(t,source_kind='textbook_core',source_id='taha10',source_section=section,**kw)
    def note(anchor,text,**kw):return dict(type='handwritten_annotation',anchor_block_id=anchor,kind='arrow_note',side='left',text=text,source_kind='editorial_synthesis',**kw)
    def side(anchor,text,**kw):return dict(anchor_block_id=anchor,text=text,source_kind='editorial_synthesis',**kw)
    def label(x,y,text,**kw):return dict(kind='label',x=x,y=y,text=text,**kw)
    def stroke(points,**kw):return dict(kind='polyline',points=points,**kw)
    def arrow(points,**kw):return dict(kind='arrow',points=points,**kw)
    def page(pid,title,kind,chapter,blocks,hand,sidebar=None,**kw):
        return dict(id=pid,title=title,type=kind,chapter_id=chapter,number=0,outline_ids=[pid],blocks=blocks,handwritten_layer=hand,handwriting_reason='知识地图以枝条关系组织，保留用户自行补注的位置。' if not hand else '',sidebar={'items':sidebar or []},**kw)
    # Coordinates: X=10+16*x, Y=88-17.5*y. Clip the second
    # constraint at Y=0, rather than moving its intercept to the origin.
    lp_graph=[dict(kind='polygon',points=[[10,88],[10,18],[42,53],[58,88]],fill='#EAF2D1'),arrow([[10,88],[90,88]]),arrow([[10,88],[10,5]]),stroke([[10,18],[74,88]],color='#B86A29'),stroke([[10+16*(6-88/17.5)/2,0],[58,88]],color='#477BA9'),label(86,98,'x'),label(2,8,'y'),label(0,98,'0'),label(12,16,'(0,4)'),label(59,97,'(3,0)'),label(44,52,'(2,2)'),label(53,16,'x+y=4'),label(58,38,'2x+y=6'),dict(kind='circle',x=42,y=53,r=2,fill='#B64930')]
    trace=[arrow([[10,77],[75,77]],color='#B86A29'),arrow([[75,77],[52,20]],color='#B64930'),label(3,94,'(0,0)'),label(72,94,'(3,0)'),label(49,15,'(2,2)'),label(20,67,'z: 0 → 9'),label(73,43,'9 → 10')]
    state=[arrow([[5,22],[44,48]]),arrow([[5,82],[44,48]]),arrow([[55,48],[90,48]]),label(0,15,'历史 A'),label(0,98,'历史 B'),label(40,39,'同一状态'),label(76,37,'相同后续'),label(29,82,'只保留影响未来的信息',size=8)]
    outline=[dict(id='guide',title='知识导览',level=1,parent_id=None,kind='volume_map',source_kind='editorial_synthesis'),dict(id='lp',title='线性规划',level=1,parent_id=None,kind='chapter',source_kind='textbook_core',source_id='taha10',source_section='2.1–2.4',textbook_chapter_number='2'),dict(id='sx',title='单纯形法',level=1,parent_id=None,kind='chapter',source_kind='textbook_core',source_id='taha10',source_section='3.1–3.5',textbook_chapter_number='3'),dict(id='dp',title='动态规划',level=1,parent_id=None,kind='chapter',source_kind='textbook_core',source_id='taha10',source_section='12.1–12.3',textbook_chapter_number='12')]
    pages=[]
    tree={'label':'运筹学','children':[{'label':'建立模型','children':[{'label':'变量与约束','formula':'x+y ≤ 4'},{'label':'可行域','drawing':lp_graph[:3]}]},{'label':'移动顶点','children':[{'label':'选入基与出基'},{'label':'枢轴与检验'}]},{'label':'分阶段决策','children':[{'label':'状态与转移'},{'label':'递推与回溯','formula':'Fᵢ(b)'}]}]}
    pages.append(page('guide-page','运筹学知识地图','volume_map','guide',[b('knowledge_map',tree=tree,height_rows=27,caption='从模型进入求解：线性规划描述资源限制；单纯形沿基本可行解迭代；动态规划记录阶段最优值。')],[],page_break=True))
    pages.append(page('lp-model','变量与约束','knowledge_dense','lp',[
        b('heading',text='生产计划',number='1'),b('paragraph',text='一家工坊生产两种可分割的混合料。每批甲获利3百元，每批乙获利2百元。两种原料分别只有4吨和6吨。'),
        core('definition','2.1',id='lp-vars',title='决策变量',symbol='x, y',text='决策变量表示需要决定的数量。本例 x、y 分别是甲、乙的生产批数；可以按小数批生产。'),
        b('table',id='lp-data',headers=['每批消耗','甲 x','乙 y','可用量'],rows=[['原料Ⅰ / 吨',1,1,4],['原料Ⅱ / 吨',2,1,6],['利润 / 百元',3,2,'最大化']]),
        core('definition','2.1',title='参数',text='参数是在本次模型中给定的数值。表中的单位消耗、利润和可用量都是参数；x、y 是待选的数量。'),
        b('formula_group',title='模型',items=[{'formula':'max z = 3x + 2y','reason':'z 是总利润，单位为百元。'},{'formula':'x + y ≤ 4;  2x + y ≤ 6','reason':'两行分别限制原料Ⅰ与原料Ⅱ的总用量。'},{'formula':'x ≥ 0;  y ≥ 0','reason':'生产量不取负数。'}]),
        core('definition','2.1',id='lp-feasible',title='可行解',text='满足全部约束的变量取值称为可行解。选 x=1、y=2 时，原料用量为3吨和4吨，均未超过库存，所以该方案可行。'),
        b('worked_micro_example',problem='方案 x=3、y=2 能否执行？',steps=['原料Ⅰ需要3+2=5吨，超过4吨。','原料Ⅱ需要2×3+2=8吨，超过6吨。'],answer='两种原料均不足，方案不可行。')
    ],[note('lp-vars','变量由我们选，参数由题目给。')],[side('lp-feasible','可行只表示做得到，尚未比较利润。',title='概念辨析')]))
    pages.append(page('lp-graph','可行域与最优解','knowledge_visual','lp',[
        core('definition','2.2',id='lp-region',title='可行域',text='全部可行解组成可行域。把每条线性不等式画成半平面，再取它们与第一象限的交集。'),
        b('concept_diagram',id='lp-figure',drawing=lp_graph,height_rows=8,caption='浅绿区域同时满足两条资源约束。红点是两条边界的交点。'),
        b('paired',left=[b('worked_micro_example',problem='求交点',steps=['x+y=4','2x+y=6','相减得 x=2，再得 y=2。'],answer='交点为(2,2)。')],right=[b('comparison_table',columns=['顶点','z'],rows=[['(0,0)',0],['(0,4)',8],['(2,2)',10],['(3,0)',9]])]),
        core('definition','2.2.1',id='lp-optimal',title='最优解',text='最优解是可行域中目标值最好的解。这里四个顶点中(2,2)利润最高，为10百元；目标等值线向利润增加的方向移动，最后接触该点。'),
        core('condition','2.2',boundary_level='A',text='本例可行域非空且有界，因此线性目标能在顶点取得最优值。无须逐一枚举区域内部的所有点。'),
        b('example_inline',text='原点利润为0；生产3批甲的利润为9百元；改为甲乙各2批，利润增加1百元。')
    ],[note('lp-region','边界画线，约束选半平面。'),note('lp-optimal','先筛可行，再比较目标。')],[side('lp-figure','在(0,0)代入不等式，可确定边界线的哪一侧满足约束。',title='选侧方法')]))
    pages.append(page('lp-translate','线性关系与约束翻译','comparison_page','lp',[
        core('property_list','2.1',id='lp-props',title='线性结构',items=[{'label':'比例性','text':'生产量乘2，消耗和利润也乘2；每批系数保持不变。'},{'label':'可加性','text':'甲乙的用量相加得到总用量，不含 xy 等相互作用项。'},{'label':'可分性','text':'变量允许小数值。按整件计数时，需要另外规定整数性。'}]),
        b('comparison_table',id='lp-trans',title='条件与式子',columns=['文字条件','数学表达','对象'],rows=[['至多4吨','x+y≤4','总用量'],['至少生产1批甲','x≥1','甲产量'],['甲不超过总量六成','x≤0.6(x+y)','产量比例'],['期末库存','Iₜ=Iₜ₋₁+qₜ−dₜ','流入减流出']]),
        b('process_steps',title='多期库存',steps=['期初库存进入本期；本期生产 qₜ 加入库存。','本期需求 dₜ 离开库存；余额成为期末库存 Iₜ。','期末库存进入下一期，同一变量连接相邻两期。']),
        b('concept_diagram',drawing=[arrow([[2,45],[95,45]]),label(1,29,'期初'),label(36,29,'生产'),label(72,29,'期末'),label(34,80,'扣除需求')],height_rows=3,caption='时间轴强调库存如何连接相邻期间。'),
        b('common_error',id='lp-error',text='“至少”应写成下界。例如 x≥1，不能写成 x≤1；先检查变量单位，再判断不等号方向。')
    ],[note('lp-trans','百分比的分母也是表达式。')],[side('lp-error','整数限制属于另一类模型。图解得到小数时，直接四舍五入可能破坏约束。',title='B级辨析')]))
    pages.append(page('lp-application','模型应用','application_page','lp',[
        b('table',headers=['资源','甲每批','乙每批','上限'],rows=[['原料Ⅰ',1,1,4],['原料Ⅱ',2,1,6]]),
        b('process_steps',id='lp-app-steps',steps=['令 x、y 为甲乙批数，利润为 z=3x+2y。','写出 x+y≤4、2x+y≤6，以及 x≥1、y≥0。','新顶点为(1,0)、(3,0)、(2,2)、(1,3)。','依次计算利润3、9、10、9百元，最大值为10百元。']),
        b('formula_relation',title='结果核查',items=[{'formula':'x=2, y=2; x+y=4; 2x+y=6','reason':'两个资源都用完，且甲产量满足最低订单1批。'},{'formula':'z=3×2+2×2=10','reason':'利润为1000元。'}]),
        b('common_error',id='lp-app-error',text='加入 x≥1 后须重新确定可行域。本例原最优点恰好仍满足新增限制，所以最优值保持不变。')
    ],[note('lp-app-steps','新增限制先改可行域。')],[side('lp-app-error','若最低甲订单改为3批，只剩(3,0)，利润降为9百元。',title='参数变化')],problem_number='01',problem='沿用混合料数据，客户要求甲至少生产1批。建立模型并求最优生产方案。',analysis='先写两条资源约束，再加入订单下界，比较新可行域的顶点。',solution='甲乙各生产2批，总利润1000元，两种原料均无剩余。',method='确定数量和单位；逐条翻译限制；计算后回代全部约束。'))
    pages.append(page('sx-basis','基与基本可行解','knowledge_dense','sx',[
        core('definition','3.1',id='sx-slack',title='松弛变量',text='在“≤”资源约束中加入非负松弛变量，使不等式变成等式。s₁、s₂ 分别表示两种原料的剩余吨数。'),
        b('formula_group',items=['x+y+s₁=4','2x+y+s₂=6','x,y,s₁,s₂ ≥ 0']),
        core('definition','3.2',id='sx-basis-def',title='基',text='从两行独立等式的系数矩阵中选择两列线性无关的列，构成一个基。对应变量称为基变量，其余称为非基变量。'),
        b('table',id='sx-columns',headers=['列','x','y','s₁','s₂'],rows=[['约束Ⅰ',1,1,1,0],['约束Ⅱ',2,1,0,1]],cell_marks=[dict(row=r,col=c) for r in (0,1,2) for c in (3,4)]),
        b('worked_micro_example',id='sx-basic-example',problem='选 s₁、s₂ 为基，令 x=y=0。',steps=['s₁=4，s₂=6。','全部变量非负，因此得到基本可行解。'],answer='生产量为0，原料全部剩余，利润为0。'),
        core('definition','3.2',title='基本解与基本可行解',text='令非基变量为0并解出基变量，得到基本解。若所得全部变量都非负，该基本解也是基本可行解。'),
        core('condition','3.2',boundary_level='A',text='选择的基矩阵必须可逆。不能任意选两列；线性相关的列无法唯一确定两个基变量。'),
        b('example_inline',text='s₁、s₂ 的列构成单位矩阵，因此本例容易得到初始基。单纯形法随后通过换基改进目标值。')
    ],[note('sx-basis-def','列的选择决定“谁由方程解出”。')],[side('sx-basic-example','基变量不保证严格大于0。等于0的基本可行解称为退化解。',title='B级辨析')]))
    pages.append(page('sx-pivot','入基与出基','process_page','sx',[
        core('rule','3.3',id='sx-enter',title='入基选择',text='从 z=3x+2y 开始，增加 x 能提高利润。本次选 x 入基；非基变量 y 保持0。'),
        b('comparison_table',id='sx-ratios',columns=['基变量','保持非负的限制','上界'],rows=[['s₁=4−x','4−x≥0',4],['s₂=6−2x','6−2x≥0',3]]),
        core('rule','3.3',id='sx-leave',title='出基选择',text='x 最多增至3，此时 s₂ 首先变为0，所以 s₂ 出基。最小比值检验只考虑限制入基变量增加的正系数行。'),
        b('formula_relation',id='sx-dict',title='一次字典更新',items=[{'formula':'x = 3 − 0.5y − 0.5s₂','reason':'由第二个约束解出入基变量 x。'},{'formula':'s₁ = 1 − 0.5y + 0.5s₂','reason':'把 x 的表达式代入第一个约束。'},{'formula':'z = 9 + 0.5y − 1.5s₂','reason':'把 x 代入目标函数并合并同类项。'}]),
        b('concept_diagram',drawing=trace,height_rows=5,caption='本轮从(0,0)移至(3,0)，利润由0增至9。下一轮沿另一条边到(2,2)。'),
        b('example_inline',text='令新非基变量 y=s₂=0，读出 x=3、s₁=1。新解依然可行，尚可增加 y 改善利润。')
    ],[note('sx-enter','这一轮只让一个非基变量增加。'),note('sx-dict','解出入基变量，再代回其他行。')],[side('sx-leave','比值3比4小，所以第二行先耗尽。选择最大比值会使第一轮越过可行域。',title='比值的含义')]))
    pages.append(page('sx-example','单纯形完整迭代','worked_example_page','sx',[
        b('table',id='sx-pivot-table',headers=['基','x','y','s₁','s₂','右端'],rows=[['s₁',0,'1/2',1,'−1/2',1],['x',1,'1/2',0,'1/2',3],['z',0,'−1/2',0,'3/2',9]],cell_marks=[dict(row=1,col=2)]),
        b('process_steps',id='sx-finish',steps=['目标行写成 z−0.5y+1.5s₂=9，因此选 y 入基。','比值为1÷0.5=2、3÷0.5=6，故 s₁ 出基。','第一行除以0.5，再消去其余两行的 y。']),
        b('table',id='sx-final-table',headers=['基','x','y','s₁','s₂','右端'],rows=[['y',0,1,2,'−1',2],['x',1,0,'−1',1,2],['z',0,0,1,1,10]]),
        b('formula_relation',items=[{'formula':'z=10−s₁−s₂ ≤ 10','reason':'松弛变量非负，故任何可行解都不超过10；当前解达到10。'}]),
    ],[note('sx-finish','枢轴行变成新基变量的表达式。'),dict(type='handwritten_annotation',kind='circle',side='inline',anchor_block_id='sx-pivot-table',target_cell=[1,2],source_kind='editorial_synthesis')],[side('sx-final-table','表中 z 行表示 z+s₁+s₂=10；目标值取右端，不能把整行当作变量取值。',title='读表')],problem_number='02',problem='接上一轮字典，完成第二次迭代，证明结果已经最优。表中各约束均按等式移项。',analysis='选择仍能增加目标值的 y，再用非负性限制决定谁出基。',solution='x=y=2，s₁=s₂=0，最大利润10百元。',method='读目标行；比值选出基；枢轴消元；以非负变量检验最优性。'))
    pages.append(page('sx-cases','特殊情形与两阶段法','core_problem_page','sx',[
        b('process_steps',id='sx-phase',steps=['引入人工变量 a≥0，写成 x+y+a=2。第一阶段最小化 w=a。','从 a=2 开始，可令 x 增至2、y=0，使 a=0；第一阶段最优值为0。','删除人工变量后，第二阶段最大化 x+2y=4−x。','由 x≥0，目标至多为4；取 x=0、y=2 达到4。']),
        b('comparison_table',title='四种情形',columns=['情形','识别线索'],rows=[['退化','基本变量中存在0'],['多重最优','最优面包含不同可行解'],['无界','目标可持续改善且无有限界'],['不可行','第一阶段最小人工变量和大于0']]),
        b('common_error',id='sx-special',text='退化不等于不可行。第一阶段检验原约束是否可满足；第二阶段才优化原来的目标。')
    ],[note('sx-phase','人工变量只为寻找起点。')],[side('sx-special','本例原约束 x+y=2 也可直接消元；这里用它展示两阶段法的两个目标。',title='方法说明')],problem_number='03',problem='最大化 x+2y，满足 x+y=2，x、y≥0。用两阶段法构造起点并求解。',analysis='等式没有现成的松弛变量基，先加入人工变量寻找可行基。',solution='第一阶段达到 a=0；第二阶段得到 x=0、y=2，最优值4。',method='第一阶段求可行；人工变量退出后，再优化原目标。'))
    pages.append(page('dp-state','阶段与状态','knowledge_visual','dp',[
        core('definition','12.1',id='dp-state-def',title='阶段与状态',text='动态规划按顺序处理决策。阶段表示处理到哪一步；状态保存决定未来可行选择和收益所需的信息。'),
        b('example_inline',id='dp-context',text='装载两类物品，容量7千克。甲每件重2千克、价值3；乙每件重3千克、价值4。每类可取任意非负整数件。按物品类别分阶段，以可用容量为状态。'),
        b('concept_diagram',drawing=state,height_rows=5,caption='只要阶段、可用容量及后续限制相同，不同历史可以共用同一个剩余问题。'),
        core('definition','12.1–12.3.1',id='dp-decision',title='决策与转移',text='在处理第 i 类物品时，决策 k 是该类选取的件数。若每件重 wᵢ，则留给前 i−1 类的容量为 b−kwᵢ。'),
        b('comparison_table',columns=['符号','本例含义','取值示例'],rows=[['i','允许使用的前 i 类物品',2],['b','容量上限 / 千克',7],['k','第 i 类取的件数','0、1、2'],['Fᵢ(b)','前 i 类在容量 b 内的最大价值','F₂(7)']]),
        core('condition','12.1',id='dp-boundary',boundary_level='A',text='状态必须包含影响未来的全部信息。若还有“甲最多两件”等限制，应限制决策集合；若收益依赖此前选择，还需补充状态。'),
        b('worked_micro_example',problem='处理乙类时取 k=1，剩余多少容量？',steps=['乙占3千克，容量由7变成4。','剩余4千克交给只允许甲类的子问题。'],answer='转到 F₁(4)，并加上乙的价值4。')
    ],[note('dp-state-def','阶段回答“到哪一步”，状态回答“还剩什么”。')],[side('dp-decision','这里 k 可为0、1、2。若是每件只能选一次的0–1背包，决策集合和递推式需相应改变。',title='模型区别')]))
    pages.append(page('dp-table','背包递推表','process_page','dp',[
        core('formula_relation','12.3.1',id='dp-recurrence',title='递推与边界',items=[{'formula':'Fᵢ(b)=max { k vᵢ + Fᵢ₋₁(b−k wᵢ) }','reason':'在整数 k=0,…,⌊b/wᵢ⌋ 中比较；vᵢ 是第 i 类单件价值。'},{'formula':'F₀(b)=0;  Fᵢ(0)=0','reason':'无物品或无容量时，最大价值为0；允许不装满。'}]),
        b('table',id='dp-values',headers=['i \\ b',0,1,2,3,4,5,6,7],rows=[['0',0,0,0,0,0,0,0,0],['甲',0,0,3,3,6,6,9,9],['甲乙',0,0,3,4,6,7,9,10]],cell_marks=[dict(row=3,col=8)]),
        b('worked_micro_example',id='dp-cell',problem='计算 F₂(7)。',steps=['k=0：0+F₁(7)=9。','k=1：4+F₁(4)=10。','k=2：8+F₁(1)=8。'],answer='取最大值10，对应乙取1件。',note='每格都在比较“本步收益 + 子问题最优值”。'),
        b('process_steps',title='回溯选择',steps=['从 F₂(7)=10 记录的 k=1，确定乙取1件。','容量变为4，转到 F₁(4)=6，确定甲取2件。','总重2×2+1×3=7，总价值2×3+1×4=10。']),
        b('common_error',id='dp-read',text='表格记录最优值，不能只看相邻数值猜选了什么。填表时同时保存达到最大值的 k，回溯才能还原方案。')
    ],[dict(type='handwritten_annotation',kind='circle',side='inline',anchor_block_id='dp-values',target_cell=[3,8],source_kind='editorial_synthesis'),note('dp-recurrence','先算小阶段，再用已有表值。')],[side('dp-cell','k=2 虽装了两件乙，但只剩1千克，甲无法装入；价值8小于10。',title='比较路径')]))
    pages.append(page('dp-application','资源分配实战','application_page','dp',[
        b('table',id='dp-return',headers=['投入单位',0,1,2,3],rows=[['项目A收益',0,4,7,8],['项目B收益',0,3,5,9]]),
        b('process_steps',id='dp-allocation',steps=['先计算项目A：F₁(b)=rA(b)，b 为可用预算。','让项目B取 k 单位，项目A最多使用3−k单位。','比较 rB(k)+F₁(3−k)，k=0、1、2、3。']),
        b('comparison_table',columns=['B分配 k','A分配 3−k','总收益'],rows=[[0,3,8],[1,2,10],[2,1,9],[3,0,9]],cell_marks=[dict(row=2,col=c) for c in range(3)]),
        b('formula_relation',items=[{'formula':'F₂(3)=max {8,10,9,9}=10','reason':'最大值出现在 k=1，因此B分1单位，A分2单位。'}]),
        b('common_error',id='dp-budget',text='两个项目的收益是给定表值，不要求与投入成正比。不能用单一“单位收益”替代整张收益表。')
    ],[note('dp-allocation','决策是本项目分多少，状态是还可分多少。')],[side('dp-budget','本表收益不减，可以用完预算；一般情形须允许余量。',title='条件说明')],problem_number='04',problem='有3单位预算，按表投资A、B两个项目，投入为非负整数，求最大收益及分配。',analysis='把预算作为状态，枚举最后一个项目的投入，余下预算交给前一阶段。',solution='A分2单位、B分1单位，总收益10。',method='列清阶段、状态、决策和收益；算最优值时记录选择，再回溯解释。'))
    dp_tree={'label':'动态规划','children':[{'label':'定义子问题','children':[{'label':'阶段 i'},{'label':'状态 b'}]},{'label':'枚举本步','children':[{'label':'决策 k'},{'label':'收益与转移','formula':'b−kwᵢ'}]},{'label':'计算与解释','children':[{'label':'边界 → 表格'},{'label':'保存选择 → 回溯'}]}]}
    pages.append(page('dp-map','动态规划方法图','chapter_map','dp',[b('knowledge_map',tree=dp_tree,height_rows=25,caption='先判断状态是否充分，再写递推。表格给出值，回溯还原决策；两者共同组成解答。'),b('memory_note',text='状态相同且未来相同，历史才能合并。')],[],page_break=True))
    pages.append(page('formula-page','模型与算法速查','formula_summary','dp',[
        b('formula_group',title='线性规划',items=[{'formula':'max cᵀx; Ax≤b; x≥0','reason':'参数 c、A、b 已给定，x 是决策向量。'}]),
        b('comparison_table',columns=['模型','先检查','再决定'],rows=[['LP','变量能否连续取值','图解或单纯形'],['背包','可选件数集合','阶段与容量状态'],['资源分配','各项目收益表','预算状态与回溯']]),
        b('formula_relation',title='单纯形终止说明',items=[{'formula':'z=10−s₁−s₂ ≤10','reason':'当前例中 s₁、s₂≥0，故10是可行解的目标上界。'}]),
        b('formula_group',id='formula-dp',title='整数件数背包',items=[{'formula':'Fᵢ(b)=maxₖ {kvᵢ+Fᵢ₋₁(b−kwᵢ)}','reason':'枚举0至⌊b/wᵢ⌋的整数 k；边界 F₀(b)=0。'}]),
        b('method_card',text='公式回查时同时读变量、决策范围、边界和单位。求得数值后回到原情境，报告可执行的方案。'),
        b('comparison_table',title='贯穿例结果',columns=['问题','最优方案','最优值'],rows=[['混合料','x=2、y=2','10百元'],['整数背包','甲2件、乙1件',10],['项目分配','A取2、B取1',10]])
    ],[note('formula-dp','决策集合也是公式的一部分。')],page_break=True))
    for n,p in enumerate(pages,1):
        p['number']=n
        if p['chapter_id']=='guide':p['outline_ids']=['guide']
        else:
            outline.append(dict(id=p['id'],title=p['title'],level=2,parent_id=p['chapter_id'],kind='feature' if p['type'] in {'worked_example_page','application_page','core_problem_page'} else 'chapter_map' if p['type']=='chapter_map' else 'section'))
            if not any(p['chapter_id'] in q['outline_ids'] for q in pages[:n-1]):p['outline_ids'].insert(0,p['chapter_id'])
    # Hierarchy order, independent of physical page headings.
    outline=sorted(outline,key=lambda n:({'guide':0,'lp':1,'sx':2,'dp':3}[n.get('parent_id') or n['id']],n['level']))
    outline.append(dict(id='glossary',title='分章专有词汇表',level=1,parent_id=None,kind='glossary'))
    # Additional visual teaching is authored, never generated from a density target.
    by_page={p['id']:p for p in pages}
    by_page['guide-page']['blocks'][0]['tree']={'label':'运筹学','children':[
        {'label':'建立模型','children':[{'label':'数量与资源','formula':'x+y ≤ 4'},{'label':'可行域','drawing':lp_graph[:3]},{'label':'目标比较','formula':'max 3x+2y'}]},
        {'label':'移动顶点','children':[{'label':'入基与出基','formula':'min {4/1,6/2}'},{'label':'更新与检验','formula':'z=10−s₁−s₂'}]},
        {'label':'阶段决策','children':[{'label':'阶段与容量','formula':'(i,b)'},{'label':'收益与转移','formula':'kvᵢ+Fᵢ₋₁(b−kwᵢ)'},{'label':'记录与回溯','formula':'甲2件 + 乙1件'}]}]}
    by_page['lp-translate']['blocks'].append(b('worked_micro_example',problem='甲恰占总产量六成，总量为5批时各产多少？',steps=['x=0.6×5=3，y=5−3=2。','这是比例条件的一个解；仍须另查资源约束。'],answer='比例成立，但它违反本例两种原料上限，所以不可行。'))
    from copy import deepcopy
    order_graph=deepcopy(lp_graph)
    order_graph[0]['points']=[[26,88],[26,35.5],[42,53],[58,88]]
    order_graph.extend([stroke([[26,0],[26,88]],color='#945E91'),label(28,12,'x=1')])
    by_page['lp-application']['blocks'].append(b('concept_diagram',drawing=order_graph,height_rows=5,caption='x≥1 删去左侧一带；浅绿部分为新的可行域，保留最优点(2,2)。'))
    by_page['lp-graph']['handwritten_layer'].append(note('lp-figure','两式相减得 x=2，再代回得 y=2。'))
    by_page['sx-example']['blocks'].insert(-1,b('concept_diagram',drawing=trace,height_rows=5,caption='两次换基的顶点轨迹，与图解法的最优点一致。'))
    by_page['sx-cases']['blocks'].insert(1,b('table',title='两个阶段的目标',headers=['阶段','目标','变量值','结束依据'],rows=[['Ⅰ','min a','x=2, a=0','人工变量和为0'],['Ⅱ','max x+2y','y=2','z=4−x≤4']]))
    by_page['sx-cases']['blocks'].append(b('example_inline',text='若原条件改为 x+y=−2 且 x、y≥0，则左边非负，原问题不可行。不可行性来自约束本身，不是“利润太小”。'))
    by_page['dp-table']['blocks'].append(b('concept_diagram',drawing=[arrow([[5,45],[42,45]]),arrow([[48,45],[88,45]]),label(0,28,'F₂(7)'),label(34,28,'F₁(4)'),label(70,28,'F₀(0)'),label(9,75,'乙1件'),label(55,75,'甲2件')],height_rows=3,caption='回溯沿保存的决策走；每一步都同时更新阶段和容量。'))
    by_page['dp-map']['blocks'][0]['height_rows']=18
    by_page['dp-map']['blocks'].insert(1,b('comparison_table',title='同一方法，不同状态',columns=['应用','阶段','状态','决策'],rows=[['背包','物品类别','容量','件数'],['人员规划','时期','期初人数','期末人数'],['设备更新','年份','设备年龄','保留或更换']]))
    by_page['formula-page']['blocks'].append(b('process_steps',title='解答检查',steps=['模型单位一致，所有约束均满足。','目标值与原情境对应，收益或成本不混淆。','算法给出了方案；证明最优时同时给界或终止依据。']))
    # Highlight spans are selected here by the author for these exact passages.
    selections={'lp-vars':('决策变量表示需要决定的数量','定义突出由决策者选择的数量'),
        'lp-feasible':('满足全部约束的变量取值称为可行解','突出全部约束同时成立'),
        'sx-basis-def':('两列线性无关的列','本例构成基的必要条件'),
        'sx-leave':('最小比值检验只考虑限制入基变量增加的正系数行','保留比值筛选的适用条件'),
        'dp-state-def':('状态保存决定未来可行选择和收益所需的信息','突出状态的充分信息作用'),
        'dp-boundary':('状态必须包含影响未来的全部信息','明确合并历史的条件')}
    from content_schema import walk_blocks
    for block in [b for p in pages for b in walk_blocks(p['blocks'])]:
        if block['id'] in selections:
            selected,reason=selections[block['id']];start=block['text'].index(selected)
            block['highlights']=[dict(start=start,end=start+len(selected),text=selected,reason=reason)]
    # Real word-level circle, in addition to the pivot-cell marks.
    target=next(b for b in by_page['lp-graph']['blocks'] if b['id']=='lp-region')['text'];selected='交集';start=target.index(selected)
    by_page['lp-graph']['handwritten_layer'].append(dict(type='handwritten_annotation',kind='circle',side='inline',anchor_block_id='lp-region',target_span=dict(start=start,end=start+len(selected),text=selected),source_kind='editorial_synthesis'))
    # A miniature column-selection diagram reinforces the basis definition.
    by_page['sx-basis']['sidebar']['items'].append(side('sx-columns','两列独立，才能解出两个基变量。',title='列选择',drawing=[arrow([[0,40],[30,40]]),label(32,44,'s₁  s₂'),label(33,78,'单位矩阵')],height_rows=3))
    concepts=[]
    for cid,definition,example,boundary in [('decision-variable','lp-vars','lp-feasible','lp-props'),('basis','sx-basis-def','sx-basic-example','sx-slack'),('stage-and-state','dp-state-def','dp-context','dp-boundary')]:
        concepts.append(dict(id=cid,importance='core',first_use_role='taught',preferred_representation=['definition','table','concept_diagram'],boundary_level='A',requires_worked_example=True,requires_visual=True,teaching_refs=dict(definition=[definition],plain_explanation=[definition],canonical_example=[example],example_mapping=[example],boundary=[boundary])))
    for c,visual,example in zip(concepts,['lp-figure','sx-columns','dp-values'],['lp-app-steps','sx-basic-example','dp-cell']):
        c['visual_refs']=[visual];c['example_refs']=[example]
    result = dict(content_schema_version=2,learning_mode='learning',scope='calibration',subject='运筹学学霸笔记',chapter='三章校准',sources=[dict(id='taha10',title='Taha, Operations Research: An Introduction, 10th edition',locator='User-supplied PDF, printed pp.45–76,99–123,469–488; physical page = printed page + 1')],outline=outline,pages=pages,concepts=concepts,annotation_policy={'chapter_min_free_fraction':.35},cover=dict(subject='运筹学',chapter='线性规划 · 单纯形 · 动态规划',subtitle='三章教学结构校准',note='依据 Taha 第十版相关章节组织；数值题与图为自编校准例。',edition_labels={'print':'打印版','digital':'电子版'}),frontmatter={'contents':{'title':'知识目录','last_page_min_density':.55,'visuals':[{'outline_id':'guide','height_rows':5,'drawing':trace},{'outline_id':'lp','height_rows':6,'drawing':lp_graph},{'outline_id':'dp','height_rows':5,'drawing':state}]}},chapter_glossary=[dict(chapter_id='lp',chapter_title='线性规划',entries=[dict(term_en='Feasible solution',meaning_zh='满足全部约束的解'),dict(term_en='Objective function',meaning_zh='评价方案优劣的目标函数')]),dict(chapter_id='sx',chapter_title='单纯形法',entries=[dict(term_en='Basis',meaning_zh='组成可逆子矩阵的基列'),dict(term_en='Pivot',meaning_zh='换基消元所用的枢轴元素')]),dict(chapter_id='dp',chapter_title='动态规划',entries=[dict(term_en='State',meaning_zh='决定未来子问题所需的信息'),dict(term_en='Backtracking',meaning_zh='依据已保存的选择还原决策')])],wide_reference={'title':'运筹学知识速查','label':'模型 · 算法 · 条件','columns':[{'title':'线性规划','formulas':['max cᵀx','Ax≤b; x≥0'],'notes':['变量、参数与单位','资源约束逐条翻译','结果回代检查']},{'title':'单纯形','formulas':['z=10−s₁−s₂'],'notes':['入基提高目标','比值控制可行','枢轴更新字典']},{'title':'动态规划','formulas':['Fᵢ(b)=maxₖ {kvᵢ+Fᵢ₋₁(b−kwᵢ)}'],'notes':['状态保留必要历史','边界给出计算起点','记录选择，回溯方案']},{'title':'贯穿例','formulas':['LP: x=y=2, z=10','DP: 2×3+1×4=10'],'notes':['收益和成本须注明单位','整数件数与连续数量区分','高级扩展单独标识']}]},metadata={'title':'运筹学三章校准','author':'','subject':'大学学霸笔记 v2 renderer calibration'})


    columns=result['wide_reference']['columns']
    columns[0]['formulas']=['max z=3x+2y','x+y≤4; 2x+y≤6','x≥0; y≥0']
    columns[0]['example']={'title':'图解回查','lines':['顶点：(0,0)、(0,4)、(2,2)、(3,0)。','两条边界联立，相减得x=2，代回得y=2。','四个目标值依次为0、8、10、9。','甲乙各2批，两种原料恰好用完。','z的单位为百元，因此利润为1000元。']}
    columns[1]['formulas']=['x=3−0.5y−0.5s₂','s₁=1−0.5y+0.5s₂','z=9+0.5y−1.5s₂']
    columns[1]['example']={'title':'第二轮枢轴','lines':['y增加可改进目标，选择y入基。','比值：1÷0.5=2，3÷0.5=6。','较小比值限制步长，因此s₁出基。','枢轴消元后：z=10−s₁−s₂。','s₁、s₂非负，故目标至多为10；当前解达到。']}
    columns[2]['formulas']=['Fᵢ(b)=maxₖ {kvᵢ+Fᵢ₋₁(b−kwᵢ)}','k=0,…,⌊b/wᵢ⌋; F₀(b)=0']
    columns[2]['example']={'title':'背包格值与回溯','lines':['甲：重2、值3；乙：重3、值4；容量7。','乙0件：F₁(7)=9。','乙1件：4+F₁(4)=10。','乙2件：8+F₁(1)=8。','选择乙1件，剩余容量4取甲2件，总价值10。']}
    columns[3]['example']={'title':'预算分配','lines':['投入0、1、2、3单位时：','项目A收益为0、4、7、8；B为0、3、5、9。','给B的预算k依次为0、1、2、3。','总收益rB(k)+rA(3−k)为8、10、9、9。','最大收益10：A分2单位、B分1单位。']}
    return result

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--output',type=Path,required=True);args=parser.parse_args();args.output.parent.mkdir(parents=True,exist_ok=True);args.output.write_text(json.dumps(build(),ensure_ascii=False,indent=2),encoding='utf-8');print(args.output)
