"""
disease_library.py  –  Disease Library page for AgriVision Paddy Inspector.

Features:
  • Trilingual support (English, தமிழ், Tanglish)
  • 2-line symptoms summary on cards with audio playback
  • Reference leaf images extracted from local dataset for every disease class
  • Full detail page structured into clear icon sections:
      - 🔍 Symptoms (What you see): ordered leaf symptoms & other parts
      - 📋 How to check ("Does your leaf look like this?"): interactive checklist
      - 💨 How it spreads & Favourable conditions
      - 🛡️ Prevention across three stages (before planting, during crop, after harvest + limit spread)
      - 🧑‍🌾 When to call the Agriculture Officer
      - ⚖️ Similar looking problems & Compare with my scan
      - 💬 Embedded AgriVision Expert Q&A Chat
  • Data-driven via app/data/disease_info.json
"""

from pathlib import Path
from PIL import Image
import streamlit as st

try:
    from core.advisory import ADVICE, get_disease
    from core.theme import apply_theme, section_header, render_html, clean_html
    from core.speech import render_tts_button, render_read_all_button
    from core.qa_engine import ask_question, get_example_questions
except ImportError:
    from app.core.advisory import ADVICE, get_disease
    from app.core.theme import apply_theme, section_header, render_html, clean_html
    from app.core.speech import render_tts_button, render_read_all_button
    from app.core.qa_engine import ask_question, get_example_questions

_PROJECT_ROOT = Path(__file__).resolve().parent.parent

# ---------------------------------------------------------------------------
# Styling and badges
# ---------------------------------------------------------------------------
_CAUSE_STYLE = {
    "Fungal":        ("rgba(46,229,157,0.12)",  "#2ee59d",  "🍄 Fungal"),
    "Bacterial":     ("rgba(255,159,67,0.12)",  "#ff9f43",  "🦠 Bacterial"),
    "Viral":         ("rgba(200,100,255,0.12)", "#c864ff",  "🔬 Viral"),
    "Physiological": ("rgba(100,181,246,0.14)", "#64b5f6",  "🧪 Nutrient / Abiotic"),
    "Various":       ("rgba(138,184,154,0.10)", "#8ab89a",  "⚠️ Various"),
    "None":          ("rgba(46,229,157,0.10)",  "#2ee59d",  "✅ No disease"),
}

_VERIFY_TAG = (
    '<span style="background:rgba(255,209,102,0.14);color:#ffd166;'
    'border:1px solid rgba(255,209,102,0.35);border-radius:6px;'
    'padding:2px 8px;font-size:0.72em;font-weight:700;'
    'font-family:Poppins,sans-serif;letter-spacing:0.03em;">'
    "⚠️ To be verified against TNAU"
    "</span>"
)


def _cause_badge(cause_type: str) -> str:
    bg, fg, label = _CAUSE_STYLE.get(
        cause_type, ("rgba(138,184,154,0.10)", "#8ab89a", f"🔍 {cause_type}")
    )
    return (
        f'<span style="background:{bg};color:{fg};'
        f'border:1px solid {fg}40;border-radius:14px;'
        f'padding:4px 12px;font-size:0.80em;font-weight:700;'
        f'font-family:Poppins,sans-serif;letter-spacing:0.04em;">'
        f"{label}</span>"
    )


def _resolve_image_path(rel_path: str) -> Path | None:
    """Find the full file path for a static reference image."""
    candidates = [
        _PROJECT_ROOT / "app" / rel_path,
        _PROJECT_ROOT / rel_path,
        Path(__file__).resolve().parent / rel_path,
    ]
    for p in candidates:
        if p.exists() and p.is_file():
            return p
    return None


def _get_field(info: dict, base_key: str, lang: str):
    """Retrieve field in requested language with fallback to en."""
    val = info.get(f"{base_key}_{lang}")
    if val:
        return val
    return info.get(f"{base_key}_en") or info.get(f"{base_key}_ta") or info.get(base_key) or ""


