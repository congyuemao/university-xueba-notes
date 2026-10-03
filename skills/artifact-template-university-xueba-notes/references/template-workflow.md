# PDF模板与v2填充接口

实现入口为scripts/fill_template.py；测量/绘制在teaching_blocks.py，分页、目录、批注在book_compositor.py，schema在content_schema.py，树状地图在knowledge_map.py。v2使用version 7母版。旧统计内容按v1路径渲染，仅用于兼容性回归。

## 能力与边界

| 功能 | 当前行为 |
| --- | --- |
| 知识块 | 定义、性质、条件、例题、表格、步骤、公式组、图、方法有独立绘制逻辑 |
| 测量 | 字体实际宽度换行；表格按最长单元格计行；图占指定槽；测量绘制共用逻辑 |
| 分页 | 同章同页型相邻知识段默认流动；group和keep_with_next链不可拆；page_break强制新页；专题/导图独立 |
| 混排 | paired左右组合，ratio设左栏比例，各栏独立测量，高度取较大值 |
| 手写 | 独立Hand，红橙短句、曲箭头、圈画、下划线、波浪线、括号、打叉、小图槽 |
| 侧栏 | anchor_block_id随实际分页；顺序分配避免侧栏碰撞，超高报错 |
| 留白 | 计算整章侧栏面积加权可写比例，默认35%，不强制每页比例 |
| 地图 | 最多4级有机贝塞尔树，公式与小图节点；PDF可检索标签，另存SVG |
| 目录 | kind样式、测量换行、全局双栏平衡、父首子同栏、点线、专题、相关插图、尾页密度告警 |
| 审查 | 块占位密度、连续同结构、章节图表/手写/漫画统计；不宣称自动理解语义或像素密度 |

作者仍须处理：长证明的合适断点、复杂地图拆分、侧栏超长内容取舍、每句准确性和视觉相似度。SVG外部图优先转为嵌入字体的PDF；不假定任意SVG中文都能被MuPDF解析。程序不自动补写知识或画装饰以填空白。

## 使用

从Skill根目录运行；字体可离线准备。离线目录须含WenKai.ttf、LongCang.ttf、SansBold.ttf、DejaVuSans.ttf、DejaVuSerif.ttf。缺少时prepare_fonts.py从原项目下载；网络不可用则报错，不替换字体。许可在assets/licenses/。

```sh
python scripts/prepare_fonts.py --output-dir /path/to/fonts --source-dir /path/to/offline-fonts
python scripts/build_pdf_templates.py --fonts /path/to/fonts --output Resources/templates
python scripts/build_calibration.py --output Resources/content/operations-research-calibration.json
python scripts/validate_book_plan.py Resources/content/operations-research-calibration.json
python scripts/fill_template.py --content Resources/content/operations-research-calibration.json --templates Resources/templates --fonts /path/to/fonts --assets Resources/illustrations --edition print --fun-seed 41 --output /path/to/print.pdf
python scripts/fill_template.py --content Resources/content/operations-research-calibration.json --templates Resources/templates --fonts /path/to/fonts --assets Resources/illustrations --edition digital --fun-seed 41 --output /path/to/digital.pdf
python scripts/fill_template.py --content Resources/content/operations-research-calibration.json --templates Resources/templates --fonts /path/to/fonts --assets Resources/illustrations --foldout-only --output /path/to/foldout.pdf
```

母版一次构建并复用。几何以manifest为准：A4、Body 11.6 pt、首基线28.8 mm、行距7.2 mm、34槽；v2内容用页型规定的31/32槽，余量用于边界；趣味条275–285 mm、页码291 mm。目录无正文横线。

输出PDF、同名.layout.json、v2最终.compiled.json、地图.assets/*.svg。layout记录模板哈希、实际块坐标、批注位置、章节可写比例、目录栏高、图表统计、告警；人工审查默认not_run。目录链接/书签由最终页号生成。

## 内容块

v2所有块需唯一id、type、source_kind。教材/课程块另需source_id与source_section。来源和教学调度详见[book-plan.md](book-plan.md)。

| type | 主要字段与绘制 |
| --- | --- |
| definition | title、symbol可选、text；蓝定义标题及Body |
| property / rule / condition | title可选、text；condition需boundary_level |
| paragraph | text、language可选；连续解释 |
| property_list | title可选、items[{label,text}]；编号性质 |
| example_inline | text；红色例标记 |
| worked_micro_example | problem、steps、answer、note可选；完整短计算 |
| comparison / comparison_table / table | columns或headers、rows；widths_mm、cell_marks可选；紧凑网格 |
| process_steps | steps字符串或{label,text}列表；编号操作 |
| formula | text；居中公式 |
| formula_relation / formula_group | items字符串或{formula,reason}；公式与理由相邻 |
| common_error / memory_note / method_card | text；易错标识、Hand、方法分隔线 |
| concept_diagram | drawing或asset二选一、height_rows、caption |
| diagram_explanation | text；读图说明 |
| knowledge_map | tree{label,formula可选,drawing可选,children}、height_rows、caption可选 |
| paired | left与right块列表、ratio可选；左右并置 |
| group | blocks；完整不可拆教学单元 |
| handwritten_annotation | text、anchor_block_id、kind；流式批注或独立手写层 |

表格widths_mm作为列宽权重，仍保留不可断词的最小宽度；最终宽度由可用区域和实际字宽确定。

drawing用0–100相对坐标：line/polyline/polygon/arrow用points；circle用x/y/r；label用x/y/text/font/size。可指定color/fill。标签超出图槽时报错。图的数学精度来自显式坐标与核对过的数据。

不要机械把所有正文拆成定义标题；先选表达方式，再选块。group可包含定义、图和例子。典例详细解答同样可用表格、图和步骤。

## 手写与侧栏

pages[].handwritten_layer为空时需handwriting_reason。每项含anchor_block_id、kind、side、source_kind、text可选。side默认outer；数字版可指定left。kind为text、arrow_note、circle、underline、wave、bracket、strike、sketch。

文字批注分配侧栏行，默认从锚点结束后起排；冲突向下顺延，溢出停止。补图用drawing和height_rows。需要靠锚点顶部时显式after_anchor=false并检查先修阅读顺序。

side=inline用于圈画已有正文，支持target_cell=[行,列]（表头第0行）或精确target_span；无范围时括号/波浪线等作用于整个块。文字批注不直接覆盖正文。

sidebar.items同样需要锚点和来源，可有title、text、drawing或comic/asset、height_rows。普通侧栏教学用Body，二次加工用Hand。数字版保留两侧写字区。

## 荧光、目录与专题

text承载的知识块可给highlights：每项start、end是clean(text)的Unicode码点区间，另存完全匹配text与编辑reason。禁止全局词表；跨行分别绘制，改稿失效范围报错。

outline节点含id、kind、level、parent_id、title，可有ordinal_label。页面outline_ids跟随首块重新分页。frontmatter.contents.visuals用outline_id绑定drawing或asset及height_rows；图参与栏平衡。

专题页要求problem_number、problem、analysis、solution、method；blocks承载详细解答。整题溢出须改为有明确承接的解答页。glossary使用专用双栏，foldout为594×210 mm四栏，不能缩成A4纵页。
