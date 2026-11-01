r"""AgriVision Paddy Inspector - software prototype (laptop demo).

Run from the project folder:
    venv2\Scripts\python.exe -m streamlit run app\app.py

Put these two files next to app.py (they come from the training step):
    paddy_int8.tflite
    labels.txt          (one class name per line)

Without the model the app still works for the OpenCV severity part.
"""
import hashlib
import io
import json
import time
from datetime import datetime
from pathlib import Path

import cv2
import numpy as np
import requests
import streamlit as st
from PIL import Image

# ---------------------------------------------------------------------------
# DB init – wrapped in try/except so a broken DB never crashes the whole app
# ---------------------------------------------------------------------------
try:
    from history_db import init_db, save_inspection
    from history_dashboard import show_history_dashboard
    _db_available = True
    init_db()
except Exception as _db_init_err:
    _db_available = False
    _db_init_msg = str(_db_init_err)

HERE = Path(__file__).parent
DEFAULT_LABELS = ["blast", "blb", "brown_spot", "healthy", "other"]

# Short advisory text only. NO doses: doses must come from the current TNAU
# guide or the product label, and be checked by an agriculture officer.
ADVICE = {
    "blast": {
        "name": "Rice Blast",
        "en": "Spindle-shaped lesions with grey centres. Confirm with an agriculture "
              "officer and use the fungicide recommended in the TNAU guide. Avoid "
              "excess nitrogen and manage field water.",
        "ta": "குலை நோய்: வேளாண் அலுவலரிடம் உறுதிசெய்து, TNAU பரிந்துரைத்த "
              "பூஞ்சைக்கொல்லியைப் பயன்படுத்தவும். அதிக தழைச்சத்து உரத்தைத் "
              "தவிர்க்கவும்; வயலில் நீர் மேலாண்மையைப் பின்பற்றவும்.",
    },
    "blb": {
        "name": "Bacterial Leaf Blight",
        "en": "Yellow-to-white stripes from the leaf tip or edges. This is NOT a fungal "
              "disease, so a fungicide will not help. Follow the agriculture officer's "
              "advice, drain standing water and reduce nitrogen.",
        "ta": "பாக்டீரியல் இலைக்கருகல்: இது பூஞ்சை நோய் அல்ல. வேளாண் அலுவலரின் "
              "ஆலோசனைப்படி பரிந்துரைக்கப்பட்ட மருந்தைப் பயன்படுத்தவும். தேங்கிய நீரை "
              "வடித்து, தழைச்சத்தைக் குறைக்கவும்.",
    },
    "brown_spot": {
        "name": "Brown Spot",
        "en": "Small round-to-oval brown spots, often linked to nutrient stress "
              "(for example potassium). For higher severity, use a fungicide as per the "
              "TNAU guide. Consider seed treatment next season.",
        "ta": "பழுப்பு புள்ளி நோய்: பொட்டாசியம் போன்ற ஊட்டச்சத்துக் குறைபாடு "
              "இருக்கலாம். தீவிரமாக இருந்தால் வேளாண் அலுவலரின் பரிந்துரைப்படி "
              "பூஞ்சைக்கொல்லி பயன்படுத்தவும்; அடுத்த பருவத்தில் விதை நேர்த்தி செய்யவும்.",
    },
    "healthy": {
        "name": "Healthy",
        "en": "No disease detected. No spray needed. Keep scouting regularly.",
        "ta": "இலை ஆரோக்கியமாக உள்ளது. மருந்து தெளிக்க வேண்டாம்; தொடர்ந்து "
              "கண்காணிக்கவும்.",
    },
    "other": {
        "name": "Other disease or damage",
        "en": "Possibly tungro, leaf smut, leaf scald, narrow brown spot or a nutrient "
              "problem. Show the leaf to the nearest agriculture officer.",
        "ta": "வேறு நோய் அல்லது பாதிப்பு இருக்கலாம் (துங்ரோ, இலைக்கருகல் போன்றவை). "
              "அருகிலுள்ள வேளாண் அலுவலரை அணுகவும்.",
    },
}


# ---------------------------------------------------------------------------
# Model helpers
# ---------------------------------------------------------------------------

@st.cache_resource(show_spinner=False)
def load_interpreter(path: str):
    """Load the TFLite interpreter, trying three runtimes in order."""
    try:
        from ai_edge_litert.interpreter import Interpreter
    except Exception:
        try:
            from tflite_runtime.interpreter import Interpreter
        except Exception:
            import tensorflow as tf
            Interpreter = tf.lite.Interpreter
    interp = Interpreter(model_path=path, num_threads=4)
    interp.allocate_tensors()
    return interp


def load_labels(path: str) -> list[str]:
    p = Path(path)
    if p.exists():
        names = [x.strip() for x in p.read_text(encoding="utf-8").splitlines() if x.strip()]
        if names:
            return names
    return DEFAULT_LABELS


