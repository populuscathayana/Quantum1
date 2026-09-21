# 环境安装与复现

## 1. 按复现目标安装

| 目标 | 必需软件 |
|---|---|
| 阅读现有图与报告 PDF | PDF 阅读器，无需计算环境 |
| 从 Gaussian 输出重建 CSV/JSON | Python + NumPy + Pillow |
| 重绘 IR/Raman PNG 与 PDF | 上述环境 + R + ggplot2 + scales + 中文字体 |
| 编译报告 TeX | XeLaTeX；现有谱图 PDF 已在仓库中，不必先重绘 |

测试环境：macOS，Python 3.12.14、NumPy 2.3.5、Pillow 12.3.0、R 4.3.1、ggplot2 3.4.3、scales 1.2.1、TeX Live 2023。Python 依赖版本固定于 `requirements.txt`。R 安装命令会安装当前仓库可用版本，不是完整的传递依赖锁文件；不同版本可能产生字体、线条或警告差异。Windows/Linux 的适配步骤供迁移使用，未在本次 macOS 环境中实机验证。

## 2. 获取仓库

先安装 Git，然后执行：

```sh
git clone https://github.com/populuscathayana/Quantum1.git
cd Quantum1
```

也可通过 GitHub 的 Download ZIP 下载并解压。以下命令除另有说明外均在仓库根目录执行。

## 3. Python

从 [Python 官网](https://www.python.org/downloads/) 安装 Python 3.12（推荐与测试环境一致）。用虚拟环境隔离依赖，方法见 [Python venv 官方文档](https://docs.python.org/3/library/venv.html)。不要上传 `.venv`。

### macOS / Linux

```sh
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python -c "import numpy, PIL; print(numpy.__version__, PIL.__version__)"
```

Debian/Ubuntu 若提示缺少 venv，可先运行 `sudo apt install python3-venv`。Python 必须满足所固定 NumPy 的版本要求，推荐 3.12，不使用系统中的旧版 Python。

### Windows PowerShell

安装 Python 并将其加入 PATH。可以直接调用虚拟环境中的解释器，无需更改 PowerShell 执行策略：

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install --upgrade pip
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe reproduce.py --data-only
```

后续示例中的 `python` 可相应替换为 `.\.venv\Scripts\python.exe`。

## 4. R 与中文字体

从 [CRAN](https://cran.r-project.org/) 安装 R。macOS 使用 CRAN macOS 安装包；Windows 使用 [CRAN Windows 安装包](https://cran.r-project.org/bin/windows/base/)，并将 R 安装目录的 `bin` 加入 PATH。Linux 可通过系统包管理器安装 `r-base`。RStudio 不是必需软件。

安装绘图包（[ggplot2 官方说明](https://ggplot2.tidyverse.org/)）：

```sh
Rscript -e 'install.packages(c("ggplot2", "scales"), repos="https://cloud.r-project.org")'
Rscript -e 'library(ggplot2); library(scales); print(sessionInfo())'
```

也可在 R 交互窗口执行 `install.packages(c("ggplot2", "scales"), repos="https://cloud.r-project.org")`，避免不同终端的引号差异。若安装当前 ggplot2 提示 R 版本过旧，先升级 R；若要贴近原图排版，可在独立环境使用上文列出的测试版本。

绘图脚本按系统选择默认中文字体：macOS 为 `Heiti SC`，Windows 为 `Microsoft YaHei`，Linux 为 `Noto Sans CJK SC`。Linux 可安装 `fonts-noto-cjk`（Debian/Ubuntu）。字体缺失时，请安装可用中文字体或指定：

```sh
export SPECTRA_FONT='Noto Sans CJK SC'  # macOS/Linux，替换为实际安装的字体族名
```

Windows PowerShell 对应 `$env:SPECTRA_FONT = 'Microsoft YaHei'`。macOS 使用 Quartz 导出 PDF；其他系统使用 Cairo，需确认 `Rscript -e 'print(capabilities("cairo"))'` 返回 TRUE。中文出现方框时，应检查字体而不是修改数据。

## 5. 重建数据与谱图

```sh
python reproduce.py --data-only
python reproduce.py
```

第一条命令从三个频率输出重新提取模式、生成展宽曲线，并核验能量和二聚体几何。第二条另外运行两份 R 脚本。预期得到 39、39、84 个正频率模式；二聚体模式 71、72 的缩放频率约为 1653.8680、1697.1630 cm⁻¹。

默认使用已提交的 `IR-comparison/experimental_ir_digitized.csv`、`IR-comparison/reference_ir_modes.csv` 以及 Raman 数值化 CSV，不访问外部数据库。该路径复现的是“已数值化数据 → 分析与图”，不是对原始图像的独立再次数值化。

若需要从源图重新数值化，须先按来源网站的使用条件自行取得原图：

- IR：把 SDBS `IR-NIDA-63340` GIF 存为 `IR-comparison/sources/SDBS_IR_NIDA63340.gif`，把 NIST B3LYP/aug-cc-pVTZ 表格页面存为 `IR-comparison/sources/nist_reference.html`，再执行 `python IR-comparison/prepare_ir_data.py --redigitize`。
- Raman：在 `Raman-comparison` 目录按其 README 的命令添加 `--sdbs-image /path/to/RM563.gif`。此选项会覆盖现有数值化实验曲线。

数值化脚本针对记录的旧版图像尺寸与坐标标定编写，网页换图后不能直接假定仍适用。源记录链接与使用说明见 [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md)。

## 6. XeLaTeX

macOS 推荐安装 [MacTeX](https://tug.org/mactex/)，Windows/Linux 可安装 [TeX Live](https://tug.org/texlive/)。需能运行 `xelatex --version`，不能用 pdfLaTeX 替代。macOS 若找不到命令，将 `/Library/TeX/texbin` 加入 PATH 后重开终端。

源文件使用 `fontspec`、`xeCJK`、`graphicx`、`amsmath`、`amssymb`、`array`、`tabularx`、`booktabs`、`float`、`caption`、`titlesec`、`titletoc`、`geometry`、`xcolor`、`listings`、`xurl`、`hyperref`、`bookmark`、`placeins`。完整 TeX Live/MacTeX 一般包含这些宏包；精简发行版需要通过其包管理器补齐。中文优先使用宋体/黑体/楷体或 macOS 对应字体，否则回退到 TeX Live 的 Fandol；英文回退到 TeX Gyre Termes。

只编译报告：

```sh
cd experiment-report
xelatex -interaction=nonstopmode -halt-on-error benzoic_acid_ir_raman.tex
xelatex -interaction=nonstopmode -halt-on-error benzoic_acid_ir_raman.tex
cd ..
```

两遍用于解析图表引用和文献编号，无需 BibTeX。以上命令会覆盖目录内报告 PDF；若希望保留已发布 PDF，可在根目录运行 `python reproduce.py --data-only --tex`，生成到忽略目录 `experiment-report/tex-build/`，或运行 `python reproduce.py --tex` 同时重绘图。谱图通过相对路径引用，不能只搬走单个 `.tex` 文件。

`image/zju.png` 为可选校徽，不在仓库中分发；缺少时自动跳过，故重新编译的封面与已发布 PDF 可能略有不同。
