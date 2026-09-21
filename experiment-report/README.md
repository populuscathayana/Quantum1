# 实验报告与复核

- `benzoic_acid_ir_raman.tex`：提交版 XeLaTeX 源文件。
- `benzoic_acid_ir_raman.pdf`：报告 PDF。
- `苯甲酸双构型红外与拉曼光谱实验报告.md`：Markdown 版本，内容包括两个单体及二聚体。

图像引用相邻 `IR-comparison` 和 `Raman-comparison` 目录中的矢量 PDF；Markdown 引用对应 PNG。移动报告时应保留这些相对目录关系。校徽源图为可选资源，未在仓库中分发，TeX 会在缺少它时跳过。

完整安装说明见 [环境指南](../ENVIRONMENT.md)。在本目录编译两遍即可解析引用，不需要 BibTeX：

```sh
xelatex -interaction=nonstopmode -halt-on-error benzoic_acid_ir_raman.tex
xelatex -interaction=nonstopmode -halt-on-error benzoic_acid_ir_raman.tex
```

在仓库根目录运行 `python experiment-report/verify_results.py`，可重建 `verified_results.json` 与 `dimer_mode_bond_projections.csv`。前者记录原始日志的 SHA-256、能量、模式数和二聚体氢键几何；后者用于定性核验羰基、O–H 正常模式。原始计算输入、输出不会被该脚本修改。
