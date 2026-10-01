# 制作与检查流程

## 当前参考

原 `assets/reference.docx`、`assets/preview.png`、`assets/icon.svg` 和 `artifact-template.json` 保留不变。`assets/examples/` 中的两份14页文件是旧版几何、语言与答案示范，其连续说明文和103号漫画不是当前要求。

按当前主指令与活跃参考进行制作。图像使用教辅边栏浅彩手绘风，正文使用多种教学单位。具体原书页面可用于视觉核对，未经实际查看不要声称截图验证。生成新图与新内容，不把原扫描页直接作为输出内容。

## 制作顺序

1. 读取来源，建立覆盖表、先修关系、术语与答案ID。
2. 选择版本与全书范围；阅读主指令列出的参考。
3. 建立页型、视觉教学与漫画脚本计划，固定同系列字体、色板、标题条、气泡和封面构图。
4. 编写完整知识，拆分为短解释、定义、条件、表格、公式、图解和例题步骤。
5. 使用生图能力制作原创漫画与场景；用精确绘图制作工作图。
6. 排版，嵌入全部最终资产，保留教学锚点和用户批注空白。
7. 生成封面、目录和学科速查，检查打印分块与正文奇偶页。
8. 渲染全部页，检查知识、视觉、版式与导航，修复后重复相关检查。
9. 按请求保存与交付实际完成的文件，标明批次范围。

计划可采用 `references/book-plan.md` 格式并运行 `scripts/validate_book_plan.py`。该检查验证ID、题目答案、页型和视觉覆盖声明，不能替代知识核对或图片检查。

## 旧版生成器

`scripts/build_reference.py` 仅用于明确请求的旧几何示范，需 `--legacy-geometry-demo`。脚本与输出中的旧103风格属于历史示范，不用于生成新书。

```sh
python scripts/build_reference.py --legacy-geometry-demo --edition print --font-dir /path/to/fonts --output old-print-reference.pdf
python scripts/build_reference.py --legacy-geometry-demo --edition digital --font-dir /path/to/fonts --output old-digital-reference.pdf
python scripts/verify_reference.py old-print-reference.pdf --edition print
python scripts/verify_reference.py old-digital-reference.pdf --edition digital
```

需要新版时复用必要绘图函数或单独构建内容驱动的稿件。不能只替换旧例子的科目名。字体可用 `scripts/prepare_fonts.py` 离线或在线准备，保留字体许可并检查所需字形。

## 三方面检查

| 方面 | 必查内容 |
| --- | --- |
| 知识 | 课程覆盖、条件、推导、术语、题目小问与完整答案、准确类比 |
| 教学视觉 | 图解释什么、各层级覆盖、学科工作图、漫画风格、页型变化、系列一致性 |
| 出版与书写 | 文字不裁切、公式完整、无重叠、字号、批注空白、装订边、页码、目录和书签 |

查看全页判断密度与阅读节奏；放大看最密的副栏、英文解答、公式与速查。PDF文本抽取只能辅助检查，不能证明视觉正确。

打印版核对奇右偶左的批注与页码、内侧20 mm完全空白、正文第1页的物理位置。电子版核对固定两侧批注、没有镜像装订偏移、标准PDF批注可用。大图页特殊布局应保持版本基本书写要求。

逐页检查五层纸面、颜色语义、黄色局部标记、红橙手写说明、精确工作图和嵌入漫画。旧样稿的缩略图不能证明新版达标。工具不可用或批次未完成时如实说明，不以提示词清单代替最终插图。
