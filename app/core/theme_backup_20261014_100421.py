"""
core/theme.py  –  Dark "smart-agriculture" theme for AgriVision Paddy Inspector.

Palette
-------
  bg        #0b1f14   deep forest night (main background)
  surface   #12301f   card surfaces
  surface2  #1a3d28   nested / hover surface
  accent    #2ee59d   fresh bright green (primary CTA, highlights)
  accent2   #1db976   medium green (secondary)
  warning   #ffd166   harvest gold (caution, uncertain)
  error     #ff5d5d   alert red (severe, poor quality)
  text      #eaf4ec   near-white text
  muted     #8ab89a   muted green-grey (labels, captions)
  border    #1e4d30   subtle border between surfaces

Public API
----------
  apply_theme()      – inject CSS via st.markdown (call once per page)
  render_header()    – hero banner with title, tagline and badges
  sidebar_logo()     – branding block at the top of the sidebar
  section_header(icon, title) – styled section divider
"""

import textwrap
import streamlit as st

# ---------------------------------------------------------------------------
# CSS
# ---------------------------------------------------------------------------
_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;500;600;700;800;900&display=swap');

/* ── 0. Global font + hide Streamlit chrome ───────────────────── */
html, body, [class*="css"] {
    font-family: 'Poppins', 'Segoe UI', Arial, sans-serif !important;
}
#MainMenu, header[data-testid="stHeader"], footer { display:none !important; }

/* ── 1. App & main background ─────────────────────────────────── */
.stApp,
[data-testid="stAppViewContainer"],
[data-testid="stMain"],
.main {
    background-color: #0b1f14 !important;
}
.main .block-container {
    background-color: #0b1f14 !important;
    padding-top: 1rem !important;
    padding-bottom: 3rem !important;
    max-width: 1150px !important;
}

/* ── 2. Default text ──────────────────────────────────────────── */
p, span, div, li, td, th {
    color: #eaf4ec;
}
h1, h2, h3, h4, h5 {
    font-family: 'Poppins', sans-serif !important;
    color: #eaf4ec !important;
    font-weight: 700 !important;
}

/* ── 3. Sidebar ───────────────────────────────────────────────── */
[data-testid="stSidebar"],
[data-testid="stSidebar"] > div:first-child {
    background: #091a0f !important;
    border-right: 1px solid #1e4d30 !important;
}
[data-testid="stSidebar"] p,
[data-testid="stSidebar"] span,
[data-testid="stSidebar"] label {
    color: #8ab89a !important;
    font-family: 'Poppins', sans-serif !important;
}
[data-testid="stSidebar"] h1,
[data-testid="stSidebar"] h2,
[data-testid="stSidebar"] h3 {
    color: #2ee59d !important;
    font-size: 0.72em !important;
    font-weight: 700 !important;
    text-transform: uppercase;
    letter-spacing: 0.12em;
    border-bottom: 1px solid #1e4d30;
    padding-bottom: 5px;
    margin-top: 18px !important;
    margin-bottom: 8px !important;
}
[data-testid="stSidebar"] input[type="text"],
[data-testid="stSidebar"] input[type="password"] {
    background: #12301f !important;
    color: #eaf4ec !important;
    border: 1px solid #1e4d30 !important;
    border-radius: 8px !important;
}
[data-testid="stSidebar"] input:focus {
    border-color: #2ee59d !important;
    box-shadow: 0 0 0 2px rgba(46,229,157,0.18) !important;
    outline: none !important;
}
/* radio labels */
[data-testid="stSidebar"] [data-testid="stRadio"] label {
    font-size: 0.95em !important;
    font-weight: 500 !important;
    padding: 6px 10px !important;
    border-radius: 8px !important;
    transition: background 0.2s !important;
}
[data-testid="stSidebar"] [data-testid="stRadio"] label:hover {
    background: #1a3d28 !important;
}
[data-testid="stSidebar"] [data-testid="stRadio"] label p {
    color: #8ab89a !important;
    font-weight: 500 !important;
}
/* sidebar expander */
[data-testid="stSidebar"] details > summary {
    background: #12301f !important;
    border: 1px solid #1e4d30 !important;
    border-radius: 8px !important;
    color: #8ab89a !important;
    padding: 8px 12px !important;
    cursor: pointer !important;
}
[data-testid="stSidebar"] .streamlit-expanderHeader {
    background: #12301f !important;
    border: 1px solid #1e4d30 !important;
    border-radius: 8px !important;
    color: #8ab89a !important;
}
/* slider thumb */
[data-testid="stSidebar"] [role="slider"] {
    background: #2ee59d !important;
    border-color: #2ee59d !important;
}
/* checkbox */
[data-testid="stSidebar"] [data-baseweb="checkbox"] div[data-checked="true"] {
    background: #2ee59d !important;
    border-color: #2ee59d !important;
}

