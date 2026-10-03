# 大学学霸笔记 · University Xueba Notes

依据课程讲义、教材和课堂笔记制作可从零学习的大学教辅 PDF。正文使用霞鹜文楷，独立龙藏手写层配合知识块、工作图、表格、完整例题与侧栏教学。

2026-10-04 已按《下一轮复刻修订方案 v2》同时更新设计规范、内容 schema、渲染器、母版和校准样稿。默认 `learning`；复习压缩版 `revision` 与打印/电子版是两组独立选择。

- [新版打印样稿](skills/artifact-template-university-xueba-notes/Resources/examples/calibration-print.pdf) · [电子样稿](skills/artifact-template-university-xueba-notes/Resources/examples/calibration-digital.pdf) · [知识折页](skills/artifact-template-university-xueba-notes/Resources/examples/calibration-foldout.pdf)
- [修订与复核记录](skills/artifact-template-university-xueba-notes/references/calibration-review.md) · [字体对比](skills/artifact-template-university-xueba-notes/Resources/examples/font-comparison.pdf)
- [Skill 入口](skills/artifact-template-university-xueba-notes/SKILL.md) · [接口说明](skills/artifact-template-university-xueba-notes/references/template-workflow.md)

样稿以线性规划、单纯形法和动态规划三章的精选教学单元进行校准，含14页正文、目录和书末词汇表，另有折页。它不是 Taha 全书重制版。数值题与工作图为自编例，章节知识映射到用户提供的第十版教材；未把自编综合篇编号成教材第22章。旧统计学样稿与数据保留为 v1 兼容性资料。

## 使用

将 `skills/artifact-template-university-xueba-notes` 文件夹放入你的 Codex skills 目录，再调用 `$artifact-template-university-xueba-notes`。本次文件修改不会自动替换其他位置的已安装副本。

示例请求：

```text
使用 $artifact-template-university-xueba-notes，依据我提供的教材制作线性规划学习版笔记。
同时输出打印版和电子版，中文讲解并保留必要英文术语。
用具体生产计划串起变量、约束、可行域和最优解，安排完整模型应用页。
正文使用霞鹜文楷；手写批注、图表和侧栏承担各自的教学作用。
附书末分章英中术语表和独立知识折页。
```

| 选择 | 含义 |
| --- | --- |
| `learning` | 默认，按先修关系展开，不把全书压成摘要 |
| `revision` | 明确用于复习，允许压缩已学内容 |
| `print` | A4；20 mm内侧空白装订区；外侧批注栏随奇偶页镜像 |
| `digital` | A4；固定双侧批注栏 |

## 本地生成

安装仓库根目录 `requirements.txt` 中的依赖后，进入 Skill 根目录运行：

```sh
python scripts/prepare_fonts.py --output-dir .fonts
python scripts/build_pdf_templates.py --fonts .fonts --output Resources/templates
python scripts/build_calibration.py --output Resources/content/operations-research-calibration.json
python scripts/validate_book_plan.py Resources/content/operations-research-calibration.json
python scripts/fill_template.py --content Resources/content/operations-research-calibration.json --templates Resources/templates --fonts .fonts --assets Resources/illustrations --edition print --fun-seed 41 --output output/calibration-print.pdf
python scripts/fill_template.py --content Resources/content/operations-research-calibration.json --templates Resources/templates --fonts .fonts --assets Resources/illustrations --edition digital --fun-seed 41 --output output/calibration-digital.pdf
python scripts/fill_template.py --content Resources/content/operations-research-calibration.json --templates Resources/templates --fonts .fonts --assets Resources/illustrations --foldout-only --output output/calibration-foldout.pdf
```

离线字体目录须包含 `WenKai.ttf`、`LongCang.ttf`、`SansBold.ttf`、`DejaVuSans.ttf`、`DejaVuSerif.ttf`；用 `--source-dir /path/to/fonts` 传给字体脚本。独立目录可避免覆盖输入。字体与参考资源许可见 [第三方说明](THIRD_PARTY_NOTICES.md)。

v2 支持实际测量分页、不可拆教学单元、左右混排、锚点批注、圈词圈单元格、有机知识树和目录栏平衡。PDF 同时输出 `.layout.json`、`.compiled.json` 和知识树 SVG。复杂图或过长内容超出槽位时会报错，需要编辑修改；程序不自动补写知识。

## 检查

```sh
python -m unittest discover -s skills/artifact-template-university-xueba-notes/tests -v
```

从仓库根目录执行。设置环境变量 `XUEBA_TEST_FONTS` 为准备好的字体目录，可运行实际字体、混排、知识树及分页回归；未设置时这4项明确跳过。自动字段/结构检查与人工内容/视觉复核分别记录，schema通过不能代表成书通过。本轮结果见复核记录及 `PACKAGE_MANIFEST.json`。
