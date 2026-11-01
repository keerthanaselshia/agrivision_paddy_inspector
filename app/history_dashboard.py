"""
history_dashboard.py  –  Inspection History page for AgriVision Paddy Inspector.

Step 6 additions:
  • Thumbnail grid view (cards with image thumbnails + key stats)
  • Grid / List toggle
  • Detail view (click a record → full image, all data, HTML report)
  • Delete one / delete selected
  • CSV export (existing) + single-scan HTML report download (new)

Dark smart-agriculture theme. All data via history_db.
"""

import base64
import io
import json
from datetime import datetime
from pathlib import Path

import pandas as pd
import streamlit as st
from PIL import Image

from history_db import (
    get_inspections,
    get_inspection_by_id,
    delete_inspection,
    delete_inspections,
    get_schema_version,
)
from core.theme import apply_theme, section_header, render_html
try:
    from core.advisory import ADVICE
except ImportError:
    from app.core.advisory import ADVICE

# Root of the project (one level above app/)
_PROJECT_ROOT = Path(__file__).resolve().parent.parent

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _safe_col(df: pd.DataFrame, col: str, default=None) -> pd.Series:
    if col in df.columns:
        return df[col]
    return pd.Series([default] * len(df), index=df.index)


def _severity_dot(grade: str) -> str:
    _DOTS = {
        "Very low (monitor)": "🟢",
        "Moderate":           "🟡",
        "High":               "🟠",
        "Severe (urgent)":    "🔴",
    }
    return _DOTS.get(grade, "⚪")


def _thumb_b64(image_path: str | None, size: int = 120) -> str | None:
    """Load the saved image, return a base-64 PNG thumbnail string, or None."""
    if not image_path:
        return None
    full = _PROJECT_ROOT / image_path
    if not full.exists():
        return None
    try:
        img = Image.open(full).convert("RGB")
        img.thumbnail((size, size))
        buf = io.BytesIO()
        img.save(buf, format="PNG")
        return base64.b64encode(buf.getvalue()).decode()
    except Exception:
        return None


def _full_img_b64(image_path: str | None) -> str | None:
    """Return base-64 encoded JPEG for detail view, or None."""
    if not image_path:
        return None
    full = _PROJECT_ROOT / image_path
    if not full.exists():
        return None
    try:
        buf = io.BytesIO()
        Image.open(full).convert("RGB").save(buf, format="JPEG", quality=90)
        return base64.b64encode(buf.getvalue()).decode()
    except Exception:
        return None


