r"""AgriVision Paddy Inspector  –  UI entry point.

Run from the project root (C:\Users\keert\paddy_dataset):
    venv2\Scripts\python.exe -m streamlit run app\app.py

Step 5 addition: Disease Library navigation page (disease_library.py).
Content lives in app/data/advisory.json — editable without code changes.
"""

import hashlib
import io
import time
from pathlib import Path

import re
import cv2
import numpy as np
import streamlit as st
from PIL import Image

# ---- core modules ----------------------------------------------------------
from core.classifier  import load_interpreter, classify
from core.severity    import severity, grade
from core.advisory    import ADVICE
from core.reports     import build_text_report
from core.scan_effect import image_to_data_uri, scanning_html
from core.quality     import check_quality
from core.strings     import t
from core.theme       import (
    apply_theme,
    render_header,
    sidebar_logo,
    section_header,
    clean_html,
    render_html,
)
from core.qa_engine   import ask_question, get_example_questions
from core.speech      import render_tts_button, render_mic_button, stop_all_speech
from history_db       import update_inspection_qa


# ---- Model runtime check ---------------------------------------------------
try:
    from tflite_runtime.interpreter import Interpreter
    _runtime_available = True
    _runtime_name = "tflite_runtime"
    _runtime_err = ""
except ImportError:
    try:
        from ai_edge_litert.interpreter import Interpreter
        _runtime_available = True
        _runtime_name = "ai_edge_litert"
        _runtime_err = ""
    except ImportError:
        try:
            from tensorflow.lite.python.interpreter import Interpreter
            _runtime_available = True
            _runtime_name = "tensorflow.lite"
            _runtime_err = ""
        except ImportError as _rt_err:
            Interpreter = None
            _runtime_available = False
            _runtime_name = None
            _runtime_err = str(_rt_err)

# ---- Database (SQLite) initialisation ---------------------------------------
try:
    from history_db import init_db, save_inspection, delete_inspection, delete_inspections
    init_db()
    _db_available = True
    _db_init_msg = ""
except Exception as _db_init_err:
    _db_available = False
    _db_init_msg = str(_db_init_err)

# ---- Navigation page modules ------------------------------------------------
try:
    from history_dashboard   import show_history_dashboard
    from disease_library     import show_disease_library
    from map_page            import show_map_page
    from field_collection    import show_field_collection
    from severity_validation import show_severity_validation
    from about_page          import show_about_page
    _pages_available = True
    _pages_err_msg = ""
except Exception as _p_err:
    _pages_available = False
    _pages_err_msg = str(_p_err)

HERE             = Path(__file__).parent
DEFAULT_LABELS   = ["blast", "blb", "brown_spot", "healthy", "other"]
_MIN_SCAN_S      = 2.0
_GRADE_DOT       = {"Good": "🟢", "Fair": "🟡", "Poor": "🔴"}
HISTORY_IMG_DIR  = HERE.parent / "history" / "images"   # full-quality image store


def _save_history_image(pil_img: "Image.Image", image_hash: str) -> str | None:
    """Save a full-quality JPEG to history/images/ and return the relative path.

    Returns a path string like 'history/images/<hash>.jpg', or None on error.
    """
    try:
        HISTORY_IMG_DIR.mkdir(parents=True, exist_ok=True)
        fname  = f"{image_hash[:32]}.jpg"
        fpath  = HISTORY_IMG_DIR / fname
        if not fpath.exists():
            pil_img.save(fpath, format="JPEG", quality=92)
        return f"history/images/{fname}"
    except Exception:
        return None

# Severity badge: grade string → (emoji, background colour, text colour)
_SEV_BADGE = {
    "Very low (monitor)": ("🟢", "#e8f5e9", "#1b5e20"),
    "Moderate":           ("🟡", "#fff8e1", "#e65100"),
    "High":               ("🟠", "#fff3e0", "#bf360c"),
    "Severe (urgent)":    ("🔴", "#ffebee", "#b71c1c"),
}


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

# _send_telegram moved to telegram_queue.py (Step 10)
from telegram_queue import (
    send_photo_telegram, test_connection, send_test_message,
    get_queue, sync_queue, delete_queued, queue_count,
    init_telegram_queue,
)
init_telegram_queue()


def _load_labels(path):
    p = Path(path)
    if p.exists():
        names = [x.strip() for x in p.read_text(encoding="utf-8").splitlines() if x.strip()]
        if names:
            return names
    return DEFAULT_LABELS


def _quality_card(q: dict) -> None:
    """Render image quality card — dark theme."""
    _DOT = {"Good": "🟢", "Fair": "🟡", "Poor": "🔴"}
    _COL = {"Good": "#2ee59d", "Fair": "#ffd166", "Poor": "#ff5d5d"}
    dot  = _DOT.get(q["grade"], "⚪")
    col  = _COL.get(q["grade"], "#8ab89a")

    with st.container(border=True):
        h_col, score_col, reason_col = st.columns([1.4, 1, 3])
        h_col.metric("Image quality",  f"{dot} {q['grade']}")
        score_col.metric("Score", f"{q['score']} / 100")
        with reason_col:
            if not q["reasons"]:
                render_html(
                    '<div style="color:#2ee59d;font-weight:600;'
                    'font-family:Poppins,sans-serif;padding:10px 0;">'
                    "✔ Image looks good for analysis.</div>"
                )
            else:
                for r in q["reasons"]:
                    st.warning(r, icon="⚠️")

    if q["grade"] == "Poor":
        render_html(
            '<div style="background:rgba(255,93,93,0.10);border-left:4px solid #ff5d5d;'
            'border-radius:12px;padding:12px 18px;color:#ff5d5d;'
            'font-family:Poppins,sans-serif;font-weight:600;font-size:0.9em;">'
            "🔴 Poor image quality — results may be unreliable. "
            "Use a single leaf on a plain background with good lighting."
            "</div>"
        )


