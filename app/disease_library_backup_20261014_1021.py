"""
disease_library.py  –  Disease Library page for AgriVision Paddy Inspector.

Dark smart-agriculture theme.  Content is driven by app/data/advisory.json
so an agriculture expert can update descriptions without touching any code.
"""

import streamlit as st
from core.advisory import ADVICE
from core.theme    import apply_theme, section_header

# ---------------------------------------------------------------------------
# Dark-theme cause-type badges  (bg, text, label)
# ---------------------------------------------------------------------------
_CAUSE_STYLE = {
    "Fungal":    ("rgba(46,229,157,0.12)",  "#2ee59d",  "🍄 Fungal"),
    "Bacterial": ("rgba(255,159,67,0.12)",  "#ff9f43",  "🦠 Bacterial"),
    "Viral":     ("rgba(200,100,255,0.12)", "#c864ff",  "🔬 Viral"),
    "Various":   ("rgba(138,184,154,0.10)", "#8ab89a",  "⚠️ Various"),
    "None":      ("rgba(46,229,157,0.10)",  "#2ee59d",  "✅ No disease"),
}

_VALIDATION_TAG = (
    '<span style="background:rgba(255,209,102,0.15);color:#ffd166;'
    'border:1px solid rgba(255,209,102,0.35);border-radius:6px;'
    'padding:2px 9px;font-size:0.73em;font-weight:700;'
    'font-family:Poppins,sans-serif;letter-spacing:0.04em;">'
    "⚠️ Needs expert validation"
    "</span>"
)


def _cause_badge(cause_type: str) -> str:
    bg, fg, label = _CAUSE_STYLE.get(
        cause_type, ("rgba(138,184,154,0.10)", "#8ab89a", f"🔍 {cause_type}")
    )
    return (
        f'<span style="background:{bg};color:{fg};'
        f'border:1px solid {fg}40;border-radius:14px;'
        f'padding:4px 14px;font-size:0.82em;font-weight:700;'
        f'font-family:Poppins,sans-serif;letter-spacing:0.04em;">'
        f"{label}</span>"
    )


def _col_label(text: str, tag: str = "") -> None:
    """Render a column header with optional tag HTML."""
    st.markdown(
        f'<div style="font-family:Poppins,sans-serif;font-weight:700;'
        f'color:#eaf4ec;font-size:0.88em;margin-bottom:8px;">'
        f"{text}&nbsp;&nbsp;{tag}</div>",
        unsafe_allow_html=True,
    )


