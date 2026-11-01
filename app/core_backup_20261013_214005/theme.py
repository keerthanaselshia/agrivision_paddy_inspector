"""
core/theme.py  –  Global visual theme for AgriVision Paddy Inspector.

Call apply_theme() once at the top of every page before any other widgets.
Call render_header() to replace the plain st.title / st.caption with a
branded green-gradient header card.
Call sidebar_logo() inside a `with st.sidebar:` block.

Colour palette (agriculture / paddy harvest):
  Primary    #1b5e20  deep forest green
  Surface    #2e7d32  medium green
  Light      #aed581  lime-green accent
  Background #f9fbe7  warm near-white
  Gold       #f9a825  harvest gold (used sparingly)
"""

import streamlit as st

# ---------------------------------------------------------------------------
# CSS (injected once via st.markdown)
# ---------------------------------------------------------------------------
_CSS = """
<style>

/* ── 1. Hide default Streamlit chrome ───────────────────────── */
#MainMenu, header[data-testid="stHeader"], footer { display: none !important; }

/* ── 2. Body & main column ───────────────────────────────────── */
html, body, [class*="css"] {
    font-family: 'Segoe UI', 'Inter', Arial, sans-serif;
}
.main .block-container {
    padding-top: 1.2rem;
    padding-bottom: 2.5rem;
}

/* ── 3. Sidebar ───────────────────────────────────────────────── */
[data-testid="stSidebar"] {
    background: linear-gradient(175deg, #1b5e20 0%, #2e7d32 55%, #33691e 100%) !important;
}
/* sidebar text */
[data-testid="stSidebar"] p,
[data-testid="stSidebar"] span,
[data-testid="stSidebar"] label,
[data-testid="stSidebar"] div[data-testid="stMarkdownContainer"] {
    color: #c8e6c9 !important;
}
/* sidebar headings */
[data-testid="stSidebar"] h1,
[data-testid="stSidebar"] h2,
[data-testid="stSidebar"] h3 {
    color: #ffffff !important;
    font-weight: 700 !important;
    border-bottom: 1px solid rgba(255,255,255,0.18);
    padding-bottom: 5px;
    margin-top: 14px !important;
    margin-bottom: 6px !important;
}
/* sidebar inputs */
[data-testid="stSidebar"] input[type="text"],
[data-testid="stSidebar"] input[type="password"] {
    background: rgba(255,255,255,0.13) !important;
    color: #ffffff !important;
    border-color: rgba(255,255,255,0.28) !important;
    border-radius: 6px !important;
}
[data-testid="stSidebar"] input[type="text"]::placeholder {
    color: rgba(255,255,255,0.45) !important;
}
/* sidebar radio */
[data-testid="stSidebar"] [data-testid="stRadio"] label p {
    color: #e8f5e9 !important;
    font-size: 1em !important;
    font-weight: 500 !important;
}
/* sidebar slider track */
[data-testid="stSidebar"] [data-testid="stSlider"] div[role="slider"] {
    background: #a5d6a7 !important;
}
/* sidebar checkbox */
[data-testid="stSidebar"] [data-testid="stCheckbox"] label p {
    color: #dcedc8 !important;
}
/* sidebar expander */
[data-testid="stSidebar"] .streamlit-expanderHeader {
    background: rgba(255,255,255,0.10) !important;
    border: 1px solid rgba(255,255,255,0.20) !important;
    border-radius: 8px !important;
    color: #dcedc8 !important;
}

/* ── 4. Metric cards ──────────────────────────────────────────── */
[data-testid="metric-container"] {
    background: linear-gradient(140deg, #f9fbe7 0%, #f1f8e9 100%) !important;
    border: 1.5px solid #aed581 !important;
    border-radius: 12px !important;
    padding: 14px 18px !important;
    box-shadow: 0 2px 10px rgba(46,125,50,0.08) !important;
    transition: transform 0.15s, box-shadow 0.15s !important;
}
[data-testid="metric-container"]:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 5px 16px rgba(46,125,50,0.15) !important;
}
[data-testid="metric-container"] [data-testid="stMetricLabel"] p {
    color: #558b2f !important;
    font-weight: 700 !important;
    font-size: 0.78em !important;
    text-transform: uppercase;
    letter-spacing: 0.07em;
}
[data-testid="metric-container"] [data-testid="stMetricValue"] {
    color: #1b5e20 !important;
    font-size: 1.55em !important;
    font-weight: 800 !important;
}
[data-testid="metric-container"] [data-testid="stMetricDelta"] {
    color: #33691e !important;
    font-weight: 600 !important;
}

/* ── 5. Buttons ───────────────────────────────────────────────── */
.stButton > button {
    border-radius: 8px !important;
    font-weight: 700 !important;
    transition: all 0.2s !important;
    letter-spacing: 0.03em;
}
.stButton > button[kind="primary"] {
    background: linear-gradient(135deg, #2e7d32 0%, #43a047 100%) !important;
    color: #ffffff !important;
    border: none !important;
    padding: 11px 0 !important;
    font-size: 1.08em !important;
    box-shadow: 0 4px 16px rgba(46,125,50,0.32) !important;
}
.stButton > button[kind="primary"]:hover {
    background: linear-gradient(135deg, #1b5e20 0%, #2e7d32 100%) !important;
    box-shadow: 0 6px 22px rgba(46,125,50,0.42) !important;
    transform: translateY(-2px) !important;
}
.stButton > button[kind="secondary"] {
    border: 2px solid #aed581 !important;
    color: #2e7d32 !important;
    background: #f9fbe7 !important;
}
.stButton > button[kind="secondary"]:hover {
    background: #f1f8e9 !important;
    border-color: #2e7d32 !important;
}

/* ── 6. Tabs ──────────────────────────────────────────────────── */
.stTabs [data-baseweb="tab-list"] {
    background: #f1f8e9 !important;
    border-radius: 10px !important;
    padding: 5px !important;
    gap: 4px !important;
}
.stTabs [data-baseweb="tab"] {
    border-radius: 7px !important;
    font-weight: 600 !important;
    color: #33691e !important;
    padding: 7px 18px !important;
    background: transparent !important;
}
.stTabs [aria-selected="true"] {
    background: #2e7d32 !important;
    color: #ffffff !important;
}
.stTabs [data-baseweb="tab-border"] { display: none !important; }

/* ── 7. Bordered containers ───────────────────────────────────── */
[data-testid="stVerticalBlockBorderWrapper"] > div {
    border: 1.5px solid #c8e6c9 !important;
    border-radius: 14px !important;
    background: #fafff8 !important;
    box-shadow: 0 2px 10px rgba(0,0,0,0.04) !important;
    padding: 4px 2px !important;
}

/* ── 8. Expanders ─────────────────────────────────────────────── */
.streamlit-expanderHeader {
    background: #f1f8e9 !important;
    border: 1.5px solid #c8e6c9 !important;
    border-radius: 10px !important;
    color: #2e7d32 !important;
    font-weight: 700 !important;
    transition: background 0.15s !important;
}
.streamlit-expanderHeader:hover {
    background: #e8f5e9 !important;
}
.streamlit-expanderContent {
    border: 1.5px solid #c8e6c9 !important;
    border-top: none !important;
    border-radius: 0 0 10px 10px !important;
    background: #fafff8 !important;
}

/* ── 9. Alerts ────────────────────────────────────────────────── */
[data-testid="stAlert"] {
    border-radius: 10px !important;
    border-left-width: 5px !important;
}

/* ── 10. Section headings ─────────────────────────────────────── */
h1 { color: #1b5e20 !important; font-weight: 800 !important; }
h2 { color: #2e7d32 !important; font-weight: 700 !important; }
h3 { color: #33691e !important; font-weight: 700 !important; }

/* ── 11. File uploader drop zone ──────────────────────────────── */
[data-testid="stFileUploadDropzone"] {
    border: 2.5px dashed #aed581 !important;
    border-radius: 12px !important;
    background: #f9fbe7 !important;
    transition: all 0.2s;
}
[data-testid="stFileUploadDropzone"]:hover {
    border-color: #2e7d32 !important;
    background: #f1f8e9 !important;
}

/* ── 12. Dataframe ─────────────────────────────────────────────── */
[data-testid="stDataFrame"] thead tr th {
    background: #e8f5e9 !important;
    color: #1b5e20 !important;
    font-weight: 700 !important;
}
[data-testid="stDataFrame"] tbody tr:nth-child(even) {
    background: #f9fbe7 !important;
}

/* ── 13. Divider ───────────────────────────────────────────────── */
hr { border-color: #c8e6c9 !important; }

/* ── 14. Caption / small text ──────────────────────────────────── */
.stCaption p, [data-testid="stCaptionContainer"] p {
    color: #6a8f4a !important;
}

/* ── 15. Info / selectbox / text input ────────────────────────── */
[data-testid="stTextInput"] input {
    border-radius: 8px !important;
    border-color: #aed581 !important;
}
[data-testid="stTextInput"] input:focus {
    border-color: #2e7d32 !important;
    box-shadow: 0 0 0 2px rgba(46,125,50,0.15) !important;
}
[data-testid="stTextArea"] textarea {
    border-radius: 8px !important;
    border-color: #aed581 !important;
    font-size: 0.9em !important;
}

</style>
"""

