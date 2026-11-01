"""
history_dashboard.py  –  Inspection History page for AgriVision Paddy Inspector.

Dark smart-agriculture theme.  All data read via history_db.get_inspections().
"""

import json
from datetime import datetime

import pandas as pd
import streamlit as st

from history_db import get_inspections, get_schema_version
from core.theme  import apply_theme, section_header

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _safe_col(df: pd.DataFrame, col: str, default=None) -> pd.Series:
    if col in df.columns:
        return df[col]
    return pd.Series([default] * len(df), index=df.index)


def _stat_card(label: str, value: str, icon: str = "", color: str = "#2ee59d") -> None:
    """Render a small dark stat card using st.metric (styled via theme CSS)."""
    st.metric(f"{icon} {label}".strip(), value)


def _severity_dot(grade: str) -> str:
    _DOTS = {
        "Very low (monitor)": "🟢",
        "Moderate":           "🟡",
        "High":               "🟠",
        "Severe (urgent)":    "🔴",
    }
    return _DOTS.get(grade, "⚪")


# ---------------------------------------------------------------------------
# Main dashboard
# ---------------------------------------------------------------------------

def show_history_dashboard() -> None:
    apply_theme()
    section_header("📊", "Inspection History")

    st.markdown(
        '<div style="color:#8ab89a;font-size:0.88em;'
        'font-family:Poppins,sans-serif;margin-bottom:18px;">'
        "All saved paddy leaf inspections. Filter, explore trends, and export."
        "</div>",
        unsafe_allow_html=True,
    )

    # DB info (debug, collapsed)
    try:
        ver = get_schema_version()
        with st.expander("🗄️ Database info", expanded=False):
            st.caption(f"Schema version: {ver}")
    except Exception:
        pass

    # ── Load data ────────────────────────────────────────────────────────────
    try:
        records = get_inspections()
    except Exception as exc:
        st.error(f"Could not load history: {exc}")
        return

    if not records:
        st.markdown(
            '<div style="text-align:center;padding:60px 20px;">'
            '<div style="font-size:3em;">🌿</div>'
            '<div style="color:#8ab89a;font-family:Poppins,sans-serif;'
            'margin-top:12px;font-size:1.05em;">No inspections saved yet.</div>'
            '<div style="color:#5a7a65;font-size:0.85em;margin-top:6px;">'
            "Complete a leaf scan with Auto-save enabled to see records here."
            "</div></div>",
            unsafe_allow_html=True,
        )
        return

    df = pd.DataFrame(records)
    df["inspected_at"]  = pd.to_datetime(df["inspected_at"], errors="coerce")
    df["uncertain"]     = _safe_col(df, "uncertain",      0).fillna(0).astype(int)
    df["source"]        = _safe_col(df, "source",         "").fillna("")
    df["model_version"] = _safe_col(df, "model_version",  "").fillna("")
    df["image_hash"]    = _safe_col(df, "image_hash",     "")
    df["severity_grade"]= _safe_col(df, "severity_grade", "").fillna("")

    # ── Summary metrics ──────────────────────────────────────────────────────
    total            = len(df)
    disease_count    = df["disease"].value_counts()
    valid_sev        = pd.to_numeric(df["severity"],   errors="coerce").dropna()
    valid_conf       = pd.to_numeric(df["confidence"], errors="coerce").dropna()
    uncertain_count  = int(df["uncertain"].sum())
    top_class        = disease_count.index[0] if not disease_count.empty else "—"

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Total scans",        total,                   "inspections")
    m2.metric("Most common",        top_class)
    m3.metric("Avg severity",
              f"{valid_sev.mean():.1f}%" if not valid_sev.empty else "—")
    m4.metric("Uncertain results",  uncertain_count)

    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

    # ── Charts ───────────────────────────────────────────────────────────────
    c_left, c_right = st.columns(2)

    with c_left:
        section_header("🍃", "Disease distribution")
        st.bar_chart(disease_count, color="#2ee59d")

    with c_right:
        conf_df = (
            df[["inspected_at", "confidence"]]
            .dropna()
            .sort_values("inspected_at")
        )
        if not conf_df.empty:
            section_header("📈", "Confidence over time")
            st.line_chart(
                conf_df.rename(
                    columns={"inspected_at": "Time", "confidence": "Confidence (%)"}
                ).set_index("Time"),
                color="#2ee59d",
            )

    # Source breakdown
    src = df["source"].value_counts()
    src = src[src.index != ""]
    if not src.empty:
        section_header("📷", "Image source")
        st.bar_chart(src, color="#ffd166")

    # ── Filters ──────────────────────────────────────────────────────────────
    section_header("🔍", "Find inspections")

    fcol1, fcol2, fcol3 = st.columns([3, 2, 1])
    with fcol1:
        search = st.text_input(
            "Search", placeholder="Disease name or location…",
            label_visibility="collapsed",
        )
    with fcol2:
        locations = sorted(v for v in df["location"].dropna().unique() if str(v).strip())
        sel_loc   = st.selectbox("Location", ["All locations"] + locations,
                                 label_visibility="collapsed")
    with fcol3:
        uncertain_only = st.checkbox("Uncertain only", value=False)

    # Date range
    min_dt = df["inspected_at"].min()
    max_dt = df["inspected_at"].max()
    if pd.notna(min_dt) and pd.notna(max_dt):
        date_range = st.date_input(
            "Date range",
            value=(min_dt.date(), max_dt.date()),
            min_value=min_dt.date(),
            max_value=max_dt.date(),
        )
    else:
        date_range = ()

    # Apply filters
    filtered = df.copy()
    if search.strip():
        q = search.strip()
        mask = (
            filtered["disease"].astype(str).str.contains(q, case=False, na=False)
            | filtered["location"].astype(str).str.contains(q, case=False, na=False)
        )
        filtered = filtered[mask]
    if sel_loc != "All locations":
        filtered = filtered[filtered["location"] == sel_loc]
    if uncertain_only:
        filtered = filtered[filtered["uncertain"] == 1]
    if len(date_range) == 2:
        s, e = date_range
        filtered = filtered[filtered["inspected_at"].dt.date.between(s, e)]

    # ── Results table ─────────────────────────────────────────────────────────
    section_header("🗂️", f"Records — {len(filtered)} match(es)")

    base_cols = {
        "id":            "ID",
        "inspected_at":  "Inspection time",
        "disease":       "Predicted class",
        "confidence":    "Confidence (%)",
        "severity":      "Severity (%)",
        "severity_grade":"Grade",
        "location":      "Location",
        "uncertain":     "Uncertain",
        "source":        "Source",
        "model_version": "Model",
    }
    available  = {k: v for k, v in base_cols.items() if k in filtered.columns}
    display_df = filtered[list(available.keys())].rename(columns=available)

    if "Uncertain" in display_df.columns:
        display_df["Uncertain"] = display_df["Uncertain"].map(
            lambda x: "Yes" if int(x) == 1 else "No"
        )
    if "Grade" in display_df.columns:
        display_df["Grade"] = display_df["Grade"].apply(
            lambda g: f"{_severity_dot(g)} {g}" if g else "—"
        )

    st.dataframe(display_df, use_container_width=True, hide_index=True)

    # ── Export ────────────────────────────────────────────────────────────────
    section_header("💾", "Export")
    csv_bytes = filtered.to_csv(index=False).encode("utf-8")
    st.download_button(
        label="⬇️ Download filtered records (CSV)",
        data=csv_bytes,
        file_name=f"agrivision_history_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
        mime="text/csv",
    )
