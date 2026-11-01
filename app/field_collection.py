"""
field_collection.py  –  Field Data Collection Mode for AgriVision Paddy Inspector.

Step 8 features:
  • Standardized file naming: F<field_id>_P<plant_id>_<class>_<number>.jpg
  • Background class support alongside standard disease classes
  • Persistent metadata.csv tracking (filename, field_id, plant_id, class, timestamp, location, notes, width, height)
  • Real-time counter dashboard (total collected, session count, breakdown per class)
  • Camera and file upload modes tailored for rapid in-field logging
  • Quick plant/field increment controls
"""

import csv
import io
import os
import re
from datetime import datetime
from pathlib import Path

import numpy as np
import pandas as pd
import streamlit as st
from PIL import Image

from core.quality import check_quality
from core.theme import apply_theme, section_header, render_html

# Storage directories under project root
_PROJECT_ROOT = Path(__file__).resolve().parent.parent
COLLECTION_DIR = _PROJECT_ROOT / "collected_data"
IMAGES_DIR = COLLECTION_DIR / "images"
METADATA_FILE = COLLECTION_DIR / "metadata.csv"

CLASSES = ["blast", "blb", "brown_spot", "healthy", "background", "other"]

CSV_COLUMNS = [
    "filename",
    "field_id",
    "plant_id",
    "class",
    "timestamp",
    "location",
    "notes",
    "width",
    "height",
]


