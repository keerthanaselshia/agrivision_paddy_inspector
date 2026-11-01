"""
map_page.py  –  Location & Map page for AgriVision Paddy Inspector.

Step 7 features:
  • Folium map with pins coloured by severity grade
  • Popup on each pin: disease, confidence, severity, date, location text
  • Timeline chart: scans per week grouped by disease class
  • Disease heatmap tile (folium HeatMap plugin)
  • Summary stats: hotspot district, busiest week, most-seen disease on map

Dark smart-agriculture theme.  Data via history_db.get_inspections().
"""

import re
from datetime import datetime, timedelta

import folium
import pandas as pd
import streamlit as st
from folium.plugins import HeatMap
from streamlit_folium import st_folium

from history_db import get_inspections
from core.theme import apply_theme, section_header

# ---------------------------------------------------------------------------
# Severity → colour mapping (matches dark theme palette)
# ---------------------------------------------------------------------------
_SEV_COLOUR = {
    "Very low (monitor)": "#2ee59d",   # accent green
    "Moderate":           "#ffd166",   # amber
    "High":               "#ff9f43",   # orange
    "Severe (urgent)":    "#ff5d5d",   # red
}
_DEFAULT_COLOUR = "#8ab89a"

# Folium circle-marker radius by grade
_SEV_RADIUS = {
    "Very low (monitor)": 8,
    "Moderate":           10,
    "High":               12,
    "Severe (urgent)":    15,
}

# Default map centre (Tamil Nadu, India)
_DEFAULT_LAT = 11.1271
_DEFAULT_LON = 78.6569
_DEFAULT_ZOOM = 7


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _parse_latlon(location_str: str | None) -> tuple[float, float] | None:
    """
    Try to extract (lat, lon) from a free-text location string.
    Accepts formats like:
        "11.1271, 78.6569"
        "lat:11.1271 lon:78.6569"
        "Erode, Tamil Nadu"   → None (no coordinates)
    Returns None if parsing fails.
    """
    if not location_str:
        return None
    # Match two floating-point numbers anywhere in the string
    nums = re.findall(r"[-+]?\d+\.?\d*", location_str)
    if len(nums) >= 2:
        try:
            lat, lon = float(nums[0]), float(nums[1])
            # Basic sanity check
            if -90 <= lat <= 90 and -180 <= lon <= 180:
                return lat, lon
        except ValueError:
            pass
    return None


def _colour(grade: str | None) -> str:
    return _SEV_COLOUR.get(grade or "", _DEFAULT_COLOUR)


def _radius(grade: str | None) -> int:
    return _SEV_RADIUS.get(grade or "", 8)


def _week_label(dt: pd.Timestamp) -> str:
    """Return 'YYYY-Www' for a timestamp."""
    return dt.strftime("%Y-W%V")


# ---------------------------------------------------------------------------
# Map builder
# ---------------------------------------------------------------------------

def _build_map(df: pd.DataFrame) -> folium.Map:
    """Build a folium map with severity-coloured pins."""
    # Centre on mean of valid coords, else default
    valid = df.dropna(subset=["latitude", "longitude"])
    if not valid.empty:
        clat = valid["latitude"].mean()
        clon = valid["longitude"].mean()
        zoom = 9
    else:
        clat, clon, zoom = _DEFAULT_LAT, _DEFAULT_LON, _DEFAULT_ZOOM

    m = folium.Map(
        location=[clat, clon],
        zoom_start=zoom,
        tiles="CartoDB dark_matter",   # dark base tile matching theme
    )

    # ── HeatMap layer (all valid coords, weighted by severity %) ─────────────
    heat_data = []
    for _, row in valid.iterrows():
        sev_w = float(row["severity"]) / 100 if pd.notna(row.get("severity")) else 0.5
        heat_data.append([row["latitude"], row["longitude"], sev_w])
    if heat_data:
        HeatMap(
            heat_data,
            radius=20,
            blur=15,
            gradient={0.2: "#2ee59d", 0.5: "#ffd166", 0.8: "#ff9f43", 1.0: "#ff5d5d"},
            name="Severity heatmap",
        ).add_to(m)

    # ── Individual pins ───────────────────────────────────────────────────────
    for _, row in valid.iterrows():
        grade  = row.get("severity_grade") or ""
        dis    = row.get("disease") or "—"
        conf   = row.get("confidence")
        sev    = row.get("severity")
        loc    = row.get("location") or ""
        ts     = str(row.get("inspected_at", ""))[:16]
        colour = _colour(grade)
        r      = _radius(grade)

        popup_html = f"""
        <div style="font-family:sans-serif;min-width:200px;">
          <b style="color:{colour};font-size:1.05em;">{dis}</b><br>
          <span style="color:#555;">🕒 {ts}</span><br>
          <span>Severity: <b>{f"{float(sev):.1f}%" if pd.notna(sev) else "—"}</b></span><br>
          <span>Grade: <b>{grade or "—"}</b></span><br>
          <span>Confidence: {f"{float(conf):.1f}%" if pd.notna(conf) else "—"}</span><br>
          <span style="color:#888;">📍 {loc}</span>
        </div>"""

        folium.CircleMarker(
            location=[row["latitude"], row["longitude"]],
            radius=r,
            color=colour,
            fill=True,
            fill_color=colour,
            fill_opacity=0.75,
            popup=folium.Popup(popup_html, max_width=260),
            tooltip=f"{dis} — {grade}",
        ).add_to(m)

    # Layer control
    folium.LayerControl().add_to(m)
    return m


