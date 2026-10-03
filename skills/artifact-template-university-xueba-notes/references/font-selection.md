# Body / Hand 字体记录

Body保留LXGW WenKai Regular（霞鹜文楷），文件WenKai.ttf，正文11.6 pt。Hand改为Long Cang Regular（龙藏），LongCang.ttf，短中文批注通常12 pt。两者不再共用文件。

2026-10-04用同一句“先看系数符号，再选入基变量；这里的3是枢轴”和英文数字在14、11、9 pt比较文楷、龙藏、马善政。实际比较页位于Resources/examples/font-comparison.pdf。龙藏笔画松动、细，和文楷差异清楚；马善政更偏毛笔且字重高。选择龙藏，正文黑色稳定，批注红橙且仅±0.7度轻微旋转。9 pt龙藏偏细，不作为常规批注字号。

- 文楷原项目：https://github.com/lxgw/LxgwWenKai
- 龙藏原始分发：https://github.com/google/fonts/tree/main/ofl/longcang
- 马善政候选：https://github.com/google/fonts/tree/main/ofl/mashanzheng

三者相应OFL许可存assets/licenses。未把商业字体加入包。prepare_fonts.py支持离线来源并下载龙藏原文件；随输出保存来源和许可。默认包不含大体积全字体，PDF按需嵌入子集。比较页也保留候选字体的许可。

数学符号缺字时使用Math配套字体，中文缺字可回退Body；必须检查实际小字和混排，不能仅凭注册成功通过。网页SVG中字体依阅读环境，交付的PDF是已嵌入字体的可复核版本。后续用户更换Hand时重新制作相同句、相同字号比较，正文文楷选择持续保留。
