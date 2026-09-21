# 苯甲酸 Raman 光谱统一对比

本目录把五组数据放在一致的坐标与处理框架中：

1. 实验：AIST SDBS 苯甲酸粉末 Raman，`RM-01-00563`，4880 Å 激发；曲线由原始谱图数值化。
2. 参考理论：Parra Figueredo 等（2023）公开的 ORCA/B3LYP/6-31+G(d,p) 频率与 Raman 活性。
3. 构型 1：`../Raman-chk1/job.out`，Gaussian/B3LYP/6-31G(d)。
4. 构型 2：`../Raman-chk2/job.out`，Gaussian/B3LYP/6-31G(d)。
5. 二聚体：`../double/job.out`，Gaussian/B3LYP/6-31G(d)，30原子、84个正频率模式；优化及频率任务正常结束。

## 统一处理

- 构型 1/2 及二聚体的谐振频率乘以 `0.9613`；沿用同一经验缩放，不针对二聚体氢键模式重新拟合。
- 参考理论使用原文给出的已缩放频率（缩放因子 `0.9679`），不重复缩放。
- 四组计算 Raman 活性统一换算为 488.0 nm、298.15 K 的相对 Stokes 强度，再以 20 cm⁻¹ FWHM 高斯函数展宽。
- 各谱独立归一化；计算谱在0–4000 cm⁻¹网格归一化后，截取200–3800及350–1800 cm⁻¹显示。部分低频强峰未显示，显示区域最大值不一定为1，指纹区不单独归一化。纵轴不代表不同样品之间的绝对散射截面。
- 灰色虚线为 SDBS 原图列出的部分实验峰位：618、797、1003、1291、1604、1654、3073 cm⁻¹。
- 五行颜色为黑、金、蓝、橙、橄榄绿，与IR一致；两图均为13.2×10.5英寸。

## 文件

- `raman_comparison.png` / `.pdf`：最终统一对比图。
- `raman_spectra_normalized.csv`：五条绘图曲线。
- `experimental_sdbs_digitized.csv`：数值化实验曲线。
- `peaks_*.csv`：四组计算的模式、原始/缩放频率、Raman 活性和换算强度；`peaks_dimer.csv` 为二聚体。
- `prepare_raman_data.py` / `plot_raman_comparison.R`：可重复生成数据与图。

## 数据来源

- AIST SDBS, *Raman spectrum of benzoic acid*, SDBS-RM-01-00563: https://sdbs.db.aist.go.jp/SpectralLanding.aspx?spcode=RM-01-00563 （访问日期：2026-09-21）。
- J. G. Parra Figueredo et al., *A procedure for obtaining IR, Raman and NMR spectra of organic compounds by means of quantum mechanical calculations with the ORCA-5.0.3 software*, Educación Química 34(1), 2023. DOI: https://doi.org/10.22201/fq.18708404e.2023.1.82742
- J. P. Merrick, D. Moran, L. Radom, *An Evaluation of Harmonic Vibrational Frequency Scale Factors*, J. Phys. Chem. A 111 (2007) 11683–11700.
- NIST CCCBDB vibrational scale-factor table: https://cccbdb.nist.gov/vsfx.asp

## 重新生成

```bash
python prepare_raman_data.py \
  --chk1 ../Raman-chk1/job.out \
  --chk2 ../Raman-chk2/job.out \
  --dimer ../double/job.out \
  --output-dir .
Rscript plot_raman_comparison.R raman_spectra_normalized.csv raman_comparison
```

默认复用本目录已有的数值化实验曲线，因此重新绘图不依赖临时文件。SDBS 原图受 AIST 权利声明约束，未复制进本目录；若需从原图重新数值化，请从上述 SDBS 页面取得 `RM563` 谱图，并额外传入 `--sdbs-image /path/to/RM563.gif`。

依赖与字体安装见 [环境指南](../ENVIRONMENT.md)。`SPECTRA_FONT` 可指定字体；macOS 使用 Quartz 导出 PDF，其他系统使用 Cairo。
