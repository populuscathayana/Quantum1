#!/usr/bin/env python3
"""Prepare experimental, reference-theory, and Gaussian Raman spectra.

The experimental trace is digitized from the SDBS RM-01-00563 raster image.
Calculated Raman activities are converted to relative Stokes intensities for
488.0 nm excitation at 298.15 K, broadened with a 20 cm-1 Gaussian FWHM, and
normalized independently.
"""

from __future__ import annotations

import argparse
import csv
import math
import re
from pathlib import Path

import numpy as np
from PIL import Image


SCALE_OWN = 0.9613
LASER_NM = 488.0
TEMPERATURE_K = 298.15
FWHM_CM = 20.0
HC_OVER_K_CM_K = 1.438776877


# Published ORCA/B3LYP/6-31+G(d,p) benzoic-acid values. The scaled frequencies
# are those reported by Parra Figueredo et al. (2023), using factor 0.9679.
REFERENCE_THEORY = [
    (70.60, 68.33, 0.49), (156.95, 151.91, 1.87), (215.41, 208.50, 0.09),
    (384.26, 371.93, 4.01), (414.19, 400.89, 0.02), (432.01, 418.14, 0.16),
    (497.02, 481.07, 1.12), (592.62, 573.60, 2.51), (629.75, 609.54, 6.55),
    (634.79, 614.41, 0.40), (701.39, 678.88, 0.02), (725.25, 701.97, 0.62),
    (777.08, 752.14, 16.66), (819.35, 793.05, 0.83), (863.99, 836.26, 0.51),
    (961.52, 930.66, 0.03), (998.67, 966.61, 0.00), (1015.09, 982.51, 0.09),
    (1018.83, 986.13, 38.39), (1048.02, 1014.38, 15.46),
    (1096.39, 1061.20, 0.24), (1120.96, 1084.98, 1.67),
    (1186.21, 1148.13, 6.32), (1191.50, 1153.25, 19.74),
    (1211.68, 1172.79, 14.15), (1344.99, 1301.82, 0.14),
    (1365.36, 1321.53, 2.62), (1372.80, 1328.73, 13.20),
    (1485.64, 1437.95, 1.69), (1529.52, 1480.42, 0.76),
    (1630.59, 1578.25, 5.70), (1651.64, 1598.62, 80.52),
    (1790.52, 1733.04, 95.90), (3185.11, 3082.87, 58.65),
    (3197.19, 3094.56, 108.27), (3206.05, 3103.14, 149.05),
    (3220.90, 3117.51, 99.98), (3228.66, 3125.02, 118.59),
    (3766.64, 3645.73, 141.59),
]


def parse_gaussian(path: Path) -> tuple[np.ndarray, np.ndarray]:
    text = path.read_text(errors="replace")
    if "Normal termination" not in text.splitlines()[-1]:
        raise ValueError(f"Gaussian job did not finish normally: {path}")
    atoms = int(re.findall(r"NAtoms=\s*(\d+)", text)[-1])
    frequencies: list[float] = []
    activities: list[float] = []
    for line in text.splitlines():
        if "Frequencies --" in line:
            frequencies.extend(float(x) for x in line.split("--", 1)[1].split())
        elif "Raman Activ --" in line:
            activities.extend(float(x) for x in line.split("--", 1)[1].split())
    if len(frequencies) != 3 * atoms - 6 or len(frequencies) != len(activities):
        raise ValueError(
            f"Could not pair Gaussian frequencies and Raman activities in {path}: "
            f"{len(frequencies)} frequencies, {len(activities)} activities"
        )
    if min(frequencies) <= 0 or min(activities) < 0:
        raise ValueError(f"Nonpositive frequency or negative Raman activity: {path}")
    return np.asarray(frequencies), np.asarray(activities)


def relative_stokes_intensity(freq_cm: np.ndarray, activity: np.ndarray) -> np.ndarray:
    """Convert Raman activity to relative Stokes intensity."""
    laser_cm = 1.0e7 / LASER_NM
    freq = np.asarray(freq_cm, dtype=float)
    activity = np.asarray(activity, dtype=float)
    thermal = 1.0 - np.exp(-HC_OVER_K_CM_K * freq / TEMPERATURE_K)
    intensity = activity * np.maximum(laser_cm - freq, 0.0) ** 4 / (freq * thermal)
    maximum = intensity.max(initial=0.0)
    return intensity / maximum if maximum > 0 else intensity


def broaden(grid: np.ndarray, centers: np.ndarray, weights: np.ndarray) -> np.ndarray:
    sigma = FWHM_CM / (2.0 * math.sqrt(2.0 * math.log(2.0)))
    profile = np.exp(-0.5 * ((grid[:, None] - centers[None, :]) / sigma) ** 2) @ weights
    maximum = profile.max(initial=0.0)
    return profile / maximum if maximum > 0 else profile