# ---------------------------------------------------------------------------
# "Compare with My Scan" Component
# ---------------------------------------------------------------------------
def _render_compare_view(disease_key: str, lang: str = "en"):
    """Show side-by-side comparison between user scanned leaf and reference image."""
    title = "Compare With My Scan" if lang == "en" else ("எனது பரிசோதனையுடன் ஒப்பிடுக" if lang == "ta" else "Enadhu Scan-udan Oppiduga")
    section_header("🔬", title)

    scan_data = st.session_state.get("_scan", {})
    last_leaf = st.session_state.get("_last_leaf_image")
    info = ADVICE.get(disease_key, {})

    col_l, col_r = st.columns(2)
    with col_l:
        st.markdown("**Your Scanned Leaf**" if lang == "en" else ("**உங்கள் நெற்பயிர் இலை**" if lang == "ta" else "**Unga Scanned Ilai**"))
        if last_leaf is not None:
            st.image(last_leaf, use_container_width=True, caption="Current Field Scan")
            if scan_data:
                sev = scan_data.get("severity", 0.0)
                grade = scan_data.get("severity_grade", "—")
                conf = scan_data.get("conf", 0.0)
                st.caption(f"Detected: **{scan_data.get('label', disease_key)}** | Confidence: **{conf:.1f}%** | Severity: **{sev:.1f}% ({grade})**")
        else:
            render_html(
                '<div style="background:#12301f;border:1px dashed #1e4d30;border-radius:12px;'
                'padding:40px 20px;text-align:center;color:#8ab89a;font-family:Poppins,sans-serif;">'
                'No scan in this session yet. Go to <b>🔬 Scan</b> page to inspect a leaf.</div>'
            )

    with col_r:
        st.markdown(f"**Reference {info.get('name', disease_key)}**" if lang == "en" else (f"**மாதிரி {info.get('name_ta', disease_key)}**" if lang == "ta" else f"**Reference {info.get('name', disease_key)}**"))
        gallery = info.get("gallery_images", [])
        ref_path = _resolve_image_path(gallery[0]) if gallery else None
        if ref_path and ref_path.exists():
            st.image(str(ref_path), use_container_width=True, caption=f"Standard Reference: {info.get('name')}")
            summary = _get_field(info, "symptoms_summary", lang)
            st.caption(f"Characteristic symptoms: {summary}")
        else:
            st.info("No local reference image available for this class.")


