# 第三方来源与许可

## 字体

| 字体 | 来源 | 许可文件 |
| --- | --- | --- |
| LXGW WenKai | https://github.com/lxgw/LxgwWenKai | `LXGW-WenKai-OFL.txt` |
| Noto Sans SC | https://github.com/google/fonts/tree/main/ofl/notosanssc | `NotoSansSC-OFL.txt` |
| Long Cang（龙藏，Hand） | https://github.com/google/fonts/tree/main/ofl/longcang | `LongCang-OFL.txt` |
| Ma Shan Zheng（马善政楷体，仅字体对比） | https://github.com/google/fonts/tree/main/ofl/mashanzheng | `MaShanZheng-OFL.txt` |
| DejaVu | https://github.com/dejavu-fonts/dejavu-fonts | `DejaVu-LICENSE.txt` |

许可文件位于 `skills/artifact-template-university-xueba-notes/assets/licenses/`。字体准备脚本支持获取字体或使用本地字体；示例 PDF 嵌入所需字形。

## 漫画参考

`Resources/reference-comics/` 的八幅裁片来自用户提供的数学、化学、物理、历史教辅，作为用户本地制作流程的图像参考保留。原书内容权利归原权利人。来源文件、页码、裁切区域与校验值见该目录的 `index.md` 和 `manifest.json`。公开分发 ZIP 不包含这八幅私人参考裁片或整本原书扫描，只保留索引与来源元数据。

制作时将参考裁片作为生成输入，输出原创场景；裁片不直接置入新成品。私人参考裁片不属于可公开再分发的原创资源。

## 当前生成资源

`Resources/illustrations/` 中三幅统计学漫画由图像生成工具制作；提示词、参考路径与修正记录保存在 `comic-prompts.json`。`Resources/templates/` 保存当前 PDF 母版，`Resources/examples/` 保存统计学旧接口样例及v2运筹学三章校准样例、字体比较与检查记录。运筹学数值题和图为本项目自编，没有复制Taha例题或原书页面。

## 趣味语料

结构化语料位于 `Resources/fun-content/`。每条记录保留来源链接与定位；来源目录保存上游版本或访问日期。

- 中文笑话选自 [Chinese_Humor_MultiLabeled](https://github.com/SamTseng/Chinese_Humor_MultiLabeled)（Copyright 2020 Yuen-Hsien Tseng）及 [60s](https://github.com/jinyiwei2012/60s)（Copyright 2022-Present Viki）。两者仓库均采用 MIT；许可证副本随附为 `assets/licenses/Chinese-Humor-MIT.txt` 和 `60s-MIT.txt`。入库时转为简体、整理标点，部分条目缩短或改为中性角色。
- 古典名句通过 [chinese-gushiwen](https://github.com/aopao/chinese-gushiwen) 检索并与篇目原文比对，只取已进入公版的古代作品原文、作者和篇名。该数据仓库未提供整体许可证；未复制其现代翻译、赏析或整套数据库。
- 学科知识参考 OpenStax《Calculus Volume 1》《University Physics Volume 1》《Introductory Statistics 2e》，按 [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) 标示来源；中文短句及部分示例由本项目重新组织。
- 其他冷知识核对 NASA、NOAA、USGS、NIST、英国皇家化学学会、自然历史博物馆、邱园与史密森尼的资料；计算机条目核对 Python Software Foundation 官方文档。只提炼事实并重新撰写中文，不复制网页图片或整段说明。Python文档版权归 Python Software Foundation；[文档许可](https://docs.python.org/3/license.html)。

逐条出处及所用章节见 [sources.json](skills/artifact-template-university-xueba-notes/Resources/fun-content/sources.json) 和各语料的 `source` 字段。

## 语言参考与校准

`Resources/private-language-reference/` 保存用户本地的 40 条短摘录与观察，来自两本用户提供的数学教辅。该目录由 `.gitignore` 排除，不进入公开分发 ZIP；不附整本扫描书。`Resources/language-calibration/` 的五份文件为抽象语言规则、自编大学课程例子与正反例，用于写法校准，不替代教材知识来源。
