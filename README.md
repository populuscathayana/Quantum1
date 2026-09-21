# 苯甲酸单体与二聚体的 IR / Raman 光谱

本仓库保存两个苯甲酸单体构型及双氢键二聚体的 Gaussian B3LYP/6-31G(d) 计算结果、谱图处理程序和实验报告。对比对象包括 SDBS 实验谱、公开理论参考、两个单体及二聚体。

- [环境安装与完整复现步骤](ENVIRONMENT.md)
- [实验报告（TeX）](experiment-report/benzoic_acid_ir_raman.tex)
- [实验报告（PDF）](experiment-report/benzoic_acid_ir_raman.pdf)
- [实验报告（Markdown）](experiment-report/苯甲酸双构型红外与拉曼光谱实验报告.md)
- [数据来源与第三方权利说明](THIRD_PARTY_NOTICES.md)

## 光谱

![IR 对比图](IR-comparison/ir_comparison.png)

![Raman 对比图](Raman-comparison/raman_comparison.png)

同名 PDF 是矢量图。三个本次计算体系均无虚频，模式数分别为 39、39、84。所有本次计算频率乘以 0.9613，使用 20 cm⁻¹ FWHM 高斯展宽；Raman 活性按 488.0 nm、298.15 K 换算为相对 Stokes 强度。各谱独立归一化，不能用于不同样品之间的绝对强度比较。二聚体仍是孤立体系，不等同于晶体模型。

## 内容与复现范围

| 路径 | 用途 |
|---|---|
| `Base1/`、`Base2/` | 单体优化输入与原始输出；重新计算时生成频率任务所需检查点 |
| `Raman-chk1/`、`Raman-chk2/` | 单体频率输入、原始输出 |
| `double/` | 二聚体优化和频率输入、原始输出 |
| `IR-comparison/`、`Raman-comparison/` | 数值化实验曲线、理论参考模式、计算模式、绘图脚本及成图 |
| `experiment-report/` | 提交版报告、能量与结构核验脚本及数据 |
| `reproduce.py` | 一次性运行数据处理、绘图及可选 TeX 编译 |

重建数据与谱图不需要 Gaussian、不需要联网抓取数据库；安装依赖后即可从仓库已有输出离线复现。环境指南仅涵盖数据后处理、绘图与 TeX 编译，不包含量子化学计算软件的安装或运行教程。

不纳入版本控制的文件包括 `.chk/.fchk`、调度器日志、旧实验报告及其图片、原始数据库网页/扫描件、个人运行环境、编译缓存。它们保留在作者本地，不影响从已提交输出重建谱图。校徽为可选排版资源，不随仓库分发；缺少它时 TeX 仍可编译。报告 PDF 的既有封面并不授予校徽的再使用权。

## 快速开始

安装 Python 3.12、R 和所需依赖后，在仓库根目录执行：

```sh
python reproduce.py --data-only  # 仅重新提取与展宽，不需要 R
python reproduce.py             # 数据 + 两张 PNG/PDF 图
python reproduce.py --tex       # 再编译 TeX，输出到 experiment-report/tex-build/
```

脚本会覆盖派生 CSV、JSON 和谱图，不修改 Gaussian 原始输入、输出或报告正文。重新绘图后的字体排版可能因系统而异，不以二进制文件完全一致作为复现判据。

## 来源和许可证

仓库原有 [MIT LICENSE](LICENSE) 保持不变，适用于作者有权许可的原创代码。SDBS、NIST、文献数据、第三方标识及 Gaussian 输出中的软件声明分别保留其原始权利和使用条件；不能将仓库许可证理解为这些内容的重新授权。详见 [第三方说明](THIRD_PARTY_NOTICES.md)。
