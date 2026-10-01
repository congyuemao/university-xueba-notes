# 大学学霸笔记 · University Xueba Notes

将大学课程编成可以反复阅读的完整知识笔记，复刻所提供教辅的格式、视觉风格与知识讲解安排，保持同一出版社学科系列的感觉。课程内容依据新资料编写。

## 当前规则

正文采用短解释、知识条目、小表格、公式、精确工作图与完整例题步骤。基础知识、条件、推导与答案保持完整。打印版使用纯白底以节省墨水，电子版使用暖白底；两版保留浅蓝横线，深蓝知识编号、绿色或黄绿笔刷式小节条、黄色荧光关键词、红橙手写批注各有固定用途。

漫画采用浅彩、Q版、简线、低细节、极少背景与短对白的教辅边栏手绘风格。原103号荒诞短漫画已退出默认流程，只作历史资源保留。生成成书时实际制作并嵌入漫画；数值图、公式和精确几何使用原生绘图与排版。

## 批注版本

| 用途 | 版式 |
| --- | --- |
| 打印后手写批注 | 奇数正文页右侧、偶数页左侧单条45 mm外侧批注栏，内侧留白20 mm |
| 电脑或平板批注 | 每页固定左右两条批注栏，宽22 / 28 mm |

沿用用户已选择的版本。需要两版时共用知识、术语、题目与答案ID，分别分页。约6:4的主副栏关系用于教学构图参考，普通批注页保留上述书写几何。

## 教学页与全书组成

按知识需要组合知识页、视觉解释页、实验或过程页、完整例题页、综合理解页和章末关系图。完整书包含学科封面、可导航目录、册级知识总览、完整章节、术语、完整答案与学科独立设计的超宽速查。章节请求按其范围制作。

英语考试提供完整英文题目与完整英文解答；每项自测和每个小问配完整答案。保留扩展中英术语、标准条件与例句。正文内容页保留最多两行的短页脚，封面、空白背面与独立速查折页不要求趣味页脚。

封面保持同系列标题、科目标牌、人物与学科名层级，按学科换色和图形。去除广告、版权页、ISBN、二维码、出版社商标与扫描水印。速查按学科选择公式、矩阵、关系图或判断流程，保留超宽页；需要常规打印时提供完整分块。

## 使用

完整skill位于 [skills/artifact-template-university-xueba-notes](skills/artifact-template-university-xueba-notes)。导入整个目录，保留参考、脚本、原始资源和许可证的相对路径。

> 使用大学学霸笔记，依据这些课程资料制作完整统计学笔记。采用打印批注版，英语考试，页面与漫画保持所提供教辅的系列风格。

> 使用大学学霸笔记，制作条件概率章节。我在平板上批注，采用电子双侧批注版。

## 规范入口

- [主流程](skills/artifact-template-university-xueba-notes/SKILL.md)
- [系列一致性](skills/artifact-template-university-xueba-notes/references/series-contract.md)
- [内容与语言](skills/artifact-template-university-xueba-notes/references/content-and-language.md)
- [视觉体系](skills/artifact-template-university-xueba-notes/references/visual-system.md)
- [教学页型](skills/artifact-template-university-xueba-notes/references/page-types.md)
- [边栏漫画独立提示词](skills/artifact-template-university-xueba-notes/references/sidebar-comics.md)
- [学科视觉](skills/artifact-template-university-xueba-notes/references/subject-visuals.md)
- [封面与超宽速查](skills/artifact-template-university-xueba-notes/references/cover-and-foldout.md)
- [参考页面校准](skills/artifact-template-university-xueba-notes/references/reference-observations.md)
- [制作与检查](skills/artifact-template-university-xueba-notes/references/production.md)
- [书稿计划格式](skills/artifact-template-university-xueba-notes/references/book-plan.md)

## 检查书稿计划

```sh
python skills/artifact-template-university-xueba-notes/scripts/validate_book_plan.py /path/to/book-plan.json --stage plan
python skills/artifact-template-university-xueba-notes/scripts/validate_book_plan.py /path/to/book-plan.json --stage delivery
```

结构检查覆盖主题、概念与图像联系、题目小问答案、页型、默认漫画风格、批注面积与最终资源文件。不能替代知识准确性审查或PDF逐页渲染检查。

## 历史样稿

assets/examples中的两份14页PDF和预览，以及原reference.docx保留作旧版几何和语言示范。它们的连续说明文和103号漫画不代表当前视觉标准。本次更新skill、参考规范与检查脚本，未将这些旧PDF重绘为新版样稿。

旧生成器需明确使用历史模式：

```sh
python skills/artifact-template-university-xueba-notes/scripts/build_reference.py --legacy-geometry-demo --edition print --font-dir /path/to/fonts --output old-print-reference.pdf
python skills/artifact-template-university-xueba-notes/scripts/verify_reference.py old-print-reference.pdf --edition print
```

字体准备仍可使用prepare_fonts.py及其source-dir离线选项。字体和历史提示词许可见 [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md)。用户提供的整本扫描与截图不加入本公开目录。
