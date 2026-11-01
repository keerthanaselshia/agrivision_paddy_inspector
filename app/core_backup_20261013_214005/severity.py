"""
core/severity.py  –  OpenCV-based leaf severity estimation.

Computes the percentage of a paddy leaf that shows brown/tan lesions.
Algorithm:
  1. Convert to HSV.
  2. Detect the largest green region as the leaf mask.
  3. Detect brown pixels inside the mask as lesions.
  4. Return lesion_pixels / leaf_pixels * 100.

The thresholds (sat_min, lesion_hue_max) are passed in from the Streamlit
sliders so the user can recalibrate for different cameras without editing code.

Note: this method over-counts on busy backgrounds and is not yet validated
against manual IRRI scoring.  A severity validation page (Feature 8) will
help collect the data needed for calibration.
"""

import cv2
import numpy as np


def severity(
    img_rgb: np.ndarray,
    sat_min: int = 40,
    lesion_hue_max: int = 28,
) -> tuple[float, np.ndarray]:
    """Estimate lesion coverage and return a colour overlay.

    Parameters
    ----------
    img_rgb : np.ndarray
        Input image in RGB format, uint8.
    sat_min : int
        Minimum HSV saturation to count a pixel as coloured (not grey/white).
    lesion_hue_max : int
        Upper HSV hue boundary for brown/yellow lesion pixels.

    Returns
    -------
    pct : float
        Lesion area as a percentage of the detected leaf area (0–100).
    overlay : np.ndarray
        RGB image with lesion pixels tinted red (50% blend).
    """
    hsv = cv2.cvtColor(img_rgb, cv2.COLOR_RGB2HSV)
    hue, sat, val = cv2.split(hsv)

    # --- Leaf mask: largest green contour (filled) --------------------------
    green = (
        (hue >= lesion_hue_max) & (hue <= 95)
        & (sat >= sat_min) & (val >= 40)
    ).astype(np.uint8) * 255
    green = cv2.morphologyEx(green, cv2.MORPH_OPEN, np.ones((5, 5), np.uint8))
    k = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (41, 41))
    closed = cv2.morphologyEx(green, cv2.MORPH_CLOSE, k)
    contours, _ = cv2.findContours(
        closed, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
    )
    leaf = np.zeros_like(closed)
    if contours:
        c = max(contours, key=cv2.contourArea)
        cv2.drawContours(leaf, [c], -1, 255, thickness=-1)

    # --- Lesion mask: brown pixels inside the leaf --------------------------
    brown = (
        (hue < lesion_hue_max) & (sat >= sat_min) & (val >= 40)
    ).astype(np.uint8) * 255
    lesion = (leaf > 0) & (brown > 0)
    lesion = (
        cv2.morphologyEx(
            lesion.astype(np.uint8) * 255,
            cv2.MORPH_OPEN,
            np.ones((3, 3), np.uint8),
        ) > 0
    )

    total = int(np.count_nonzero(leaf))
    pct = 100.0 * int(np.count_nonzero(lesion)) / total if total else 0.0

    # --- Red overlay --------------------------------------------------------
    overlay = img_rgb.copy()
    overlay[lesion] = (
        0.5 * overlay[lesion] + 0.5 * np.array([255, 0, 0])
    ).astype(np.uint8)

    return pct, overlay


def grade(pct: float) -> str:
    """Map lesion percentage to a human-readable severity grade.

    Bands match the original app:
      < 1 %  → Very low (monitor)
      < 10 % → Moderate
      < 25 % → High
      >= 25 % → Severe (urgent)
    """
    if pct < 1:
        return "Very low (monitor)"
    if pct < 10:
        return "Moderate"
    if pct < 25:
        return "High"
    return "Severe (urgent)"