def _severity_badge(sev_pct: float) -> None:
    """Show a prominent colour-coded severity badge (dark theme)."""
    g = grade(sev_pct)
    _DARK_SEV = {
        "Very low (monitor)": ("🟢", "rgba(46,229,157,0.12)",  "#2ee59d"),
        "Moderate":           ("🟡", "rgba(255,209,102,0.12)", "#ffd166"),
        "High":               ("🟠", "rgba(255,140,0,0.14)",   "#ff9f43"),
        "Severe (urgent)":    ("🔴", "rgba(255,93,93,0.14)",   "#ff5d5d"),
    }
    dot, bg, fg = _DARK_SEV.get(g, ("⚪", "rgba(255,255,255,0.08)", "#8ab89a"))
    render_html(
        f'<div style="text-align:center;margin:18px 0 8px 0;">'
        f'<span style="display:inline-block;background:{bg};color:{fg};'
        f'border:2px solid {fg};border-radius:24px;padding:10px 32px;'
        f'font-family:\'Poppins\',sans-serif;font-weight:700;font-size:1.1em;'
        f'letter-spacing:0.04em;box-shadow:0 4px 20px {fg}30;">'
        f'{dot}&nbsp; {g}&nbsp;&nbsp;<span style="opacity:0.7;font-size:0.85em;">{sev_pct:.1f}% lesion area</span>'
        f'</span></div>'
    )


def _confidence_meter(label: str, conf: float, conf_min: float) -> None:
    """Show a prominent 0-100% confidence meter."""
    info = ADVICE.get(label, {})
    name = info.get("name", label)
    sci  = info.get("scientific", "")
    is_conf = (conf >= conf_min)
    status_col = "#2ee59d" if is_conf else "#ffd166"
    status_txt = "Confidence threshold met" if is_conf else f"Below threshold ({conf_min}%)"
    status_icon = "✅" if is_conf else "⚠️"

    render_html(
        f'<div style="background:#12301f;border:1px solid #1e4d30;border-radius:14px;padding:16px 20px;margin:12px 0;">'
        f'<div style="display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:10px;">'
        f'<div>'
        f'<div style="color:#8ab89a;font-size:0.80em;text-transform:uppercase;letter-spacing:0.06em;font-weight:700;">Top Detection Result</div>'
        f'<div style="color:#eaf4ec;font-size:1.25em;font-weight:800;margin-top:2px;">{name}'
        + (f' <span style="font-size:0.75em;color:#5a7a65;font-style:italic;font-weight:400;">({sci})</span>' if sci else "") +
        f'</div></div>'
        f'<div style="text-align:right;">'
        f'<div style="font-size:1.6em;font-weight:900;color:{status_col};line-height:1;">{conf:.1f}%'
        f'<span style="font-size:0.55em;color:#8ab89a;font-weight:600;"> / 100%</span></div>'
        f'<div style="color:{status_col};font-size:0.8em;font-weight:600;margin-top:4px;">{status_icon} {status_txt}</div>'
        f'</div></div>'
        f'<div style="background:#0b1f14;border-radius:8px;height:12px;overflow:hidden;margin-top:12px;border:1px solid #1e4d30;">'
        f'<div style="width:{min(max(conf, 0.0), 100.0):.1f}%;background:linear-gradient(90deg, #1db976, {status_col});height:100%;border-radius:6px;box-shadow:0 0 10px {status_col}60;"></div>'
        f'</div>'
        f'</div>'
    )


def _top3_predictions(probs: np.ndarray, labels: list, conf_min: float) -> None:
    """Show top-3 predictions with dark-theme confidence bars."""
    sorted_idx = np.argsort(probs)[::-1][:3]
    section_header("🔬", "Class Probabilities (0–100%)")

    for rank, idx in enumerate(sorted_idx):
        lbl    = labels[idx] if idx < len(labels) else f"class_{idx}"
        p      = float(probs[idx]) * 100
        info   = ADVICE.get(lbl, {})
        name   = info.get("name", lbl)
        sci    = info.get("scientific", "")
        is_1st = (rank == 0)

        bar_col = "#2ee59d" if is_1st else "#1e4d30"
        glow    = "0 0 8px rgba(46,229,157,0.5)" if is_1st else "none"
        txt_col = "#eaf4ec" if is_1st else "#8ab89a"
        width   = max(p, 1.5)

        c_name, c_bar, c_pct = st.columns([2.8, 5, 1.6])
        with c_name:
            render_html(
                f'<div style="font-family:Poppins,sans-serif;font-weight:{"700" if is_1st else "500"};'
                f'color:{txt_col};font-size:{"1em" if is_1st else "0.9em"};">{name}</div>'
                + (f'<div style="font-size:0.74em;color:#5a7a65;font-style:italic;margin-top:2px;">{sci}</div>' if sci else "")
            )
        render_html(
            f'<div style="background:#1a3d28;border-radius:8px;padding:3px;margin-top:10px;">'
            f'<div style="width:{width:.1f}%;background:{bar_col};height:10px;border-radius:6px;box-shadow:{glow};min-width:3px;transition:width 0.4s ease;"></div>'
            f'</div>',
            container=c_bar,
        )
        c_pct.metric("", f"{p:.1f}% / 100%")


def _uncertain_panel(conf_min: int) -> None:
    """Explain the Uncertain state (dark theme)."""
    render_html(
        f'<div style="background:rgba(255,209,102,0.08);border-left:4px solid #ffd166;border-radius:12px;padding:16px 20px;margin:10px 0;font-family:\'Poppins\',sans-serif;">'
        f'<div style="color:#ffd166;font-weight:700;font-size:1em;margin-bottom:8px;">⚠️ Uncertain prediction</div>'
        f'<div style="color:#b8d4c0;font-size:0.9em;line-height:1.6;">The model\'s top confidence is below your threshold (<b style="color:#ffd166;">{conf_min}%</b>).</div>'
        f'<div style="color:#8ab89a;font-size:0.85em;margin-top:10px;line-height:1.8;">'
        f'<b style="color:#b8d4c0;">Common causes:</b><br>&nbsp;· Busy or coloured background &nbsp;· Mixed/early-stage symptoms<br>&nbsp;· Leaf does not fill the frame &nbsp;· Poor lighting or blur<br><br>'
        f'<b style="color:#b8d4c0;">Suggestions:</b><br>&nbsp;· Retake with a single leaf on a plain white surface<br>&nbsp;· Ensure leaf fills ≥ 60% of the frame<br>&nbsp;· Use bright, even lighting — avoid shadows<br>&nbsp;· If problem persists, consult a local agriculture officer'
        f'</div></div>'
    )


