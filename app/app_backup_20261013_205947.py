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
    core/scan_effect.py  – Scanning animation HTML/CSS overlaid on the image

Prototype disclaimer: trained on public datasets only.
See the About page (Step 11) for known limits.
"""

import hashlib
import io
import time
from pathlib import Path

import cv2
import numpy as np
import requests
import streamlit as st
from PIL import Image

# ---- core modules ----------------------------------------------------------
from core.classifier  import load_interpreter, classify
from core.severity    import severity, grade
from core.advisory    import ADVICE
from core.reports     import build_text_report
from core.scan_effect import image_to_data_uri, scanning_html

# ---- DB / history ----------------------------------------------------------
try:
    from history_db        import init_db, save_inspection
    from history_dashboard import show_history_dashboard
    _db_available = True
    init_db()
except Exception as _db_init_err:
    _db_available = False
    _db_init_msg  = str(_db_init_err)

HERE           = Path(__file__).parent
DEFAULT_LABELS = ["blast", "blb", "brown_spot", "healthy", "other"]
_MIN_SCAN_S    = 2.0   # minimum seconds the scan animation stays visible


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _send_telegram(token: str, chat_id: str, photo_rgb: np.ndarray, caption: str):
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


# ============================================================= UI ============
st.set_page_config(page_title="AgriVision Paddy Inspector", layout="wide")
st.title("AgriVision Paddy Inspector")
st.caption(
    "🌾 Software prototype — trained on public datasets, not yet field-validated. "
    "Raspberry Pi 4 integration is the next phase."
)

if not _db_available:
    st.error(
        "Could not open the inspection database. "
        f"History will not be saved this session.\n\nDetail: {_db_init_msg}"
    )

# ---------------------------------------------------------------------------
# Navigation
# ---------------------------------------------------------------------------
page = st.sidebar.radio("Navigation", ["Inspect Leaf", "Inspection History"])
if page == "Inspection History":
    if _db_available:
        show_history_dashboard()
    else:
        st.error("Database is unavailable.")
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
    location = st.text_input("Location (GPS module comes later)", "Erode, Tamil Nadu")
    tg_token = st.text_input("Telegram bot token (optional)", type="password")
    tg_chat  = st.text_input("Telegram chat id (optional)")

    st.subheader("Auto-save")
    auto_save = st.checkbox(
        "Auto-save results", value=True,
        help="Save each new scan automatically to the inspection database.",
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
model_version = Path(model_path).name

# Detect image change: clear stored scan when a new image arrives
_img_id = hashlib.md5(img.tobytes()).hexdigest()[:16]
if st.session_state.get("_img_id") != _img_id:
    st.session_state.pop("_scan", None)
    st.session_state.pop("_last_saved", None)
    st.session_state["_img_id"] = _img_id

# ---------------------------------------------------------------------------
# Two-column image layout
# Left  → leaf image  OR  scanning animation while busy
# Right → severity overlay OR "press Scan" hint
# ---------------------------------------------------------------------------
col_img, col_ovl = st.columns(2)

with col_img:
    img_slot = st.empty()   # will hold the normal image OR the scan animation

with col_ovl:
    ovl_slot = st.empty()   # will hold the severity overlay OR a hint

# Fill slots based on current state (before the Scan button is handled)
if "_scan" not in st.session_state:
    # No result yet – show the leaf image and a hint
    img_slot.image(img, caption="Input leaf", use_container_width=True)
    ovl_slot.info("Press **🔍 Scan Leaf** to analyse.")
else:
    # Results exist – show leaf + overlay (recompute overlay: fast, no inference)
    img_slot.image(img, caption="Input leaf", use_container_width=True)
    _, _prev_overlay = severity(img, sat_min, hue_max)
    ovl_slot.image(_prev_overlay, caption="Detected diseased area (red)",
                   use_container_width=True)

# ---------------------------------------------------------------------------
# Scan button
# ---------------------------------------------------------------------------
scan_clicked = st.button("🔍 Scan Leaf", type="primary", use_container_width=True)

if scan_clicked:
    # ------------------------------------------------------------------ 1. Animation
    # Convert the numpy image → PIL → base64 data URI → scanning HTML
    # The HTML is injected into img_slot so the animation appears ONLY over the leaf.
    pil_img  = Image.fromarray(img)
    data_uri = image_to_data_uri(pil_img, max_side=800)
    img_slot.markdown(scanning_html(data_uri, label="Scanning leaf..."),
                      unsafe_allow_html=True)
    ovl_slot.info("⏳ Computing severity...")

    t_start = time.perf_counter()

    # ------------------------------------------------------------------ 2. Classify
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

    # ------------------------------------------------------------------ 3. Severity
    sev, _ = severity(img, sat_min, hue_max)

    # ------------------------------------------------------------------ 4. Store
    st.session_state["_scan"] = {
        "probs":     probs.tolist() if probs is not None else None,
        "ms":        ms,
        "label":     label,
        "conf":      conf,
        "sev":       sev,
        "model_err": model_err,
    }

    # ------------------------------------------------------------------ 5. Minimum animation time
    elapsed = time.perf_counter() - t_start
    wait_s  = max(0.0, _MIN_SCAN_S - elapsed)
    if wait_s > 0:
        time.sleep(wait_s)

    # ------------------------------------------------------------------ 6. Refresh to show results
    st.rerun()

# ---------------------------------------------------------------------------
# Results (shown every rerun once a scan has been completed)
# ---------------------------------------------------------------------------
if "_scan" not in st.session_state:
    st.stop()   # waiting for first scan

sc        = st.session_state["_scan"]
label     = sc["label"]
conf      = sc["conf"]
ms        = sc["ms"]
sev       = sc["sev"]
model_err = sc["model_err"]
probs     = np.array(sc["probs"]) if sc["probs"] is not None else None

# Recompute the overlay (pure OpenCV, very fast, avoids storing large arrays)
_, overlay = severity(img, sat_min, hue_max)

# (img_slot already filled with the normal image above; update ovl_slot)
ovl_slot.image(overlay, caption="Detected diseased area (red)", use_container_width=True)

if model_err:
    st.warning(f"Classifier: {model_err}")

uncertain = label is not None and conf < conf_min

# ---------------------------------------------------------------------------
# Metrics
# ---------------------------------------------------------------------------
m1, m2, m3, m4 = st.columns(4)
if label is None:
    m1.metric("Disease", "model not loaded")
elif uncertain:
    m1.metric("Disease", "Uncertain")
else:
    m1.metric("Disease", ADVICE.get(label, {}).get("name", label))

m2.metric("Confidence",     f"{conf:.1f}%" if conf is not None else "—")
m3.metric("Severity index", f"{sev:.1f}%",  grade(sev))
m4.metric("Inference time", f"{ms:.0f} ms"  if ms else "—")

# Probability bar chart
if probs is not None:
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
        try:
            ok = save_inspection(
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
            if ok:
                st.session_state["_last_saved"] = image_hash
        except RuntimeError as db_err:
            st.error(f"Could not save: {db_err}")

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
        "or product label and be checked by an agriculture officer."
    )

# ---------------------------------------------------------------------------
# Report + Telegram
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

if st.button("Send report to Telegram"):
    if not tg_token or not tg_chat:
        st.error("Enter bot token and chat id in the sidebar first.")
    else:
        try:
            ok, msg = _send_telegram(tg_token, tg_chat, overlay, report)
            st.success("Sent.") if ok else st.error(f"Telegram error: {msg}")
        except Exception as e:
            st.error(f"Could not send (check internet): {e}")
