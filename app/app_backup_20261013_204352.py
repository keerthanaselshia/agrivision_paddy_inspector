r"""AgriVision Paddy Inspector  –  UI entry point.

Run from the project root (C:\Users\keert\paddy_dataset):
    venv2\Scripts\python.exe -m streamlit run app\app.py

This file contains ONLY Streamlit UI code.
All logic lives in app\core\ modules:
    core/classifier.py   – TFLite inference
    core/severity.py     – OpenCV severity estimation
    core/advisory.py     – Disease advice (loaded from data/advisory.json)
    core/quality.py      – Image quality checks
    core/location.py     – Location helper (GPS stub)
    core/reports.py      – Report text builder

Prototype disclaimer: trained on public datasets only.
See the About page for known limits.
"""

import hashlib
import io
from datetime import datetime
from pathlib import Path

import cv2
import numpy as np
import requests
import streamlit as st
from PIL import Image

# ---- core modules ----------------------------------------------------------
from core.classifier import load_interpreter, classify
from core.severity   import severity, grade
from core.advisory   import ADVICE
from core.reports    import build_text_report

# ---- DB / history (stay in app/ for now) -----------------------------------
try:
    from history_db        import init_db, save_inspection
    from history_dashboard import show_history_dashboard
    _db_available = True
    init_db()
except Exception as _db_init_err:
    _db_available  = False
    _db_init_msg   = str(_db_init_err)

HERE           = Path(__file__).parent
DEFAULT_LABELS = ["blast", "blb", "brown_spot", "healthy", "other"]


# ---------------------------------------------------------------------------
# Telegram helper (UI-only helper, stays here for now)
# ---------------------------------------------------------------------------

def _send_telegram(token: str, chat_id: str, photo_rgb: np.ndarray, caption: str) -> tuple[bool, str]:
    buf = io.BytesIO()
    Image.fromarray(photo_rgb).save(buf, format="JPEG", quality=90)
    buf.seek(0)
    r = requests.post(
        f"https://api.telegram.org/bot{token}/sendPhoto",
        data={"chat_id": chat_id, "caption": caption[:1000]},
        files={"photo": ("report.jpg", buf, "image/jpeg")},
        timeout=20,
    )
    return r.ok, r.text[:200]


def _load_labels(path: str) -> list[str]:
    p = Path(path)
    if p.exists():
        names = [x.strip() for x in p.read_text(encoding="utf-8").splitlines() if x.strip()]
        if names:
            return names
    return DEFAULT_LABELS


# ============================================================== UI ===========
st.set_page_config(page_title="AgriVision Paddy Inspector", layout="wide")
st.title("AgriVision Paddy Inspector")
st.caption(
    "🌾 Software prototype — trained on public datasets, not yet field-validated. "
    "Raspberry Pi 4 + camera + LED chamber integration is the next phase."
)

# Show DB init failure banner once (does not crash the app)
if not _db_available:
    st.error(
        f"Could not open the inspection database. "
        f"History will not be saved this session.\n\nDetail: {_db_init_msg}"
    )

# ---------------------------------------------------------------------------
# Navigation
# ---------------------------------------------------------------------------
page = st.sidebar.radio(
    "Navigation",
    ["Inspect Leaf", "Inspection History"],
)
if page == "Inspection History":
    if _db_available:
        show_history_dashboard()
    else:
        st.error("Database is unavailable. Cannot show history.")
    st.stop()

# ---------------------------------------------------------------------------
# Sidebar – Settings
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

    st.subheader("Report")
    location = st.text_input(
        "Location (GPS module comes later)", "Erode, Tamil Nadu"
    )
    tg_token = st.text_input("Telegram bot token (optional)", type="password")
    tg_chat  = st.text_input("Telegram chat id (optional)")

    st.subheader("Auto-save")
    auto_save = st.checkbox(
        "Auto-save results",
        value=True,
        help="Save each new image automatically to the inspection database.",
    )

# ---------------------------------------------------------------------------
# Image input
# ---------------------------------------------------------------------------
tab_up, tab_cam = st.tabs(["Upload leaf photo", "Use camera"])
with tab_up:
    up  = st.file_uploader("Paddy leaf image", type=["jpg", "jpeg", "png"])
with tab_cam:
    cam = st.camera_input("Take a photo of the leaf")

img_source = "camera" if cam else ("upload" if up else None)
src = cam or up

