# 苯甲酸 IR 对比图

输出：`ir_comparison.png`（300 dpi）和 `ir_comparison.pdf`（矢量）。与 Raman 图统一使用黑/金/蓝/橙/橄榄绿配色，五行分别为实验、参考理论、构型1、构型2、二聚体；两列为400–4000及400–1800 cm⁻¹。两张图均为13.2×10.5英寸。

实验来源：[AIST SDBS IR-NIDA-63340](https://sdbs.db.aist.go.jp/SpectralLanding.aspx?spcode=IR-NIDA-63340)，苯甲酸 KBr 压片，2026-09-21访问。仓库默认读取已数值化 CSV，不依赖原图或网页。谱图横轴在2000 cm⁻¹处改变比例，数值化时按两段坐标校准。黑色曲线逐列取中位像素，按 T=(418-y)/321 还原透过率，再转换 A=-log10(T)，减去最小吸光度并归一化。未经额外平滑。图像分辨率约为高波数区7.6、低波数区3.8 cm⁻¹/像素；数值化数据不能替代原始仪器数据。边界没有原始数据的点保留缺失，不外推。SDBS 的使用及引用须遵守其声明。

参考理论来源：[NIST CCCBDB，B3LYP/aug-cc-pVTZ 苯甲酸](https://cccbdb.nist.gov/energy3x.asp?basis=18&casno=65850&method=8)，共39个模式，使用网页所列缩放频率（0.9675）及 IR 强度（km/mol）。该参考不同于 Raman 图的 ORCA 参考，因为后者所用表格没有 IR 强度；不能把 Raman 活性当成 IR 强度。

构型1/2：分别读取 `../Raman-chk1/job.out`、`../Raman-chk2/job.out` 中 Frequencies 和 IR Inten，各39个正频率模式。二聚体读取 `../double/job.out`，有30个原子、84个正频率模式，优化及频率计算正常结束。三者均以0.9613缩放，与 Raman 图一致。所有计算谱以20 cm⁻¹ FWHM高斯函数展宽，并在400–4000 cm⁻¹区间独立归一化。IR 不使用激光波长或 Raman 的热占据强度换算。归一化曲线比较的是峰位和相对谱形，并不比较绝对吸收量；指纹区不单独重新归一化。孤立二聚体包含双氢键，但仍不等同于固态压片实验。

`double_ir_modes.csv` 保留二聚体的84个模式。模式72缩放后为1697.1630 cm⁻¹，IR强度847.9886 km/mol；模式74、76在3062.2170、3064.4462 cm⁻¹处强度更大，展宽后成为全谱最大峰，故二聚体羰基峰在归一化图中并非最高峰。

实验灰色参考线标出708、936、1294、1689、3073 cm⁻¹。其中数值化羰基最大值约1688.4 cm⁻¹，与1689参考一致。数据和代码保留在本目录，原始Gaussian文件不变。

重建（在本目录执行）：

```sh
python prepare_ir_data.py
Rscript plot_ir_comparison.R ir_spectra_normalized.csv ir_comparison
```

若需重新提取源图和网页，按 [环境指南](../ENVIRONMENT.md) 自行取得对应源文件后添加 `--redigitize`。绘图支持 `SPECTRA_FONT` 指定中文字体；macOS 使用 Quartz，其他系统使用 Cairo。依赖安装见环境指南。
