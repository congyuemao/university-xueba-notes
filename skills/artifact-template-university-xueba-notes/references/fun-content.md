# 短笑话、冷知识与名言

生成笔记时，`fill_template.py` 默认从随包语料库为每个有趣味条的页面抽一条。目录续页、正文和书末词汇表续页共用同一个抽取器；封面、空白页和独立折页不抽取。优先一行，最多两行，名句署名也参加排版。

## 直接用于 PDF

以下参数加在原有 `fill_template.py` 命令末尾：

```sh
--fun-seed 42 --fun-subject 统计学 --fun-include-general --fun-used-file output/book-used.json
```

| 参数 | 用法 |
| --- | --- |
| `--fun-seed 42` | 固定随机种子；同一语料、版式、筛选条件和历史起点下复现抽取 |
| `--fun-subject 统计学` | 按学科筛选；可重复指定多个学科，匹配任意一个即可 |
| `--fun-include-general` | 按学科筛选时，也加入通用笑话和名言 |
| `--fun-types joke trivia` | 只使用指定类型；省略时使用全部四类 |
| `--fun-max-lines 1` | 只抽可排成一行的内容；默认上限为两行 |
| `--fun-used-file output/book-used.json` | 跨次记录已用内容；同一本书的各章共用一个文件 |
| `--fun-mode content` | 使用章节JSON原有的 `humour` 字段，适合已经手工编排的页脚 |
| `--fun-catalog 路径` | 使用另一份相同字段结构的JSONL语料 |

每页所选条目的ID、正文、署名、来源保存在PDF旁的 `.layout.json` 的 `pages[].fun_content` 中。随机模式按类型轮换，类型内随机抽取，并优先选择能放进一行的短句。PDF使用当前页真实可用宽度与10 pt文楷测量。

历史只在PDF及定位记录都成功保存后更新。已用内容不会在库耗尽时自动循环；换一本书时使用新的历史文件。`content` 模式由章节作者自己安排与去重。

## 单独抽取结构化语料

以下命令在skill根目录运行；基础抽取仅用Python标准库，离线即可运行。

```sh
# 随机抽20条，保存正文、署名与出处
python -X utf8 scripts/pick_fun_content.py --count 20 --seed 42 --output output/selection.json

# 只选数学与统计学知识，每条一行
python -X utf8 scripts/pick_fun_content.py --count 10 --subject 数学 --subject 统计学 --types subject_fact --max-lines 1 --output output/math.json

# 给下一章挑笑话，并沿用同一本书的去重记录
python -X utf8 scripts/pick_fun_content.py --count 8 --types joke --used-file output/book-used.json --output output/chapter-2-jokes.json

# 改用100mm文字宽度时，用真实字体重新计算换行
python -X utf8 scripts/pick_fun_content.py --count 8 --fonts .fonts --width-mm 100 --output output/narrow.json
```

`--max-chars` 限制含署名的总字符数，默认70；`--max-lines` 默认2。独立脚本未指定字体时使用语料附带的测量值：10 pt `Hand` 文楷、172 mm可用宽度，对应当前打印版页脚。电子版当前可用宽度为180 mm。改变字体或宽度时，用 `--fonts` 重新测量。

独立抽取的 `selection.json` 是完整选文结果，可交给内容作者放入每页的 `humour`，再使用 `--fun-mode content`；PDF默认随机模式会自行抽取。单独抽取时提供 `--used-file` 会将这批条目标记为已用，因此已经选好的一批应直接复用，不要再让随机模式重新抽同一批。

## 类型和学科

| 类型键 | 内容 |
| --- | --- |
| `joke` | 短笑话、谐音梗、校园与生活段子 |
| `trivia` | 自然、天文、技术等趣味冷知识 |
| `subject_fact` | 数学、统计、物理、化学、生物、计算机等学科短知识 |
| `quote` | 有作者和作品出处的名言名句，以古典诗文原文为主 |

学科支持：`general`（通用）、`mathematics`（数学）、`statistics`（统计学）、`physics`（物理）、`chemistry`（化学）、`biology`（生物）、`astronomy`（天文）、`earth_science`（地球科学）、`computer_science`（计算机）、`literature`（文学）、`language`（语言）。也可直接输入表中的中文名；“概率”“高数”“地理”“编程”等常用名也能识别。

不指定学科时可抽所有条目。指定学科时默认严格按标签筛选；希望同时穿插生活笑话和名句时加 `--include-general`，PDF中对应 `--fun-include-general`。

## 语料结构与扩充

- [items.jsonl](../Resources/fun-content/items.jsonl)：每行一个JSON对象，可逐条读取、搜索或编辑。
- [sources.json](../Resources/fun-content/sources.json)：来源目录、网址、上游提交版本、访问日期和使用说明。
- [catalog-info.json](../Resources/fun-content/catalog-info.json)：条数、分类和排版行数统计。

| 字段 | 含义 |
| --- | --- |
| `id` | 条目唯一ID，供去重记录使用 |
| `kind`、`subjects`、`tags` | 类型、可多选学科、编辑标签 |
| `text` | 一条完整短句，不含强制换行 |
| `author`、`work` | 名句作者和篇名；其他类型为null |
| `source.id`、`url`、`locator` | 来源目录键、可访问网址、原文件条目或网页章节 |
| `source.adaptation` | 简体转换、压缩、改写或原文摘句说明 |
| `layout` | 参考宽度、字体、字号、含署名字符数及实测行数 |

新增笑话先阅读完整语义，避开性别歧视、政治冒犯或政治敏感、种族主义内容；笑点尽量来自日常生活、文字双关或学科概念。短句优先一行，最多两行。事实保留成立条件与来源；名句从原文摘录并注明真实作者、篇名。不要把改写后的句子当成名人原话。

添加记录后使用实际字体重新测量，并检查是否与已有条目重复或只是同一笑点的换人版本。抽取时同时按ID与规范化正文排除已用内容，历史会跨章节生效。