def _init_storage():
    IMAGES_DIR.mkdir(parents=True, exist_ok=True)
    if not METADATA_FILE.exists():
        with open(METADATA_FILE, mode="w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(CSV_COLUMNS)


def _load_metadata() -> pd.DataFrame:
    _init_storage()
    if METADATA_FILE.exists() and METADATA_FILE.stat().st_size > 0:
        try:
            return pd.read_csv(METADATA_FILE)
        except Exception:
            return pd.DataFrame(columns=CSV_COLUMNS)
    return pd.DataFrame(columns=CSV_COLUMNS)


def _get_next_number(field_clean: str, plant_clean: str, class_name: str) -> int:
    """Find next sequence number for this field, plant, and class combination."""
    prefix = f"F{field_clean}_P{plant_clean}_{class_name}_"
    max_num = 0
    if IMAGES_DIR.exists():
        for fname in os.listdir(IMAGES_DIR):
            if fname.startswith(prefix) and fname.lower().endswith((".jpg", ".jpeg")):
                match = re.search(rf"{re.escape(prefix)}(\d+)\.jpg", fname, re.IGNORECASE)
                if match:
                    try:
                        n = int(match.group(1))
                        if n > max_num:
                            max_num = n
                    except ValueError:
                        pass
    return max_num + 1


def _clean_id(raw_val: str, prefix: str = "") -> str:
    """Normalize user input like 'F01' or '1' into '01'."""
    val = str(raw_val).strip()
    if prefix and val.upper().startswith(prefix.upper()):
        val = val[len(prefix):].strip()
    # Strip any invalid characters
    val = re.sub(r"[^A-Za-z0-9_-]", "", val)
    return val if val else "01"


def show_field_collection() -> None:
    apply_theme()
    _init_storage()

    section_header("🌾", "Field Data Collection Mode")

    render_html(
        '<div style="color:#8ab89a;font-size:0.88em;'
        'font-family:Poppins,sans-serif;margin-bottom:18px;">'
        "Standardized in-field dataset collection for retraining and validation. "
        "Images are auto-named with <code>F&lt;field&gt;_P&lt;plant&gt;_&lt;class&gt;_&lt;number&gt;.jpg</code> "
        "and logged in <code>collected_data/metadata.csv</code>."
        "</div>"
    )

    df_meta = _load_metadata()

    # Session stats
    if "session_collected_count" not in st.session_state:
        st.session_state["session_collected_count"] = 0

    # ── Dashboard & Counters ─────────────────────────────────────────────────
    total_samples = len(df_meta)
    session_samples = st.session_state["session_collected_count"]

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Total Collected", total_samples, "samples")
    m2.metric("This Session", session_samples, "photos")

    # Counts by class
    class_counts = {c: 0 for c in CLASSES}
    if not df_meta.empty and "class" in df_meta.columns:
        counts = df_meta["class"].value_counts().to_dict()
        for c in CLASSES:
            class_counts[c] = counts.get(c, 0)

    top_class = max(class_counts, key=class_counts.get) if total_samples > 0 else "—"
    m3.metric("Leading Class", top_class, f"{class_counts.get(top_class, 0)} items")

    bg_count = class_counts.get("background", 0)
    m4.metric("Background Samples", bg_count, "negatives")

    render_html("<div style='height:8px'></div>")

    # ── Collection Settings & Form ───────────────────────────────────────────
    with st.container(border=True):
        render_html(
            '<div style="color:#2ee59d;font-weight:600;font-family:Poppins,sans-serif;'
            'font-size:0.95em;margin-bottom:12px;">🏷️ Sample Metadata & Naming Setup</div>'
        )

        col_f, col_p, col_c = st.columns([1.5, 1.5, 2])

        # State keys for easy incrementing
        if "fc_field_id" not in st.session_state:
            st.session_state["fc_field_id"] = "01"
        if "fc_plant_id" not in st.session_state:
            st.session_state["fc_plant_id"] = "01"

        with col_f:
            field_raw = st.text_input("Field ID (e.g. 01, North, F1)", value=st.session_state["fc_field_id"])
            st.session_state["fc_field_id"] = field_raw
            field_clean = _clean_id(field_raw, prefix="F")

        with col_p:
            plant_raw = st.text_input("Plant ID (e.g. 01, P2)", value=st.session_state["fc_plant_id"])
            st.session_state["fc_plant_id"] = plant_raw
            plant_clean = _clean_id(plant_raw, prefix="P")

        with col_c:
            sel_class = st.selectbox(
                "Ground Truth Class",
                CLASSES,
                index=0,
                help="Select the confirmed diagnosis or background (non-leaf/soil/weeds)",
            )

        col_ctrl1, col_ctrl2, col_loc, col_notes = st.columns([1, 1, 2, 2])
        with col_ctrl1:
            if st.button("➕ Next Plant (P+1)", use_container_width=True):
                try:
                    p_num = int(re.search(r"\d+", plant_clean).group(0))
                    new_p = f"{p_num + 1:02d}"
                except Exception:
                    new_p = f"{plant_clean}_next"
                st.session_state["fc_plant_id"] = new_p
                st.rerun()

        with col_ctrl2:
            if st.button("➕ Next Field (F+1)", use_container_width=True):
                try:
                    f_num = int(re.search(r"\d+", field_clean).group(0))
                    new_f = f"{f_num + 1:02d}"
                except Exception:
                    new_f = f"{field_clean}_next"
                st.session_state["fc_field_id"] = new_f
                st.session_state["fc_plant_id"] = "01"
                st.rerun()

        with col_loc:
            loc_val = st.text_input("Location / GPS", "11.34, 77.72 (Erode)", key="fc_location")

        with col_notes:
            notes_val = st.text_input("Notes (e.g. stage, leaf position)", "", key="fc_notes")

        # Computed filename preview
        next_num = _get_next_number(field_clean, plant_clean, sel_class)
        generated_name = f"F{field_clean}_P{plant_clean}_{sel_class}_{next_num:03d}.jpg"

        render_html(
            f'<div style="background:#1a3d28;padding:8px 14px;border-radius:8px;'
            f'font-family:monospace;color:#2ee59d;font-size:0.9em;margin-top:6px;">'
            f'Target Filename: <b>{generated_name}</b>'
            f'</div>'
        )

    # ── Image Capture / Upload ────────────────────────────────────────────────
    render_html("<div style='height:10px'></div>")
    section_header("📸", "Capture or Upload Sample")

    cap_col, preview_col = st.columns([1.2, 1])

    with cap_col:
        tab_cam, tab_file = st.tabs(["📷 Field Camera", "📁 File Upload"])
        with tab_cam:
            cam_file = st.camera_input("Snap picture of leaf / background", key="fc_camera")
        with tab_file:
            up_file = st.file_uploader(
                "Upload field picture",
                type=["jpg", "jpeg", "png"],
                key="fc_uploader",
            )

    active_file = cam_file if cam_file is not None else up_file

    with preview_col:
        if active_file is not None:
            img = Image.open(active_file).convert("RGB")
            img_np = np.array(img)

            # Quick quality verification
            q = check_quality(img_np)
            q_color = "#2ee59d" if q["grade"] == "Good" else ("#ffd166" if q["grade"] == "Fair" else "#ff5d5d")

            st.image(img, caption=f"Captured preview ({img.width}x{img.height})", use_container_width=True)
            render_html(
                f'<div style="font-family:Poppins,sans-serif;font-size:0.85em;color:{q_color};margin-bottom:8px;">'
                f'Quality: <b>{q["grade"]}</b> (Score: {q["score"]}/100)'
                + (f" – {', '.join(q['reasons'])}" if q["reasons"] else "")
                + "</div>"
            )

            # Save action
            if st.button("💾 Save Sample to Dataset", type="primary", use_container_width=True):
                save_path = IMAGES_DIR / generated_name
                img.save(save_path, format="JPEG", quality=95)

                now_ts = datetime.now().astimezone().isoformat(timespec="seconds")
                new_row = [
                    generated_name,
                    field_clean,
                    plant_clean,
                    sel_class,
                    now_ts,
                    loc_val,
                    notes_val,
                    img.width,
                    img.height,
                ]

                with open(METADATA_FILE, mode="a", newline="", encoding="utf-8") as f:
                    writer = csv.writer(f)
                    writer.writerow(new_row)

                st.session_state["session_collected_count"] += 1
                st.session_state["last_saved_sample"] = generated_name
                st.toast(f"Saved {generated_name}!", icon="✅")
                st.rerun()
        else:
            st.info("Take a photo with the camera or upload a file to preview and save.")

    # ── Counter Dashboard & Breakdown ─────────────────────────────────────────
    render_html("<div style='height:16px'></div>")
    section_header("📊", "Collection Counter & Class Balance")

    c_chart, c_table = st.columns([1.2, 1])

    with c_chart:
        chart_series = pd.Series(class_counts, name="Samples")
        st.bar_chart(chart_series, color="#2ee59d")

    with c_table:
        summary_rows = [
            {"Class": c.capitalize(), "Samples": class_counts[c]}
            for c in CLASSES
        ]
        st.dataframe(pd.DataFrame(summary_rows), hide_index=True, use_container_width=True)

    # ── Recent Samples & Download ─────────────────────────────────────────────
    if not df_meta.empty:
        section_header("🗂️", f"Collected Samples Log ({len(df_meta)})")
        rev_df = df_meta.iloc[::-1]
        st.dataframe(rev_df, hide_index=True, use_container_width=True)

        d1, d2 = st.columns([2, 3])
        with d1:
            csv_data = df_meta.to_csv(index=False).encode("utf-8")
            st.download_button(
                label="⬇️ Download metadata.csv",
                data=csv_data,
                file_name=f"paddy_collection_metadata_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
                mime="text/csv",
                use_container_width=True,
            )