def _multi_segment_section(main_sev: float, sat_min: int, hue_max: int) -> float:
    """Show the multi-segment severity expander.

    Returns the average severity across all provided segments.
    The main_sev (from the already-scanned image) is Segment 1 (Base).
    """
    with st.expander("📐 Multi-segment severity (optional — for long paddy blades)"):
        st.caption(
            "Paddy leaves can have different lesion densities at the base, middle "
            "and tip. Upload up to 2 more crops of the same leaf to get an averaged "
            "severity score. Classification is not re-run for extra segments."
        )

        seg_imgs = [None, None]
        c1, c2 = st.columns(2)
        with c1:
            f2 = st.file_uploader(
                "Segment 2 – Middle of leaf",
                type=["jpg", "jpeg", "png"],
                key="seg2",
            )
        with c2:
            f3 = st.file_uploader(
                "Segment 3 – Tip of leaf",
                type=["jpg", "jpeg", "png"],
                key="seg3",
            )

        segs_pct  = [main_sev]
        seg_labels = ["Base (main image)"]

        for i, (fobj, lbl) in enumerate([(f2, "Middle"), (f3, "Tip")]):
            if fobj is not None:
                try:
                    arr = np.array(Image.open(fobj).convert("RGB"))
                    # Resize if very large
                    if max(arr.shape[:2]) > 1280:
                        s   = 1280 / max(arr.shape[:2])
                        arr = cv2.resize(arr, None, fx=s, fy=s,
                                         interpolation=cv2.INTER_AREA)
                    s_pct, _ = severity(arr, sat_min, hue_max)
                    segs_pct.append(s_pct)
                    seg_labels.append(lbl)
                except Exception as exc:
                    st.warning(f"Could not read Segment {i+2}: {exc}")

        # Build results table
        import pandas as pd
        rows = [{"Segment": lbl, "Severity (%)": f"{s:.1f}",
                 "Grade": grade(s)}
                for lbl, s in zip(seg_labels, segs_pct)]
        avg = sum(segs_pct) / len(segs_pct)
        rows.append({"Segment": f"**Average ({len(segs_pct)} segment(s))**",
                     "Severity (%)": f"**{avg:.1f}**",
                     "Grade": f"**{grade(avg)}**"})

        st.dataframe(
            pd.DataFrame(rows),
            hide_index=True,
            use_container_width=True,
        )

        if len(segs_pct) > 1:
            st.info(
                f"Averaged over {len(segs_pct)} segments: **{avg:.1f}%** — {grade(avg)}"
            )

        return avg


# ============================================================= UI ============
st.set_page_config(
    page_title = "AgriVision Paddy Inspector",
    layout     = "wide",
    page_icon  = "🌾",
)
apply_theme()     # inject global CSS (must be first after set_page_config)
render_header()   # branded green gradient banner

if not _db_available:
    st.error(
        "Could not open the inspection database (SQLite). "
        f"History will not be saved this session.\n\nDetail: {_db_init_msg}"
    )

if not _runtime_available:
    st.warning(
        "⚠️ No TensorFlow Lite runtime found (ai-edge-litert, tflite-runtime, or tensorflow). "
        f"Deep learning classification is disabled; severity analysis remains available.\n\nDetail: {_runtime_err}"
    )

if not _pages_available:
    st.error(
        f"Could not load application sub-pages.\n\nDetail: {_pages_err_msg}"
    )

# ---------------------------------------------------------------------------
# Navigation
# ---------------------------------------------------------------------------
sidebar_logo()

# Language selector toggle (English / தமிழ் / Tanglish)
lang_options = ["English", "தமிழ்", "Tanglish"]
cur_lang = st.session_state.get("lang", "en")
cur_idx = 0 if cur_lang == "en" else (1 if cur_lang == "ta" else 2)
lang_choice = st.sidebar.selectbox(
    "🌐 Language / மொழி",
    lang_options,
    index=cur_idx,
    key="app_lang_choice",
)
if lang_choice == "தமிழ்":
    lang = "ta"
elif lang_choice == "Tanglish":
    lang = "tanglish"
else:
    lang = "en"
st.session_state["lang"] = lang

nav_items = [
    t("nav_scan", lang),
    t("nav_library", lang),
    t("nav_history", lang),
    t("nav_map", lang),
    t("nav_collection", lang),
    t("nav_validation", lang),
    t("nav_about", lang),
]

page = st.sidebar.radio(
    "",
    nav_items,
    label_visibility="collapsed",
)
if st.session_state.get("_go_to_library") or "Library" in page or "வழிகாட்டி" in page:
    if st.session_state.get("_go_to_library"):
        st.session_state["_go_to_library"] = False
    show_disease_library()
    st.stop()
if "History" in page or "வரலாறு" in page:
    if _db_available:
        show_history_dashboard()
    else:
        st.error("Database is unavailable.")
    st.stop()
if "Map" in page or "வரைபடம்" in page:
    if _db_available:
        show_map_page()
    else:
        st.error("Database is unavailable.")
    st.stop()
if "Collection" in page or "சேகரிப்பு" in page:
    show_field_collection()
    st.stop()
if "Validation" in page or "சரிபார்ப்பு" in page:
    show_severity_validation()
    st.stop()
if "About" in page or "பற்றி" in page:
    show_about_page()
    st.stop()

