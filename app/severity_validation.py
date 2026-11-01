"""
severity_validation.py  –  Severity Validation & IRRI Benchmark Helper.

Step 9 features:
  • Manual IRRI SES (Standard Evaluation System) score entry (0-9 scale)
  • Pairing with automated OpenCV device severity measurements
  • Interactive scatter plots with linear regression fit and 1:1 concordance line
  • Statistical error analysis: Pearson r, Spearman rho, MAE, RMSE, systematic bias
  • Tolerance / concordance breakdown (Underestimating, Concordant, Overestimating)
  • Export validation report to CSV
"""

import math
from datetime import datetime
from pathlib import Path

import altair as alt
import numpy as np
import pandas as pd
import streamlit as st
from PIL import Image
from scipy import stats

from core.theme import apply_theme, section_header, render_html
from history_db import get_inspections
from validation_db import (
    delete_validation,
    get_validations,
    init_validation_table,
    save_validation,
)

_PROJECT_ROOT = Path(__file__).resolve().parent.parent

# IRRI Standard Evaluation System (SES) scale mapping for rice foliar diseases
# Format: score -> (Description, approximate midpoint lesion area %)
IRRI_SES_SCALE = {
    0: ("No lesions observed (0%)", 0.0),
    1: ("Small brown pinhead specks (< 1%)", 0.5),
    2: ("Few small spots (1 - 2%)", 1.5),
    3: ("Small necrotic spots, 1-2 mm (2 - 5%)", 3.5),
    4: ("Enlarged lesions (6 - 10%)", 8.0),
    5: ("Typical spindle lesions, infected area 11 - 25%", 18.0),
    6: ("Lesions coalescing (26 - 35%)", 30.5),
    7: ("Lesions coalescing, infected area 36 - 50%", 43.0),
    8: ("Severe coalescing (51 - 65%)", 58.0),
    9: ("Lesions coalesced, leaf dead / dying (> 65%)", 75.0),
}


def _get_image_preview(image_path: str | None, width: int = 140) -> Image.Image | None:
    if not image_path:
        return None
    full = _PROJECT_ROOT / image_path
    if full.exists():
        try:
            return Image.open(full)
        except Exception:
            return None
    return None