# ---------------------------------------------------------------------------
# Detailed Disease View
# ---------------------------------------------------------------------------
def _render_disease_detail_page(lbl: str, info: dict, lang: str, speed: float):
    """Render full detail view with multi-image gallery, icon sections, and AgriVision Expert chat."""
    back_lbl = "⬅ Back to Library" if lang == "en" else ("⬅ நூலகத்திற்கு திரும்புக" if lang == "ta" else "⬅ Library-kku Thirumbavum")
    if st.button(back_lbl, key=f"back_{lbl}"):
        st.session_state["_lib_detail_key"] = None
        st.rerun()

    name_en = info.get("name", lbl)
    name_ta = info.get("name_ta", "")
    sci = info.get("scientific", "")
    cause = info.get("cause_type", "")

    # Top banner with Title and Read All
    st.markdown(f"## {name_en}  *({name_ta})*")
    if sci:
        st.markdown(f"*{sci}* &nbsp; | &nbsp; {_cause_badge(cause)} &nbsp; {_VERIFY_TAG}", unsafe_allow_html=True)

    # Audio Read-All
    s_sym = _get_field(info, "symptoms_summary", lang)
    s_spread = _get_field(info, "how_it_spreads", lang)
    s_prev = _get_field(info, "prevention_during_crop", lang)
    sections_to_read = [
        ("Disease Name", f"{name_en}, {name_ta}"),
        ("Cause", f"Caused by {cause}. {sci}"),
        ("Symptoms", s_sym),
        ("How it spreads", s_spread),
        ("Prevention", s_prev),
    ]
    render_read_all_button(sections_to_read, lang=lang, speed=speed, button_id=f"detail_read_all_{lbl}")

    # Reference Image Gallery
    gallery = info.get("gallery_images", [])
    if gallery:
        g_title = "Reference Leaf Image Gallery" if lang == "en" else ("மாதிரி இலை படத்தொகுப்பு" if lang == "ta" else "Reference Leaf Images Gallery")
        section_header("📸", g_title)
        g_cols = st.columns(len(gallery))
        for g_idx, g_rel in enumerate(gallery):
            g_path = _resolve_image_path(g_rel)
            if g_path and g_path.exists():
                with g_cols[g_idx]:
                    st.image(str(g_path), caption=f"Sample {g_idx+1}: {name_en}", use_container_width=True)

    # -----------------------------------------------------------------------
    # Section 1: 🔍 Symptoms (What you see)
    # -----------------------------------------------------------------------
    sec1_title = "Symptoms (What You See)" if lang == "en" else ("அறிகுறிகள் (இலையில் காண்பவை)" if lang == "ta" else "Symptoms (Enna theriyum)")
    section_header("🔍", sec1_title)

    sym_leaf = _get_field(info, "symptoms_leaf", lang)
    sym_other = _get_field(info, "symptoms_other_parts", lang)

    c_leaf, c_other = st.columns([1.6, 1.4])
    with c_leaf:
        st.markdown("**🍃 Leaf Symptoms (In Order of Appearance):**" if lang == "en" else ("**🍃 இலை அறிகுறிகள் (தோன்றும் வரிசையில்):**" if lang == "ta" else "**🍃 Leaf Symptoms (Varisaiyil):**"))
        if isinstance(sym_leaf, list):
            for idx, item in enumerate(sym_leaf, 1):
                st.markdown(f"**{idx}.** {item}")
        else:
            st.write(sym_leaf or "—")

    with c_other:
        st.markdown("**🌾 Other Plant Parts Affected:**" if lang == "en" else ("**🌾 பிற பாகங்களில் பாதிப்பு:**" if lang == "ta" else "**🌾 Matra Pagangalil Pathippu:**"))
        st.markdown(sym_other or "—")

    # -----------------------------------------------------------------------
    # Section 2: 📋 How to check ("Does your leaf look like this?")
    # -----------------------------------------------------------------------
    sec2_title = 'How to Check ("Does your leaf look like this?")' if lang == "en" else ('சரிபார்க்கும் முறை ("உங்கள் இலை இப்படி உள்ளதா?")' if lang == "ta" else 'Epadi Check Pannurathu ("Unga ilai ipadi irukka?")')
    section_header("📋", sec2_title)

    checks = _get_field(info, "how_to_check", lang)
    if isinstance(checks, list):
        render_html(
            '<div style="background:#12301f;border:1px solid #1e4d30;border-radius:12px;padding:14px 18px;margin-bottom:12px;">'
            '<span style="color:#2ee59d;font-weight:700;">Diagnostic Leaf Checklist:</span> '
            '<span style="color:#8ab89a;font-size:0.88em;">Tick each matching feature to confirm disease identity.</span>'
            '</div>'
        )
        for c_idx, check_txt in enumerate(checks):
            st.checkbox(check_txt, key=f"chk_leaf_{lbl}_{c_idx}")
    else:
        st.write(checks or "—")

    # -----------------------------------------------------------------------
    # Section 3: 💨 How it spreads & Favourable conditions
    # -----------------------------------------------------------------------
    sec3_title = "How It Spreads & Favourable Conditions" if lang == "en" else ("நோய் பரவும் முறை & சாதகமான சூழல்" if lang == "ta" else "Epadi Spread Aagum & Sadhagamaana Condition")
    section_header("💨", sec3_title)

    spread_txt = _get_field(info, "how_it_spreads", lang)
    fav_txt = _get_field(info, "favourable_conditions", lang)

    sp_col1, sp_col2 = st.columns(2)
    with sp_col1:
        st.markdown("**🌬️ How It Spreads:**" if lang == "en" else ("**🌬️ எவ்வாறு பரவுகிறது:**" if lang == "ta" else "**🌬️ Epadi Paravum:**"))
        st.info(spread_txt or "—")
    with sp_col2:
        st.markdown("**🌡️ Favourable Weather:**" if lang == "en" else ("**🌡️ சாதகமான வானிலை:**" if lang == "ta" else "**🌡️ Sadhagamaana Weather:**"))
        st.warning(fav_txt or "—")

    # -----------------------------------------------------------------------
    # Section 4: 🛡️ Prevention (Three Stages & Spread Limit)
    # -----------------------------------------------------------------------
    sec4_title = "Prevention & Management (Three Stages)" if lang == "en" else ("தடுப்பு & மேலாண்மை முறைகள் (மூன்று நிலைகள்)" if lang == "ta" else "Thadukkum Muraigal (3 Stages)")
    section_header("🛡️", sec4_title)

    prev_plant = _get_field(info, "prevention_before_planting", lang)
    prev_crop = _get_field(info, "prevention_during_crop", lang)
    prev_harv = _get_field(info, "prevention_after_harvest", lang)
    prev_limit = _get_field(info, "prevention_to_limit_spread", lang)

    p_tab1, p_tab2, p_tab3, p_tab4 = st.tabs([
        "🌱 Before Planting" if lang == "en" else ("🌱 நடவுக்கு முன்" if lang == "ta" else "🌱 Nadavukku Mun"),
        "🌾 During Crop Growth" if lang == "en" else ("🌾 பயிர் வளர்ச்சியின் போது" if lang == "ta" else "🌾 Payir Valarchiyin Bodhu"),
        "🚜 After Harvest" if lang == "en" else ("🚜 அறுவடைக்கு பின்" if lang == "ta" else "🚜 Aruvadaiukku Pin"),
        "🛑 To Limit Field Spread" if lang == "en" else ("🛑 பரவலைக் கட்டுப்படுத்த" if lang == "ta" else "🛑 Spread Kuraikka"),
    ])
    with p_tab1:
        st.markdown(prev_plant or "—")
    with p_tab2:
        st.markdown(prev_crop or "—")
    with p_tab3:
        st.markdown(prev_harv or "—")
    with p_tab4:
        st.markdown(prev_limit or "—")

    render_html(
        '<div style="background:rgba(255,209,102,0.07);border-left:3px solid rgba(255,209,102,0.5);'
        'border-radius:6px;padding:8px 14px;margin-top:10px;color:#ffd166;font-size:0.80em;">'
        '⚠️ Use only products and cultural practices recommended by TNAU or your local Agriculture Officer. Never use unauthorized chemicals.'
        '</div>'
    )

    # -----------------------------------------------------------------------
    # Section 5: 🧑‍🌾 When to call the Agriculture Officer
    # -----------------------------------------------------------------------
    sec5_title = "When to Call the Agriculture Officer" if lang == "en" else ("வேளாண் அலுவலரை எப்போது தொடர்பு கொள்ள வேண்டும்?" if lang == "ta" else "Eppo Agriculture Officer-ai Contact Pannanum?")
    section_header("🧑‍🌾", sec5_title)
    call_off = _get_field(info, "when_to_call_officer", lang)
    st.error(call_off or "Ask your agriculture extension officer if lesions rapidly expand or severity exceeds threshold.")

    # -----------------------------------------------------------------------
    # Section 6: ⚖️ Similar looking problems
    # -----------------------------------------------------------------------
    sec6_title = "Similar Looking Problems" if lang == "en" else ("ஒத்த அறிகுறிகள் கொண்ட பிற நோய்கள்" if lang == "ta" else "Orey Maadhiri Irukka Koodiya Matra Noigal")
    section_header("⚖️", sec6_title)
    similar_txt = _get_field(info, "similar_looking_problems", lang)
    st.markdown(similar_txt or "—")

    # Expandable side-by-side scan comparison
    with st.expander("🔬 Compare with My Scan (Side-by-side)" if lang == "en" else ("🔬 எனது பரிசோதனையுடன் ஒப்பிடுக" if lang == "ta" else "🔬 Enadhu Scan-udan Oppiduga"), expanded=False):
        _render_compare_view(lbl, lang=lang)

    st.divider()

    # -----------------------------------------------------------------------
    # Section 7: 💬 AgriVision Expert Q&A Chat
    # -----------------------------------------------------------------------
    sec7_title = "AgriVision Expert — Ask About This Disease" if lang == "en" else ("அக்ரிவிஷன் நிபுணர் — இந்த நோய் பற்றி கேளுங்கள்" if lang == "ta" else "AgriVision Expert — Indha noi pathi kelunga")
    section_header("💬", sec7_title)

    lib_chat_history_key = f"_lib_chat_history_{lbl}"
    if lib_chat_history_key not in st.session_state:
        st.session_state[lib_chat_history_key] = []

    hints = get_example_questions(lbl, lang)
    if hints:
        hint_title = "💡 Example questions you can ask:" if lang == "en" else ("💡 நீங்கள் கேட்கக்கூடிய மாதிரி கேள்விகள்:" if lang == "ta" else "💡 Neenga kekka koodiya example kelvigal:")
        hint_items = "".join([f"• <i>\"{h}\"</i><br>" for h in hints[:5]])
        render_html(
            f'<div style="color:#5a7a65;font-size:0.82em;margin-top:2px;margin-bottom:12px;line-height:1.6;background:#0d2617;padding:10px 14px;border-radius:8px;border:1px solid #1e4d30;">'
            f'<b>{hint_title}</b><br>{hint_items}</div>'
        )

    with st.form(f"lib_qa_form_{lbl}", clear_on_submit=True):
        placeholder_text = f"Ask about {name_en}..." if lang == "en" else (f"{name_ta} பற்றி கேளுங்கள்..." if lang == "ta" else f"{name_en} pathi kelunga...")
        user_q = st.text_input(
            "Ask a question",
            placeholder=placeholder_text,
            label_visibility="collapsed",
            key=f"lib_qa_input_{lbl}",
        )
        submit_q = st.form_submit_button("Send Question ➔" if lang == "en" else ("கேள்வியை அனுப்பு ➔" if lang == "ta" else "Kelviya Anuppu ➔"))

    if submit_q and user_q.strip():
        with st.spinner("Consulting knowledge base..."):
            ans_data = ask_question(
                question=user_q.strip(),
                disease_label=lbl,
                scan_metrics={"disease": name_en},
                conversation_history=st.session_state[lib_chat_history_key],
            )
            st.session_state[lib_chat_history_key].append({
                "question": user_q.strip(),
                "answer": ans_data.get("answer", ""),
                "tamil_script_answer": ans_data.get("tamil_script_answer"),
                "language": ans_data.get("language", lang),
                "intent": ans_data.get("intent", ""),
            })

    if st.session_state[lib_chat_history_key]:
        for turn_idx, turn in enumerate(st.session_state[lib_chat_history_key]):
            st.markdown(f"**🧑‍🌾 Q:** {turn['question']}")
            st.markdown(f"**🤖 A:** {turn['answer']}")
            render_tts_button(
                text=turn['answer'],
                lang=turn.get("language", lang),
                tamil_script_text=turn.get("tamil_script_answer"),
                speed=speed,
                button_id=f"lib_tts_{lbl}_{turn_idx}",
                label="🔊 Listen to Answer" if lang == "en" else ("🔊 பதிலைக் கேளுங்கள்" if lang == "ta" else "🔊 Badhilai Kelunga"),
            )
            st.markdown("---")


