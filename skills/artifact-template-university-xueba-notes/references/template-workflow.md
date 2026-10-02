# PDF模板填充

## 固定资源

| 资源 | 路径与用途 |
| --- | --- |
| 打印母版 | `Resources/templates/print-master.pdf`，保留奇偶页外侧栏及空白装订边 |
| 电子母版 | `Resources/templates/digital-master.pdf`，保留固定左右批注栏 |
| 模板清单 | `Resources/templates/template-manifest.json`，定义页型、位置、网格、字段和行容量 |
| 填充脚本 | `scripts/fill_template.py`，读取独立内容JSON并填入母版 |
| 趣味语料 | `Resources/fun-content/items.jsonl`；抽取入口为 `scripts/pick_fun_content.py` |
| 版式示例 | `Resources/examples/print-reference.pdf`、`digital-reference.pdf`、`foldout.pdf` |
| 漫画源图 | `Resources/reference-comics/`，使用实际原书裁片与来源索引 |

母版PDF负责固定纸面、横线、栏位、标题条、物理页底浅绿趣味横条和页码位置。内容JSON负责学科名称、章节、完整知识、题目答案、精确图与漫画资产。填充器复制对应模板页并叠加可搜索文字及图片，不重新绘制整套页面。

## 常规生成

1. 读取模板清单及填充脚本帮助，选择版本、页型与可用行槽。
2. 从完整课程稿组织有逻辑联系的分目，依实际原书密度校准，写入独立内容JSON。
3. 使用正文网格安排文字、公式、表格与工作图。内容超过字段容量时调整完整分目的分页，禁止静默裁切或无限缩小字号。
4. 原书漫画裁片作为实际图像参考生成新插图，登记资产路径及教学锚点。
5. 调用填充器复用母版，生成PDF及定位记录。
6. 先逐段复核高亮片段的语境和作用，再渲染全部页，核对实际文字与横线、图表尺寸、主栏知识密度、物理页底浅绿横条及其一至两行深色（#252823）趣味文字、奇偶侧栏和导航。

模板清单是坐标与网格的唯一来源。当前目标网格间距约7.2 mm，文字基线位于对应横线上方约1 mm；最终采用清单所列值；中文正文恢复第一版 LXGW WenKai Regular（霞鹜文楷，`Body`、`Hand` / `WenKai.ttf`），正文、中文标题、英文与数学字体均实际嵌入并核对字形。当前正文11.6 pt，首行基线28.8 mm，间距7.2 mm，共34行，最末横线267.4 mm。页底浅绿趣味横条位于y=275 mm、高10 mm，底色#F3F7E0、文字#252823；恢复首版物理位置，浅绿底与深色文字遵循所供截图。页码基线291 mm。上述数值与清单一致时采用，之后统一由清单读取；不同字体可调整基线的字体度量，不能引入每段随意移动。

## 扩充页型

只有内容确实需要清单未覆盖的页型时才增加母版。增加后保留PDF页、字段、基线、图槽、容量规则和一页填充示例，再用于后续相同任务。修复模板缺陷时修改母版或填充器一次，并重跑受影响页面，不能在每册稿件中复制一套新的排版代码。

打印与电子版可以采用不同字段位置，知识、题目和答案ID一致。最终PDF中的文字应可检索；填字以内容数据驱动，不要求用户手工在PDF表单内输入长篇课程内容。若用户另外要求可交互表单，再提供带文本字段的版本。

## 填充命令

以下命令在 skill 根目录运行。字体目录可以使用已准备的离线字体，输出目录先创建。打印与电子版共用内容文件。

```sh
python scripts/prepare_fonts.py --output-dir /path/to/fonts --source-dir /path/to/offline-fonts
python scripts/fill_template.py --content Resources/content/statistics-chapter.json --templates Resources/templates --fonts /path/to/fonts --assets Resources/illustrations --edition print --output /path/to/output/print-reference.pdf
python scripts/fill_template.py --content Resources/content/statistics-chapter.json --templates Resources/templates --fonts /path/to/fonts --assets Resources/illustrations --edition digital --output /path/to/output/digital-reference.pdf
python scripts/fill_template.py --content Resources/content/statistics-chapter.json --templates Resources/templates --fonts /path/to/fonts --assets Resources/illustrations --edition print --foldout-only --output /path/to/output/foldout.pdf
```

每次输出PDF和同名 `.layout.json` 定位记录，记录中每页的 `fun_content` 包含所选条目和出处。图像路径相对 `--assets` 指定的目录。

趣味条默认自动从随包语料随机抽取，每个有效页面使用不同条目。加 `--fun-seed 42` 固定随机结果；加 `--fun-used-file output/book-used.json` 让各章共用历史；加 `--fun-subject 统计学 --fun-include-general` 混合统计学内容与通用笑话、名句。用 `--fun-mode content` 可改用内容JSON原有的 `humour` 字段。完整用法见[趣味语料](fun-content.md)。

## 内容字段