def show_severity_validation() -> None:
    apply_theme()
    init_validation_table()

    section_header("📐", "Severity Validation Helper")

    render_html(
        '<div style="color:#8ab89a;font-size:0.88em;'
        'font-family:Poppins,sans-serif;margin-bottom:18px;">'
        "Benchmark the automated OpenCV leaf lesion severity against the "
        "<b>IRRI Standard Evaluation System (SES)</b> (0–9 scale) and expert manual assessments. "
        "Calculate correlation, Mean Absolute Error (MAE), and systematic bias."
        "</div>"
    )

    # ── IRRI Reference Guide (Expander) ───────────────────────────────────────
    with st.expander("📖 IRRI SES (Standard Evaluation System) Reference Scale", expanded=False):
        render_html(
            '<div style="color:#eaf4ec;font-size:0.9em;line-height:1.7;">'
            "The International Rice Research Institute (IRRI) SES uses a 0–9 ordinal rating "
            "for leaf blast, bacterial blight, and brown spot based on relative leaf area affected:"
            "</div>"
        )
        scale_rows = [
            {"IRRI Score": k, "Description & Range": v[0], "Benchmark Midpoint": f"{v[1]}%"}
            for k, v in IRRI_SES_SCALE.items()
        ]
        st.dataframe(pd.DataFrame(scale_rows), hide_index=True, use_container_width=True)

    # ── Entry Form: Pair a Scan or Add Validation ─────────────────────────────
    render_html("<div style='height:8px'></div>")
    section_header("📝", "Record Validation Benchmark Pair")

    tab_from_hist, tab_direct = st.tabs(["📂 Select from Scan History", "✍️ Direct Manual Entry"])

    # Load history inspections for dropdown
    inspections = []
    try:
        inspections = get_inspections()
    except Exception:
        pass

    with tab_from_hist:
        if not inspections:
            st.info("No scan history records found yet. Use Direct Manual Entry or perform a scan first.")
        else:
            hist_options = {}
            for r in inspections:
                r_id = r.get("id")
                r_dis = r.get("disease", "Unknown")
                r_sev = r.get("severity")
                r_sev_str = f"{float(r_sev):.1f}%" if r_sev is not None else "N/A"
                r_ts = str(r.get("inspected_at", ""))[:16]
                hist_options[f"#{r_id} — {r_dis} (Device: {r_sev_str}) · {r_ts}"] = r

            selected_key = st.selectbox("Choose a past inspection to validate:", list(hist_options.keys()))
            selected_rec = hist_options[selected_key]

            col_preview, col_inputs = st.columns([1, 2.5])

            with col_preview:
                img_path = selected_rec.get("image_path")
                pil_prev = _get_image_preview(img_path)
                if pil_prev:
                    st.image(pil_prev, caption=f"Scan #{selected_rec.get('id')}", use_container_width=True)
                else:
                    render_html(
                        '<div style="width:100%;height:130px;background:#1a3d28;border-radius:8px;'
                        'display:flex;align-items:center;justify-content:center;color:#5a7a65;'
                        'font-size:2em;">🌿</div>'
                    )

            with col_inputs:
                c1, c2, c3 = st.columns(3)
                dev_sev = selected_rec.get("severity") or 0.0
                with c1:
                    st.metric("Device Severity", f"{float(dev_sev):.1f}%", selected_rec.get("severity_grade") or "")
                with c2:
                    irri_score = st.selectbox(
                        "IRRI SES Score (0–9)",
                        options=list(range(10)),
                        index=min(int(math.ceil(dev_sev / 10)), 9) if dev_sev > 0 else 0,
                        help="Standard IRRI 0-9 visual rating",
                        key="hist_irri_sel",
                    )
                with c3:
                    irri_mid = IRRI_SES_SCALE[irri_score][1]
                    man_pct = st.number_input(
                        "Manual Visual Severity (%)",
                        min_value=0.0,
                        max_value=100.0,
                        value=float(irri_mid),
                        step=0.5,
                        help="Exact manual visual lesion area percentage",
                        key="hist_man_pct",
                    )

                c_eval, c_note = st.columns([1, 2])
                with c_eval:
                    eval_name = st.text_input("Evaluator Name", "Agronomist / Expert", key="hist_eval")
                with c_note:
                    val_notes = st.text_input("Validation Notes", "", key="hist_notes")

                if st.button("💾 Save Validation Pair", type="primary", key="save_from_hist"):
                    save_validation(
                        device_severity=float(dev_sev),
                        manual_irri_score=irri_score,
                        manual_severity_pct=man_pct,
                        inspection_id=selected_rec.get("id"),
                        disease_class=selected_rec.get("disease"),
                        evaluator_name=eval_name,
                        notes=val_notes,
                        image_path=selected_rec.get("image_path"),
                    )
                    st.toast("Validation pair recorded!", icon="✅")
                    st.rerun()

    with tab_direct:
        cd1, cd2, cd3 = st.columns(3)
        with cd1:
            direct_dev_sev = st.number_input("Device Severity (%)", 0.0, 100.0, 12.5, step=0.5, key="dir_dev")
        with cd2:
            direct_irri = st.selectbox("Manual IRRI Score", options=list(range(10)), index=3, key="dir_irri")
        with cd3:
            direct_man_pct = st.number_input(
                "Manual Visual %", 0.0, 100.0, float(IRRI_SES_SCALE[3][1]), step=0.5, key="dir_pct"
            )

        cd_dis, cd_eval, cd_notes = st.columns(3)
        with cd_dis:
            direct_dis = st.selectbox("Disease Class", ["blast", "blb", "brown_spot", "healthy", "other"], key="dir_dis")
        with cd_eval:
            direct_eval = st.text_input("Evaluator", "Field Researcher", key="dir_eval")
        with cd_notes:
            direct_notes = st.text_input("Notes", "Calibration test", key="dir_notes")

        if st.button("💾 Save Direct Validation Pair", type="primary", key="save_direct"):
            save_validation(
                device_severity=direct_dev_sev,
                manual_irri_score=direct_irri,
                manual_severity_pct=direct_man_pct,
                disease_class=direct_dis,
                evaluator_name=direct_eval,
                notes=direct_notes,
            )
            st.toast("Direct validation recorded!", icon="✅")
            st.rerun()

    # ── Load Validations & Statistical Analysis ──────────────────────────────
    validations = get_validations()

    render_html("<div style='height:16px'></div>")
    section_header("📊", f"Validation Analytics ({len(validations)} pairs recorded)")

    if len(validations) < 2:
        st.info(
            "Record at least 2 validation pairs above to generate correlation charts, "
            "scatter plots, and error metrics."
        )
        if validations:
            st.dataframe(pd.DataFrame(validations), use_container_width=True, hide_index=True)
        return

    df_val = pd.DataFrame(validations)
    df_val["device_severity"] = pd.to_numeric(df_val["device_severity"], errors="coerce")
    df_val["manual_irri_score"] = pd.to_numeric(df_val["manual_irri_score"], errors="coerce")
    df_val["manual_severity_pct"] = pd.to_numeric(df_val["manual_severity_pct"], errors="coerce")

    # If manual_severity_pct is null, fill with IRRI midpoint
    df_val["effective_manual_pct"] = df_val["manual_severity_pct"].fillna(
        df_val["manual_irri_score"].map(lambda s: IRRI_SES_SCALE.get(s, (None, 0.0))[1])
    )

    # Statistical metrics
    x_dev = df_val["device_severity"].values
    y_irri = df_val["manual_irri_score"].values
    y_man = df_val["effective_manual_pct"].values

    # Pearson correlation
    pearson_r, pearson_p = stats.pearsonr(x_dev, y_man) if len(df_val) >= 2 else (0.0, 1.0)
    spearman_rho, _ = stats.spearmanr(x_dev, y_irri) if len(df_val) >= 2 else (0.0, 1.0)

    # Errors
    errors = x_dev - y_man
    mae = float(np.mean(np.abs(errors)))
    rmse = float(np.sqrt(np.mean(errors ** 2)))
    bias = float(np.mean(errors))  # positive = device overestimates, negative = underestimates

    # ── Metrics Cards ─────────────────────────────────────────────────────────
    m1, m2, m3, m4, m5 = st.columns(5)
    m1.metric("Pearson r", f"{pearson_r:.3f}", f"R² = {pearson_r**2:.3f}")
    m2.metric("Spearman ρ", f"{spearman_rho:.3f}", "Rank correlation")
    m3.metric("MAE", f"{mae:.2f}%", "Mean Abs Error")
    m4.metric("RMSE", f"{rmse:.2f}%", "Root Mean Sq Err")

    bias_sign = "+" if bias > 0 else ""
    bias_label = "Overestimating" if bias > 0.5 else ("Underestimating" if bias < -0.5 else "Neutral")
    m5.metric("Systematic Bias", f"{bias_sign}{bias:.2f}%", bias_label)

    # ── Scatter Plots ─────────────────────────────────────────────────────────
    render_html("<div style='height:8px'></div>")
    plot_col1, plot_col2 = st.columns(2)

    with plot_col1:
        render_html(
            '<div style="font-family:Poppins,sans-serif;font-weight:600;color:#2ee59d;'
            'font-size:0.95em;margin-bottom:6px;">📈 Device Severity (%) vs Manual IRRI Score</div>'
        )

        # Altair chart with regression trendline
        base1 = alt.Chart(df_val).encode(
            x=alt.X("device_severity:Q", title="Device Severity (%)", scale=alt.Scale(zero=True)),
            y=alt.Y("manual_irri_score:Q", title="Manual IRRI SES Score (0–9)", scale=alt.Scale(domain=[0, 9])),
        )
        points1 = base1.mark_circle(size=80, color="#2ee59d", opacity=0.85).encode(
            tooltip=["id:N", "disease_class:N", "device_severity:Q", "manual_irri_score:Q", "evaluator_name:N"]
        )
        trend1 = base1.transform_regression("device_severity", "manual_irri_score").mark_line(
            color="#ffd166", strokeWidth=2
        )
        chart1 = (points1 + trend1).properties(height=320)
        st.altair_chart(chart1, use_container_width=True)

    with plot_col2:
        render_html(
            '<div style="font-family:Poppins,sans-serif;font-weight:600;color:#2ee59d;'
            'font-size:0.95em;margin-bottom:6px;">🎯 Device Severity (%) vs Manual Visual (%) [1:1 Concordance]</div>'
        )

        # Max axis bound
        max_bound = max(max(x_dev), max(y_man), 10.0) * 1.05
        df_diag = pd.DataFrame({"x": [0, max_bound], "y": [0, max_bound]})
        diag_line = alt.Chart(df_diag).mark_line(
            strokeDash=[4, 4], color="#8ab89a", strokeWidth=1.5
        ).encode(x="x:Q", y="y:Q")

        base2 = alt.Chart(df_val).encode(
            x=alt.X("device_severity:Q", title="Device Computed Severity (%)", scale=alt.Scale(domain=[0, max_bound])),
            y=alt.Y("effective_manual_pct:Q", title="Manual Visual Severity (%)", scale=alt.Scale(domain=[0, max_bound])),
        )
        points2 = base2.mark_circle(size=80, color="#2ee59d", opacity=0.85).encode(
            tooltip=["id:N", "disease_class:N", "device_severity:Q", "effective_manual_pct:Q", "evaluator_name:N"]
        )
        trend2 = base2.transform_regression("device_severity", "effective_manual_pct").mark_line(
            color="#ff5d5d", strokeWidth=2
        )
        chart2 = (diag_line + points2 + trend2).properties(height=320)
        st.altair_chart(chart2, use_container_width=True)

    # ── Concordance & Tolerance Analysis ─────────────────────────────────────
    render_html("<div style='height:8px'></div>")
    section_header("⚖️", "Error & Concordance Breakdown")

    tolerance = 5.0  # +/- 5% error tolerance
    concordant = int((np.abs(errors) <= tolerance).sum())
    over_est = int((errors > tolerance).sum())
    under_est = int((errors < -tolerance).sum())
    total_v = len(df_val)

    c_box1, c_box2, c_box3 = st.columns(3)
    c_box1.metric("Concordant (within ±5%)", f"{concordant}/{total_v}", f"{concordant/total_v*100:.1f}%")
    c_box2.metric("Device Overestimating (> +5%)", f"{over_est}/{total_v}", f"{over_est/total_v*100:.1f}%")
    c_box3.metric("Device Underestimating (< -5%)", f"{under_est}/{total_v}", f"{under_est/total_v*100:.1f}%")

    # ── Validations Data Table & Deletion ─────────────────────────────────────
    section_header("📋", "Validation Records Log")

    display_cols = {
        "id": "ID",
        "created_at": "Timestamp",
        "disease_class": "Class",
        "device_severity": "Device %",
        "manual_irri_score": "IRRI Score",
        "effective_manual_pct": "Manual %",
        "evaluator_name": "Evaluator",
        "notes": "Notes",
    }
    avail_cols = [c for c in display_cols if c in df_val.columns]
    show_df = df_val[avail_cols].rename(columns=display_cols)
    st.dataframe(show_df, hide_index=True, use_container_width=True)

    c_del, c_dl = st.columns([1.5, 2.5])
    with c_del:
        val_to_del = st.number_input("Delete Validation ID", min_value=1, step=1, value=int(df_val["id"].iloc[0]))
        if st.button("🗑️ Delete Validation Record", type="secondary"):
            if delete_validation(val_to_del):
                st.success(f"Validation record #{val_to_del} removed.")
                st.rerun()
            else:
                st.warning("Record ID not found.")

    with c_dl:
        csv_bytes = df_val.to_csv(index=False).encode("utf-8")
        st.download_button(
            label="⬇️ Download Validation Report (CSV)",
            data=csv_bytes,
            file_name=f"agrivision_severity_validation_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
            mime="text/csv",
            use_container_width=True,
        )
