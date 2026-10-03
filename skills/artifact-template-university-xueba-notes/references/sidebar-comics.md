# 学霸笔记边栏漫画

## 必需参考

每次生成先读取 `Resources/reference-comics/index.md` 与 `manifest.json` 来源索引，实际查看数学、物理、化学、历史原书的侧边批注漫画。按当前知识任务选用相关裁片，记录文件名和对应源页，将裁片路径传给 imagegen 的 `referenced_image_paths`。有文字提示词但没有传入实际裁片，不算完成参考步骤。若运行环境没有附带私人裁片，先查找用户已提供的原书并提取相关侧栏；原书也无法取得时明确说明缺少参考，不能凭通用风格词声称已匹配。

原书截图是视觉参考资料。新书绘制原创知识角色、动作和对白，保留参考的画法与教学构图；成书不得直接拼贴截图中的原角色、长段台词、版权页或水印。私人参考裁片不自动进入公开分发包。

## 观察与复现

- 依选定原书裁片复现细灰黑轮廓、轻微手绘线条变化、平涂印刷色与有限阴影。颜色小面积使用，边缘清楚，不加粉雾或彩铅颗粒。
- 概念拟人优先采用原书可见的豆形、袋形或简单物体形态。眼白、瞳孔、眉毛与嘴形共同表达情绪，依裁片保持实际比例。
- 人物型漫画保持参考中的头身比例、五官和动作。禁止默认生成巨大头部、婴幼儿短肢、点眼 kawaii 人物；禁止上一版可爱学生贴纸画法。
- 保留原书的紧凑窄栏构图、短对白、少量道具和大部分无背景区域。角色通常一至三个，具体数量服从教学关系。
- 教学动作应有明确含义，例如共有、排除、选择、比较、平衡或指向一个条件。表情与构图随知识变化，无需强制荒诞笑点。
- 同章使用一致轮廓、平涂色板、五官比例、气泡线宽和常用角色。先查看最终窄栏尺寸，不能仅检查放大的单张原图。

不得用“浅彩”“Q版”“手绘感”等宽泛词替代源图对照。生成后与传入裁片并排查看线宽、填色、角色比例、眼睛眉毛、阴影、气泡和留白；明显不符时修订提示与参考组合后重新生成。

## 参考记录

每幅漫画记录：

1. 概念ID、准确命题、用途及类比边界。
2. 原书裁片文件、索引中的源页和选用理由。
3. 角色、动作、道具及每个元素对应的知识含义。
4. 独立排版的短对白、术语及公式。
5. 目标栏宽、角色占位、对白占位和具体主栏块锚点；记录对白所需概念与符号已在该位置之前教完，检查最终页面的垂直阅读顺序。
6. 实际传给生成工具的参考文件列表、提示词、输出路径和嵌入页。
7. 源图并排比对结果及知识核对结果。

## 教学类型

| 类型 | 适用知识 | 构图 |
| --- | --- | --- |
| 概念拟人 | 概念区别、关系与误区 | 豆形或袋形角色以动作和短对白表达关系 |
| 具体例子 | 抽象对象、分类与集合 | 少量熟悉物体形成明确分组 |
| 关系类比 | 包含、条件、对应与平衡 | 道具与关系一一对应，保留适用边界 |
| 学生提问 | 常见疑问与解题条件 | 依原书人物比例设计疑问与指示动作 |
| 图解辅助 | 公式、工作图与流程 | 精确图旁放小角色，字符和关系另行排版 |

选择能准确表达当前关系的最紧凑方案。一个字符标签或原生小图已经足够时无需扩大漫画。窄栏漫画占比按原书裁片测量，避免整页大人物和无知识作用的装饰。

## 全章分布

内容规划时同步安排侧栏批注漫画，在章节前、中、后部持续出现。普通讲解页通常每一至两页考虑一幅有具体教学用途的小漫画；连续三页或更多没有漫画时，逐页检查是否遗漏了适合图解的关系、过程或疑问。密集题目、答案和索引页可按内容调整。漫画覆盖与工作图、表格分别核对，不能用几张表格充抵漫画，也不能让十余页章节仅有相邻两页出现漫画。

每幅图靠近相应主栏锚点，用不同动作、场景与简短对白解释当前知识。保持原书的窄栏小尺寸，必要时增加分布页数，避免放大单图或重复贴同一个角色来增加存在感。先列知识任务和所在页，再生成相应资产并实际嵌入。沿用同章角色可以保持系列感，但每处教学关系应明确。

核对所有普通知识页的漫画分布与未配图原因，优先补足可帮助理解的空缺。无适当图像表达时保留正文，避免无关装饰。全章约半数或更多批注空间继续留给用户书写。

## 独立提示词

```text
你负责制作学霸笔记系列的边栏漫画。
先查看 Resources/reference-comics 的原书裁片与来源索引，选出适合当前知识关系的实际图片，并将文件路径作为 imagegen 参考图传入。
严格对照参考的细灰黑线、平涂印刷色、有限阴影、眼白瞳孔眉毛、豆形或袋形概念角色，以及紧凑的窄栏教学构图。
人物型场景沿用实际源图的头身与五官比例，禁止巨大头幼儿Q版、点眼贴纸人物、彩铅颗粒和粉雾渐变。
为新的知识命题绘制原创角色与动作；说明每个图像元素对应什么，并标明类比边界。
单独排版简短对白、术语和公式。生成图不带文字，透明背景，只保留必要道具。
对白表达已经讲过的一项具体关系；不要只喊“别搞混”“记住它”。必要定义和例子留在主栏，漫画跟随主栏锚点，不抢先使用新概念或符号。
按成稿实际尺寸检查，与选定原书裁片并排比较；不符时重新生成。
精确图、公式、概率和坐标由原生绘图及文字排版完成。
```

## 生图提示词

```text
Create an original compact educational sidebar cartoon for a university study book.
Use the attached source-book sidebar crops as the visual reference. Match their fine grey-black printed linework, flat light ink colours, limited shadows, small white eyes with pupils and expressive eyebrows, and compact bean-shaped or bag-shaped concept characters where appropriate.
Keep the specific reference proportions, facial construction, line weight, colour treatment and narrow-column composition.
Teaching proposition: {accurate proposition}.
Original composition: {characters, action, necessary props and their meanings}.
Target column width: {width_mm} mm. Image slot: {height_mm} mm high. Keep the arrangement compact and legible at this actual size.
Use a transparent background with only necessary props. Reserve space for separately typeset dialogue and labels. Generate no text, letters, numbers or formulas.
Do not use giant-headed infant chibi students, dot-eye kawaii stickers, coloured-pencil texture, chalky haze, powdery pastel gradients, glossy rendering, heavy outlines or a full background scene.
Do not reproduce the reference's exact characters or dialogue; create the new teaching scene with its visual language.
```

该提示词必须和实际图像参考一起调用。不要只复制提示词便声称完成原书风格匹配。

## 知识核对

条件概率图应表现条件事件限定后的参考群体，不暗示因果方向。独立与互斥分别核对正概率条件和共同发生的可能性。集合重复表达同一元素不能改变元素数，外观相同的两个不同对象仍可共存。贝叶斯推断说明依据证据更新概率，不能保证已找出真实原因。无法通过漫画表达的前提保留在相邻正文。
