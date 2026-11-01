"""
core/classifier.py  –  TFLite inference helpers.

Keeps the Streamlit-cached interpreter separate from the UI so this module
can also be imported by tests and the future Pi CLI without Streamlit.
"""

import time

import cv2
import numpy as np
import streamlit as st

# ---------------------------------------------------------------------------
# Interpreter loader (cached per model path so weights stay in memory)
# ---------------------------------------------------------------------------

@st.cache_resource(show_spinner=False)
def load_interpreter(path: str):
    """Load a TFLite model and return an allocated interpreter."""
    try:
        from tflite_runtime.interpreter import Interpreter
    except ImportError:
        try:
            from ai_edge_litert.interpreter import Interpreter
        except ImportError:
            from tensorflow.lite.python.interpreter import Interpreter

    interp = Interpreter(model_path=str(path), num_threads=4)
    interp.allocate_tensors()
    return interp


# ---------------------------------------------------------------------------
# Inference
# ---------------------------------------------------------------------------

def classify(interp, img_rgb: np.ndarray) -> tuple[np.ndarray, float]:
    """Run inference on a single RGB image.

    The paddy_int8.tflite model has a Rescaling layer inside, so it accepts
    raw uint8 pixels (0-255).  INT8 output is dequantized here.

    Returns
    -------
    probs : np.ndarray
        Softmax probabilities, shape (num_classes,), dtype float32, sum ~ 1.0.
    ms : float
        Wall-clock inference time in milliseconds.
    """
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
