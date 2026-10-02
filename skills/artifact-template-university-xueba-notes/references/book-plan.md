# 书稿计划与检查

较长书稿、多个批次或双版本使用JSON计划保存教学语义、知识目录、页面承载和视觉关系。短任务可以在内部保留同样记录。

## 顶层字段

| 字段 | 内容 |
| --- | --- |
| scope | `chapter`或`whole_book` |
| edition | `print`或`digital`，双版本分别保存分页计划 |
| body_format | 固定为`teaching-units` |
| comic_style | 固定为`reference-anchored-sidebar` |
| required_topics | 需要覆盖的topic ID列表 |
| concepts | 教学概念对象列表 |
| outline | 独立知识目录列表 |
| worked_examples | 可选的典例与完整解答列表 |
| visuals | 教学视觉对象列表 |
| pages | 页面承载列表 |
| chapter_glossary | 完整书末尾的分章专有词汇组 |
| template_manifest | 实际使用的模板清单路径 |
| content_data | 供填充脚本读取的独立内容JSON路径 |
| source_comic_references | 实际查看并传入生图的原书裁片路径 |
| annotation_free_fraction | 当前章或书的可书写批注面积比例，0至1 |

## 核心概念

每项至少包含`id`、`topic`、`core`、`prerequisite_ids`、`definition`、`plain_explanation`和`canonical_example`。核心概念的定义、通俗解释和例子必须出现在正文首次承载该概念的位置。按学科需要增加`conditions`、`symbols`、`contrast_ids`、`derivation`、`evidence`或`causal_links`。`main_text`只记录最终教材稿或摘要，不能替代上述教学字段。

概念仍可记录`visual_ids`；没有图时写`prose_reason`。视觉引用必须双向对应。

## 知识目录

`outline`每项包含：

| 字段 | 内容 |
| --- | --- |
| id | 稳定目录节点ID |
| title | 真实知识名称或正式教学栏目名 |
| level | 从1开始的层级 |
| parent_id | 上级节点，顶层为`null` |
| kind | `part`、`chapter`、`unit`、`section`、`lesson`、`feature`或`appendix` |
| include_in_toc | 是否进入目录，默认`true` |

页面使用`outline_ids`登记自己承载的节点。目录页码取节点第一次出现的页面。页面标题不自动成为目录条目；分页产生的“续页”“答案一”“答案二”等标题不得进入目录。书末分章词汇表使用一个`appendix`节点，词条本身不进入目录。

## 典例与题目

默认完整书不要求自测、闭书回忆、独立答案页或答案词汇。`worked_examples`只记录实际需要的典例，包含稳定ID、所用概念、题目、完整解答及承载页。用户明确要求独立练习册时，才增加`questions`与`answers`并检查一一对应。

## 视觉与页面

visual kind可为`microdiagram`、`working_diagram`、`sidebar_comic`或`overview`。method可为`native`、`generated`或`source`。计划阶段status为`planned`，成品阶段为`embedded`；asset_path相对计划文件或绝对路径。精确图使用native或经核对的source。

page type可为`cover`、`contents`、`overview`、`knowledge`、`visual_explanation`、`process`、`worked_example`、`synthesis`、`recap`、`glossary`、`references`、`foldout`或`blank`。独立`answers`页只在用户明确要求练习系统时使用。完整书覆盖封面、分级目录、总览、知识、典例或方法、综合、书末词汇表和速查。页面包含`id`、`type`、`concept_ids`、`outline_ids`、`visual_ids`与可选`worked_example_ids`。

除封面、空白页和独立折页外，成品页面的`humour_lines`为1或2，`humour_position`固定为`page-bottom`。物理页底趣味条属于页面家具，不属于正文blocks。

## 分章专有词汇表

`chapter_glossary`按章分组。每组包含`chapter_id`、`chapter_title`和`entries`；每项只含`term_en`与`meaning_zh`。程序检查字段、空值、章节引用和重复项。人工检查每项是否为真正的学科专有词汇，并删除普通动词、连接语、句子碎片、题目措辞和答案表达。

## 执行

```sh
python scripts/validate_book_plan.py /path/to/book-plan.json --stage plan
python scripts/validate_book_plan.py /path/to/book-plan.json --stage delivery
```

检查教学字段、先修关系、目录父子关系、页面锚点、视觉双向引用、书末词汇表、趣味条位置和成品资产。连续三个普通知识页没有工作视觉或没有侧栏漫画时分别给出复查提醒。人工仍检查内容准确性、首次解释是否真正可懂、图像意义、目录层级和最终渲染。