if src is None:
    st.info(
        "Upload or capture a paddy leaf photo to start. "
        "Use a plain white or grey background for best severity results."
    )
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
label, conf, ms, probs = None, None, None, None
model_version = Path(model_path).name

# ---------------------------------------------------------------------------
# Classification
# ---------------------------------------------------------------------------
if Path(model_path).exists():
    try:
        probs, ms = classify(load_interpreter(model_path), img)
        i     = int(np.argmax(probs))
        label = labels[i] if i < len(labels) else f"class_{i}"
        conf  = float(probs[i]) * 100
    except Exception as e:
        st.error(f"Model error: {e}")
else:
    st.warning("Model file not found – showing the OpenCV severity part only.")

# ---------------------------------------------------------------------------
# Severity
# ---------------------------------------------------------------------------
sev, overlay = severity(img, sat_min, hue_max)

# ---------------------------------------------------------------------------
# Display – images side by side
# ---------------------------------------------------------------------------
c1, c2 = st.columns(2)
c1.image(img,     caption="Input leaf",                   use_container_width=True)
c2.image(overlay, caption="Detected diseased area (red)", use_container_width=True)

# ---------------------------------------------------------------------------
# Metrics row
# ---------------------------------------------------------------------------
m1, m2, m3, m4 = st.columns(4)
uncertain = label is not None and conf < conf_min

if label is None:
    m1.metric("Disease", "model not loaded")
elif uncertain:
    m1.metric("Disease", "Uncertain")
else:
    m1.metric("Disease", ADVICE.get(label, {}).get("name", label))

m2.metric("Confidence",     f"{conf:.1f}%" if conf is not None else "-")
m3.metric("Severity index", f"{sev:.1f}%",  grade(sev))
m4.metric("Inference time", f"{ms:.0f} ms" if ms is not None else "-")

# Probability bar chart
if probs is not None:
    st.bar_chart(
        {(labels[i] if i < len(labels) else str(i)): float(p) * 100
         for i, p in enumerate(probs)}
    )

# ---------------------------------------------------------------------------
# Auto-save
# ---------------------------------------------------------------------------
if label is not None:
    image_hash = hashlib.sha256(img.tobytes()).hexdigest()
    new_image  = image_hash != st.session_state.get("last_saved_image_hash")

    if auto_save and new_image and _db_available:
        saved_label = ADVICE.get(label, {}).get("name", label)
        if uncertain:
            saved_label = f"Uncertain - {saved_label}"
        try:
            saved = save_inspection(
                disease        = saved_label,
                confidence     = conf,
                severity       = sev,
                severity_grade = grade(sev),
                location       = location,
                image_hash     = image_hash,
                probabilities  = probs.tolist() if probs is not None else None,
                uncertain      = uncertain,
                source         = img_source,
                model_version  = model_version,
            )
            if saved:
                st.session_state["last_saved_image_hash"] = image_hash
        except RuntimeError as db_err:
            st.error(f"Could not save inspection: {db_err}")

# ---------------------------------------------------------------------------
# Advisory
# ---------------------------------------------------------------------------
advice_en = advice_ta = ""
if label is not None and uncertain:
    st.warning(
        "Confidence is low. Retake the photo (single leaf, plain background, "
        "good light) or consult an agriculture officer."
    )
elif label in ADVICE:
    advice_en = ADVICE[label]["en"]
    advice_ta = ADVICE[label]["ta"]
    st.subheader("Advisory")
    st.write(advice_en)
    st.write(advice_ta)
    st.caption(
        "Decision support only. Doses must come from the current TNAU guide "
        "or the product label and be checked by an agriculture officer."
    )

# ---------------------------------------------------------------------------
# Report text area
# ---------------------------------------------------------------------------
name   = ADVICE.get(label, {}).get("name", label or "n/a")
report = build_text_report(
    name      = name,
    conf      = conf,
    sev       = sev,
    sev_grade = grade(sev),
    location  = location,
    advice_en = advice_en,
    advice_ta = advice_ta,
)
st.text_area("Report", report, height=180)

# ---------------------------------------------------------------------------
# Telegram button
# ---------------------------------------------------------------------------
if st.button("Send report to Telegram"):
    if not tg_token or not tg_chat:
        st.error("Enter the bot token and chat id in the sidebar first.")
    else:
        try:
            ok, msg = _send_telegram(tg_token, tg_chat, overlay, report)
            st.success("Sent.") if ok else st.error(f"Telegram error: {msg}")
        except Exception as e:
            st.error(f"Could not send (check internet): {e}")
