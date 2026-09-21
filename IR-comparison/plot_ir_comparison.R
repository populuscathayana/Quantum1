#!/usr/bin/env Rscript

suppressPackageStartupMessages(library(ggplot2))
os_name <- Sys.info()[["sysname"]]
default_font <- if (os_name == "Darwin") "Heiti SC" else if (os_name == "Windows") "Microsoft YaHei" else "Noto Sans CJK SC"
font_family <- Sys.getenv("SPECTRA_FONT", unset = default_font)

args <- commandArgs(trailingOnly = TRUE)
if (length(args) != 2) stop("Usage: plot_ir_comparison.R INPUT_CSV OUTPUT_PREFIX")
input_csv <- args[[1]]
output_prefix <- args[[2]]

wide <- read.csv(input_csv, check.names = FALSE)
series_names <- names(wide)[-1]
labels <- c(
  "实验：SDBS KBr 压片 IR",
  "参考理论：NIST B3LYP/aug-cc-pVTZ",
  "构型 1：Gaussian B3LYP/6-31G(d)",
  "构型 2：Gaussian B3LYP/6-31G(d)",
  "二聚体：Gaussian B3LYP/6-31G(d)"
)
colors <- c("#202124", "#C98910", "#2F6FA3", "#C85A3A", "#657D36")
stopifnot(identical(series_names, c("experiment", "reference", "conformer1", "conformer2", "dimer")))

long <- do.call(rbind, lapply(seq_along(series_names), function(i) {
  data.frame(
    wavenumber = wide[[1]], intensity = wide[[series_names[[i]]]],
    series = labels[[i]], stringsAsFactors = FALSE
  )
}))
long$series <- factor(long$series, levels = labels)

full <- subset(long, wavenumber >= 400 & wavenumber <= 4000)
full$region <- "全谱：400–4000 cm-1"
finger <- subset(long, wavenumber >= 400 & wavenumber <= 1800)
finger$region <- "指纹区：400–1800 cm-1"
plot_data <- rbind(full, finger)
plot_data$region <- factor(plot_data$region,
                           levels = c("全谱：400–4000 cm-1", "指纹区：400–1800 cm-1"))

guide_peaks <- c(708, 936, 1294, 1689, 3073)
guide_data <- expand.grid(series = labels, region = levels(plot_data$region),
                          peak = guide_peaks, stringsAsFactors = FALSE)
guide_data$series <- factor(guide_data$series, levels = labels)
guide_data$region <- factor(guide_data$region, levels = levels(plot_data$region))
guide_data <- subset(guide_data,
  (region == "全谱：400–4000 cm-1" & peak >= 400 & peak <= 4000) |
  (region == "指纹区：400–1800 cm-1" & peak >= 400 & peak <= 1800))

peak_labels <- subset(guide_data, series == labels[[1]])
peak_labels$label <- peak_labels$peak
peak_labels$y <- 0.70

panel_titles <- expand.grid(series = labels, region = levels(plot_data$region),
                            stringsAsFactors = FALSE)
panel_titles$series <- factor(panel_titles$series, levels = labels)
panel_titles$region <- factor(panel_titles$region, levels = levels(plot_data$region))
panel_titles$x <- ifelse(panel_titles$region == "全谱：400–4000 cm-1", 435, 415)
panel_titles$y <- 0.95

p <- ggplot(plot_data, aes(wavenumber, intensity, color = series)) +
  geom_vline(data = guide_data, aes(xintercept = peak),
             color = "#C7CBD1", linewidth = 0.28, linetype = "22") +
  geom_line(linewidth = 0.62, lineend = "round", na.rm = TRUE) +
  geom_label(data = panel_titles,
             aes(x = x, y = y, label = series, color = series), inherit.aes = FALSE,
             hjust = 0, vjust = 1, size = 2.75, fontface = "bold", family = font_family,
             fill = scales::alpha("white", 0.82), label.size = 0,
             label.padding = unit(0.12, "lines")) +
  geom_text(data = peak_labels,
            aes(x = peak, y = y, label = label), inherit.aes = FALSE,
            size = 2.25, color = "#5F6368", angle = 90, vjust = -0.25,
            family = font_family) +
  facet_grid(rows = vars(series), cols = vars(region), scales = "free_x", space = "free_x") +
  scale_color_manual(values = setNames(colors, labels), guide = "none") +
  scale_x_continuous(expand = expansion(mult = c(0.008, 0.008)),
                     breaks = function(x) pretty(x, n = 7)) +
  scale_y_continuous(limits = c(0, 1.02), breaks = c(0, 0.5, 1),
                     labels = c("0", "0.5", "1.0"), expand = c(0, 0)) +
  labs(
    title = "苯甲酸 IR 光谱统一对比",
    subtitle = "实验谱、公开参考理论谱、两个单体构型与二聚体；各谱独立归一化",
    x = expression(paste("Wavenumber / cm"^{-1})),
    y = "归一化吸收强度",
    caption = paste0(
      "实验：SDBS IR-NIDA-63340（KBr 压片；原图数值化，A = -log10(T)）。计算谱：Gaussian FWHM = 20 cm-1。\n",
      "单体与二聚体缩放因子 0.9613；参考理论 0.9675。归一化范围：400–4000 cm-1；孤立二聚体仍不等同于晶体。"

    )
  ) +
  theme_minimal(base_family = font_family, base_size = 10.5) +
  theme(
    plot.background = element_rect(fill = "white", color = NA),
    panel.background = element_rect(fill = "#FCFCFD", color = NA),
    panel.grid.minor = element_blank(),
    panel.grid.major.x = element_line(color = "#E5E7EB", linewidth = 0.28),
    panel.grid.major.y = element_line(color = "#ECEEF1", linewidth = 0.28),
    strip.background = element_rect(fill = "#F1F3F5", color = NA),
    strip.text.x = element_text(face = "bold", color = "#30343B", size = 10),
    strip.text.y = element_blank(),
    axis.title = element_text(color = "#30343B"),
    axis.text = element_text(color = "#555B65"),
    plot.title = element_text(face = "bold", size = 17, color = "#202124"),
    plot.subtitle = element_text(size = 10.5, color = "#5F6368", margin = margin(b = 8)),
    plot.caption = element_text(size = 7.8, color = "#6B7280", hjust = 0, lineheight = 1.15,
                                margin = margin(t = 10)),
    panel.spacing = unit(0.65, "lines"),
    panel.spacing.x = unit(1.6, "lines"),
    plot.margin = margin(16, 18, 14, 14)
  )

ggsave(paste0(output_prefix, ".png"), p, width = 13.2, height = 10.5,
       units = "in", dpi = 300, bg = "white")
if (os_name == "Darwin") {
  quartz(file = paste0(output_prefix, ".pdf"), type = "pdf",
         width = 13.2, height = 10.5, bg = "white")
} else {
  if (!capabilities("cairo")) stop("Cairo graphics support is required for PDF export.")
  cairo_pdf(filename = paste0(output_prefix, ".pdf"), family = font_family,
            width = 13.2, height = 10.5, bg = "white")
}
print(p)
dev.off()
cat("Saved", paste0(output_prefix, ".png/.pdf"), "\n")
