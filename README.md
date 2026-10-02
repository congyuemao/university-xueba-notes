# 大学学霸笔记 · 清理完整版

本包包含当前使用的 skill 规范、生成脚本、PDF 母版及统计学完整示例。导入 `skills/artifact-template-university-xueba-notes/` 整个目录，保持文件的相对路径。

## 文件入口

以下路径均相对于 `skills/artifact-template-university-xueba-notes/`。

| 内容 | 路径 |
| --- | --- |
| Skill 主规范 | `SKILL.md` |
| 内容、语言、视觉与版式规范 | `references/` |
| 6 个现行生成与检查脚本 | `scripts/` |
| 打印版、电子版 PDF 母版及坐标清单 | `Resources/templates/` |
| 统计学章节内容 | `Resources/content/statistics-chapter.json` |
| 17 页打印版示例 | `Resources/examples/print-reference.pdf` |
| 17 页电子版示例 | `Resources/examples/digital-reference.pdf` |
| 独立知识速查 | `Resources/examples/foldout.pdf` |
| 当前预览图 | `Resources/examples/print-preview.png` |
| 定位及检查记录 | `Resources/examples/*.layout.json`、`verification.json` |
| 3 幅生成漫画及提示词 | `Resources/illustrations/` |
| 8 幅漫画参考裁片与来源索引 | `Resources/reference-comics/` |
| 图标与字体许可 | `assets/` |

当前规范包括中文词汇、英文对应及中文解释的开篇术语表，按具体段落语境选择的局部高亮，分散于章节中的教学漫画，以及完整英文答案后的扩展词汇。统计学示例包含 27 项开篇术语、20 项答案词汇；新章节按实际知识范围确定数量。

两版均采用纯白纸面、蓝色横线和霞鹜文楷正文。打印版保留奇右偶左外栏与 20 mm 内侧空白，电子版保留固定双侧批注栏。

## 使用脚本

先在解压目录安装依赖：

```sh
python -m pip install -r requirements.txt
cd skills/artifact-template-university-xueba-notes
python scripts/prepare_fonts.py --output-dir ./fonts
mkdir output
python scripts/fill_template.py --content Resources/content/statistics-chapter.json --templates Resources/templates --fonts ./fonts --assets Resources/illustrations --edition print --output output/print-reference.pdf
python scripts/fill_template.py --content Resources/content/statistics-chapter.json --templates Resources/templates --fonts ./fonts --assets Resources/illustrations --edition digital --output output/digital-reference.pdf
python scripts/fill_template.py --content Resources/content/statistics-chapter.json --templates Resources/templates --fonts ./fonts --assets Resources/illustrations --edition print --foldout-only --output output/foldout.pdf
```

首次准备字体需要联网；已有字体时增加 `--source-dir /path/to/offline-fonts`。现行排版使用 `WenKai.ttf`、`SansBold.ttf`、`DejaVuSerif.ttf` 和 `DejaVuSans.ttf`。现成 PDF 已嵌入所需字体，可直接阅读与打印。

母版可直接复用。需要修改母版时，使用 `scripts/build_pdf_templates.py`；内容与漫画资产通过 JSON 及路径替换。生成新内容后应逐页检查。详细流程见 `references/template-workflow.md`。

本次移除了 29 个废弃文件，并清理旧文档入口及未使用的字体依赖。包内保留当前流程需要的资源，无旧样稿归档、旧生成器、缓存或嵌套压缩包。`PACKAGE_MANIFEST.json` 提供文件清单和 SHA-256 校验值。