def digitize_sdbs_image(path: Path) -> tuple[np.ndarray, np.ndarray]:
    """Digitize the trace from the 738x457 legacy SDBS spectrum raster.

    The legacy plot uses two linear x-axis sections: 4000--2000 cm-1 from
    pixels 25--262 and 2000--0 cm-1 from pixels 262--737.
    """
    image = np.asarray(Image.open(path).convert("L"))
    if image.shape[1] < 738 or image.shape[0] < 280:
        raise ValueError(f"Unexpected SDBS image dimensions: {image.shape}")
    xs = np.arange(26, 737)
    intensity = np.full(xs.shape, np.nan, dtype=float)
    for i, x in enumerate(xs):
        dark = np.where(image[5:279, x] < 128)[0]
        if dark.size:
            y = dark.min() + 5
            intensity[i] = (280.0 - y) / (280.0 - 4.0)

    valid = np.isfinite(intensity)
    intensity = np.interp(np.arange(intensity.size), np.where(valid)[0], intensity[valid])
    baseline = np.quantile(intensity, 0.05)
    intensity = np.clip(intensity - baseline, 0.0, None)
    intensity /= intensity.max()

    frequency = np.where(
        xs <= 262,
        4000.0 - (xs - 25.0) * 2000.0 / (262.0 - 25.0),
        2000.0 - (xs - 262.0) * 2000.0 / (737.0 - 262.0),
    )
    order = np.argsort(frequency)
    return frequency[order], intensity[order]


def write_peak_csv(path: Path, raw: np.ndarray, scaled: np.ndarray, activity: np.ndarray) -> None:
    rel = relative_stokes_intensity(scaled, activity)
    with path.open("w", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(["mode", "raw_cm-1", "scaled_cm-1", "raman_activity", "relative_intensity_488nm"])
        for i, values in enumerate(zip(raw, scaled, activity, rel), start=1):
            writer.writerow([i, *(f"{v:.6f}" for v in values)])


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--chk1", type=Path, required=True)
    parser.add_argument("--chk2", type=Path, required=True)
    parser.add_argument("--dimer", type=Path, required=True)
    parser.add_argument("--sdbs-image", type=Path,
                        help="Optional: otherwise reuse experimental_sdbs_digitized.csv")
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)

    freq1, act1 = parse_gaussian(args.chk1)
    freq2, act2 = parse_gaussian(args.chk2)
    freqd, actd = parse_gaussian(args.dimer)
    ref = np.asarray(REFERENCE_THEORY)
    if args.sdbs_image:
        exp_freq, exp_int = digitize_sdbs_image(args.sdbs_image)
    else:
        experiment = np.loadtxt(args.output_dir / "experimental_sdbs_digitized.csv",
                                delimiter=",", skiprows=1)
        exp_freq, exp_int = experiment[:, 0], experiment[:, 1]

    scaled1 = freq1 * SCALE_OWN
    scaled2 = freq2 * SCALE_OWN
    scaledd = freqd * SCALE_OWN
    write_peak_csv(args.output_dir / "peaks_raman_chk1.csv", freq1, scaled1, act1)
    write_peak_csv(args.output_dir / "peaks_raman_chk2.csv", freq2, scaled2, act2)
    write_peak_csv(args.output_dir / "peaks_dimer.csv", freqd, scaledd, actd)
    write_peak_csv(args.output_dir / "peaks_theory_reference.csv", ref[:, 0], ref[:, 1], ref[:, 2])

    with (args.output_dir / "experimental_sdbs_digitized.csv").open("w", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(["wavenumber_cm-1", "normalized_intensity"])
        writer.writerows((f"{x:.6f}", f"{y:.6f}") for x, y in zip(exp_freq, exp_int))

    grid = np.arange(0.0, 4000.0 + 1.0, 1.0)
    exp_grid = np.interp(grid, exp_freq, exp_int, left=0.0, right=0.0)
    series = {
        "实验：SDBS 粉末 Raman": exp_grid,
        "参考理论：ORCA B3LYP/6-31+G(d,p)": broaden(
            grid, ref[:, 1], relative_stokes_intensity(ref[:, 1], ref[:, 2])
        ),
        "构型 1：Gaussian B3LYP/6-31G(d)": broaden(
            grid, scaled1, relative_stokes_intensity(scaled1, act1)
        ),
        "构型 2：Gaussian B3LYP/6-31G(d)": broaden(
            grid, scaled2, relative_stokes_intensity(scaled2, act2)
        ),
        "二聚体：Gaussian B3LYP/6-31G(d)": broaden(
            grid, scaledd, relative_stokes_intensity(scaledd, actd)
        ),
    }
    with (args.output_dir / "raman_spectra_normalized.csv").open("w", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(["wavenumber_cm-1", *series.keys()])
        for i, x in enumerate(grid):
            writer.writerow([f"{x:.1f}", *(f"{values[i]:.8f}" for values in series.values())])

    print(f"Prepared {len(freq1)}, {len(freq2)} monomer and {len(freqd)} dimer modes in {args.output_dir}")


if __name__ == "__main__":
    main()