def classify(interp, img_rgb: np.ndarray) -> tuple[np.ndarray, float]:
    """Return (probabilities, milliseconds). The model has Rescaling inside,
    so it takes raw 0-255 pixels."""
    inp = interp.get_input_details()[0]
    out = interp.get_output_details()[0]
    h, w = int(inp["shape"][1]), int(inp["shape"][2])
    x = cv2.resize(img_rgb, (w, h), interpolation=cv2.INTER_AREA)
    x = x.astype(np.uint8) if inp["dtype"] == np.uint8 else x.astype(np.float32)
    interp.set_tensor(inp["index"], np.expand_dims(x, 0))
    t0 = time.perf_counter()
    interp.invoke()
    ms = (time.perf_counter() - t0) * 1000.0
    y = interp.get_tensor(out["index"])[0].astype(np.float32)
    if out["dtype"] == np.uint8:
        scale, zero = out["quantization"]
        y = (y - zero) * scale
    y = np.clip(y, 0, None)
    return y / max(float(y.sum()), 1e-9), ms


# ---------------------------------------------------------------------------
# Severity (OpenCV)
# ---------------------------------------------------------------------------

def severity(img_rgb: np.ndarray, sat_min: int, lesion_hue_max: int) -> tuple[float, np.ndarray]:
    """Return (lesion_percent, overlay_image).

    Leaf region = largest green area (holes filled).
    Lesion      = brown/tan pixels inside the leaf mask.
    Pale veins are not counted because they are low-saturation green.
    """
    hsv = cv2.cvtColor(img_rgb, cv2.COLOR_RGB2HSV)
    hue, sat, val = cv2.split(hsv)
    green = (
        (hue >= lesion_hue_max) & (hue <= 95) & (sat >= sat_min) & (val >= 40)
    ).astype(np.uint8) * 255
    green = cv2.morphologyEx(green, cv2.MORPH_OPEN, np.ones((5, 5), np.uint8))
    k = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (41, 41))
    closed = cv2.morphologyEx(green, cv2.MORPH_CLOSE, k)
    contours, _ = cv2.findContours(closed, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    leaf = np.zeros_like(closed)
    if contours:
        c = max(contours, key=cv2.contourArea)
        cv2.drawContours(leaf, [c], -1, 255, thickness=-1)
    brown = ((hue < lesion_hue_max) & (sat >= sat_min) & (val >= 40)).astype(np.uint8) * 255
    lesion = (leaf > 0) & (brown > 0)
    lesion = cv2.morphologyEx(
        lesion.astype(np.uint8) * 255, cv2.MORPH_OPEN, np.ones((3, 3), np.uint8)
    ) > 0
    total = int(np.count_nonzero(leaf))
    pct = 100.0 * int(np.count_nonzero(lesion)) / total if total else 0.0
    overlay = img_rgb.copy()
    overlay[lesion] = (0.5 * overlay[lesion] + 0.5 * np.array([255, 0, 0])).astype(np.uint8)
    return pct, overlay


def grade(pct: float) -> str:
    if pct < 1:
        return "Very low (monitor)"
    if pct < 10:
        return "Moderate"
    if pct < 25:
        return "High"
    return "Severe (urgent)"


# ---------------------------------------------------------------------------
# Telegram
# ---------------------------------------------------------------------------

def send_telegram(token: str, chat_id: str, photo_rgb: np.ndarray, caption: str) -> tuple[bool, str]:
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


# ============================================================== UI ===========
st.set_page_config(page_title="AgriVision Paddy Inspector", layout="wide")
st.title("AgriVision Paddy Inspector")
st.caption(
    "Software prototype. Raspberry Pi 4 + camera + LED chamber integration is the next phase."
)

# Show DB init failure once, prominently, but do not crash
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
        st.error("Database is unavailable. Cannot show history.")
    st.stop()

# ---------------------------------------------------------------------------
# Sidebar – Settings
# ---------------------------------------------------------------------------
with st.sidebar:
    st.header("Settings")
    model_path  = st.text_input("Model file",   str(HERE / "paddy_int8.tflite"))
    labels_path = st.text_input("Labels file",  str(HERE / "labels.txt"))
    conf_min    = st.slider("Minimum confidence (%)", 40, 95, 70)

    st.subheader("Severity (OpenCV)")
    sat_min = st.slider("Leaf saturation minimum",        10, 120, 40)
    hue_max = st.slider("Lesion hue below (brown/yellow)", 10,  40, 28)
    crop    = st.slider("Ignore image edges (%)",           0,  40,  0)

    st.subheader("Report")
    location = st.text_input("Location (GPS module comes later)", "Erode, Tamil Nadu")
    tg_token = st.text_input("Telegram bot token (optional)", type="password")
    tg_chat  = st.text_input("Telegram chat id (optional)")

    st.subheader("Auto-save")
    auto_save = st.checkbox(
        "Auto-save results",
        value=True,
        help="When enabled, each new image is automatically saved to the inspection database.",
    )

# ---------------------------------------------------------------------------
# Image input
# ---------------------------------------------------------------------------
tab_up, tab_cam = st.tabs(["Upload leaf photo", "Use camera"])
with tab_up:
    up  = st.file_uploader("Paddy leaf image", type=["jpg", "jpeg", "png"])
with tab_cam:
    cam = st.camera_input("Take a photo of the leaf")

# Remember which tab provided the image so we can record the source
img_source = "camera" if cam else ("upload" if up else None)
src = cam or up

if src is None:
    st.info(
        "Upload or capture a paddy leaf photo to start. "
        "Use a plain white or grey background for best severity results."
    )
    st.stop()

# ---------------------------------------------------------------------------
# Pre-process image
# ---------------------------------------------------------------------------
img = np.array(Image.open(src).convert("RGB"))
if max(img.shape[:2]) > 1280:
    s   = 1280 / max(img.shape[:2])
    img = cv2.resize(img, None, fx=s, fy=s, interpolation=cv2.INTER_AREA)

m = int(min(img.shape[:2]) * crop / 100)
if m > 0:
    img = img[m:img.shape[0] - m, m:img.shape[1] - m]

# ---------------------------------------------------------------------------
# Classification
# ---------------------------------------------------------------------------
labels = load_labels(labels_path)
label, conf, ms, probs = None, None, None, None
model_version = Path(model_path).name  # e.g. 'paddy_int8.tflite'

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
# Display
# ---------------------------------------------------------------------------
c1, c2 = st.columns(2)
c1.image(img,     caption="Input leaf",                   use_container_width=True)
c2.image(overlay, caption="Detected diseased area (red)", use_container_width=True)

m1, m2, m3, m4 = st.columns(4)
uncertain = label is not None and conf < conf_min

# ---------------------------------------------------------------------------
# Auto-save
# ---------------------------------------------------------------------------
if label is not None:
    # SHA-256 of the raw pixel array identifies this exact image
    image_hash = hashlib.sha256(img.tobytes()).hexdigest()
    new_image  = image_hash != st.session_state.get("last_saved_image_hash")

    if auto_save and new_image and _db_available:
        # Build a human-readable disease name (with Uncertain prefix if needed)
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
                # ---- new keyword arguments (Phase 1) ----
                image_hash     = image_hash,
                probabilities  = probs.tolist() if probs is not None else None,
                uncertain      = uncertain,
                source         = img_source,
                model_version  = model_version,
                created_at     = datetime.now().astimezone().isoformat(timespec="seconds"),
            )
            if saved:
                st.session_state["last_saved_image_hash"] = image_hash
            # If saved is False it means this exact image_hash is already in the DB –
            # silently skip; no need to warn the user.
        except RuntimeError as db_err:
            st.error(f"Could not save inspection: {db_err}")

