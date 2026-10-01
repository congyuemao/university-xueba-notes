# 书稿计划与检查

可用JSON计划保存覆盖关系并执行结构检查。用于较长书稿、多个批次或两个版本，短任务可以在内部保留同样记录而不要求额外文件。

## 字段

| 字段 | 内容 |
| --- | --- |
| scope | `chapter` 或 `whole_book` |
| edition | `print` 或 `digital`，双版本分别保存分页计划 |
| body_format | `teaching-units` |
| comic_style | `pastel-educational-sidebar` |
| required_topics | 需要覆盖的topic ID列表 |
| concepts | 对象列表：id、topic、main_text、visual_ids；没有图时写 prose_reason |
| questions | 扁平问题列表：id、prompt，每个小问单独登记 |
| answers | 对象列表：question_id、content、status=`complete` |
| visuals | 对象列表：id、concept_ids、purpose、kind、method、status；成品阶段另有asset_path |
| pages | 对象列表：id、type、concept_ids、visual_ids、question_ids、answer_ids；成品另有footer_lines |
| annotation_free_fraction | 当前章或书的可书写批注面积比例，0至1 |

`main_text`写实际短知识段或由完整稿件提取的摘要，用于记录知识确实有主栏位置，不能写“稍后补充”。`visual_ids`指向具体教学图。无图概念的理由解释为什么文字足够。

visual kind可为`microdiagram`、`working_diagram`、`sidebar_comic`或`overview`。method可为`native`、`generated`或`source`。计划阶段status为`planned`，成品阶段为`embedded`；asset_path相对计划文件或绝对路径。精确图使用native或经核对的source。计划文件不进入学习正文。

page type可为`cover`、`contents`、`overview`、`knowledge`、`visual_explanation`、`process`、`worked_example`、`synthesis`、`recap`、`glossary`、`answers`、`foldout`或`blank`。完整书需覆盖封面、目录、总览、知识、例题、综合、速查等教学任务，可在具体页面组合处理，拆分页时保证导航。成品的正文内容页footer_lines为1或2，其他页型可为0。

## 执行

```sh
python scripts/validate_book_plan.py /path/to/book-plan.json --stage plan
python scripts/validate_book_plan.py /path/to/book-plan.json --stage delivery
```

检查覆盖、引用、遗漏小问答案、孤立图、唯一页型、风格选择、批注空白与成品资产位置。连续3页没有工作视觉会给出复查提醒，属于审查信号，不是图片配额。人工仍检查内容准确性、答案完整性、图像意义、图文关系及最终渲染。声明status和文件存在不能证明内容正确或资产已实际出现在PDF中。