# ---------------------------------------------------------------------------
# Sidebar
# ---------------------------------------------------------------------------
with st.sidebar:

    st.header("Settings")
    model_path  = st.text_input("Model file",  str(HERE / "paddy_int8.tflite"))
    labels_path = st.text_input("Labels file", str(HERE / "labels.txt"))
    conf_min    = st.slider("Minimum confidence (%)", 0, 100, 70)

    st.subheader("Severity (OpenCV)")
    sat_min = st.slider("Leaf saturation minimum",         10, 120, 40)
    hue_max = st.slider("Lesion hue below (brown/yellow)", 10,  40, 28)
    crop    = st.slider("Ignore image edges (%)",           0,  40,  0)

    with st.sidebar.expander("Quality check thresholds"):
        q_blur    = st.slider("Min sharpness (Laplacian)", 10, 300, 80)
        q_dark    = st.slider("Min brightness",            10, 100, 50)
        q_bright  = st.slider("Max brightness",           150, 255, 210)
        q_overexp = st.slider("Max over-exposed pixels (%)", 1, 40, 15)
        q_green   = st.slider("Min green leaf area (%)",     1, 30,  5)

    st.subheader("Report")
    location = st.text_input("Location (GPS module comes later)", "Erode, Tamil Nadu")

    st.subheader("Telegram")
    tg_token = st.text_input("Bot token", type="password", key="tg_token")
    tg_chat  = st.text_input("Chat ID", key="tg_chat")

    tg_btn1, tg_btn2 = st.columns(2)
    with tg_btn1:
        if st.button("🔌 Test", use_container_width=True, help="Verify token & chat ID"):
            if tg_token and tg_chat:
                ok, msg = test_connection(tg_token, tg_chat)
                if ok:
                    st.success(msg)
                else:
                    st.error(msg)
            else:
                st.warning("Enter token and chat ID first.")
    with tg_btn2:
        if st.button("💬 Ping", use_container_width=True, help="Send a test text message"):
            if tg_token and tg_chat:
                ok, msg = send_test_message(tg_token, tg_chat)
                if ok:
                    st.success(msg)
                else:
                    st.error(msg)
            else:
                st.warning("Enter token and chat ID first.")

    # Offline queue indicator + Sync
    pending = queue_count()
    if pending > 0:
        render_html(
            f'<div style="background:rgba(255,209,102,0.12);border-left:4px solid #ffd166;'
            f'border-radius:8px;padding:8px 12px;margin:8px 0;font-family:Poppins,sans-serif;'
            f'font-size:0.85em;color:#ffd166;">'
            f'📴 <b>{pending}</b> message(s) queued offline</div>',
            sidebar=True,
        )
        if st.button("🔄 Sync now", use_container_width=True):
            if tg_token and tg_chat:
                sent, failed = sync_queue(tg_token, tg_chat)
                if sent:
                    st.success(f"✅ Synced {sent} message(s).")
                if failed:
                    st.warning(f"⚠️ {failed} message(s) still failed.")
                st.rerun()
            else:
                st.warning("Enter token and chat ID to sync.")

    st.subheader("Auto-save")
    auto_save = st.checkbox("Auto-save results", value=True,
                            help="Save each new scan to the database.")

# ---------------------------------------------------------------------------
# Image input
# ---------------------------------------------------------------------------
tab_up, tab_cam = st.tabs([t("tab_upload", lang), t("tab_camera", lang)])
with tab_up:
    up  = st.file_uploader("Paddy leaf image", type=["jpg", "jpeg", "png"])
with tab_cam:
    cam = st.camera_input(t("take_photo", lang))

img_source = "camera" if cam else ("upload" if up else None)
src = cam or up

if src is None:
    st.info(t("upload_instruction", lang))
    st.stop()
    raise SystemExit(0)

# ---------------------------------------------------------------------------
# Pre-process
# ---------------------------------------------------------------------------
img = np.array(Image.open(src).convert("RGB"))
if max(img.shape[:2]) > 1280:
    s   = 1280 / max(img.shape[:2])
    img = cv2.resize(img, None, fx=s, fy=s, interpolation=cv2.INTER_AREA)

m = int(min(img.shape[:2]) * crop / 100)
if m > 0:
    img = img[m:img.shape[0] - m, m:img.shape[1] - m]

labels        = _load_labels(labels_path)
model_version = Path(model_path).name

# Detect image change
_img_id = hashlib.md5(img.tobytes()).hexdigest()[:16]
if st.session_state.get("_img_id") != _img_id:
    st.session_state.pop("_scan", None)
    st.session_state.pop("_last_saved", None)
    st.session_state.pop("_qa_history", None)
    st.session_state["_img_id"] = _img_id
    stop_all_speech()

# ---------------------------------------------------------------------------
# Quality check (fast — runs every rerun)
# ---------------------------------------------------------------------------
q_result = check_quality(
    img,
    min_width         = 224,
    min_height        = 224,
    blur_threshold    = float(q_blur),
    dark_threshold    = float(q_dark),
    bright_threshold  = float(q_bright),
    overexp_fraction  = q_overexp / 100.0,
    min_green_fraction= q_green / 100.0,
)
section_header("📊", t("quality_header", lang))
_quality_card(q_result)

# ---------------------------------------------------------------------------
# Image columns
# ---------------------------------------------------------------------------
col_img, col_ovl = st.columns(2)
with col_img:
    img_slot = st.empty()
with col_ovl:
    ovl_slot = st.empty()

if "_scan" not in st.session_state:
    ovl_slot.info(t("analysing_label", lang))

# ---------------------------------------------------------------------------
# AUTO-SCAN
# ---------------------------------------------------------------------------
if "_scan" not in st.session_state:
    pil_img  = Image.fromarray(img)
    data_uri = image_to_data_uri(pil_img, max_side=800)
    render_html(
        scanning_html(data_uri, label=t("scanning_label", lang)),
        container=img_slot,
    )

    t_start = time.perf_counter()

    probs, ms, label, conf, model_err = None, 0.0, None, None, None
    if Path(model_path).exists():
        try:
            probs, ms = classify(load_interpreter(model_path), img)
            i     = int(np.argmax(probs))
            label = labels[i] if i < len(labels) else f"class_{i}"
            conf  = float(probs[i]) * 100
        except Exception as exc:
            model_err = str(exc)
    else:
        model_err = "Model file not found – showing severity only."

    st.session_state["_scan"] = {
        "probs":     probs.tolist() if probs is not None else None,
        "ms":        ms,
        "label":     label,
        "conf":      conf,
        "model_err": model_err,
    }

    elapsed = time.perf_counter() - t_start
    wait_s  = max(0.0, _MIN_SCAN_S - elapsed)
    if wait_s > 0:
        time.sleep(wait_s)

    st.rerun()

# ---------------------------------------------------------------------------
# RESULTS
# ---------------------------------------------------------------------------
sc        = st.session_state["_scan"]
label     = sc["label"]
conf      = sc["conf"]
ms        = sc["ms"]
model_err = sc["model_err"]
probs     = np.array(sc["probs"]) if sc["probs"] is not None else None

# Severity (recomputed live so sliders update overlay in real time)
sev, overlay = severity(img, sat_min, hue_max)

img_slot.image(img,     caption=t("input_leaf", lang),                   use_container_width=True)
ovl_slot.image(overlay, caption=t("detected_lesion", lang), use_container_width=True)

if model_err:
    st.warning(f"Classifier: {model_err}")

uncertain = label is not None and conf < conf_min

# ---- Multi-segment severity (expander) → returns averaged severity --------
avg_sev = _multi_segment_section(sev, sat_min, hue_max)

# ---- Severity badge -------------------------------------------------------
st.markdown("---")
_severity_badge(avg_sev)
st.caption(
    f"Inference: {ms:.0f} ms  |  "
    f"Model: {model_version}  |  "
    f"Severity computed on {1 if avg_sev == sev else 'averaged'} segment(s)."
)
st.markdown("---")