# ---------------------------------------------------------------------------
# Disease Card in Grid
# ---------------------------------------------------------------------------
def _disease_card(label: str, info: dict, lang: str = "en", speed: float = 1.0) -> None:
    """Render one disease card with reference photo, 2-line symptoms summary, and buttons."""
    name_en = info.get("name", label)
    name_ta = info.get("name_ta", "")
    sci     = info.get("scientific", "")
    cause   = info.get("cause_type", "")
    gallery = info.get("gallery_images", [])

    with st.container(border=True):
        row_img, row_body = st.columns([1.2, 2.8])

        with row_img:
            # Main reference photo
            first_img_path = _resolve_image_path(gallery[0]) if gallery else None
            if first_img_path and first_img_path.exists():
                st.image(str(first_img_path), use_container_width=True, caption="Reference Leaf")
            else:
                st.markdown("🌿 *(No reference photo)*")

            # Small 2-3 thumbnail gallery underneath
            if len(gallery) > 1:
                t_cols = st.columns(len(gallery))
                for idx, g_rel in enumerate(gallery):
                    g_path = _resolve_image_path(g_rel)
                    if g_path and g_path.exists():
                        with t_cols[idx]:
                            st.image(str(g_path), use_container_width=True)

        with row_body:
            # Header
            st.markdown(f"### {name_en}")
            if name_ta:
                st.markdown(f"<span style='color:#2ee59d;font-weight:600;'>{name_ta}</span>", unsafe_allow_html=True)
            if sci:
                st.caption(f"*{sci}*")

            st.markdown(f"{_cause_badge(cause)} &nbsp;&nbsp; {_VERIFY_TAG}", unsafe_allow_html=True)

            # 2-line symptoms summary
            summary = _get_field(info, "symptoms_summary", lang)
            if not summary:
                desc = info.get(f"symptoms_{lang}") or info.get("symptoms_en", "")
                summary = (desc[:140] + "...") if len(desc) > 140 else desc
            st.markdown(f"<p style='color:#b8d4c0;font-size:0.86em;margin-top:6px;line-height:1.4;'>{summary}</p>", unsafe_allow_html=True)

            # Audio Listen button + View Details button
            b1, b2 = st.columns([1.2, 1.8])
            with b1:
                tamil_script = info.get("symptoms_summary_ta") if lang == "tanglish" else None
                read_text = f"{name_en}. {summary}"
                render_tts_button(read_text, lang=lang, tamil_script_text=tamil_script, speed=speed, button_id=f"tts_card_{label}")
            with b2:
                btn_lbl = "📖 View Full Guide & Gallery" if lang == "en" else ("📖 முழு விபரம் & படங்கள்" if lang == "ta" else "📖 Full Guide & Photos")
                if st.button(btn_lbl, key=f"view_btn_{label}", use_container_width=True):
                    st.session_state["_lib_detail_key"] = label
                    st.rerun()