# ---------------------------------------------------------------------------
# Metrics
# ---------------------------------------------------------------------------
if label is None:
    m1.metric("Disease", "model not loaded")
elif uncertain:
    m1.metric("Disease", "Uncertain")
else:
    m1.metric("Disease", ADVICE.get(label, {}).get("name", label))

m2.metric("Confidence",     f"{conf:.1f}%" if conf is not None else "-")
m3.metric("Severity index", f"{sev:.1f}%", grade(sev))
m4.metric("Inference time", f"{ms:.0f} ms" if ms is not None else "-")

if probs is not None:
    st.bar_chart(
        {(labels[i] if i < len(labels) else str(i)): float(p) * 100
         for i, p in enumerate(probs)}
    )

# ---------------------------------------------------------------------------
# Advisory
# ---------------------------------------------------------------------------
advice_en = advice_ta = ""
if label is not None and uncertain:
    st.warning(
        "Confidence is low. Retake the photo (single leaf, plain background, good light) "
        "or consult an agriculture officer."
    )
elif label in ADVICE:
    advice_en, advice_ta = ADVICE[label]["en"], ADVICE[label]["ta"]
    st.subheader("Advisory")
    st.write(advice_en)
    st.write(advice_ta)
    st.caption(
        "Decision support only. Doses must come from the current TNAU guide or the "
        "product label and be checked by an agriculture officer."
    )

# ---------------------------------------------------------------------------
# Report text area
# ---------------------------------------------------------------------------
name   = ADVICE.get(label, {}).get("name", label or "n/a")
report = (
    f"AgriVision Paddy Inspector\nDisease: {name}"
    + (f" ({conf:.0f}%)" if conf else "")
    + f"\nSeverity: {sev:.1f}% - {grade(sev)}\nLocation: {location}"
)
if advice_en:
    report += f"\nAdvice: {advice_en}\n{advice_ta}"
st.text_area("Report", report, height=180)

# ---------------------------------------------------------------------------
# Telegram
# ---------------------------------------------------------------------------
if st.button("Send report to Telegram"):
    if not tg_token or not tg_chat:
        st.error("Enter the bot token and chat id in the sidebar first.")
    else:
        try:
            ok, msg = send_telegram(tg_token, tg_chat, overlay, report)
            st.success("Sent.") if ok else st.error(f"Telegram error: {msg}")
        except Exception as e:
            st.error(f"Could not send (check internet): {e}")
