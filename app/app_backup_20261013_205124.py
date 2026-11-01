r"""AgriVision Paddy Inspector  –  UI entry point.

Run from the project root (C:\Users\keert\paddy_dataset):
    venv2\Scripts\python.exe -m streamlit run app\app.py

UI-only file.  All logic lives in app\core\ modules.
Prototype disclaimer: trained on public datasets only.
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
from core.classifier import load_interpreter, classify
from core.severity   import severity, grade
from core.advisory   import ADVICE
from core.reports    import build_text_report

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

# ---------------------------------------------------------------------------
# Scanning animation  (pure HTML + CSS, works in any browser incl. Pi)
# ---------------------------------------------------------------------------
_SCAN_HTML = """
<style>
  .agv-wrap {
    position: relative;
    background: #0a1628;
    border: 2px solid #00e676;
    border-radius: 10px;
    padding: 38px 28px 28px 28px;
    margin: 6px 0 14px 0;
    overflow: hidden;
    font-family: 'Courier New', monospace;
  }
  /* moving scan line */
  .agv-line {
    position: absolute;
    left: 0; right: 0;
    height: 3px;
    background: linear-gradient(90deg,
      transparent 0%, #00e676 40%, #b9ffdc 50%, #00e676 60%, transparent 100%);
    box-shadow: 0 0 10px #00e676, 0 0 20px #00e676;
    animation: agv-scan 1.8s linear infinite;
  }
  @keyframes agv-scan { from { top: 0%; } to { top: 100%; } }

  /* corner brackets */
  .agv-c { position: absolute; width: 22px; height: 22px; }
  .agv-tl { top:10px; left:10px;
    border-top: 3px solid #00e676; border-left: 3px solid #00e676; }
  .agv-tr { top:10px; right:10px;
    border-top: 3px solid #00e676; border-right: 3px solid #00e676; }
  .agv-bl { bottom:10px; left:10px;
    border-bottom: 3px solid #00e676; border-left: 3px solid #00e676; }
  .agv-br { bottom:10px; right:10px;
    border-bottom: 3px solid #00e676; border-right: 3px solid #00e676; }
  .agv-c { animation: agv-pulse 1.1s ease-in-out infinite; }
  @keyframes agv-pulse { 0%,100%{opacity:1} 50%{opacity:0.25} }

  /* main label */
  .agv-title {
    text-align: center;
    color: #00e676;
    font-size: 1.15em;
    letter-spacing: 0.14em;
    margin-bottom: 6px;
    animation: agv-pulse 1.1s ease-in-out infinite;
  }
  .agv-sub {
    text-align: center;
    color: #4caf84;
    font-size: 0.78em;
    letter-spacing: 0.06em;
    margin-bottom: 16px;
  }
  /* scrolling data lines */
  .agv-data {
    color: #2e7d52;
    font-size: 0.72em;
    line-height: 1.9;
    border-top: 1px solid #1a3a2a;
    padding-top: 10px;
  }
  .agv-data span {
    display: inline-block;
    animation: agv-fade 2s ease-in-out infinite;
  }
  .agv-data span:nth-child(2) { animation-delay: 0.4s; }
  .agv-data span:nth-child(3) { animation-delay: 0.8s; }
  @keyframes agv-fade { 0%,100%{opacity:0.4} 50%{opacity:1} }
</style>

<div class="agv-wrap">
  <div class="agv-line"></div>
  <div class="agv-c agv-tl"></div>
  <div class="agv-c agv-tr"></div>
  <div class="agv-c agv-bl"></div>
  <div class="agv-c agv-br"></div>
  <div class="agv-title">&#x1F52C; ANALYZING LEAF &hellip;</div>
  <div class="agv-sub">MobileNetV2 &nbsp;|&nbsp; INT8 &nbsp;|&nbsp; 224&times;224</div>
  <div class="agv-data">
    <span>&#x25B8; Extracting visual features &hellip;</span><br>
    <span>&#x25B8; Running disease classifier &hellip;</span><br>
    <span>&#x25B8; Computing severity index &hellip;</span>
  </div>
</div>
"""

_MIN_SCAN_MS = 1500   # animation shown for at least this long (ms)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _send_telegram(token, chat_id, photo_rgb, caption):
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


def _load_labels(path):
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
        f"Could not open the inspection database. "
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

# Use a short hash to detect when the user loads a new image
_img_id = hashlib.md5(img.tobytes()).hexdigest()[:16]

# Clear stored scan results whenever the image changes
if st.session_state.get("_img_id") != _img_id:
    st.session_state.pop("_scan", None)
    st.session_state["_img_id"] = _img_id

# ---------------------------------------------------------------------------
# Image display (left column always shows original; right fills after scan)
# ---------------------------------------------------------------------------
col_img, col_ovl = st.columns(2)
col_img.image(img, caption="Input leaf", use_container_width=True)

# Placeholder for overlay image (shown after scan completes)
ovl_placeholder = col_ovl.empty()
if "_scan" not in st.session_state:
    ovl_placeholder.info("Press **Scan Leaf** to analyse.")

# ---------------------------------------------------------------------------
# Scan button + animation
# ---------------------------------------------------------------------------
scan_clicked = st.button("🔍 Scan Leaf", type="primary", use_container_width=True)
anim_slot    = st.empty()   # will hold the animation OR the results area

if scan_clicked:
    # 1. Show animation immediately (browser renders CSS while Python runs)
    anim_slot.markdown(_SCAN_HTML, unsafe_allow_html=True)

    # 2. Classification
    probs, ms, label, conf = None, 0.0, None, None
    model_err = None
    if Path(model_path).exists():
        try:
            probs, ms = classify(load_interpreter(model_path), img)
            i     = int(np.argmax(probs))
            label = labels[i] if i < len(labels) else f"class_{i}"
            conf  = float(probs[i]) * 100
        except Exception as exc:
            model_err = str(exc)
    else:
        model_err = "Model file not found."

    # 3. Severity (fast – no inference)
    sev, _ = severity(img, sat_min, hue_max)

    # 4. Store results
    st.session_state["_scan"] = {
        "probs":     probs.tolist() if probs is not None else None,
        "ms":        ms,
        "label":     label,
        "conf":      conf,
        "sev":       sev,
        "model_err": model_err,
    }

    # 5. Hold animation for the minimum visible time
    wait_s = max(0.0, (_MIN_SCAN_MS - ms) / 1000.0)
    if wait_s > 0:
        time.sleep(wait_s)

    # 6. Clear animation and refresh to show results
    anim_slot.empty()
    st.rerun()

# ---------------------------------------------------------------------------
# Results (shown on all reruns once a scan has been done)
# ---------------------------------------------------------------------------
if "_scan" not in st.session_state:
    st.stop()   # nothing to show yet

sc        = st.session_state["_scan"]
label     = sc["label"]
conf      = sc["conf"]
ms        = sc["ms"]
sev       = sc["sev"]
model_err = sc["model_err"]
probs     = np.array(sc["probs"]) if sc["probs"] is not None else None

# Recompute overlay (pure OpenCV, very fast, avoids storing large arrays)
_, overlay = severity(img, sat_min, hue_max)
ovl_placeholder.image(overlay, caption="Detected diseased area (red)", use_container_width=True)

uncertain = label is not None and conf < conf_min

if model_err:
    st.warning(f"Classifier: {model_err} — showing severity only.")

# Metrics
m1, m2, m3, m4 = st.columns(4)
if label is None:
    m1.metric("Disease", "model not loaded")
elif uncertain:
    m1.metric("Disease", "Uncertain")
else:
    m1.metric("Disease", ADVICE.get(label, {}).get("name", label))

m2.metric("Confidence",     f"{conf:.1f}%" if conf is not None else "—")
m3.metric("Severity index", f"{sev:.1f}%", grade(sev))
m4.metric("Inference time", f"{ms:.0f} ms" if ms else "—")

# Probability chart
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