| 字段 | 用途 |
| --- | --- |
| subject、chapter、chapter_heading | 学科、章节名称与开章标题 |
| running_header.left、right | 左右页眉文字，可省略以采用学科和章节 |
| cover | 封面subtitle、note、image及按print/digital区分的edition_labels；可覆盖subject和chapter |
| frontmatter.contents | 目录title与可选humour；目录条目由outline自动生成 |
| concepts | 核心概念的definition、plain_explanation、boundary和canonical_example，用于教学覆盖检查 |
| outline | 独立知识目录；每项含id、title、level、parent_id、kind与include_in_toc |
| pages | number、title、outline_ids、blocks和sidebar；每页可单独给humour |
| blocks | heading、paragraph、formula、table、comparison_bars；段落语言用language=en |
| comparison_bars | values、parameter_label和legend，数据和图注随章节替换 |
| sidebar | title、text、keywords、comic和calculation；所有教学内容来自当前页数据 |
| sidebar.comic | asset与speech，省略时不插入漫画或对白 |
| sidebar.calculation | title、lines和note，用于紧凑计算路径或公式补充 |
| chapter_glossary | 书末分章词汇组；每组含chapter_id、chapter_title与entries，每项只含term_en和meaning_zh |
| paragraph.highlights | 当前段落内人工审定的具体重点片段，每项含start、end、text、reason；按语境决定，不接受全局词表 |
| humour | `--fun-mode content` 时按页面顺序采用的手写趣味文字；默认random模式从语料库抽取。两种模式都填入固定页底横条，不进入正文blocks |
| wide_reference | title、label和最多四栏columns；各栏含title、formulas、notes和可选example |
| example | title与lines，速查栏内的例子或辨析 |
| metadata | PDF的title、author、subject和keywords |

空缺的可选漫画、对白、计算路径、关键词、回顾、封面副标题和折页例子自然省略。原有comic_brief与comic_text可保留为编辑记录，实际插图只由sidebar.comic指定。另一章节替换内容JSON及对应图像即可，不能通过修改填充器中的页码条件选择该章的漫画、关键词或学科文字。每页内容仍须遵守模板行容量，复杂图形需要对应受支持的块类型。

## 语境高亮

先通读完整分目，判断当前段落承担的解释任务，再选出有学习价值的具体判断、条件、对比或因果关系。高亮可以是一小段短语或一句关键论述，应保留理解它所需的对象、限定和关系。普通复现、铺垫和例子背景可以完全不标。同一词语在别处出现时重新判断，不能沿用命中结果。禁止通过关键词列表、词频、正则或全文搜索自动决定高亮范围；禁止将旧emphasis列表批量转换为局部命中列表。

内容作者负责意义判断，填充器只验证并绘制已经选定的片段。每个paragraph块可给highlights，未提供时完全不标。每项记录：

- start和end：在`pdf_template_layout.clean(block["text"])`结果中的Unicode字符索引，零起点、左闭右开；不按UTF-8字节或UTF-16单元计数。
- text：该索引对应的原文片段，用于检查正文改动后标记是否失效。
- reason：此处值得强调的具体理由，仅存编辑数据，不印入笔记。不得只写“关键词”或“重要”。

例如段落“已知B发生后，条件B决定分母，联合事件A∩B决定分子。”可针对定义中的分子分母对应关系选择下列片段。另一段落提到B时仍需独立判断。

```json
{
  "type": "paragraph",
  "text": "已知B发生后，条件B决定分母，联合事件A∩B决定分子。",
  "highlights": [
    {"start": 7, "end": 26, "text": "条件B决定分母，联合事件A∩B决定分子", "reason": "此处解释条件概率定义中分母与分子的对应关系，复习时需要连同对象一起读。"}
  ]
}
```

正文调整后重新阅读并核对片段；跨行时标记跟随同一片段分成相邻行的笔触。填充器拒绝非空顶层emphasis、索引越界、片段文本不符或重叠的标记，不静默退回关键词匹配。渲染后既检查位置，也检查高亮内容能否帮助重建该段的论述。

## 正文术语与书末词汇表

核心概念在正文第一次实质出现的位置完成教学：给出规范定义、通俗解释、必要条件或边界及代表性例子。不能把这些说明推迟到词汇表，也不能用侧栏中的英文提示代替正文。

完整书的最后一个正式内容区为分章专有词汇表。按正文首次实质出现顺序分组，每项只写标准英文术语与简明中文释义。排除普通动词、连接语、句子碎片、单题措辞、英文例句、题号和答题用途说明。词汇较多时增加页数，保持字号、基线和完整条目，不挤进过小表格，也不静默截断。

填充器先由outline和页面锚点生成多级目录，再按整条词汇分页；打印版继续保持左右侧栏和正文首页正面起排。过长到一页无法容纳的单条释义会报错，由作者重新组织。漫画分布、概念覆盖、词条选择与语境判断需按技能的编辑检查执行，程序不以数量或关键词代替判断。

`Resources/content/statistics-chapter.json`是当前内容字段示例，`Resources/examples/`中的打印版、电子版及速查PDF由该数据生成，展示分级知识目录、正文首次解释、局部语境高亮与书末分章专有词汇表。示例的词条和漫画分布只对应本章，不构成其他课程的数量配额；新章节仍按实际知识组织。
