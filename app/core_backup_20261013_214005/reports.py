"""
core/reports.py  –  Report generation helpers (stub).

Full implementation comes in Step 6 (Feature 5 – Scan history).
Placeholders are here so app.py can import the module without errors.
"""

from __future__ import annotations


def build_text_report(
    name: str,
    conf: float | None,
    sev: float,
    sev_grade: str,
    location: str,
    advice_en: str = "",
    advice_ta: str = "",
) -> str:
    """Return a plain-text scan report string.

    This is the same report that already appears in app.py's text area.
    Moving it here keeps the UI file clean.
    """
    lines = ["AgriVision Paddy Inspector", f"Disease: {name}"]
    if conf is not None:
        lines[1] += f" ({conf:.0f}%)"
    lines += [
        f"Severity: {sev:.1f}% - {sev_grade}",
        f"Location: {location}",
    ]
    if advice_en:
        lines += [f"Advice: {advice_en}", advice_ta]
    return "\n".join(lines)