# ---- Top-3 predictions OR Uncertain panel ---------------------------------
if probs is None:
    st.info("No classifier results (model not loaded).")
elif uncertain:
    _confidence_meter(label, conf, conf_min)
    _uncertain_panel(conf_min)
    # Still show predictions, but dimmed / for reference
    st.caption("Predictions shown for reference (confidence below threshold):")
    _top3_predictions(probs, labels, conf_min)
else:
    _confidence_meter(label, conf, conf_min)
    _top3_predictions(probs, labels, conf_min)

st.session_state["_last_leaf_image"] = img
image_hash = hashlib.sha256(img.tobytes()).hexdigest()
st.session_state["_current_image_hash"] = image_hash

if label is not None:
    c_diag_act1, c_diag_act2 = st.columns([1, 1])
    with c_diag_act1:
        d_name_voice = ADVICE.get(label, {}).get("name", label)
        d_name_ta_voice = ADVICE.get(label, {}).get("name_ta", label)
        diag_voice = (
            f"Diagnosis: {d_name_voice}. "
            f"Confidence: {conf:.1f} percent. Severity: {avg_sev:.1f} percent, grade {grade(avg_sev)}."
        )
        if lang == "ta":
            diag_voice = (
                f"கண்டறிதல்: {d_name_ta_voice}. "
                f"நம்பிக்கை: {conf:.1f} சதவீதம். தீவிரத்தன்மை: {avg_sev:.1f} சதவீதம், தரம் {grade(avg_sev)}."
            )
        render_tts_button(diag_voice, lang=lang, button_id="tts_diag_res", label="🔊 Listen to Result")
    with c_diag_act2:
        if st.button("📖 View in Disease Library" if lang != "ta" else "📖 நோய் நூலகத்தில் பார்க்க", key="btn_view_lib_from_scan", use_container_width=True):
            st.session_state["_lib_detail_key"] = label
            st.session_state["_go_to_library"] = True
            st.rerun()

    with st.expander("⚖️ Compare Scanned Leaf with Reference Image" if lang != "ta" else "⚖️ மாதிரி இலையுடன் ஒப்பிடுக", expanded=False):
        c_cmp1, c_cmp2 = st.columns(2)
        with c_cmp1:
            st.image(img, caption="Your Scanned Leaf" if lang != "ta" else "உங்கள் பரிசோதனை இலை", use_container_width=True)
            st.caption(f"Detected: {ADVICE.get(label, {}).get('name', label)} ({conf:.1f}%)")
        with c_cmp2:
            gallery = ADVICE.get(label, {}).get("gallery_images", [])
            ref_path = None
            if gallery:
                for cand in [HERE.parent / "app" / gallery[0], HERE.parent / gallery[0], HERE / gallery[0]]:
                    if cand.exists():
                        ref_path = cand
                        break
            if ref_path:
                st.image(str(ref_path), caption=f"Standard Reference: {ADVICE.get(label, {}).get('name', label)}", use_container_width=True)
                st.caption(ADVICE.get(label, {}).get("symptoms_en" if lang != "ta" else "symptoms_ta", "")[:120] + "...")
            else:
                st.info("No local reference image available for this class.")

# ---- Full probability chart (all 5 classes) -------------------------------
if probs is not None:
    with st.expander("📊 Full probability chart (all classes)"):
        st.bar_chart(
            {(labels[i] if i < len(labels) else str(i)): float(p) * 100
             for i, p in enumerate(probs)}
        )

# ---------------------------------------------------------------------------
# Auto-save
# ---------------------------------------------------------------------------
if label is not None and _db_available and auto_save:
    image_hash = hashlib.sha256(img.tobytes()).hexdigest()
    if image_hash != st.session_state.get("_last_saved"):
        saved_label = ADVICE.get(label, {}).get("name", label)
        if uncertain:
            saved_label = f"Uncertain - {saved_label}"
        # Save full-quality image to history/images/
        pil_for_save = Image.fromarray(img)
        img_rel_path = _save_history_image(pil_for_save, image_hash)
        try:
            ok = save_inspection(
                disease        = saved_label,
                confidence     = conf,
                severity       = avg_sev,
                severity_grade = grade(avg_sev),
                location       = location,
                image_hash     = image_hash,
                probabilities  = probs.tolist() if probs is not None else None,
                uncertain      = uncertain,
                source         = img_source,
                model_version  = model_version,
                image_path     = img_rel_path,
            )
            if ok:
                st.session_state["_last_saved"] = image_hash
        except RuntimeError as db_err:
            st.error(f"Could not save: {db_err}")