# ---------------------------------------------------------------------------
# HTML header banner (replaces st.title + st.caption)
# ---------------------------------------------------------------------------
_HEADER_HTML = """
<div style="
    background: linear-gradient(135deg, #1b5e20 0%, #2e7d32 55%, #558b2f 100%);
    padding: 26px 36px 22px 32px;
    border-radius: 16px;
    margin-bottom: 22px;
    box-shadow: 0 6px 24px rgba(27,94,32,0.28);
    display: flex;
    align-items: center;
    gap: 22px;
">
    <div style="font-size:3.2em;line-height:1;filter:drop-shadow(0 2px 4px rgba(0,0,0,0.3));">
        🌾
    </div>
    <div>
        <div style="color:#ffffff;font-size:1.85em;font-weight:900;
                    letter-spacing:-0.5px;line-height:1.15;
                    text-shadow:0 2px 6px rgba(0,0,0,0.20);">
            AgriVision Paddy Inspector
        </div>
        <div style="color:#a5d6a7;font-size:0.88em;margin-top:5px;font-weight:400;
                    letter-spacing:0.02em;">
            AI-powered paddy leaf disease detection &nbsp;·&nbsp;
            Kongu Engineering College, Erode
        </div>
    </div>
    <div style="margin-left:auto;text-align:right;">
        <div style="background:rgba(255,255,255,0.15);border-radius:20px;
                    padding:5px 14px;font-size:0.76em;color:#dcedc8;
                    border:1px solid rgba(255,255,255,0.25);
                    backdrop-filter:blur(4px);">
            🧪 Prototype
        </div>
    </div>
</div>
"""

