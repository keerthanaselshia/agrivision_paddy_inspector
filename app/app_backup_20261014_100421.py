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
from core.theme       import apply_theme, render_header, sidebar_logo, section_header


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
                st.markdown(
                    '<div style="color:#2ee59d;font-weight:600;'
                    'font-family:Poppins,sans-serif;padding:10px 0;">'
                    "✔ Image looks good for analysis.</div>",
                    unsafe_allow_html=True,
                )
            else:
                for r in q["reasons"]:
                    st.warning(r, icon="⚠️")

    if q["grade"] == "Poor":
        st.markdown(
            '<div style="background:rgba(255,93,93,0.10);border-left:4px solid #ff5d5d;'
            'border-radius:12px;padding:12px 18px;color:#ff5d5d;'
            'font-family:Poppins,sans-serif;font-weight:600;font-size:0.9em;">'
            "🔴 Poor image quality — results may be unreliable. "
            "Use a single leaf on a plain background with good lighting."
            "</div>",
            unsafe_allow_html=True,
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
    st.markdown(
        f"""
        <div style="text-align:center;margin:18px 0 8px 0;">
          <span style="display:inline-block;background:{bg};color:{fg};
                       border:2px solid {fg};border-radius:24px;
                       padding:10px 32px;font-family:'Poppins',sans-serif;
                       font-weight:700;font-size:1.1em;letter-spacing:0.04em;
                       box-shadow:0 4px 20px {fg}30;">
            {dot}&nbsp; {g}
            &nbsp;&nbsp;<span style="opacity:0.7;font-size:0.85em;">{sev_pct:.1f}% lesion area</span>
          </span>
        </div>""",
        unsafe_allow_html=True,
    )


def _top3_predictions(probs: np.ndarray, labels: list, conf_min: float) -> None:
    """Show top-3 predictions with dark-theme confidence bars."""
    sorted_idx = np.argsort(probs)[::-1][:3]
    section_header("🔬", "Predictions")

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

        c_name, c_bar, c_pct = st.columns([2.8, 5, 1.5])
        with c_name:
            st.markdown(
                f'<div style="font-family:Poppins,sans-serif;font-weight:{"700" if is_1st else "500"};'
                f'color:{txt_col};font-size:{"1em" if is_1st else "0.9em"};">'
                f'{name}</div>'
                + (f'<div style="font-size:0.74em;color:#5a7a65;font-style:italic;margin-top:2px;">{sci}</div>' if sci else ""),
                unsafe_allow_html=True,
            )
        c_bar.markdown(
            f"""<div style="background:#1a3d28;border-radius:8px;
                            padding:3px;margin-top:10px;">
                  <div style="width:{width:.1f}%;background:{bar_col};
                              height:10px;border-radius:6px;
                              box-shadow:{glow};min-width:3px;
                              transition:width 0.4s ease;"></div>
                </div>""",
            unsafe_allow_html=True,
        )
        c_pct.metric("", f"{p:.1f}%")


def _uncertain_panel(conf_min: int) -> None:
    """Explain the Uncertain state (dark theme)."""
    st.markdown(
        f"""
        <div style="background:rgba(255,209,102,0.08);
                    border-left:4px solid #ffd166;
                    border-radius:12px;padding:16px 20px;margin:10px 0;
                    font-family:'Poppins',sans-serif;">
          <div style="color:#ffd166;font-weight:700;font-size:1em;margin-bottom:8px;">
            ⚠️ Uncertain prediction
          </div>
          <div style="color:#b8d4c0;font-size:0.9em;line-height:1.6;">
            The model's top confidence is below your threshold (<b style="color:#ffd166;">{conf_min}%</b>).
          </div>
          <div style="color:#8ab89a;font-size:0.85em;margin-top:10px;line-height:1.8;">
            <b style="color:#b8d4c0;">Common causes:</b><br>
            &nbsp;· Busy or coloured background &nbsp;· Mixed/early-stage symptoms<br>
            &nbsp;· Leaf does not fill the frame &nbsp;· Poor lighting or blur<br><br>
            <b style="color:#b8d4c0;">Suggestions:</b><br>
            &nbsp;· Retake with a single leaf on a plain white surface<br>
            &nbsp;· Ensure leaf fills ≥ 60% of the frame<br>
            &nbsp;· Use bright, even lighting — avoid shadows<br>
            &nbsp;· If problem persists, consult a local agriculture officer
          </div>
        </div>""",
        unsafe_allow_html=True,
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

# Language selector toggle (English / தமிழ்)
lang_choice = st.sidebar.selectbox(
    "🌐 Language / மொழி",
    ["English", "தமிழ்"],
    index=0 if st.session_state.get("lang", "en") == "en" else 1,
    key="app_lang_choice",
)
lang = "ta" if lang_choice == "தமிழ்" else "en"
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
if "Library" in page or "வழிகாட்டி" in page:
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
    conf_min    = st.slider("Minimum confidence (%)", 40, 95, 70)

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
        st.markdown(
            f'<div style="background:rgba(255,209,102,0.12);border-left:4px solid #ffd166;'
            f'border-radius:8px;padding:8px 12px;margin:8px 0;font-family:Poppins,sans-serif;'
            f'font-size:0.85em;color:#ffd166;">'
            f'📴 <b>{pending}</b> message(s) queued offline</div>',
            unsafe_allow_html=True,
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
    st.session_state["_img_id"] = _img_id

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
    img_slot.markdown(
        scanning_html(data_uri, label=t("scanning_label", lang)),
        unsafe_allow_html=True,
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
    f"Inference: {ms:.0f} ms &nbsp;|&nbsp; "
    f"Model: {model_version} &nbsp;|&nbsp; "
    f"Severity computed on {1 if avg_sev == sev else 'averaged'} segment(s).",
    unsafe_allow_html=True,
)
st.markdown("---")

# ---- Top-3 predictions OR Uncertain panel ---------------------------------
if probs is None:
    st.info("No classifier results (model not loaded).")
elif uncertain:
    _uncertain_panel(conf_min)
    # Still show predictions, but dimmed / for reference
    st.caption("Predictions shown for reference (confidence below threshold):")
    _top3_predictions(probs, labels, conf_min)
else:
    _top3_predictions(probs, labels, conf_min)

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
# Advisory
# ---------------------------------------------------------------------------
advice_en = advice_ta = ""
if label is not None and not uncertain and label in ADVICE:
    advice_en = ADVICE[label]["en"]
    advice_ta = ADVICE[label]["ta"]
    st.subheader(t("advisory_header", lang))
    st.write(advice_en)
    st.write(advice_ta)
    st.caption(t("advisory_disclaimer", lang))

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
    st.markdown(
        f'<div style="background:rgba(255,209,102,0.10);border-left:4px solid #ffd166;'
        f'border-radius:8px;padding:8px 14px;margin:8px 0;font-family:Poppins,sans-serif;'
        f'font-size:0.85em;color:#ffd166;">'
        f'📴 <b>{_pend}</b> unsent message(s) in offline queue. '
        f'Open the Telegram section in the sidebar and click <b>🔄 Sync now</b> when online.</div>',
        unsafe_allow_html=True,
    )