def _disease_card(label: str, info: dict) -> None:
    """Render one disease card in the dark theme."""
    name_en   = info.get("name", label)
    name_ta   = info.get("name_ta", "")
    sci       = info.get("scientific", "")
    cause     = info.get("cause_type", "")
    needs_val = info.get("tamil_needs_validation", True)

    with st.container(border=True):
        # ── header ──────────────────────────────────────────────────────────
        head_l, head_r = st.columns([3, 2])

        with head_l:
            st.markdown(
                f'<div style="font-family:Poppins,sans-serif;font-weight:800;'
                f'font-size:1.18em;color:#eaf4ec;margin-bottom:2px;">'
                f"{name_en}</div>"
                + (f'<div style="font-style:italic;color:#5a7a65;font-size:0.84em;'
                   f'font-family:Poppins,sans-serif;">{sci}</div>' if sci else ""),
                unsafe_allow_html=True,
            )

        with head_r:
            st.markdown(
                f'<div style="text-align:right;margin-top:4px;">'
                f'{_cause_badge(cause)}</div>'
                + (f'<div style="text-align:right;color:#8ab89a;'
                   f'font-family:Poppins,sans-serif;font-size:1em;'
                   f'margin-top:6px;">{name_ta}</div>' if name_ta else ""),
                unsafe_allow_html=True,
            )

        # ── tabs ─────────────────────────────────────────────────────────────
        tab_sym, tab_cond, tab_mgmt = st.tabs(
            ["🔍 Symptoms", "🌡️ Conditions", "🌱 Management"]
        )

        val_tag = _VALIDATION_TAG if needs_val else ""

        with tab_sym:
            col_en, col_ta = st.columns(2)
            with col_en:
                _col_label("English")
                st.markdown(
                    f'<div style="color:#b8d4c0;font-size:0.9em;'
                    f'line-height:1.65;font-family:Poppins,sans-serif;">'
                    f'{info.get("symptoms_en","—")}</div>',
                    unsafe_allow_html=True,
                )
            with col_ta:
                _col_label("Tamil", val_tag)
                st.markdown(
                    f'<div style="color:#8ab89a;font-size:0.9em;'
                    f'line-height:1.65;font-family:Poppins,sans-serif;">'
                    f'{info.get("symptoms_ta","—")}</div>',
                    unsafe_allow_html=True,
                )

        with tab_cond:
            col_en, col_ta = st.columns(2)
            with col_en:
                _col_label("English")
                st.markdown(
                    f'<div style="color:#b8d4c0;font-size:0.9em;'
                    f'line-height:1.65;font-family:Poppins,sans-serif;">'
                    f'{info.get("conditions_en","—")}</div>',
                    unsafe_allow_html=True,
                )
            with col_ta:
                _col_label("Tamil", val_tag)
                st.markdown(
                    f'<div style="color:#8ab89a;font-size:0.9em;'
                    f'line-height:1.65;font-family:Poppins,sans-serif;">'
                    f'{info.get("conditions_ta","—")}</div>',
                    unsafe_allow_html=True,
                )

        with tab_mgmt:
            col_en, col_ta = st.columns(2)
            with col_en:
                _col_label("English")
                st.markdown(
                    f'<div style="color:#b8d4c0;font-size:0.9em;'
                    f'line-height:1.8;font-family:Poppins,sans-serif;">'
                    f'{info.get("en_full","—")}</div>',
                    unsafe_allow_html=True,
                )
            with col_ta:
                _col_label("Tamil", val_tag)
                st.markdown(
                    f'<div style="color:#8ab89a;font-size:0.9em;'
                    f'line-height:1.8;font-family:Poppins,sans-serif;">'
                    f'{info.get("ta_full","—")}</div>',
                    unsafe_allow_html=True,
                )

            # No-doses disclaimer
            st.markdown(
                '<div style="background:rgba(255,209,102,0.07);'
                'border-left:3px solid rgba(255,209,102,0.5);'
                'border-radius:6px;padding:8px 14px;margin-top:12px;'
                'color:#ffd16699;font-size:0.78em;'
                'font-family:Poppins,sans-serif;">'
                "⚠️ No pesticide doses shown. Confirm product and dose with "
                "the current TNAU Crop Protection Guide or a licensed agriculture officer."
                "</div>",
                unsafe_allow_html=True,
            )


# ---------------------------------------------------------------------------
# Main page
# ---------------------------------------------------------------------------

def show_disease_library() -> None:
    apply_theme()
    section_header("📚", "Disease Library")

    st.markdown(
        '<div style="color:#8ab89a;font-size:0.88em;'
        'font-family:Poppins,sans-serif;margin-bottom:18px;">'
        "Reference guide for paddy leaf diseases. Content is stored in "
        "<code>app/data/advisory.json</code> — editable without touching code."
        "</div>",
        unsafe_allow_html=True,
    )

    # Search
    search = st.text_input(
        "🔍 Search diseases",
        placeholder="e.g. blast · fungal · yellow stripe · பழுப்பு…",
        label_visibility="collapsed",
    )

    # Filter
    q = search.strip().lower()
    matches = []
    for lbl, info in ADVICE.items():
        if not q:
            matches.append(lbl)
            continue
        haystack = " ".join([
            info.get("name", ""), info.get("name_ta", ""),
            info.get("scientific", ""), info.get("cause_type", ""),
            info.get("symptoms_en", ""), info.get("conditions_en", ""),
            info.get("en_full", ""),
        ]).lower()
        if q in haystack:
            matches.append(lbl)

    if not matches:
        st.markdown(
            '<div style="color:#8ab89a;font-style:italic;padding:20px 0;">'
            "No diseases match your search. Try a different keyword.</div>",
            unsafe_allow_html=True,
        )
        return

    st.markdown(
        f'<div style="color:#5a7a65;font-size:0.8em;margin-bottom:12px;">'
        f"Showing {len(matches)} of {len(ADVICE)} disease(s)</div>",
        unsafe_allow_html=True,
    )

    for lbl in matches:
        _disease_card(lbl, ADVICE[lbl])

    st.divider()
    st.markdown(
        '<div style="color:#5a7a65;font-size:0.78em;line-height:1.6;">'
        "Tamil text marked <b style='color:#ffd166;'>⚠️ Needs expert validation</b> "
        "has not been reviewed by a qualified Tamil-speaking agriculture officer. "
        "Do not use it in official printed material until validated."
        "</div>",
        unsafe_allow_html=True,
    )
