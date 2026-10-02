# 大学学霸笔记 · University Xueba Notes

用课程讲义、教材、课堂笔记和习题制作大学学习笔记，输出适合打印或平板批注的 PDF。笔记采用白底蓝色横线、霞鹜文楷正文，配合中英术语、知识讲解、例题、教学漫画与章末自测。

查看示例：[打印版](skills/artifact-template-university-xueba-notes/Resources/examples/print-reference.pdf) · [电子版](skills/artifact-template-university-xueba-notes/Resources/examples/digital-reference.pdf) · [知识速查](skills/artifact-template-university-xueba-notes/Resources/examples/foldout.pdf)

## 在 Codex 中使用

### 1. 安装 skill

在 Codex 对话中发送：

```text
$skill-installer 请安装这个 skill：
https://github.com/congyuemao/university-xueba-notes/tree/main/skills/artifact-template-university-xueba-notes
```

安装后可以在后续对话中通过名称调用。安装与调用方式见 [OpenAI Skills 文档](https://learn.chatgpt.com/docs/build-skills)。

首次生成 PDF 时，让 Codex 根据本仓库根目录的 `requirements.txt` 安装 Python 依赖，并运行 skill 内的 `scripts/prepare_fonts.py` 准备字体。字体准备支持联网下载和本地字体目录，具体命令见下方。

### 2. 提供课程资料

上传讲义、教材章节、课堂笔记或习题，并说明：

- **内容范围**：课程名称、章节或考试范围。
- **阅读方式**：打印后手写批注，或在电脑、平板上批注。
- **语言要求**：例如中文讲解、保留英文术语、英文作答。

### 3. 直接描述要制作的笔记

**打印版**

```text
使用 $artifact-template-university-xueba-notes，根据我上传的讲义制作条件概率章节笔记。
采用打印批注版，中文讲解，保留英文术语。
包括知识讲解、推导、例题、教学漫画和章末自测，自测配英文答案。
输出章节 PDF 和独立知识速查页。
```

**平板批注版**

```text
使用大学学霸笔记，根据这些课程资料制作线性代数第一章笔记。
我在平板上阅读，采用电子双侧批注版。
重点讲解向量空间、线性无关和基，配合例题与图示，输出 PDF。
```

**接着编下一章**

```text
继续使用大学学霸笔记，依据新上传的资料编写下一章。
沿用上一章的批注版本、术语译法和页面风格。
```

## 选择批注版本

| 使用方式 | 版本 | 页面安排 |
| --- | --- | --- |
| 打印、装订后手写批注 | `print` | 外侧批注栏随奇偶页左右交替，内侧留出 20 mm 装订空间 |
| 电脑或平板阅读、批注 | `digital` | 正文两侧固定批注栏 |

需要两版时，在请求中写明“同时输出打印版和电子版”。两版使用同一份课程内容，分别排版。

## 在本地生成示例 PDF

下面的命令使用仓库附带的统计学内容，生成与示例对应的 PDF。

### 1. 下载项目并准备字体

安装 Python 和 Git 后，在终端运行：

```sh
git clone https://github.com/congyuemao/university-xueba-notes.git
cd university-xueba-notes
python -m pip install -r requirements.txt
cd skills/artifact-template-university-xueba-notes
python -X utf8 scripts/prepare_fonts.py --output-dir .fonts
mkdir output
```

也可以从仓库页面选择 **Code → Download ZIP**，解压后进入项目根目录，从 `python -m pip install -r requirements.txt` 开始。

### 2. 生成需要的版本

以下命令均在 `skills/artifact-template-university-xueba-notes/` 目录运行。

**打印版**

```sh
python -X utf8 scripts/fill_template.py --content Resources/content/statistics-chapter.json --templates Resources/templates --fonts .fonts --assets Resources/illustrations --edition print --output output/print-notes.pdf
```

**电子版**

```sh
python -X utf8 scripts/fill_template.py --content Resources/content/statistics-chapter.json --templates Resources/templates --fonts .fonts --assets Resources/illustrations --edition digital --output output/digital-notes.pdf
```

**独立知识速查页**

```sh
python -X utf8 scripts/fill_template.py --content Resources/content/statistics-chapter.json --templates Resources/templates --fonts .fonts --assets Resources/illustrations --edition print --foldout-only --output output/foldout.pdf
```

生成的 PDF 保存在 skill 目录下的 `output/` 文件夹中。

### 使用已有字体

将 `WenKai.ttf`、`SansBold.ttf`、`DejaVuSerif.ttf` 和 `DejaVuSans.ttf` 放在同一个目录，将下面的路径替换为该目录：

```sh
python -X utf8 scripts/prepare_fonts.py --output-dir .fonts --source-dir "/path/to/fonts"
```

## 制作自己的章节

在 Codex 中提供课程资料并调用 skill，即可让助手编写内容、准备插图和排版。手动运行脚本时，按下面的方式替换输入：

1. 参考 [统计学内容文件](skills/artifact-template-university-xueba-notes/Resources/content/statistics-chapter.json)，另存一份章节 JSON，填写课程名称、正文、术语、例题、自测和答案。
2. 将本章插图放入一个文件夹，在内容 JSON 的 `sidebar.comic.asset` 中填写相对于该文件夹的图片路径。
3. 将生成命令中的 `--content` 改为新 JSON 路径，`--assets` 改为插图目录，`--output` 改为目标 PDF 路径。

内容字段、页型和高亮写法见 [模板填充说明](skills/artifact-template-university-xueba-notes/references/template-workflow.md)；调整笔记风格可从 [skill 主规范](skills/artifact-template-university-xueba-notes/SKILL.md) 进入对应说明。