# ---------------------------------------------------------------------------
# Timeline chart
# ---------------------------------------------------------------------------

def _timeline_chart(df: pd.DataFrame) -> None:
    """Scans per week, grouped by disease class."""
    t_df = df.copy()
    t_df["week"] = t_df["inspected_at"].dt.to_period("W").apply(lambda p: p.start_time)
    weekly = (
        t_df.groupby(["week", "disease"])
        .size()
        .reset_index(name="count")
    )

    if weekly.empty:
        st.info("No timeline data available yet.")
        return

    # Pivot: rows = weeks, cols = diseases
    pivot = weekly.pivot(index="week", columns="disease", values="count").fillna(0)
    pivot.index = pivot.index.strftime("%d %b")

    section_header("📅", "Scans per week by disease")
    st.bar_chart(pivot, use_container_width=True)


# ---------------------------------------------------------------------------
# Main page
# ---------------------------------------------------------------------------

def show_map_page() -> None:
    apply_theme()
    section_header("🗺️", "Location & Disease Map")

    st.markdown(
        '<div style="color:#8ab89a;font-size:0.88em;'
        'font-family:Poppins,sans-serif;margin-bottom:18px;">'
        "Severity pins on the map use GPS coordinates saved with each scan. "
        "Enter coordinates in the Location field (e.g. <code>11.34, 77.72</code>) "
        "to place pins precisely."
        "</div>",
        unsafe_allow_html=True,
    )

    # ── Load data ─────────────────────────────────────────────────────────────
    try:
        records = get_inspections()
    except Exception as exc:
        st.error(f"Could not load history: {exc}")
        return

    if not records:
        st.markdown(
            '<div style="text-align:center;padding:60px 20px;">'
            '<div style="font-size:3em;">🗺️</div>'
            '<div style="color:#8ab89a;font-family:Poppins,sans-serif;'
            'margin-top:12px;">No inspection records yet.</div>'
            '<div style="color:#5a7a65;font-size:0.85em;margin-top:6px;">'
            "Scan a leaf with Auto-save ON to start building your map."
            "</div></div>",
            unsafe_allow_html=True,
        )
        return

    df = pd.DataFrame(records)
    df["inspected_at"]   = pd.to_datetime(df["inspected_at"],   errors="coerce")
    df["severity"]       = pd.to_numeric(df["severity"],        errors="coerce")
    df["confidence"]     = pd.to_numeric(df["confidence"],      errors="coerce")
    df["severity_grade"] = df.get("severity_grade", pd.Series(dtype=str)).fillna("")

    # Try DB latitude/longitude first; fall back to parsing the location string
    df["latitude"]  = pd.to_numeric(df.get("latitude",  pd.Series(dtype=float)), errors="coerce")
    df["longitude"] = pd.to_numeric(df.get("longitude", pd.Series(dtype=float)), errors="coerce")

    if df["latitude"].isna().all():
        # No GPS stored — try to parse from location text
        parsed = df["location"].apply(_parse_latlon)
        df["latitude"]  = parsed.apply(lambda x: x[0] if x else None)
        df["longitude"] = parsed.apply(lambda x: x[1] if x else None)

    mapped   = df.dropna(subset=["latitude", "longitude"])
    unmapped = df[df["latitude"].isna()]

    # ── Summary metrics ───────────────────────────────────────────────────────
    total        = len(df)
    mapped_count = len(mapped)

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Total scans",  total)
    m2.metric("Pinned on map", mapped_count)

    if not mapped.empty:
        top_district = (
            mapped["location"].value_counts().index[0]
            if "location" in mapped.columns and not mapped["location"].dropna().empty
            else "—"
        )
        severe_count = int((mapped["severity_grade"] == "Severe (urgent)").sum())
        m3.metric("Hotspot location", top_district)
        m4.metric("Severe pins",      severe_count)

    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

    # ── Legend ───────────────────────────────────────────────────────────────
    legend_items = "".join(
        f'<span style="display:inline-flex;align-items:center;gap:5px;'
        f'margin-right:18px;font-size:0.82em;color:#b8d4c0;">'
        f'<span style="width:12px;height:12px;border-radius:50%;'
        f'background:{col};display:inline-block;"></span>{grade}</span>'
        for grade, col in _SEV_COLOUR.items()
    )
    st.markdown(
        f'<div style="font-family:Poppins,sans-serif;margin-bottom:10px;">'
        f'{legend_items}</div>',
        unsafe_allow_html=True,
    )

    # ── Map ───────────────────────────────────────────────────────────────────
    if mapped.empty:
        st.warning(
            "No GPS coordinates found in your scan records. "
            "Enter coordinates like **11.34, 77.72** in the Location field "
            "on the Scan page to place pins on the map."
        )
    else:
        fmap = _build_map(mapped)
        st_folium(fmap, width="100%", height=480, returned_objects=[])

    # ── No-coords table (unmapped records) ────────────────────────────────────
    if not unmapped.empty:
        with st.expander(f"📋 {len(unmapped)} record(s) without coordinates"):
            cols_show = ["id", "inspected_at", "disease", "severity_grade", "location"]
            cols_show = [c for c in cols_show if c in unmapped.columns]
            st.dataframe(
                unmapped[cols_show].rename(columns={
                    "id": "ID", "inspected_at": "Time",
                    "disease": "Disease", "severity_grade": "Grade",
                    "location": "Location text",
                }),
                hide_index=True,
                use_container_width=True,
            )
            st.caption(
                "Add coordinates (e.g. 11.34, 77.72) to the Location field "
                "when scanning to pin these records on the map."
            )

    # ── Filters for timeline ─────────────────────────────────────────────────
    st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)

    all_diseases = sorted(df["disease"].dropna().unique().tolist())
    f1, f2 = st.columns([3, 2])
    with f1:
        sel_diseases = st.multiselect(
            "Filter diseases for timeline",
            all_diseases,
            default=all_diseases,
        )
    with f2:
        weeks_back = st.slider("Show last N weeks", 2, 52, 12)

    cutoff = pd.Timestamp.now() - pd.Timedelta(weeks=weeks_back)
    t_filtered = df[
        (df["disease"].isin(sel_diseases)) &
        (df["inspected_at"] >= cutoff)
    ].copy()

    # ── Timeline chart ────────────────────────────────────────────────────────
    if not t_filtered.empty:
        _timeline_chart(t_filtered)
    else:
        st.info("No records in selected range. Adjust the filters above.")

    # ── Severity breakdown for mapped area ────────────────────────────────────
    if not mapped.empty:
        section_header("📊", "Severity breakdown (mapped scans)")
        grade_counts = mapped["severity_grade"].value_counts()
        grade_colours = [_SEV_COLOUR.get(g, _DEFAULT_COLOUR) for g in grade_counts.index]

        # Use a simple bar chart coloured green (Streamlit limitation: single colour only)
        st.bar_chart(grade_counts, color="#2ee59d")
        st.caption(
            "Colour coding: 🟢 Very low  🟡 Moderate  🟠 High  🔴 Severe (urgent)"
        )
