"""
about_page.py  –  About & System Architecture page for AgriVision Paddy Inspector.

Step 11 features:
  • System Overview & Edge AI architecture
  • Hardware & Raspberry Pi readiness details
  • Diagnostic checklist (Model presence, SQLite schema, library versions)
  • Agricultural guidelines reference & official disclaimers
"""

import os
import platform
import sys
from pathlib import Path

import cv2
import numpy as np
import streamlit as st
import tflite_runtime.interpreter as tflite  # or standard import check

from core.strings import t
from core.theme import apply_theme, section_header
from history_db import get_schema_version

_PROJECT_ROOT = Path(__file__).resolve().parent.parent
MODEL_PATH = Path(__file__).resolve().parent / "paddy_int8.tflite"
LABELS_PATH = Path(__file__).resolve().parent / "labels.txt"


def show_about_page() -> None:
    apply_theme()
    lang = st.session_state.get("lang", "en")

    section_header("ℹ️", t("nav_about", lang).replace("ℹ️", "").strip() or "About AgriVision")

    st.markdown(
        '<div style="color:#8ab89a;font-size:0.95em;'
        'font-family:Poppins,sans-serif;margin-bottom:20px;line-height:1.6;">'
        "<b>AgriVision Paddy Inspector</b> is an edge-first, offline-capable smart agriculture "
        "decision support system designed for smallholder farmers, agronomists, and extension workers. "
        "It integrates quantized deep learning inference with classical computer vision to detect, "
        "quantify, and manage foliar rice diseases directly in the field."
        "</div>",
        unsafe_allow_html=True,
    )

    # ── High Level Architecture Cards ─────────────────────────────────────────
    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown(
            """
            <div style="background:#12301f;border:1px solid #1e4d30;border-radius:14px;padding:18px;min-height:220px;">
              <div style="font-size:1.8em;margin-bottom:8px;">🧠</div>
              <div style="color:#2ee59d;font-weight:700;font-size:1.05em;margin-bottom:6px;">Edge AI Classifier</div>
              <div style="color:#b8d4c0;font-size:0.85em;line-height:1.5;">
                Fully INT8-quantized MobileNetV2 architecture compiled for micro-edge runtimes.
                Evaluates Blast, BLB, Brown Spot, and Healthy leaves with sub-50ms inference.
              </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with c2:
        st.markdown(
            """
            <div style="background:#12301f;border:1px solid #1e4d30;border-radius:14px;padding:18px;min-height:220px;">
              <div style="font-size:1.8em;margin-bottom:8px;">🔬</div>
              <div style="color:#2ee59d;font-weight:700;font-size:1.05em;margin-bottom:6px;">OpenCV Lesion Severity</div>
              <div style="color:#b8d4c0;font-size:0.85em;line-height:1.5;">
                Classical color-space segmentation in HSV. Isolates necrotic lesions and computes
                exact affected leaf surface area %, benchmarking against the IRRI SES (0–9) standard.
              </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with c3:
        st.markdown(
            """
            <div style="background:#12301f;border:1px solid #1e4d30;border-radius:14px;padding:18px;min-height:220px;">
              <div style="font-size:1.8em;margin-bottom:8px;">📴</div>
              <div style="color:#2ee59d;font-weight:700;font-size:1.05em;margin-bottom:6px;">Zero Cloud Dependency</div>
              <div style="color:#b8d4c0;font-size:0.85em;line-height:1.5;">
                100% local SQLite storage for inspection records, image history, and field dataset
                collection. Offline Telegram queue automatically syncs alerts when cellular connectivity resumes.
              </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)

    # ── Raspberry Pi & Field Hardware Guide ────────────────────────────────────
    section_header("🍓", "Raspberry Pi & Field Hardware Deployment")

    st.markdown(
        """
        <div style="background:#12301f;border:1px solid #1e4d30;border-radius:14px;padding:20px;font-family:Poppins,sans-serif;">
          <div style="color:#2ee59d;font-weight:600;margin-bottom:8px;">Recommended Hardware Stack:</div>
          <ul style="color:#b8d4c0;font-size:0.88em;line-height:1.8;margin-bottom:12px;">
            <li><b>Single Board Computer:</b> Raspberry Pi 4 Model B (2GB/4GB) or Raspberry Pi 5.</li>
            <li><b>Operating System:</b> Raspberry Pi OS (64-bit Bookworm / Bullseye).</li>
            <li><b>Camera:</b> Raspberry Pi Camera Module 3 (Wide/Standard) or any UVC Plug-and-Play USB webcam.</li>
            <li><b>Power Supply:</b> 5V / 3A USB-C Power Bank (provides 6–8 hours of active field mobility).</li>
            <li><b>Enclosure:</b> 3D-printed handheld grip with diffuser ring light for shadow-free leaf illumination.</li>
          </ul>
          <div style="color:#8ab89a;font-size:0.84em;">
            💡 <i>Install via <code>requirements_pi.txt</code> using prebuilt wheels for ARM64 without heavy compilation steps.</i>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)

    # ── System & Diagnostic Status ────────────────────────────────────────────
    section_header("⚙️", "Environment Diagnostics")

    model_found = MODEL_PATH.exists()
    model_size_mb = f"{MODEL_PATH.stat().st_size / (1024 * 1024):.2f} MB" if model_found else "Missing"
    labels_found = LABELS_PATH.exists()
    schema_ver = get_schema_version()

    diag_data = [
        {"Component": "Operating System", "Status": "Active", "Detail": f"{platform.system()} {platform.release()} ({platform.machine()})"},
        {"Component": "Python Version", "Status": "Active", "Detail": sys.version.split()[0]},
        {"Component": "Streamlit Engine", "Status": "Active", "Detail": st.__version__},
        {"Component": "OpenCV Runtime", "Status": "Active", "Detail": cv2.__version__},
        {"Component": "INT8 Quantized Model", "Status": "Ready" if model_found else "Error", "Detail": f"{MODEL_PATH.name} ({model_size_mb})"},
        {"Component": "Disease Class Labels", "Status": "Ready" if labels_found else "Default", "Detail": f"{LABELS_PATH.name}"},
        {"Component": "SQLite Database Schema", "Status": "Healthy", "Detail": f"Version {schema_ver} (inspection_history.db)"},
    ]

    st.dataframe(diag_data, hide_index=True, use_container_width=True)

    # ── Official Agricultural Disclaimer ──────────────────────────────────────
    st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)
    section_header("📜", "Agricultural Advisory & Scientific Disclaimer")

    st.markdown(
        """
        <div style="background:rgba(255,209,102,0.06);border-left:4px solid #ffd166;border-radius:10px;padding:16px 20px;">
          <div style="color:#ffd166;font-weight:700;font-size:0.95em;margin-bottom:6px;">Important Decision Support Notice</div>
          <div style="color:#eaf4ec;font-size:0.86em;line-height:1.7;">
            The diagnoses, severity classifications, and management recommendations surfaced by this system are
            intended strictly for <b>preliminary screening and decision support</b>.
            Chemical dosages, biological treatments, and application schedules must comply with the current
            <b>Tamil Nadu Agricultural University (TNAU) Crop Production Guide</b>, <b>ICAR-NRRI</b> bulletins,
            and local government agricultural extension advisory officers.
            Always confirm symptoms with certified crop health experts before chemical intervention.
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