# ---------------------------------------------------------------------------
# Farmer Advisory & Disease Management
# ---------------------------------------------------------------------------
advice_en = advice_ta = ""
if label is not None and label in ADVICE:
    info = ADVICE[label]
    advice_en = info.get("en", "")
    advice_ta = info.get("ta", "")
    name_display = info.get("name", label)
    name_ta_display = info.get("name_ta", "")
    sci_display = info.get("scientific", "")
    cause_display = info.get("cause_type", "Disease")

    section_header("🌾", t("advisory_header", lang))

    render_html(
        f'<div style="background:#12301f;border:1px solid #1e4d30;border-radius:14px;padding:16px 20px;margin-bottom:12px;">'
        f'<div style="display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:8px;">'
        f'<div><span style="font-size:1.15em;font-weight:700;color:#eaf4ec;">{name_display}</span>'
        + (f' &nbsp;<span style="color:#2ee59d;font-size:0.95em;">({name_ta_display})</span>' if name_ta_display else "")
        + (f'<div style="font-size:0.82em;color:#5a7a65;font-style:italic;margin-top:2px;">{sci_display}</div>' if sci_display else "") +
        f'</div>'
        f'<span style="background:rgba(46,229,157,0.12);color:#2ee59d;border:1px solid rgba(46,229,157,0.3);border-radius:14px;padding:3px 12px;font-size:0.8em;font-weight:700;">{cause_display}</span>'
        f'</div>'
        f'<div style="margin-top:10px;padding-top:10px;border-top:1px solid #1e4d30;color:#b8d4c0;font-size:0.9em;line-height:1.6;">'
        f'<b>Advisory Summary:</b> {advice_en}<br>'
        + (f'<b style="color:#2ee59d;">தமிழில்:</b> {advice_ta}' if advice_ta else "") +
        f'</div></div>'
    )

    # Open in Disease Library shortcut button
    btn_lib_txt = "📖 Open in Disease Library" if lang == "en" else ("📖 நோய் வழிகாட்டியில் திறக்க" if lang == "ta" else "📖 Open in Disease Library")
    if st.button(btn_lib_txt, key="btn_open_lib"):
        st.session_state["_lib_detail_key"] = label
        st.session_state["_go_to_library"] = True
        st.rerun()

    # Severity-specific action guide
    sev_grade_cur = grade(avg_sev)
    sev_actions = {
        "Very low (monitor)": {
            "en": "• Low severity: Monitor weekly. Ensure balanced fertilization. Avoid excess nitrogen. No chemical spray needed.",
            "ta": "• குறைந்த பாதிப்பு: வாரம் ஒருமுறை கண்காணிக்கவும். தழைச்சத்தை சமச்சீராக இடவும். ரசாயன தெளிப்பு தேவையில்லை.",
            "tanglish": "• Low severity: Weekly monitor pannunga. Balanced urea use pannunga. Excess nitrogen vendam. Chemical spray thevai illa.",
        },
        "Moderate": {
            "en": "• Moderate severity: Remove severely spotted lower leaves. Maintain proper field drainage. Consult agricultural officer for recommended preventive bio-fungicide or neem spray.",
            "ta": "• மிதமான பாதிப்பு: பாதிக்கப்பட்ட கீழ் இலைகளை அகற்றவும். வயலில் சரியான வடிகால் வசதி செய்யவும். வேளாண் அலுவலரின் ஆலோசனையுடன் வேப்ப எண்ணெய் அல்லது பரிந்துரைக்கப்பட்ட தடுப்பு மருந்து தெளிக்கவும்.",
            "tanglish": "• Moderate severity: Pathikkapatta keezh ilaikalai remove pannunga. Vayalil water drainage nalla vaiyunga. Agriculture officer solra preventive spray panna mudiyum.",
        },
        "High": {
            "en": "• High severity: Crop yield may be affected. Check economic threshold level (ETL). Contact local Agriculture Extension Officer immediately for authorized protocol.",
            "ta": "• அதிக பாதிப்பு: மகசூல் பாதிக்கப்படலாம். பொருளாதார சேத நிலையை (ETL) சரிபார்க்கவும். பரிந்துரைக்கப்பட்ட மேலாண்மைக்கு உடனடியாக வேளாண் அலுவலரைத் தொடர்பு கொள்ளவும்.",
            "tanglish": "• High severity: Magasool kuraia vaaipu irukku. ETL check pannunga. Udane local Agriculture Officer-ai contact panni authorized protocol follow pannunga.",
        },
        "Severe (urgent)": {
            "en": "• Severe damage: Immediate intervention required. Stop all nitrogen application. Isolate irrigation water from adjacent plots. Contact your Agriculture Officer urgently.",
            "ta": "• தீவிர பாதிப்பு: உடனடி நடவடிக்கை தேவை. யூரியா இடுவதை உடனே நிறுத்தவும். பாசன நீர் பிற வயல்களுக்கு செல்வதைத் தடுக்கவும். வேளாண் அலுவலரை உடனடியாக அணுகவும்.",
            "tanglish": "• Severe damage: Udane action venum. Urea poduratha stop pannunga. Paasana thanni matra vayalukku pogama thadunga. Agriculture Officer-ai udane paakkavum.",
        },
    }
    sev_msg = sev_actions.get(sev_grade_cur, {}).get(lang) or sev_actions.get(sev_grade_cur, {}).get("en", "")
    if sev_msg:
        render_html(
            f'<div style="background:rgba(46,229,157,0.08);border-left:4px solid #2ee59d;border-radius:8px;'
            f'padding:10px 14px;margin-bottom:14px;color:#eaf4ec;font-size:0.88em;line-height:1.5;">'
            f'<b>🎯 Action for Measured Severity ({sev_grade_cur} — {avg_sev:.1f}%):</b><br>{sev_msg}'
            f'</div>'
        )

    # Helper to fetch localized content
    def _field(base_k: str):
        return info.get(f"{base_k}_{lang}") or info.get(f"{base_k}_en") or info.get(f"{base_k}_ta") or ""

    # Differentiate between Healthy, Other/Uncertain, and specific Diseases
    if label == "healthy":
        section_header("🌿", "Keeping Your Paddy Crop Healthy" if lang == "en" else ("பயிரை ஆரோக்கியமாக பராமரிக்கும் வழிகள்" if lang == "ta" else "Payirai Healthy-aga Maintain Panna Steps"))
        p_crop = _field("prevention_during_crop")
        p_harv = _field("prevention_after_harvest")
        st.markdown(f"**During Crop Growth:**\n\n{p_crop}")
        st.markdown(f"**Field Maintenance & Prevention:**\n\n{p_harv}")

    elif label == "other" or uncertain:
        section_header("⚠️", "Differential Diagnosis — Compare with Known Diseases" if lang == "en" else ("வேறுபட்ட நோய்களை ஒப்பிடுதல்" if lang == "ta" else "Differential Diagnosis — Matra Noigaludan Oppiduga"))
        render_html(
            '<div style="background:#12301f;border:1px solid #1e4d30;border-radius:10px;padding:12px 16px;margin-bottom:12px;color:#ffd166;font-size:0.88em;">'
            'The scan result is classified as <b>Other</b> or confidence is uncertain. Compare your leaf with the characteristic symptoms below:'
            '</div>'
        )
        compare_classes = [("blast", "Rice Blast"), ("brown_spot", "Brown Spot"), ("blb", "Bacterial Leaf Blight"), ("sheath_blight", "Sheath Blight"), ("tungro", "Tungro Virus")]
        for comp_k, comp_name in compare_classes:
            if comp_k in ADVICE:
                c_inf = ADVICE[comp_k]
                c_sum = c_inf.get(f"symptoms_summary_{lang}") or c_inf.get("symptoms_summary_en", "")
                c_col1, c_col2 = st.columns([3.5, 1.5])
                with c_col1:
                    st.markdown(f"**{c_inf.get('name', comp_name)}:** {c_sum}")
                with c_col2:
                    if st.button(f"Inspect {comp_name}", key=f"btn_inspect_{comp_k}", use_container_width=True):
                        st.session_state["_lib_detail_key"] = comp_k
                        st.session_state["_go_to_library"] = True
                        st.rerun()
                st.markdown("---")

    else:
        # Full Disease Details Panel
        adv_tab1, adv_tab2, adv_tab3, adv_tab4 = st.tabs([
            "📋 Diagnostic Symptoms Checklist",
            "🛡️ Multi-Stage Prevention",
            "💨 Transmission & Favourable Weather",
            "📚 Compare with Other Diseases",
        ])

        with adv_tab1:
            st.markdown("#### Does your leaf look like this?")
            chk_items = _field("how_to_check")
            if isinstance(chk_items, list):
                for c_i, chk in enumerate(chk_items):
                    st.checkbox(chk, key=f"scan_chk_{c_i}")
            else:
                st.write(chk_items or "—")

            st.markdown("---")
            st.markdown("#### Leaf Symptoms in Order of Appearance")
            sym_l = _field("symptoms_leaf")
            if isinstance(sym_l, list):
                for s_i, sym_txt in enumerate(sym_l, 1):
                    st.markdown(f"**{s_i}.** {sym_txt}")
            else:
                st.write(sym_l or "—")

            sym_oth = _field("symptoms_other_parts")
            if sym_oth:
                st.markdown(f"**Other Parts Affected:** {sym_oth}")

        with adv_tab2:
            p_plant = _field("prevention_before_planting")
            p_crop = _field("prevention_during_crop")
            p_harv = _field("prevention_after_harvest")
            p_limit = _field("prevention_to_limit_spread")

            c_p1, c_p2 = st.columns(2)
            with c_p1:
                st.markdown(f"**🌱 Before Planting:**\n\n{p_plant}")
                st.markdown(f"**🚜 After Harvest:**\n\n{p_harv}")
            with c_p2:
                st.markdown(f"**🌾 During Crop Growth:**\n\n{p_crop}")
                st.markdown(f"**🛑 To Limit Field Spread:**\n\n{p_limit}")

            off_call = _field("when_to_call_officer")
            if off_call:
                st.warning(f"**🧑‍🌾 When to Call the Agriculture Officer:** {off_call}")

            render_html(
                '<div style="background:rgba(255,209,102,0.07);border-left:3px solid rgba(255,209,102,0.5);border-radius:6px;padding:6px 12px;margin-top:10px;color:#ffd16699;font-size:0.76em;">'
                '⚠️ Confirm chemical product and dose with your local TNAU Agriculture Extension Officer.'
                '</div>'
            )

        with adv_tab3:
            spr_txt = _field("how_it_spreads")
            fav_txt = _field("favourable_conditions")
            w1, w2 = st.columns(2)
            with w1:
                st.info(f"**🌬️ How It Spreads:**\n\n{spr_txt}")
            with w2:
                st.warning(f"**🌡️ Favourable Conditions:**\n\n{fav_txt}")

        with adv_tab4:
            st.caption("Inspect and compare symptoms with other rice disease categories:")
            other_lbl = st.selectbox(
                "Select disease to view advisory",
                options=list(ADVICE.keys()),
                format_func=lambda k: f"{ADVICE[k].get('name', k)} ({ADVICE[k].get('cause_type', '')})",
                key="scan_adv_selectbox",
            )
            if other_lbl and other_lbl in ADVICE:
                o_info = ADVICE[other_lbl]
                st.markdown(f"**{o_info.get('name', other_lbl)}** — *{o_info.get('scientific', '')}*")
                o_sum = o_info.get(f"symptoms_summary_{lang}") or o_info.get("symptoms_summary_en", "")
                st.info(f"**Symptoms Summary:** {o_sum}")

