# 书稿、来源与教学调度

v2的权威字段校验为scripts/content_schema.py。以Resources/content/operations-research-calibration.json为可执行示例。填写字段只证明结构，不能证明教会读者。

## 顶层

content_schema_version=2；learning_mode为learning（默认）或revision；sources、outline、pages、concepts、chapter_glossary；annotation_policy.chapter_min_free_fraction默认.35。print/digital由填充命令选择，与学习/复习模式独立。封面、目录、页眉、趣味条和折页接口见[模板工作流](template-workflow.md)。

sources每项含id、title、locator。locator记录用户材料的版次、印刷页与PDF物理页规则；不把文件名当成内容已检查的证明。

outline是独立知识树，不从分页标题推导。字段id、title、kind、level（1–4）、parent_id；可有ordinal_label。kind包括part、chapter、unit、section、lesson、feature、chapter_map、volume_map、appendix、glossary。目录节点有首个实际页锚点；父首子不能被拆到两栏。专题和导图作为正式节点。

## 来源身份

每个正文块、嵌套子块、侧栏项和手写批注都记录source_kind：

| 值 | 含义 |
| --- | --- |
| textbook_core | 指定教材范围内的知识；source_id与source_section必需 |
| course_core | 课程讲义/大纲规定的知识；同样需来源定位 |
| authored_example | 自编情境、数字题、工作图和解答，不伪装教材原题 |
| supplement | 教材/课程之外的补充；在章节或专题入口向读者明确标识 |
| editorial_synthesis | 作者整理的关系、总结、跨章综合 |

不必每段打印来源，但编辑数据必须区分。直接引文、争议事实和补充知识的边界在读者页可见。自编综合篇不使用textbook_chapter_number；映射教材章时需source_id/source_section。Taha第十版纸本1–21章之后，companion目录另有Chapter 22；自编综合建模不可冒用22。Bellman-Ford不能因属于最短路就标作该教材相应节核心内容。

## 概念调度

concepts包含id、importance（core/supporting/extension）、first_use_role、preferred_representation列表、boundary_level（A/B/C）、requires_worked_example、requires_visual。先修关系用prerequisite_ids；正文块中可用concept_ids建立对应。

- introduced：名称作为导航或分类出现，尚不代表学会；后续须安排正式教学位置。
- taught：五项教学检查已有实际块证据；不是因为字段非空自动成立。
- reused：调用已教知识，仅补当前推理所需回顾。

teaching_refs把definition、plain_explanation、canonical_example、example_mapping、boundary分别映射到真实块ID列表。五项可分布于不同载体，多个角色也可共用一个有证据的块；核心定义/主推理在主栏。A条件须同教学单元出现，B放后部或侧栏，C仅按课程要求进入主线。人工审查必须阅读引用位置，不能用无关块满足字段。

第一处introduced和首次taught位置可分别记录在occurrences中；例如导图先提到“随机模型”，并不要求第一页同时完成全部模型分类。requires_visual和requires_worked_example提醒作者安排实际图例，校验器检查关联，人工检查其教学作用。

## 页面及分页

pages含唯一id、title、type、chapter_id、outline_ids、blocks、handwritten_layer、sidebar.items。块含唯一id、type、source_kind及对应字段。页型见[page-types.md](page-types.md)。

同章同类型相邻段默认合流；page_break=true保留独立页面；group与keep_with_next链保持完整；标题与后块自动同页。目录锚点跟随起始块，批注跟随anchor_block_id迁移。页码以compiled.json为最终依据；不要持有失效的手工页码。

handwritten_layer必须评估，确实无必要时为空并写handwriting_reason。侧栏、手写、教学引用都必须能定位到实际输出。学习版按块完整性增加页数，不用大量首次定义填满章节概要页。

## 检查与交付

validate_book_plan.py识别v2并检查字段、唯一ID、引用、来源、专题构件等；旧计划接口保留兼容。即使用--stage delivery，自动通过仍不意味着人工内容或视觉通过。

分别保存automatic_structure、automatic_fields、human_content、human_visual，记录文件校验值、实际页和块ID；未执行为not_run。逐页语义检查数字所指对象、单位、符号和例题推理，尤其不能用“每期订为120”含混表达“三次开机费合计120元”。

chapter_glossary仍按章分组，每项只含term_en和meaning_zh。默认没有单独练习册；完整典例/综合应用直接嵌在教学正文。