# ---------------------------------------------------------------------------
# Main Page Router
# ---------------------------------------------------------------------------
def show_disease_library() -> None:
    apply_theme()
    section_header("📚", "Paddy Disease Library & Reference Gallery")

    render_html(
        '<div style="color:#8ab89a;font-size:0.88em;font-family:Poppins,sans-serif;margin-bottom:14px;">'
        'Explore verified reference images, symptoms, checklist, transmission, and multi-stage prevention for every rice disease. '
        'All data is loaded from <code>app/data/disease_info.json</code>.'
        '</div>'
    )

    # Top Control Bar: Language, Speech Speed, and Compare shortcut
    c_ctrl1, c_ctrl2, c_ctrl3 = st.columns([1.5, 1.5, 2])
    with c_ctrl1:
        lang_options = ["English", "தமிழ்", "Tanglish"]
        cur_lang = st.session_state.get("lang", "en")
        cur_idx = 0 if cur_lang == "en" else (1 if cur_lang == "ta" else 2)
        lang_sel = st.selectbox("🌐 Language", lang_options, index=cur_idx, key="lib_lang")
        if lang_sel == "தமிழ்":
            lang = "ta"
        elif lang_sel == "Tanglish":
            lang = "tanglish"
        else:
            lang = "en"
        st.session_state["lang"] = lang
    with c_ctrl2:
        speed_sel = st.selectbox("🔊 Speech Speed", ["Normal (1.0x)", "Slow (0.8x)"], index=0, key="lib_speed")
        speed = 0.8 if "Slow" in speed_sel else 1.0
    with c_ctrl3:
        cmp_btn = "⚖️ Compare My Last Scan" if lang == "en" else ("⚖️ எனது பரிசோதனையுடன் ஒப்பிடு" if lang == "ta" else "⚖️ Enadhu Scan Oppidu")
        if st.button(cmp_btn, use_container_width=True):
            st.session_state["_lib_show_compare"] = not st.session_state.get("_lib_show_compare", False)

    # Toggle Compare View at top if requested
    if st.session_state.get("_lib_show_compare", False):
        last_label = st.session_state.get("_scan", {}).get("label", "blast")
        _render_compare_view(last_label, lang=lang)
        st.divider()

    # If detail view is active, render the dedicated detail page
    detail_key = st.session_state.get("_lib_detail_key")
    if detail_key and detail_key in ADVICE:
        _render_disease_detail_page(detail_key, ADVICE[detail_key], lang=lang, speed=speed)
        return

    # Category Selector Pills
    cat_options = [
        "All Categories",
        "🍄 Fungal",
        "🦠 Bacterial",
        "🔬 Viral",
        "🧪 Nutrient / Abiotic",
        "🌾 Healthy & Other",
    ]
    sel_cat = st.radio(
        "Disease Category Filter",
        cat_options,
        horizontal=True,
        label_visibility="collapsed",
    )

    # Search Bar
    search = st.text_input(
        "🔍 Search diseases",
        placeholder="Search by disease name, symptom, leaf effect, or Tamil term (e.g. blast, bacterial, nitrogen, மஞ்சள்)...",
        label_visibility="collapsed",
    )

    # Filter diseases
    category_filter_map = {
        "🍄 Fungal": ["Fungal"],
        "🦠 Bacterial": ["Bacterial"],
        "🔬 Viral": ["Viral"],
        "🧪 Nutrient / Abiotic": ["Physiological"],
        "🌾 Healthy & Other": ["None", "Various"],
    }
    allowed_causes = category_filter_map.get(sel_cat, None)

    q = search.strip().lower()
    matches = []
    for lbl, info in ADVICE.items():
        if allowed_causes is not None and info.get("cause_type") not in allowed_causes:
            continue
        if not q:
            matches.append(lbl)
            continue
        haystack = " ".join([
            info.get("name", ""), info.get("name_ta", ""),
            info.get("scientific", ""), info.get("cause_type", ""),
            info.get("symptoms_en", ""), info.get("conditions_en", ""),
            info.get("treatment_en", ""), info.get("prevention_en", ""),
            info.get("symptoms_summary_en", ""), info.get("symptoms_summary_ta", ""),
            info.get("symptoms_summary_tanglish", ""),
        ]).lower()
        if q in haystack:
            matches.append(lbl)

    if not matches:
        render_html(
            '<div style="color:#8ab89a;font-style:italic;padding:20px 0;">'
            'No diseases match your search or filter. Try a different keyword or category.</div>'
        )
        return

    render_html(
        f'<div style="color:#5a7a65;font-size:0.82em;margin-bottom:14px;font-weight:600;">'
        f'Showing {len(matches)} of {len(ADVICE)} reference disease classes (Tap "View Full Guide & Gallery" for full details)</div>'
    )

    for lbl in matches:
        _disease_card(lbl, ADVICE[lbl], lang=lang, speed=speed)

    st.divider()
    render_html(
        '<div style="color:#5a7a65;font-size:0.78em;line-height:1.6;">'
        'All disease profiles are starter content marked <b style="color:#ffd166;">⚠️ To be verified against TNAU recommendations</b>. '
        'Always consult with a qualified agricultural officer before spraying chemical pesticides.'
        '</div>'
    )