# ---------------------------------------------------------------------------
# FEATURE 2 & 3: Ask-Your-Own-Question After Scanning (Offline Q&A + Speech)
# ---------------------------------------------------------------------------
if label is not None:
    section_header("💬", "Ask a Question About This Disease" if lang != "ta" else "இந்த நோய் பற்றி கேள்வி கேளுங்கள்")

    qa_col_cfg1, qa_col_cfg2 = st.columns([1, 1])
    with qa_col_cfg1:
        auto_read = st.toggle(
            "🔊 Read answers aloud" if lang != "ta" else "🔊 பதில்களை தானாக வாசி",
            value=False,
            key="qa_auto_read",
        )
    with qa_col_cfg2:
        qa_speed_label = st.radio(
            "Voice Speed",
            ["Normal (1.0x)", "Slow (0.8x)"],
            horizontal=True,
            label_visibility="collapsed",
            key="qa_speed_sel",
        )
        qa_speed = 0.8 if "Slow" in qa_speed_label else 1.0

    # STT Microphone Button
    render_mic_button(target_input_label="Ask a question about this disease...", lang=lang)

    # 3 Example Question Placeholder Hints
    hints = get_example_questions(label, lang)
    render_html(
        f'<div style="color:#5a7a65;font-size:0.80em;margin-top:2px;margin-bottom:10px;line-height:1.5;">'
        f'<b>💡 Example questions you can ask:</b><br>'
        f'• <i>"{hints[0]}"</i><br>'
        f'• <i>"{hints[1]}"</i><br>'
        f'• <i>"{hints[2]}"</i>'
        f'</div>'
    )

    with st.form("qa_form", clear_on_submit=True):
        user_q = st.text_input(
            "Ask a question about this disease" if lang != "ta" else "இந்த நோய் பற்றி கேள்வி கேளுங்கள்",
            placeholder=f"Type or speak a question about {ADVICE.get(label, {}).get('name', label)} in English or Tamil...",
            label_visibility="collapsed",
            key="qa_input_field",
        )
        submit_q = st.form_submit_button("Send Question ➔" if lang != "ta" else "கேள்வியை அனுப்பு ➔")

    if "_qa_history" not in st.session_state:
        st.session_state["_qa_history"] = []

    scan_metrics = {
        "disease": ADVICE.get(label, {}).get("name", label),
        "confidence": conf,
        "severity": avg_sev,
        "severity_grade": grade(avg_sev),
    }

    if submit_q and user_q and user_q.strip():
        q_text = user_q.strip()
        res = ask_question(
            question=q_text,
            disease=label,
            scan_data=scan_metrics,
            conversation_history=st.session_state["_qa_history"],
            preferred_lang=lang,
        )
        qa_entry = {
            "question": q_text,
            "answer": res["answer"],
            "title": res.get("title", ""),
            "topic_id": res.get("topic_id"),
            "matched": res.get("matched", False),
            "suggestions": res.get("suggestions", []),
            "lang": res.get("lang", lang),
            "tamil_script_answer": res.get("tamil_script_answer", ""),
        }
        st.session_state["_qa_history"].append(qa_entry)

        curr_hash = st.session_state.get("_current_image_hash")
        if curr_hash and _db_available:
            try:
                update_inspection_qa(curr_hash, st.session_state["_qa_history"])
            except Exception:
                pass

        if auto_read:
            st.session_state["_speak_auto"] = {
                "text": res["answer"],
                "lang": res.get("lang", lang),
                "tamil_script_answer": res.get("tamil_script_answer", ""),
            }
        st.rerun()

    # Render Conversation Thread
    if st.session_state.get("_qa_history"):
        import html as py_html
        for idx, msg in enumerate(st.session_state["_qa_history"]):
            q_safe = py_html.escape(msg.get("question", ""))
            a_safe = py_html.escape(msg.get("answer", "")).replace("\n", "<br>")
            matched = msg.get("matched", True)
            border_col = "#2ee59d" if matched else "#ffd166"

            render_html(
                f'<div style="background:#1a3d28;border-radius:10px;padding:10px 14px;margin-bottom:6px;color:#eaf4ec;font-size:0.90em;">'
                f'<b>🧑‍🌾 Farmer:</b> {q_safe}'
                f'</div>'
            )
            render_html(
                f'<div style="background:#12301f;border-left:3px solid {border_col};border-radius:10px;padding:12px 16px;margin-bottom:8px;color:#b8d4c0;font-size:0.90em;line-height:1.6;">'
                f'<div style="font-weight:700;color:{border_col};font-size:0.85em;margin-bottom:4px;">🤖 AgriVision Expert:</div>'
                f'{a_safe}'
                f'</div>'
            )
            ans_lang = msg.get("lang", lang)
            render_tts_button(
                msg.get("answer", ""),
                lang=ans_lang,
                speed=qa_speed,
                button_id=f"tts_ans_{idx}",
                label="🔊 Listen to Answer",
                tamil_script_text=msg.get("tamil_script_answer"),
            )

            suggestions = msg.get("suggestions", [])
            if suggestions:
                st.caption("You may also want to know / Example questions:" if lang != "ta" else "மாதிரி கேள்விகள் / இதையும் தெரிந்துகொள்ளலாம்:")
                cols_sug = st.columns(min(len(suggestions), 3))
                for s_i, sugg in enumerate(suggestions[:3]):
                    with cols_sug[s_i]:
                        s_title = sugg if isinstance(sugg, str) else sugg.get("title", "")
                        # Remove leading number like '1. ' if present for display button
                        btn_label = re.sub(r"^\d+\.\s*", "", s_title)
                        if st.button(f"📌 {btn_label}", key=f"sugg_{idx}_{s_i}"):
                            res_s = ask_question(
                                question=btn_label,
                                disease=label,
                                scan_data=scan_metrics,
                                conversation_history=st.session_state["_qa_history"],
                                preferred_lang=lang,
                            )
                            st.session_state["_qa_history"].append({
                                "question": btn_label,
                                "answer": res_s["answer"],
                                "title": res_s.get("title", ""),
                                "topic_id": res_s.get("topic_id"),
                                "matched": res_s.get("matched", False),
                                "suggestions": res_s.get("suggestions", []),
                                "lang": res_s.get("lang", lang),
                                "tamil_script_answer": res_s.get("tamil_script_answer", ""),
                            })
                            curr_hash = st.session_state.get("_current_image_hash")
                            if curr_hash and _db_available:
                                try:
                                    update_inspection_qa(curr_hash, st.session_state["_qa_history"])
                                except Exception:
                                    pass
                            if auto_read:
                                st.session_state["_speak_auto"] = {
                                    "text": res_s["answer"],
                                    "lang": res_s.get("lang", lang),
                                    "tamil_script_answer": res_s.get("tamil_script_answer", ""),
                                }
                            st.rerun()

        if st.button("🗑️ Clear conversation" if lang != "ta" else "🗑️ உரையாடலை அழிக்க", key="clear_qa_btn"):
            st.session_state["_qa_history"] = []
            curr_hash = st.session_state.get("_current_image_hash")
            if curr_hash and _db_available:
                try:
                    update_inspection_qa(curr_hash, [])
                except Exception:
                    pass
            st.rerun()

    if st.session_state.get("_speak_auto"):
        auto_item = st.session_state.pop("_speak_auto")
        if isinstance(auto_item, dict):
            text_to_speak = auto_item.get("text", "")
            speak_lang = auto_item.get("lang", lang)
            tamil_text = auto_item.get("tamil_script_answer")
        else:
            text_to_speak = str(auto_item)
            speak_lang = lang
            tamil_text = None

        render_tts_button(
            text_to_speak,
            lang=speak_lang,
            speed=qa_speed,
            button_id="tts_auto_speak",
            label="🔊 Speaking Answer...",
            tamil_script_text=tamil_text,
        )

