# 大学学霸笔记 · University Xueba Notes

依据课程讲义、教材和课堂笔记制作可从零学习的大学教辅 PDF。正文使用霞鹜文楷，独立龙藏手写层配合知识块、工作图、表格、完整例题与侧栏教学。

2026-10-04 本轮完成语言、例题、分段与语料库修订，沿用上一轮字体、Hand 层与 version 7 母版。默认 `learning`；复习压缩版 `revision` 与打印/电子版是两组独立选择。

- [打印样稿](skills/artifact-template-university-xueba-notes/Resources/examples/calibration-print.pdf)（23 页）· [电子样稿](skills/artifact-template-university-xueba-notes/Resources/examples/calibration-digital.pdf)（21 页）· [知识折页](skills/artifact-template-university-xueba-notes/Resources/examples/calibration-foldout.pdf)（1 页）
- [修订与复核记录](skills/artifact-template-university-xueba-notes/references/calibration-review.md) · [Skill 入口](skills/artifact-template-university-xueba-notes/SKILL.md) · [接口说明](skills/artifact-template-university-xueba-notes/references/template-workflow.md)

样稿以线性规划、单纯形法和动态规划三章的精选教学单元校准，共 18 页正文，另有封面、目录与书末词汇表。数值题与工作图为自编例，章节知识映射到用户提供的 Taha 第十版教材；没有重制全书。旧统计学样稿与数据保留为 v1 兼容性资料。

## 本轮能力

- 按 L1 首次教学、L2 概念复现、L3 例题、L4 侧栏/手写/速查分配语言密度。允许有教学作用的解释性重复，按语义主动分段。
- `worked_example` 分区渲染题目、分析、编号步骤、结果与方法；续页保留题号并标“续”。`formula_step` 把原因与关键公式分别排出。
- 默认不生成独立思维导图页。只有用户明确要求且同时满足信息量、已学内容总结、不挤占教学内容三项条件时启用；本样稿将有用内容移到速查页。
- 渲染后检查长段，标记隐式依赖前文和多步压缩的候选问题；自动结果与阅读、视觉复核分别记录。

公开语言资源包含 [语体指南](skills/artifact-template-university-xueba-notes/Resources/language-calibration/style-guide.md)、[自编例子](skills/artifact-template-university-xueba-notes/Resources/language-calibration/synthetic-examples.md)、[正反例](skills/artifact-template-university-xueba-notes/Resources/language-calibration/contrastive-examples.md)、[例题写法](skills/artifact-template-university-xueba-notes/Resources/language-calibration/example-writing.md)和[四层压缩等级](skills/artifact-template-university-xueba-notes/Resources/language-calibration/compression-levels.md)。私人参考目录另有 40 条短摘录，记录来源页码、语言功能与观察；它由 `.gitignore` 排除，不加入公开分发包。

## 使用

将 `skills/artifact-template-university-xueba-notes` 文件夹放入你的 Codex skills 目录，再调用 `$artifact-template-university-xueba-notes`。仓库修改不会自动替换其他位置的已安装副本。

```text
使用 $artifact-template-university-xueba-notes，依据我提供的教材制作线性规划学习版笔记。
同时输出打印版和电子版，中文讲解并保留必要英文术语。
用具体生产计划串起变量、约束、可行域和最优解，安排题干自足的完整例题。
首次教学使用完整自然的解释，例题分步解答，关键公式独立成行。
附书末分章英中术语表和独立知识折页。
```

| 选择 | 含义 |
| --- | --- |
| `learning` | 默认，按先修关系展开 |
| `revision` | 明确用于复习，允许压缩已学内容 |
| `print` | A4；20 mm 内侧空白装订区；外侧批注栏随奇偶页镜像 |
| `digital` | A4；固定双侧批注栏 |

## 本地生成

安装仓库根目录 `requirements.txt` 中的依赖后，进入 Skill 根目录运行。母版已随包提供，普通内容修订直接使用；只有修改页面几何或字体设置时才重建母版。

```sh
python scripts/prepare_fonts.py --output-dir .fonts
python scripts/validate_book_plan.py Resources/content/operations-research-calibration.json
python scripts/fill_template.py --content Resources/content/operations-research-calibration.json --templates Resources/templates --fonts .fonts --assets Resources/illustrations --edition print --fun-seed 41 --output output/calibration-print.pdf
python scripts/fill_template.py --content Resources/content/operations-research-calibration.json --templates Resources/templates --fonts .fonts --assets Resources/illustrations --edition digital --fun-seed 41 --output output/calibration-digital.pdf
python scripts/fill_template.py --content Resources/content/operations-research-calibration.json --templates Resources/templates --fonts .fonts --assets Resources/illustrations --foldout-only --output output/calibration-foldout.pdf
```

直接编辑 `Resources/content/operations-research-calibration.json`。`build_calibration.py --output <path>` 只校验并导出这份权威内容，不再用旧生成器覆盖已校准的语言。

离线字体目录须包含 `WenKai.ttf`、`LongCang.ttf`、`SansBold.ttf`、`DejaVuSans.ttf`、`DejaVuSerif.ttf`；用 `--source-dir /path/to/fonts` 传给字体脚本。字体与参考资源许可见[第三方说明](THIRD_PARTY_NOTICES.md)。

PDF 同时输出 `.layout.json` 与 `.compiled.json`，显式启用地图时另输出相应 SVG。超高不可拆教学单元会报错，需要编辑决定拆分位置；程序不自动补写知识。

## 检查

从仓库根目录运行：

```sh
python -m unittest discover -s skills/artifact-template-university-xueba-notes/tests -v
```

设置环境变量 `XUEBA_TEST_FONTS` 为准备好的字体目录，可运行真实字体与 PDF 渲染检查；未设置时相关检查会明确跳过。本轮 46 项测试通过、0 跳过；另通过官方 Skill 校验、v2 计划校验、v1 兼容生成与三份 PDF 自动审计。自动检查不能代替内容和视觉复核，具体范围及一项已复核的分页提示见修订记录。`PACKAGE_MANIFEST.json` 按公开分发范围记录当前工作副本的实际字节校验值。