def _html_report(rec: dict) -> str:
    """Generate a standalone HTML report for one inspection."""
    ts  = rec.get("inspected_at", "")
    dis = rec.get("disease", "—")
    con = rec.get("confidence")
    sev = rec.get("severity")
    gr  = rec.get("severity_grade", "—")
    src = rec.get("source", "—")
    loc = rec.get("location", "—")
    mod = rec.get("model_version", "—")
    unc = "Yes" if rec.get("uncertain") else "No"

    # Probabilities
    probs_html = ""
    try:
        probs = json.loads(rec.get("probabilities_json") or "[]")
        if probs:
            labels = ["blast", "blb", "brown_spot", "healthy", "other"]
            rows = "".join(
                f"<tr><td>{labels[i] if i < len(labels) else i}</td>"
                f"<td>{float(p)*100:.1f}%</td></tr>"
                for i, p in enumerate(probs)
            )
            probs_html = f"<h3>Class Probabilities</h3><table>{rows}</table>"
    except Exception:
        pass

    # Thumbnail
    img_html = ""
    b64 = _full_img_b64(rec.get("image_path"))
    if b64:
        img_html = f'<img src="data:image/jpeg;base64,{b64}" style="max-width:400px;border-radius:12px;margin:12px 0;">'

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>AgriVision Report – {dis}</title>
<style>
  body{{font-family:Segoe UI,Arial,sans-serif;background:#0b1f14;color:#eaf4ec;padding:32px;}}
  h1{{color:#2ee59d;margin-bottom:4px;}}
  h3{{color:#8ab89a;margin-top:24px;}}
  table{{border-collapse:collapse;width:100%;max-width:500px;}}
  td{{padding:8px 14px;border-bottom:1px solid #1e4d30;}}
  td:first-child{{color:#8ab89a;font-weight:600;}}
  .badge{{display:inline-block;padding:4px 14px;border-radius:20px;
          font-weight:700;background:rgba(46,229,157,0.15);color:#2ee59d;}}
  .footer{{margin-top:40px;font-size:0.8em;color:#5a7a65;}}
</style>
</head>
<body>
<h1>🌿 AgriVision Paddy Inspector</h1>
<p style="color:#5a7a65;margin-top:0;">Inspection Report</p>
{img_html}
<h3>Summary</h3>
<table>
  <tr><td>Inspection time</td><td>{ts}</td></tr>
  <tr><td>Predicted class</td><td><span class="badge">{dis}</span></td></tr>
  <tr><td>Confidence</td><td>{f"{float(con):.1f}%" if con else "—"}</td></tr>
  <tr><td>Severity</td><td>{f"{float(sev):.1f}%" if sev else "—"}</td></tr>
  <tr><td>Severity grade</td><td>{gr}</td></tr>
  <tr><td>Uncertain</td><td>{unc}</td></tr>
  <tr><td>Source</td><td>{src}</td></tr>
  <tr><td>Location</td><td>{loc}</td></tr>
  <tr><td>Model</td><td>{mod}</td></tr>
</table>
{probs_html}
<p class="footer">Generated by AgriVision Paddy Inspector &nbsp;·&nbsp; {datetime.now().strftime("%Y-%m-%d %H:%M")}</p>
</body>
</html>"""


# ---------------------------------------------------------------------------
# Grid view
# ---------------------------------------------------------------------------

def _grid_view(filtered: pd.DataFrame) -> None:
    """Render a thumbnail card grid. Clicking 'Details' opens the detail panel."""
    cols_per_row = 3
    records = filtered.to_dict("records")

    for row_start in range(0, len(records), cols_per_row):
        row_recs = records[row_start : row_start + cols_per_row]
        cols = st.columns(cols_per_row)
        for col, rec in zip(cols, row_recs):
            with col:
                thumb = _thumb_b64(rec.get("image_path"), size=160)
                if thumb:
                    render_html(
                        f'<img src="data:image/png;base64,{thumb}" '
                        f'style="width:100%;border-radius:10px;'
                        f'border:2px solid #1e4d30;margin-bottom:6px;">'
                    )
                else:
                    render_html(
                        '<div style="width:100%;height:120px;background:#1a3d28;'
                        'border-radius:10px;display:flex;align-items:center;'
                        'justify-content:center;color:#5a7a65;font-size:2em;'
                        'margin-bottom:6px;">🌿</div>'
                    )

                dis = rec.get("disease", "—")
                gr  = rec.get("severity_grade") or "—"
                dot = _severity_dot(gr)
                ts  = str(rec.get("inspected_at", ""))[:16]
                con = rec.get("confidence")
                con_str = f"{float(con):.0f}%" if con else "—"

                render_html(
                    f'<div style="font-family:Poppins,sans-serif;">'
                    f'<div style="font-weight:700;color:#eaf4ec;font-size:0.95em;">{dis}</div>'
                    f'<div style="font-size:0.78em;color:#8ab89a;">{ts}</div>'
                    f'<div style="font-size:0.82em;color:#b8d4c0;">'
                    f'{dot} {gr} &nbsp;·&nbsp; conf {con_str}</div>'
                    f'</div>'
                )

                rid = int(rec["id"])
                if st.button("🔍 Details", key=f"detail_{rid}"):
                    st.session_state["_detail_id"] = rid
                    st.rerun()

                if st.button("🗑️", key=f"del_grid_{rid}", help="Delete this record"):
                    delete_inspection(rid)
                    st.success("Deleted.")
                    st.rerun()


# ---------------------------------------------------------------------------
# Detail panel
# ---------------------------------------------------------------------------

def _detail_panel(rec_id: int) -> None:
    """Show a full-screen detail card for one inspection record."""
    rec = get_inspection_by_id(rec_id)
    if rec is None:
        st.warning(f"Record #{rec_id} not found.")
        if st.button("← Back"):
            st.session_state.pop("_detail_id", None)
            st.rerun()
        return

    if st.button("← Back to history"):
        st.session_state.pop("_detail_id", None)
        st.rerun()

    section_header("🔍", f"Inspection #{rec_id} — {rec.get('disease','—')}")

    # Image
    b64 = _full_img_b64(rec.get("image_path"))
    if b64:
        render_html(
            f'<img src="data:image/jpeg;base64,{b64}" '
            f'style="max-width:480px;width:100%;border-radius:14px;'
            f'border:2px solid #1e4d30;margin-bottom:18px;">'
        )
    else:
        st.info("No saved image for this record.")

    # Key stats
    m1, m2, m3, m4 = st.columns(4)
    gr   = rec.get("severity_grade") or "—"
    sev  = rec.get("severity")
    con  = rec.get("confidence")
    m1.metric("Disease",   rec.get("disease", "—"))
    m2.metric("Confidence", f"{float(con):.1f}%" if con else "—")
    m3.metric("Severity",   f"{float(sev):.1f}%" if sev else "—")
    m4.metric("Grade",      f"{_severity_dot(gr)} {gr}")

    # Full data table
    with st.expander("📋 Full record data", expanded=False):
        rows = {k: str(v) for k, v in rec.items() if k not in ("probabilities_json", "image_path")}
        st.table(pd.DataFrame(rows.items(), columns=["Field", "Value"]))

    # Probabilities chart
    try:
        probs = json.loads(rec.get("probabilities_json") or "[]")
        if probs:
            labels = ["blast", "blb", "brown_spot", "healthy", "other"]
            with st.expander("📊 Class probabilities"):
                st.bar_chart(
                    {(labels[i] if i < len(labels) else str(i)): float(p) * 100
                     for i, p in enumerate(probs)},
                    color="#2ee59d",
                )
    except Exception:
        pass

    # Q&A Conversation History
    qa_json_str = rec.get("qa_history_json")
    if qa_json_str:
        try:
            qa_list = json.loads(qa_json_str)
            if qa_list:
                with st.expander(f"💬 Q&A History ({len(qa_list)} conversation turn{'s' if len(qa_list) > 1 else ''})", expanded=True):
                    for item in qa_list:
                        q_txt = item.get("question", "")
                        a_txt = item.get("answer", "")
                        st.markdown(f"<div style='color:#ffd166;font-weight:600;'>🧑‍🌾 Q: {q_txt}</div>", unsafe_allow_html=True)
                        st.markdown(f"<div style='color:#eaf4ec;margin-top:4px;margin-bottom:12px;background:#1a3d28;padding:8px 12px;border-radius:8px;'>🤖 {a_txt}</div>", unsafe_allow_html=True)
        except Exception:
            pass

    # Symptoms and Prevention Guide for stored disease
    dis_name = str(rec.get("disease", "")).strip().lower()
    dis_key = None
    for k in ADVICE:
        if k == dis_name or ADVICE[k].get("name", "").lower() == dis_name:
            dis_key = k
            break
    if not dis_key:
        if "blast" in dis_name:
            dis_key = "blast"
        elif "blb" in dis_name or "bacterial" in dis_name:
            dis_key = "blb"
        elif "brown" in dis_name or "spot" in dis_name:
            dis_key = "brown_spot"
        elif "tungro" in dis_name:
            dis_key = "tungro"
        elif "sheath" in dis_name:
            dis_key = "sheath_blight"
        elif "smut" in dis_name:
            dis_key = "false_smut"
        elif "healthy" in dis_name:
            dis_key = "healthy"
        else:
            dis_key = "other"

    cur_lang = st.session_state.get("lang", "en")
    if dis_key and dis_key in ADVICE:
        dis_info = ADVICE[dis_key]
        def _dis_field(base_k: str):
            return dis_info.get(f"{base_k}_{cur_lang}") or dis_info.get(f"{base_k}_en") or dis_info.get(f"{base_k}_ta") or ""

        with st.expander(f"🌾 Symptoms & Prevention Guide ({dis_info.get('name', dis_key)})", expanded=True):
            sym_l = _dis_field("symptoms_leaf")
            chk_items = _dis_field("how_to_check")
            p_plant = _dis_field("prevention_before_planting")
            p_crop = _dis_field("prevention_during_crop")
            p_harv = _dis_field("prevention_after_harvest")
            p_limit = _dis_field("prevention_to_limit_spread")
            off_call = _dis_field("when_to_call_officer")

            col_s1, col_s2 = st.columns(2)
            with col_s1:
                st.markdown("**🔍 Characteristic Leaf Symptoms:**")
                if isinstance(sym_l, list):
                    for idx_s, s_item in enumerate(sym_l, 1):
                        st.markdown(f"**{idx_s}.** {s_item}")
                else:
                    st.write(sym_l or "—")

                if isinstance(chk_items, list) and chk_items:
                    st.markdown("**📋 Diagnostic Leaf Checklist:**")
                    for chk_txt in chk_items:
                        st.markdown(f"• {chk_txt}")

            with col_s2:
                st.markdown("**🛡️ Multi-Stage Prevention:**")
                st.markdown(f"• **Before Planting:** {p_plant}")
                st.markdown(f"• **During Crop:** {p_crop}")
                st.markdown(f"• **After Harvest:** {p_harv}")
                st.markdown(f"• **To Limit Spread:** {p_limit}")
                if off_call:
                    st.warning(f"🧑‍🌾 **When to Call Officer:** {off_call}")

    # HTML report download
    html_bytes = _html_report(rec).encode("utf-8")
    ts_str = str(rec.get("inspected_at", "report"))[:10]
    st.download_button(
        label="⬇️ Download HTML report",
        data=html_bytes,
        file_name=f"agrivision_report_{rec_id}_{ts_str}.html",
        mime="text/html",
    )

    # Delete
    st.markdown("---")
    if st.button("🗑️ Delete this inspection", type="secondary"):
        delete_inspection(rec_id)
        st.session_state.pop("_detail_id", None)
        st.success(f"Record #{rec_id} deleted.")
        st.rerun()


# ---------------------------------------------------------------------------
# Main dashboard
# ---------------------------------------------------------------------------

def show_history_dashboard() -> None:
    apply_theme()

    # If a detail record is selected, show that instead
    if "detail_id" in st.session_state:
        _detail_panel(st.session_state["detail_id"])
        return
    if "_detail_id" in st.session_state:
        _detail_panel(st.session_state["_detail_id"])
        return

    section_header("📊", "Inspection History")
    render_html(
        '<div style="color:#8ab89a;font-size:0.88em;'
        'font-family:Poppins,sans-serif;margin-bottom:18px;">'
        "All saved paddy leaf inspections. Filter, explore trends, and export."
        "</div>"
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
        render_html(
            '<div style="text-align:center;padding:60px 20px;">'
            '<div style="font-size:3em;">🌿</div>'
            '<div style="color:#8ab89a;font-family:Poppins,sans-serif;'
            'margin-top:12px;font-size:1.05em;">No inspections saved yet.</div>'
            '<div style="color:#5a7a65;font-size:0.85em;margin-top:6px;">'
            "Complete a leaf scan with Auto-save enabled to see records here."
            "</div></div>"
        )
        return

    df = pd.DataFrame(records)
    df["inspected_at"]   = pd.to_datetime(df["inspected_at"],   errors="coerce")
    df["uncertain"]      = _safe_col(df, "uncertain",      0).fillna(0).astype(int)
    df["source"]         = _safe_col(df, "source",         "").fillna("")
    df["model_version"]  = _safe_col(df, "model_version",  "").fillna("")
    df["image_hash"]     = _safe_col(df, "image_hash",     "")
    df["severity_grade"] = _safe_col(df, "severity_grade", "").fillna("")
    df["image_path"]     = _safe_col(df, "image_path",     "")

    # ── Summary metrics ──────────────────────────────────────────────────────
    total           = len(df)
    disease_count   = df["disease"].value_counts()
    valid_sev       = pd.to_numeric(df["severity"],   errors="coerce").dropna()
    uncertain_count = int(df["uncertain"].sum())
    top_class       = disease_count.index[0] if not disease_count.empty else "—"

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Total scans",       total,       "inspections")
    m2.metric("Most common",       top_class)
    m3.metric("Avg severity",
              f"{valid_sev.mean():.1f}%" if not valid_sev.empty else "—")
    m4.metric("Uncertain results", uncertain_count)

    render_html("<div style='height:8px'></div>")

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

    src_count = df["source"].value_counts()
    src_count = src_count[src_count.index != ""]
    if not src_count.empty:
        section_header("📷", "Image source")
        st.bar_chart(src_count, color="#ffd166")

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

    # ── View toggle ──────────────────────────────────────────────────────────
    section_header("🗂️", f"Records — {len(filtered)} match(es)")

    view_col, _ = st.columns([2, 5])
    with view_col:
        view_mode = st.radio(
            "View",
            ["📋 List", "🖼️ Grid"],
            horizontal=True,
            label_visibility="collapsed",
        )

    # ── Bulk delete ──────────────────────────────────────────────────────────
    if not filtered.empty:
        with st.expander("🗑️ Bulk delete selected records"):
            id_options = {f"#{int(r['id'])} — {r['disease']} ({str(r['inspected_at'])[:10]})": int(r["id"])
                          for _, r in filtered.iterrows()}
            to_delete = st.multiselect("Select records to delete", list(id_options.keys()))
            if to_delete and st.button("🗑️ Delete selected", type="secondary"):
                ids = [id_options[k] for k in to_delete]
                n = delete_inspections(ids)
                st.success(f"Deleted {n} record(s).")
                st.rerun()

    # ── Grid or List view ────────────────────────────────────────────────────
    if "Grid" in view_mode:
        _grid_view(filtered)
    else:
        base_cols = {
            "id":             "ID",
            "inspected_at":   "Inspection time",
            "disease":        "Predicted class",
            "confidence":     "Confidence (%)",
            "severity":       "Severity (%)",
            "severity_grade": "Grade",
            "location":       "Location",
            "uncertain":      "Uncertain",
            "source":         "Source",
            "model_version":  "Model",
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

        # Quick detail/delete buttons below list
        sel_id = st.number_input(
            "Enter record ID to view details or delete",
            min_value=1, step=1, value=1,
        )
        btn_col1, btn_col2, _ = st.columns([1, 1, 4])
        with btn_col1:
            if st.button("🔍 View details"):
                st.session_state["_detail_id"] = int(sel_id)
                st.rerun()
        with btn_col2:
            if st.button("🗑️ Delete", type="secondary"):
                if delete_inspection(int(sel_id)):
                    st.success(f"Record #{sel_id} deleted.")
                    st.rerun()
                else:
                    st.warning(f"Record #{sel_id} not found.")

    # ── Export ────────────────────────────────────────────────────────────────
    section_header("💾", "Export")
    csv_bytes = filtered.to_csv(index=False).encode("utf-8")
    st.download_button(
        label="⬇️ Download filtered records (CSV)",
        data=csv_bytes,
        file_name=f"agrivision_history_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
        mime="text/csv",
    )