# ---------------------------------------------------------------------------
# Report + Telegram
# ---------------------------------------------------------------------------
name   = ADVICE.get(label, {}).get("name", label or "n/a")
report = build_text_report(
    name      = name,
    conf      = conf,
    sev       = avg_sev,
    sev_grade = grade(avg_sev),
    location  = location,
    advice_en = advice_en,
    advice_ta = advice_ta,
)
st.text_area(t("report_header", lang), report, height=180)

if st.button(t("send_telegram", lang)):
    if not tg_token or not tg_chat:
        st.error("Enter bot token and chat ID in the sidebar first.")
    else:
        ok, msg = send_photo_telegram(tg_token, tg_chat, overlay, report, queue_on_fail=True)
        if ok:
            st.success(msg)
        else:
            st.warning(msg)

# Show queue badge inline if there are pending items
_pend = queue_count()
if _pend > 0:
    render_html(
        f'<div style="background:rgba(255,209,102,0.10);border-left:4px solid #ffd166;'
        f'border-radius:8px;padding:8px 14px;margin:8px 0;font-family:Poppins,sans-serif;'
        f'font-size:0.85em;color:#ffd166;">'
        f'📴 <b>{_pend}</b> unsent message(s) in offline queue. '
        f'Open the Telegram section in the sidebar and click <b>🔄 Sync now</b> when online.</div>'
    )
