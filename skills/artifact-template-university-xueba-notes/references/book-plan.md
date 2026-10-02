# 书稿计划与检查

可用JSON计划保存覆盖关系并执行结构检查。用于较长书稿、多个批次或两个版本，短任务可以在内部保留同样记录而不要求额外文件。

## 字段

| 字段 | 内容 |
| --- | --- |
| scope | `chapter` 或 `whole_book` |
| edition | `print` 或 `digital`，双版本分别保存分页计划 |
| body_format | `teaching-units` |
| comic_style | `reference-anchored-sidebar` |
| required_topics | 需要覆盖的topic ID列表 |
| concepts | 对象列表：id、topic、main_text、visual_ids；没有图时写 prose_reason |
| questions | 扁平问题列表：id、prompt，每个小问单独登记；自测、自查及闭书回忆的prompt使用中文 |
| answers | 对象列表：question_id、content、status=`complete`；自测答案的content使用完整英文 |
| visuals | 对象列表：id、concept_ids、purpose、kind、method、status；成品阶段另有asset_path |
| pages | 对象列表：id、type、concept_ids、visual_ids、question_ids、answer_ids；成品另有humour_lines与humour_position |
| template_manifest | 实际使用的模板清单路径 |
| content_data | 供填充脚本读取的独立内容JSON路径 |
| source_comic_references | 实际查看并传入生图的原书裁片路径 |
| annotation_free_fraction | 当前章或书的可书写批注面积比例，0至1 |

`main_text`写实际短知识段或由完整稿件提取的摘要，用于记录知识确实有主栏位置，不能写“稍后补充”。`visual_ids`指向具体教学图。无图概念的理由解释为什么文字足够。

visual kind可为`microdiagram`、`working_diagram`、`sidebar_comic`或`overview`。method可为`native`、`generated`或`source`。计划阶段status为`planned`，成品阶段为`embedded`；asset_path相对计划文件或绝对路径。精确图使用native或经核对的source。计划文件不进入学习正文。

page type可为`cover`、`contents`、`overview`、`knowledge`、`visual_explanation`、`process`、`worked_example`、`synthesis`、`recap`、`glossary`、`answers`、`foldout`或`blank`。完整书需覆盖封面、目录、总览、知识、例题、综合、速查等教学任务，可在具体页面组合处理，拆分页时保证导航。除封面、空白页和独立折页外，成品页面（包括目录）的humour_lines为1或2，humour_position固定为`page-bottom`，表示物理页面最底部的独立浅绿（#F3F7E0）底、深色（#252823）文字横条。它是正文网格之外的固定页家具，不是正文结尾的知识栏目或blocks中的内容块；`top`和正文末尾位置均不合规。封面、空白页和独立折页可为0。字段使用humour_lines与humour_position，不恢复旧footer_lines字段。页码与趣味条文字互不遮挡。

## 执行

```sh
python scripts/validate_book_plan.py /path/to/book-plan.json --stage plan
python scripts/validate_book_plan.py /path/to/book-plan.json --stage delivery
```

检查覆盖、引用、遗漏小问答案、孤立图、唯一页型、风格选择、批注空白、趣味条位置声明与成品资产位置。连续3个普通知识页没有工作视觉或没有侧栏漫画时，分别给出复查提醒；工作图不能充抵漫画，漫画也不能充抵工作图。两类提醒独立统计，遇到其他页型时重新计数，属于审查信号，不是图片配额或交付错误。人工仍检查内容准确性、自测中文题干与完整英文答案、图像意义、图文关系及最终渲染，并确认趣味条实际位于物理页底、浅绿（#F3F7E0）底、深色（#252823）文字且不属于正文分区。声明status和文件存在不能证明内容正确或资产已实际出现在PDF中。

计划阶段还记录原书知识密度观察、标题候选、图表行槽和对应模板页。分目的知识联系与完整性需要人工核对，不能由页数、字数或短段数量代替。