# ---------------------------------------------------------------------------
# Sidebar logo / app identity block
# ---------------------------------------------------------------------------
_SIDEBAR_LOGO_HTML = """
<div style="text-align:center;padding:18px 0 14px 0;
            border-bottom:1px solid rgba(255,255,255,0.18);
            margin-bottom:14px;">
    <div style="font-size:2.6em;line-height:1;">🌾</div>
    <div style="color:#ffffff;font-weight:900;font-size:1.05em;
                margin-top:6px;letter-spacing:0.02em;">AgriVision</div>
    <div style="color:#a5d6a7;font-size:0.75em;margin-top:2px;">Paddy Inspector</div>
</div>
"""

# ---------------------------------------------------------------------------
# Section divider with label
# ---------------------------------------------------------------------------
def section_header(icon: str, title: str) -> None:
    """Render a styled section title with a coloured left bar."""
    st.markdown(
        f"""
        <div style="display:flex;align-items:center;gap:10px;
                    margin:18px 0 10px 0;">
          <div style="width:4px;height:28px;background:#2e7d32;
                      border-radius:3px;flex-shrink:0;"></div>
          <div style="font-size:1.12em;font-weight:700;color:#1b5e20;">
            {icon}&nbsp; {title}
          </div>
        </div>""",
        unsafe_allow_html=True,
    )


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def apply_theme() -> None:
    """Inject global CSS. Call once at the start of every page."""
    st.markdown(_CSS, unsafe_allow_html=True)


def render_header() -> None:
    """Render the green gradient branded header banner."""
    st.markdown(_HEADER_HTML, unsafe_allow_html=True)


def sidebar_logo() -> None:
    """Render the app logo/identity block inside the sidebar."""
    st.sidebar.markdown(_SIDEBAR_LOGO_HTML, unsafe_allow_html=True)
