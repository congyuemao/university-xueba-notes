# 第三方来源与许可

## 字体

| 字体 | 来源 | 许可文件 |
| --- | --- | --- |
| LXGW WenKai | https://github.com/lxgw/LxgwWenKai | `LXGW-WenKai-OFL.txt` |
| Noto Sans SC | https://github.com/google/fonts/tree/main/ofl/notosanssc | `NotoSansSC-OFL.txt` |
| DejaVu | https://github.com/dejavu-fonts/dejavu-fonts | `DejaVu-LICENSE.txt` |

许可文件位于 `skills/artifact-template-university-xueba-notes/assets/licenses/`。字体准备脚本支持获取字体或使用本地字体；示例 PDF 嵌入所需字形。

## 漫画参考

`Resources/reference-comics/` 的八幅裁片来自用户提供的数学、化学、物理、历史教辅，作为用户本地制作流程的图像参考保留。原书内容权利归原权利人。来源文件、页码、裁切区域与校验值见该目录的 `index.md` 和 `manifest.json`。本包不包含整本原书扫描。

制作时将参考裁片作为生成输入，输出原创场景；裁片不直接置入新成品。私人参考裁片不属于可公开再分发的原创资源。

## 当前生成资源

`Resources/illustrations/` 中三幅统计学漫画由图像生成工具制作；提示词、参考路径与修正记录保存在 `comic-prompts.json`。`Resources/templates/` 保存当前 PDF 母版，`Resources/examples/` 保存配套统计学示例与检查记录。
