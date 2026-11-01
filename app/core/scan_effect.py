"""
core/scan_effect.py  –  Scanning animation overlaid ON the leaf image.

Public API
----------
image_to_data_uri(pil_image, max_side=800) -> str
    Resize + JPEG-encode a PIL image and return a base64 data URI so it can
    be embedded directly in HTML without a separate HTTP request.

scanning_html(data_uri, label="Scanning leaf...") -> str
    Return a self-contained HTML string that shows the leaf image with a
    live scanning effect on top of it:
        - Light green tint over the whole image
        - Glowing green scan line sweeping top <-> bottom
        - Four pulsing corner brackets
        - A small label bar at the bottom of the image

All CSS is scoped under unique class names (agv-* prefix) so it cannot
accidentally affect other Streamlit elements.
No JavaScript.  Works in any browser including the Raspberry Pi Chromium.
"""

from __future__ import annotations

import base64
import io

from PIL import Image

from core.theme import clean_html


# ---------------------------------------------------------------------------
# Image → base64 data URI
# ---------------------------------------------------------------------------

def image_to_data_uri(pil_image: Image.Image, max_side: int = 800) -> str:
    """Resize (aspect-preserving) and encode a PIL image as a JPEG data URI.

    Parameters
    ----------
    pil_image : PIL.Image.Image
        Source image in any mode.
    max_side : int
        Maximum pixel size on the longer side before encoding.
        Keeps the embedded data URI small; 800 px is enough for display.

    Returns
    -------
    str – "data:image/jpeg;base64,<base64-encoded JPEG>"
    """
    img = pil_image.convert("RGB")
    w, h = img.size
    if max(w, h) > max_side:
        scale = max_side / max(w, h)
        new_w = max(1, int(w * scale))
        new_h = max(1, int(h * scale))
        img = img.resize((new_w, new_h), Image.LANCZOS)

    buf = io.BytesIO()
    img.save(buf, format="JPEG", quality=85, optimize=True)
    b64 = base64.b64encode(buf.getvalue()).decode("ascii")
    return f"data:image/jpeg;base64,{b64}"


# ---------------------------------------------------------------------------
# Scanning HTML
# ---------------------------------------------------------------------------

def scanning_html(data_uri: str, label: str = "Scanning leaf...") -> str:
    """Return HTML that displays the leaf image with a live scan effect on top.

    The returned string is safe to pass to
        st.markdown(..., unsafe_allow_html=True)
    or to inject into an st.empty() placeholder.

    Layout (all positions are relative to the image area only):
    ┌──[TL bracket]──────────────[TR bracket]──┐
    │  ░░░░░░░  green tint overlay  ░░░░░░░░░  │
    │  ─────── glowing scan line ──────────    │
    │                                          │
    └──[BL bracket]──[Scanning leaf...]──[BR]──┘

    Parameters
    ----------
    data_uri : str
        Base64 data URI as returned by image_to_data_uri().
    label : str
        Text shown in the bottom badge bar.
    """
    return clean_html(f"""
<style>
/* Wrapper — establishes the stacking context for the overlay elements.
   display:block + width:100% makes it fill the Streamlit column. */
.agv-img-wrap {{
  position: relative;
  display: block;
  width: 100%;
  max-width: 100%;
  overflow: hidden;
  border-radius: 6px;
  line-height: 0;        /* removes the inline-block gap below the img tag */
  box-shadow: 0 0 0 2px rgba(0,230,118,0.6);
}}

/* The actual leaf image — fills the wrapper, no extra space */
.agv-img-wrap img.agv-leaf {{
  display: block;
  width: 100%;
  max-width: 100%;
  height: auto;
  border-radius: 6px;
}}

/* Light green tint: rgba so the image is still visible underneath */
.agv-tint {{
  position: absolute;
  inset: 0;
  background: rgba(0, 230, 118, 0.10);
  pointer-events: none;
  border-radius: 6px;
}}

/* Glowing scan line — sweeps from top to bottom and back (alternate) */
.agv-scanline {{
  position: absolute;
  left: 0;
  right: 0;
  height: 4px;
  background: linear-gradient(
    90deg,
    transparent          0%,
    rgba(0,230,118,0.55) 20%,
    rgba(190,255,220,1)  50%,
    rgba(0,230,118,0.55) 80%,
    transparent          100%
  );
  box-shadow: 0 0 12px 4px rgba(0, 230, 118, 0.45);
  pointer-events: none;
  animation: agv-sweep 1.8s ease-in-out infinite alternate;
}}
@keyframes agv-sweep {{
  from {{ top: 0px; }}
  to   {{ top: calc(100% - 4px); }}
}}

/* Corner bracket shared style */
.agv-corner {{
  position: absolute;
  width: 20px;
  height: 20px;
  pointer-events: none;
  animation: agv-blink 1.0s ease-in-out infinite;
}}
@keyframes agv-blink {{
  0%, 100% {{ opacity: 1;    }}
  50%       {{ opacity: 0.2; }}
}}

/* Individual corner positions and borders */
.agv-tl {{
  top: 8px; left: 8px;
  border-top:  3px solid #00e676;
  border-left: 3px solid #00e676;
}}
.agv-tr {{
  top: 8px; right: 8px;
  border-top:   3px solid #00e676;
  border-right: 3px solid #00e676;
}}
.agv-bl {{
  bottom: 36px; left: 8px;   /* 36px leaves room above the badge */
  border-bottom: 3px solid #00e676;
  border-left:   3px solid #00e676;
}}
.agv-br {{
  bottom: 36px; right: 8px;
  border-bottom: 3px solid #00e676;
  border-right:  3px solid #00e676;
}}

/* Bottom label badge */
.agv-badge {{
  position: absolute;
  bottom: 0; left: 0; right: 0;
  background: rgba(0, 0, 0, 0.60);
  color: #00e676;
  font-family: 'Courier New', monospace;
  font-size: 0.80em;
  letter-spacing: 0.12em;
  text-align: center;
  padding: 6px 0 7px 0;
  line-height: 1;
  pointer-events: none;
  animation: agv-blink 1.0s ease-in-out infinite;
}}
</style>

<div class="agv-img-wrap">
  <img class="agv-leaf" src="{data_uri}" alt="Leaf image being scanned" />
  <div class="agv-tint"></div>
  <div class="agv-scanline"></div>
  <div class="agv-corner agv-tl"></div>
  <div class="agv-corner agv-tr"></div>
  <div class="agv-corner agv-bl"></div>
  <div class="agv-corner agv-br"></div>
  <div class="agv-badge">&#x1F50D;&nbsp; {label}</div>
</div>
""")
