"""
core/quality.py  –  Image quality checks before classification.

Checks performed:
  1. Resolution  – image must be at least min_w x min_h pixels.
  2. Blur        – Laplacian variance; low variance = blurry.
  3. Brightness  – mean pixel value; too dark or too bright.
  4. Over-exposure – fraction of saturated pixels.
  5. Leaf visible – estimated green-area fraction.

All thresholds are passed in as keyword arguments so they can be loaded from
config.yaml and adjusted from the Streamlit sidebar for the Pi camera.

Returns a dict:
  score  : int        0-100 (100 = perfect)
  grade  : str        'Good' | 'Fair' | 'Poor'
  reasons: list[str]  human-readable issues (empty when Good)
"""

from __future__ import annotations

import cv2
import numpy as np


def check_quality(
    img_rgb: np.ndarray,
    *,
    min_width: int = 224,
    min_height: int = 224,
    blur_threshold: float = 80.0,
    dark_threshold: float = 50.0,
    bright_threshold: float = 210.0,
    overexp_fraction: float = 0.15,
    min_green_fraction: float = 0.05,
) -> dict:
    """Run all quality checks and return a quality report dict.

    Parameters
    ----------
    img_rgb         : RGB uint8 image (H, W, 3).
    min_width/height: minimum acceptable resolution in pixels.
    blur_threshold  : Laplacian variance below this → blurry.
    dark_threshold  : mean brightness below this → too dark.
    bright_threshold: mean brightness above this → too bright.
    overexp_fraction: fraction of near-white pixels above this → over-exposed.
    min_green_fraction: fraction of green pixels below this → leaf not visible.

    Returns
    -------
    dict:
        score   int   0-100
        grade   str   'Good' | 'Fair' | 'Poor'
        reasons list  human-readable issues found
        details dict  raw metric values (for sidebar/debug display)
    """
    reasons: list[str] = []
    details: dict[str, float] = {}

    h, w = img_rgb.shape[:2]

    # 1. Resolution
    details["width"] = w
    details["height"] = h
    if w < min_width or h < min_height:
        reasons.append(f"Resolution too low ({w}x{h}; need {min_width}x{min_height})")

    # 2. Blur (Laplacian variance on grayscale)
    gray = cv2.cvtColor(img_rgb, cv2.COLOR_RGB2GRAY)
    lap_var = float(cv2.Laplacian(gray, cv2.CV_64F).var())
    details["blur_var"] = round(lap_var, 1)
    if lap_var < blur_threshold:
        reasons.append(f"Image blurry (sharpness {lap_var:.0f}; need >{blur_threshold:.0f})")

    # 3. Brightness
    mean_bright = float(gray.mean())
    details["brightness"] = round(mean_bright, 1)
    if mean_bright < dark_threshold:
        reasons.append(f"Too dark (brightness {mean_bright:.0f}; need >{dark_threshold:.0f})")
    elif mean_bright > bright_threshold:
        reasons.append(f"Too bright (brightness {mean_bright:.0f}; need <{bright_threshold:.0f})")

    # 4. Over-exposure (fraction of pixels with all channels ≥ 245)
    overexp = float(np.mean(np.all(img_rgb >= 245, axis=2)))
    details["overexp_frac"] = round(overexp, 3)
    if overexp > overexp_fraction:
        reasons.append(f"Over-exposed ({overexp*100:.1f}% blown pixels; limit {overexp_fraction*100:.0f}%)")

    # 5. Leaf visible: fraction of green-ish pixels in HSV
    hsv = cv2.cvtColor(img_rgb, cv2.COLOR_RGB2HSV)
    hue, sat, val = cv2.split(hsv)
    green_mask = (hue >= 28) & (hue <= 95) & (sat >= 40) & (val >= 40)
    green_frac = float(np.mean(green_mask))
    details["green_frac"] = round(green_frac, 3)
    if green_frac < min_green_fraction:
        reasons.append(
            f"Leaf not visible (only {green_frac*100:.1f}% green; need >{min_green_fraction*100:.0f}%)"
        )

    # Score: start at 100, deduct per issue
    deductions = {1: 10, 2: 20, 3: 30, 4: 40}   # issues → score deducted
    n = len(reasons)
    score = max(0, 100 - deductions.get(n, 50 + (n - 4) * 10))

    if score >= 75:
        quality_grade = "Good"
    elif score >= 45:
        quality_grade = "Fair"
    else:
        quality_grade = "Poor"

    return {
        "score": score,
        "grade": quality_grade,
        "reasons": reasons,
        "details": details,
    }