/* ── 4. Metric cards ──────────────────────────────────────────── */
[data-testid="metric-container"] {
    background: linear-gradient(145deg, #12301f 0%, #1a3d28 100%) !important;
    border: 1px solid rgba(46,229,157,0.18) !important;
    border-radius: 16px !important;
    padding: 16px 20px !important;
    box-shadow: 0 4px 24px rgba(0,0,0,0.35) !important;
    transition: transform 0.2s, box-shadow 0.2s, border-color 0.2s !important;
}
[data-testid="metric-container"]:hover {
    transform: translateY(-3px) !important;
    border-color: rgba(46,229,157,0.45) !important;
    box-shadow: 0 8px 32px rgba(46,229,157,0.12) !important;
}
[data-testid="metric-container"] [data-testid="stMetricLabel"] p {
    color: #8ab89a !important;
    font-size: 0.72em !important;
    font-weight: 600 !important;
    text-transform: uppercase;
    letter-spacing: 0.1em;
}
[data-testid="metric-container"] [data-testid="stMetricValue"] {
    color: #2ee59d !important;
    font-size: 1.65em !important;
    font-weight: 800 !important;
}
[data-testid="metric-container"] [data-testid="stMetricDelta"] {
    color: #8ab89a !important;
    font-weight: 600 !important;
    font-size: 0.85em !important;
}

/* ── 5. Primary button ────────────────────────────────────────── */
.stButton > button {
    font-family: 'Poppins', sans-serif !important;
    font-weight: 700 !important;
    border-radius: 10px !important;
    transition: all 0.25s !important;
    letter-spacing: 0.04em !important;
}
.stButton > button[kind="primary"] {
    background: linear-gradient(135deg, #2ee59d 0%, #1db976 100%) !important;
    color: #0b1f14 !important;
    border: none !important;
    padding: 12px 0 !important;
    font-size: 1.05em !important;
    box-shadow: 0 4px 20px rgba(46,229,157,0.38) !important;
}
.stButton > button[kind="primary"]:hover {
    background: linear-gradient(135deg, #5ff0ba 0%, #2ee59d 100%) !important;
    box-shadow: 0 6px 28px rgba(46,229,157,0.55) !important;
    transform: translateY(-2px) !important;
}
.stButton > button[kind="secondary"],
.stButton > button:not([kind]) {
    background: #12301f !important;
    color: #2ee59d !important;
    border: 1.5px solid rgba(46,229,157,0.35) !important;
}
.stButton > button[kind="secondary"]:hover,
.stButton > button:not([kind]):hover {
    background: #1a3d28 !important;
    border-color: #2ee59d !important;
    color: #5ff0ba !important;
}

/* ── 6. Tabs ──────────────────────────────────────────────────── */
.stTabs [data-baseweb="tab-list"] {
    background: #12301f !important;
    border: 1px solid #1e4d30 !important;
    border-radius: 12px !important;
    padding: 5px !important;
    gap: 4px !important;
}
.stTabs [data-baseweb="tab"] {
    background: transparent !important;
    color: #8ab89a !important;
    font-weight: 600 !important;
    border-radius: 8px !important;
    padding: 7px 18px !important;
    transition: all 0.2s !important;
    font-family: 'Poppins', sans-serif !important;
}
.stTabs [data-baseweb="tab"]:hover {
    background: #1a3d28 !important;
    color: #eaf4ec !important;
}
.stTabs [aria-selected="true"] {
    background: linear-gradient(135deg,
        rgba(46,229,157,0.18) 0%,
        rgba(29,185,118,0.22) 100%) !important;
    color: #2ee59d !important;
    font-weight: 700 !important;
    border-bottom: 2px solid #2ee59d !important;
}
.stTabs [data-baseweb="tab-border"] { display:none !important; }
.stTabs [data-baseweb="tab-panel"] { padding-top: 16px !important; }

/* ── 7. Bordered containers ───────────────────────────────────── */
[data-testid="stVerticalBlockBorderWrapper"] > div {
    background: #12301f !important;
    border: 1px solid #1e4d30 !important;
    border-radius: 16px !important;
    box-shadow: 0 4px 24px rgba(0,0,0,0.3) !important;
}

/* ── 8. Expanders ─────────────────────────────────────────────── */
.streamlit-expanderHeader {
    background: #12301f !important;
    border: 1px solid #1e4d30 !important;
    border-radius: 12px !important;
    color: #2ee59d !important;
    font-weight: 600 !important;
    font-family: 'Poppins', sans-serif !important;
    transition: background 0.2s, border-color 0.2s !important;
}
.streamlit-expanderHeader:hover {
    background: #1a3d28 !important;
    border-color: rgba(46,229,157,0.4) !important;
}
.streamlit-expanderContent {
    background: #0f2819 !important;
    border: 1px solid #1e4d30 !important;
    border-top: none !important;
    border-radius: 0 0 12px 12px !important;
}

/* ── 9. Alerts ────────────────────────────────────────────────── */
[data-testid="stAlert"] {
    border-radius: 12px !important;
    border-left-width: 4px !important;
    background: #12301f !important;
}
[data-testid="stAlert"] p { color: #eaf4ec !important; }

/* ── 10. Text / textarea inputs ───────────────────────────────── */
input[type="text"], input[type="password"],
[data-testid="stTextInput"] input,
[data-testid="stTextArea"] textarea {
    background: #12301f !important;
    color: #eaf4ec !important;
    border: 1px solid #1e4d30 !important;
    border-radius: 10px !important;
    font-family: 'Poppins', sans-serif !important;
}
input:focus, textarea:focus {
    border-color: #2ee59d !important;
    box-shadow: 0 0 0 2px rgba(46,229,157,0.2) !important;
    outline: none !important;
}

/* ── 11. File uploader ────────────────────────────────────────── */
[data-testid="stFileUploadDropzone"] {
    background: #12301f !important;
    border: 2px dashed rgba(46,229,157,0.4) !important;
    border-radius: 14px !important;
    transition: all 0.2s !important;
}
[data-testid="stFileUploadDropzone"]:hover {
    border-color: #2ee59d !important;
    background: #1a3d28 !important;
}
[data-testid="stFileUploadDropzone"] p,
[data-testid="stFileUploadDropzone"] span {
    color: #8ab89a !important;
}

/* ── 12. Camera input ─────────────────────────────────────────── */
[data-testid="stCameraInputButton"],
[data-testid="stCameraInput"] > div {
    background: #12301f !important;
    border: 1px solid #1e4d30 !important;
    border-radius: 14px !important;
}

/* ── 13. Dataframe ────────────────────────────────────────────── */
[data-testid="stDataFrame"] iframe {
    border-radius: 12px !important;
}

/* ── 14. Widget labels ────────────────────────────────────────── */
[data-testid="stWidgetLabel"] p {
    color: #8ab89a !important;
    font-size: 0.83em !important;
    font-weight: 600 !important;
    letter-spacing: 0.04em;
}

/* ── 15. Captions ─────────────────────────────────────────────── */
[data-testid="stCaptionContainer"] p,
.stCaption p { color: #5a7a65 !important; font-size: 0.8em !important; }

/* ── 16. Divider ──────────────────────────────────────────────── */
hr { border-color: #1e4d30 !important; margin: 20px 0 !important; }

/* ── 17. Scrollbar ────────────────────────────────────────────── */
::-webkit-scrollbar { width: 5px; height: 5px; }
::-webkit-scrollbar-track { background: #0b1f14; }
::-webkit-scrollbar-thumb { background: #1e4d30; border-radius: 4px; }
::-webkit-scrollbar-thumb:hover { background: rgba(46,229,157,0.3); }

/* ── 18. Bar chart wrapper ────────────────────────────────────── */
[data-testid="stArrowVegaLiteChart"] > div,
[data-testid="stVegaLiteChart"] > div {
    background: #12301f !important;
    border-radius: 12px !important;
    border: 1px solid #1e4d30 !important;
    padding: 8px !important;
}

</style>
"""

# ---------------------------------------------------------------------------
# Header & Badges
# ---------------------------------------------------------------------------

def render_header() -> None:
    """Render the hero header banner with title and badges."""
    col_left, col_right = st.columns([3.6, 1.4])

    with col_left:
        st.markdown(
            textwrap.dedent("""
<div style="display:flex;align-items:center;gap:18px;">
<div style="font-size:3.0em;line-height:1;filter:drop-shadow(0 0 18px rgba(46,229,157,0.65));">🌿</div>
<div>
<div style="font-family:'Poppins',sans-serif;font-size:1.85em;font-weight:900;color:#eaf4ec;letter-spacing:-0.02em;line-height:1.15;text-shadow:0 2px 10px rgba(0,0,0,0.4);">
AgriVision Paddy Inspector
</div>
<div style="font-family:'Poppins',sans-serif;font-size:0.90em;color:#2ee59d;font-weight:500;margin-top:5px;letter-spacing:0.06em;">
Scan.&nbsp; Detect.&nbsp; Protect your paddy.
</div>
</div>
</div>
            """).strip(),
            unsafe_allow_html=True,
        )

    with col_right:
        st.markdown(
            textwrap.dedent("""
<div style="display:flex;flex-direction:column;gap:6px;align-items:flex-end;">
<span style="background:rgba(46,229,157,0.12);color:#2ee59d;border:1px solid rgba(46,229,157,0.3);border-radius:20px;padding:4px 12px;font-size:0.72em;font-weight:700;font-family:'Poppins',sans-serif;letter-spacing:0.05em;white-space:nowrap;">⚡ Edge AI</span>
<span style="background:rgba(255,209,102,0.10);color:#ffd166;border:1px solid rgba(255,209,102,0.25);border-radius:20px;padding:4px 12px;font-size:0.72em;font-weight:700;font-family:'Poppins',sans-serif;letter-spacing:0.05em;white-space:nowrap;">🧪 Prototype</span>
</div>
            """).strip(),
            unsafe_allow_html=True,
        )

    st.markdown(
        textwrap.dedent("""
<div style="display:flex;gap:8px;flex-wrap:wrap;margin:14px 0 22px 0;padding-top:14px;border-top:1px solid rgba(255,255,255,0.06);">
<span style="background:#1a3d28;color:#8ab89a;border:1px solid #1e4d30;border-radius:20px;padding:4px 14px;font-size:0.75em;font-weight:600;font-family:'Poppins',sans-serif;">📶 Works offline</span>
<span style="background:#1a3d28;color:#8ab89a;border:1px solid #1e4d30;border-radius:20px;padding:4px 14px;font-size:0.75em;font-weight:600;font-family:'Poppins',sans-serif;">🌐 Tamil + English</span>
<span style="background:#1a3d28;color:#8ab89a;border:1px solid #1e4d30;border-radius:20px;padding:4px 14px;font-size:0.75em;font-weight:600;font-family:'Poppins',sans-serif;">🤖 MobileNetV2 INT8</span>
<span style="background:#1a3d28;color:#8ab89a;border:1px solid #1e4d30;border-radius:20px;padding:4px 14px;font-size:0.75em;font-weight:600;font-family:'Poppins',sans-serif;">🍃 4 disease classes</span>
</div>
        """).strip(),
        unsafe_allow_html=True,
    )


# ---------------------------------------------------------------------------
# Sidebar logo / identity block
# ---------------------------------------------------------------------------
_SIDEBAR_LOGO_HTML = textwrap.dedent("""
<link href="https://fonts.googleapis.com/css2?family=Poppins:wght@700;900&display=swap" rel="stylesheet">
<div style="text-align:center;padding:24px 12px 18px 12px;border-bottom:1px solid #1e4d30;margin-bottom:8px;">
<div style="font-size:2.4em;line-height:1;filter:drop-shadow(0 0 14px rgba(46,229,157,0.55));">🌿</div>
<div style="font-family:'Poppins',sans-serif;font-weight:900;font-size:1.0em;color:#eaf4ec;margin-top:8px;letter-spacing:0.02em;">AgriVision</div>
<div style="font-family:'Poppins',sans-serif;font-size:0.72em;color:#2ee59d;letter-spacing:0.14em;text-transform:uppercase;margin-top:2px;font-weight:600;">Paddy Inspector</div>
<div style="margin-top:10px;display:inline-block;background:rgba(46,229,157,0.1);border:1px solid rgba(46,229,157,0.25);border-radius:20px;padding:3px 12px;font-size:0.68em;color:#2ee59d;font-family:'Poppins',sans-serif;font-weight:600;">v1.0 · Prototype</div>
</div>
""").strip()


# ---------------------------------------------------------------------------
# Section header with left accent bar
# ---------------------------------------------------------------------------
def section_header(icon: str, title: str) -> None:
    html = textwrap.dedent(f"""
<div style="display:flex;align-items:center;gap:12px;margin:22px 0 12px 0;">
<div style="width:4px;height:26px;background:linear-gradient(180deg,#2ee59d,#1db976);border-radius:4px;flex-shrink:0;"></div>
<div style="font-family:'Poppins',sans-serif;font-size:1.05em;font-weight:700;color:#eaf4ec;letter-spacing:0.01em;">
{icon}&nbsp; {title}
</div>
</div>
    """).strip()
    st.markdown(html, unsafe_allow_html=True)


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def apply_theme() -> None:
    """Inject global dark CSS. Call once per page, after set_page_config."""
    st.markdown(_CSS, unsafe_allow_html=True)


def sidebar_logo() -> None:
    """Render the branding block at the top of the sidebar."""
    st.sidebar.markdown(_SIDEBAR_LOGO_HTML, unsafe_allow_html=True)

