import os
import sys
import json
import io
import base64
import streamlit as st
import streamlit.components.v1 as components
from gtts import gTTS
from streamlit_mic_recorder import speech_to_text

# Setup path
PROJECT_DIR = os.path.abspath(os.path.dirname(__file__))
if PROJECT_DIR not in sys.path:
    sys.path.insert(0, PROJECT_DIR)

from src.agent import answer_question, VERSION_INFO, DISCLAIMER_EN, DISCLAIMER_HI, extract_parameters, detect_language
from src.calculators import calculate_comprehensive_building_plan
from src.checker import check_building_plan
from src.tracker import get_all_amendments, get_comparison_tables
from src.auth import (
    generate_otp,
    verify_otp,
    validate_destination,
    get_user_preferences,
    save_user_preferences
)
from src.theme import get_theme_css, get_strings

LOGO_PATH = os.path.join(PROJECT_DIR, "assets", "logo.jpg")

def get_logo_b64():
    if os.path.exists(LOGO_PATH):
        with open(LOGO_PATH, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode("utf-8")
    return ""

logo_b64 = get_logo_b64()

st.set_page_config(
    page_title="Bhumi Vikas Sahayak | भूमि विकास सहायक",
    page_icon=LOGO_PATH if os.path.exists(LOGO_PATH) else "🏛️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize Session State
if "auth_user" not in st.session_state:
    st.session_state["auth_user"] = None

if "user_prefs" not in st.session_state:
    st.session_state["user_prefs"] = {
        "language": "hi",
        "theme": "dark",
        "auto_voice_playback": True
    }

current_theme = st.session_state["user_prefs"].get("theme", "dark")
current_lang = st.session_state["user_prefs"].get("language", "hi")
strings = get_strings(current_lang)

# Apply dynamic CSS based on Natural Dark / Light Theme
st.markdown(get_theme_css(current_theme), unsafe_allow_html=True)

# -------------------------------------------------------------
# LOGIN PORTAL (Displayed when not logged in - Phone/Email OTP Only)
# -------------------------------------------------------------
if not st.session_state.get("auth_user"):
    # Header with Official Logo
    st.markdown(f"""
    <div style="text-align: center; margin-bottom: 24px;">
        <img src="data:image/jpeg;base64,{logo_b64}" width="135" style="border-radius: 50%; box-shadow: 0 4px 16px rgba(0,0,0,0.25); margin-bottom: 12px;" />
        <h1 style="margin:0; font-size: 2.2rem; color: #22c55e;">{strings['app_title']}</h1>
        <h3 style="margin:4px 0 0 0; font-weight: 500; opacity: 0.9;">मध्य प्रदेश शासन &bull; भोपाल नगर निगम</h3>
        <p style="margin:4px 0 0 0; opacity: 0.8; font-size: 0.95rem;">{strings['tagline']}</p>
        <div class="version-tag">📌 {VERSION_INFO}</div>
    </div>
    """, unsafe_allow_html=True)

    # Auth Card with clear choice between Phone and Email
    st.markdown('<div class="auth-card" style="max-width: 580px; margin: 0 auto;">', unsafe_allow_html=True)
    st.markdown(f"### 🔐 {strings['otp_title']}")
    st.caption(strings['login_sub'])

    login_type = st.radio(
        strings["choose_method"],
        [strings["phone_opt"], strings["email_opt"]],
        horizontal=True,
        key="login_type_choice"
    )

    is_phone_login = strings["phone_opt"] in login_type

    if is_phone_login:
        login_val = st.text_input(strings["enter_phone"], placeholder="उदा. 9876543210", key="phone_input_field")
    else:
        login_val = st.text_input(strings["enter_email"], placeholder="उदा. officer@bhopal.gov.in", key="email_input_field")

    if st.button(strings["send_otp"], type="secondary", use_container_width=True):
        is_valid, norm_val, err_msg = validate_destination("phone" if is_phone_login else "email", login_val)
        if is_valid:
            otp, msg = generate_otp(norm_val, "phone" if is_phone_login else "email")
            st.session_state["active_dest"] = norm_val
            st.session_state["last_otp"] = otp
            st.session_state["otp_sent"] = True
            st.toast("OTP Sent Successfully!")
        else:
            st.error(err_msg)

    if st.session_state.get("otp_sent"):
        st.info(f"📲 **[BMC Gateway Notification]**: सत्यापन कोड (OTP) भेजा गया: `{st.session_state.get('last_otp')}` (परीक्षण हेतु: `123456`)")

        entered_otp = st.text_input(strings["enter_otp"], max_chars=6, key="otp_code_field")

        if st.button(strings["verify_login"], type="primary", use_container_width=True):
            dest = st.session_state.get("active_dest", login_val.strip())
            ok, user, msg = verify_otp(dest, entered_otp)
            if ok:
                st.session_state["auth_user"] = user
                st.session_state["user_prefs"] = get_user_preferences(user["user_id"])
                st.toast("लॉगिन सफल!")
                st.rerun()
            else:
                st.error(msg)

    st.markdown('</div>', unsafe_allow_html=True)
    st.stop()

# -------------------------------------------------------------
# AUTHENTICATED APP SCREEN
# -------------------------------------------------------------
current_user = st.session_state["auth_user"]

# App Header with Official App Logo
st.markdown(f"""
<div class="main-header">
    <div style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:16px;">
        <div style="display:flex; align-items:center; gap:16px;">
            <img src="data:image/jpeg;base64,{logo_b64}" width="78" style="border-radius:50%; box-shadow:0 2px 8px rgba(0,0,0,0.25);" />
            <div>
                <h1 style="margin:0; font-size: 2.1rem; line-height:1.2;">{strings['app_title']}</h1>
                <p style="margin:3px 0 0 0; opacity: 0.9; font-size: 0.98rem;">
                    {strings['app_subtitle']}
                </p>
                <div style="font-size:0.8rem; color:#86efac; margin-top:2px;">{strings['tagline']}</div>
            </div>
        </div>
        <div style="text-align:right; background:rgba(0,0,0,0.2); padding:10px 16px; border-radius:10px; border:1px solid rgba(255,255,255,0.12);">
            <div style="font-size:0.8rem; opacity:0.85;">{strings['logged_in_as']}</div>
            <div style="font-weight:700; font-size:1rem;">👤 {current_user.get('identifier', current_user.get('name'))}</div>
            <div style="font-size:0.75rem; color:#4ade80;">● Online &bull; BMC Ward 14</div>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# Sidebar with Official Logo, Clean Navigation & Minimalist Theme Control
with st.sidebar:
    st.markdown(f"""
    <div style="text-align:center; padding:10px 0 15px 0;">
        <img src="data:image/jpeg;base64,{logo_b64}" width="120" style="border-radius:50%; box-shadow:0 2px 10px rgba(0,0,0,0.25); margin-bottom:8px;" />
        <div style="font-weight:700; font-size:1.05rem; color:#22c55e;">{strings['app_title']}</div>
        <div style="font-size:0.8rem; color:#94a3b8;">भोपाल नगर निगम</div>
    </div>
    """, unsafe_allow_html=True)

    # User Profile Chip
    st.markdown(f"""
    <div class="user-badge">
        <div style="font-weight:600; font-size:0.9rem;">👤 {current_user.get('identifier', current_user.get('name'))}</div>
        <div style="font-size:0.78rem; color:#94a3b8;">{current_user.get('role')}</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown(f"#### {strings['sidebar_nav']}")
    feature = st.radio(
        strings['sidebar_nav'],
        strings['modules'],
        label_visibility="collapsed"
    )

    st.markdown("---")
    # Clean Natural Theme Switcher
    theme_choice = st.radio(
        strings["theme_toggle"],
        ["dark", "light"],
        format_func=lambda x: strings["theme_dark"] if x == "dark" else strings["theme_light"],
        index=0 if current_theme == "dark" else 1,
        horizontal=True,
        key="sb_theme_toggle"
    )
    if theme_choice != current_theme:
        st.session_state["user_prefs"]["theme"] = theme_choice
        save_user_preferences(current_user["user_id"], st.session_state["user_prefs"])
        st.rerun()

    st.markdown("---")
    if st.button("🚪 " + strings['logout'], use_container_width=True):
        st.session_state["auth_user"] = None
        st.session_state["otp_sent"] = False
        st.toast("लॉग आउट सफल!")
        st.rerun()

# -------------------------------------------------------------
# FEATURE 1: AI CHATBOT
# -------------------------------------------------------------
if feature.startswith("💬"):
    st.subheader(f"💬 {strings['modules'][0]}")
    st.caption("Ask questions in Hindi or English. Get precise answers with exact rule numbers, verified quotes, and automated math.")

    # Quick example buttons
    st.markdown("**⚡ Quick Example Questions (क्विक प्रश्न):**")
    col_e1, col_e2, col_h1, col_h2 = st.columns(4)
    with col_e1:
        if st.button("🇬🇧 200 sqm on 9m road (Setback/FAR/Fees)"):
            st.session_state["query_input"] = "My plot is 200 sq m on a 9 m road. How much gap do I leave at the front, how many floors can I build, and what fee do I pay?"
    with col_e2:
        if st.button("🇬🇧 Farm House plot size & FAR?"):
            st.session_state["query_input"] = "What is the minimum plot size and maximum FAR allowed for a Farm House in an agricultural zone?"
    with col_h1:
        if st.button("🇮🇳 15m सड़क पर 300 वर्ग मीटर फ्रंट सेटबैक"):
            st.session_state["query_input"] = "15 मीटर चौड़ी सड़क पर 300 वर्ग मीटर के आवासीय प्लॉट के लिए सामने कितना खुला स्थान (Front MOS) छोड़ना होगा?"
    with col_h2:
        if st.button("🇮🇳 नियम 12-A डीम्ड भवन अनुज्ञा"):
            st.session_state["query_input"] = "कितने वर्ग मीटर तक के आवासीय भूखंडों पर तत्काल या डीम्ड भवन अनुज्ञा (instant/deemed approval) का प्रावधान नियम 12-A में है?"

    # Query Input Box with Clean Minimalist Mic
    col_input, col_mic = st.columns([5, 1])
    with col_mic:
        st.write("&nbsp;")
        chat_spoken = speech_to_text(
            language="hi-IN" if current_lang == "hi" else "en-IN",
            start_prompt="🎙️",
            stop_prompt="⏹️",
            just_once=True,
            use_container_width=True,
            key="chat_minimal_mic"
        )
        if chat_spoken and chat_spoken.strip():
            st.session_state["query_input"] = chat_spoken.strip()

    with col_input:
        default_q = st.session_state.get("query_input", "")
        query = st.text_input(
            "Enter your question:" if current_lang == "en" else "अपना प्रश्न दर्ज करें:",
            value=default_q,
            placeholder=strings["query_placeholder"],
            key="chat_query_box"
        )

    # Process Query
    if st.button(strings["get_answer"], type="primary") or query:
        if query.strip():
            # Automatic Language Switching on Typing
            det_lang = detect_language(query)
            if det_lang != current_lang:
                st.session_state["user_prefs"]["language"] = det_lang
                save_user_preferences(current_user["user_id"], st.session_state["user_prefs"])
                st.rerun()

            with st.spinner("Retrieving official rules and verifying quotes..."):
                response = answer_question(query)

            # Amendment warning banner if triggered
            if response.get("amendment_warning"):
                st.markdown(f"""
                <div class="warning-banner">
                    ⚠️ <b>AMENDMENT ALERT:</b> {response['amendment_warning']}
                    <br><a href="https://teamleaseregtech.com/updates/article/59469/government-of-madhya-pradesh-amendment-to-land-development-rules" target="_blank" style="color:#b91c1c; text-decoration: underline;">View Gazette Notification &rarr;</a>
                </div>
                """, unsafe_allow_html=True)

            # Answer Card
            if response["found"]:
                st.success(f"### Answer ({'हिंदी' if response['language'] == 'hi' else 'English'}):")
                st.write(response["answer"])

                # Citation Cards
                st.markdown(f"#### {strings['official_citations']}")
                if response.get("citations"):
                    for cit in response["citations"]:
                        is_verif = cit.get("verified", False)
                        verif_badge = f'<div class="verified-badge">{strings["verif_badge"]}</div>' if is_verif else '<div class="verified-badge" style="background:#fee2e2; color:#991b1b;">⚠️ PENDING AUDIT</div>'
                        st.markdown(f"""
                        <div class="citation-card">
                            {verif_badge}
                            <div style="font-weight: 700; color: #16a34a; font-size: 1.05rem;">{cit.get('rule_number')} &bull; {cit.get('page_range')}</div>
                            <blockquote style="margin: 8px 0 0 0; font-style: italic; color: #cbd5e1; border-left: 3px solid #6b7280; padding-left: 10px;">
                                &ldquo;{cit.get('exact_quote')}&rdquo;
                            </blockquote>
                        </div>
                        """, unsafe_allow_html=True)

                if response.get("extracted_numbers"):
                    with st.expander("🔢 Extracted Parameters (कोड द्वारा निकाले गए आंकड़े)"):
                        st.json(response["extracted_numbers"])
            else:
                st.warning(f"### {response['answer']}")
                st.info("The Bhumi Vikas Rules specifically govern land development and construction sanction standards. External municipal taxes, utility bills, or non-technical matters are outside its scope.")

            # Legal Disclaimer
            st.markdown(f"""
            <div class="disclaimer-box">
                {response.get('disclaimer', DISCLAIMER_EN if current_lang == 'en' else DISCLAIMER_HI)}
            </div>
            """, unsafe_allow_html=True)

# -------------------------------------------------------------
# FEATURE 2: SMART BUILDING CALCULATOR
# -------------------------------------------------------------
elif feature.startswith("📐"):
    st.subheader(f"📐 {strings['modules'][1]}")
    st.caption("Calculate Front MOS, Rear MOS, Side MOS, Base FAR, permitted built-up area, and Rule 21 municipal fees purely via verified Python formulas.")

    with st.form("calc_form"):
        col1, col2 = st.columns(2)
        with col1:
            plot_area = st.number_input("Plot Area (वर्ग मीटर / sq m):", min_value=10.0, max_value=50000.0, value=200.0, step=10.0)
            road_width = st.number_input("Road Width / Abutting Street (मीटर / m):", min_value=3.0, max_value=60.0, value=9.0, step=0.5)
            building_type = st.selectbox("Building Type (भवन का प्रकार):", ["residential", "commercial", "farmhouse"])

        with col2:
            calc_builtup = st.number_input("Proposed Built-Up Area for Fees (sq m):", min_value=0.0, max_value=100000.0, value=180.0, step=10.0)
            structure_type = st.selectbox("Structure Layout:", ["detached", "semi_detached", "row"])
            height_m = st.number_input("Proposed Building Height (meters):", min_value=3.0, max_value=100.0, value=12.0, step=0.5)

        submit_calc = st.form_submit_button("⚡ Calculate Official Norms (गणना करें)", type="primary")

    if submit_calc:
        res = calculate_comprehensive_building_plan(
            plot_area_sqm=plot_area,
            road_width_m=road_width,
            building_type=building_type,
            builtup_area_sqm=calc_builtup,
            structure_type=structure_type,
            height_m=height_m
        )

        st.markdown("### 📊 Verified Calculation Results:")
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Front MOS (सामने खुला स्थान)", f"{res['front_mos_m']} m")
        m2.metric("Rear MOS (पीछे खुला स्थान)", f"{res['rear_mos_m']} m")
        m3.metric("Side MOS (दोनों तरफ)", f"{res['side_mos_1_m']}m & {res['side_mos_2_m']}m")
        m4.metric("Base FAR", f"{res['base_far']}")

        m5, m6, m7 = st.columns(3)
        m5.metric("Max Built-up Permitted", f"{res['max_permissible_builtup_sqm']} sq m")
        m6.metric("Rule 21 Permission Fee", f"₹ {res['fee_inr']:,}")
        m7.metric("High Rise Classification", "Yes (Rule 56)" if res['is_high_rise'] else "No (<15m/18m)")

        st.markdown("#### 📜 Grounding Rule Citations:")
        for r_name, r_cit in res["citations"].items():
            st.info(f"**{r_name.upper()}**: {r_cit}")

# -------------------------------------------------------------
# FEATURE 3: BUILDING PLAN CHECKER
# -------------------------------------------------------------
elif feature.startswith("📋"):
    st.subheader(f"📋 {strings['modules'][2]}")
    st.caption("Pre-submission compliance checker: Flags violations of setbacks, heights, FAR, tree planting, and rainwater harvesting.")

    with st.form("checker_form"):
        st.markdown("#### 1. Site Specifications")
        c1, c2, c3 = st.columns(3)
        with c1:
            p_area = st.number_input("Plot Area (sq m):", value=250.0, step=10.0)
            p_road = st.number_input("Road Width (m):", value=12.0, step=0.5)
        with c2:
            p_type = st.selectbox("Use Type:", ["residential", "commercial", "farmhouse"])
            p_layout = st.selectbox("Layout:", ["detached", "semi_detached", "row"])
        with c3:
            p_height = st.number_input("Proposed Height (m):", value=12.0, step=0.5)
            p_floors = st.number_input("Proposed Floors:", value=3, min_value=1, max_value=30)

        st.markdown("#### 2. Proposed Plan Values (To Verify)")
        d1, d2, d3, d4 = st.columns(4)
        with d1:
            prop_front = st.number_input("Proposed Front MOS (m):", value=4.5, step=0.5)
        with d2:
            prop_rear = st.number_input("Proposed Rear MOS (m):", value=3.0, step=0.5)
        with d3:
            prop_side1 = st.number_input("Proposed Side 1 MOS (m):", value=2.0, step=0.5)
            prop_side2 = st.number_input("Proposed Side 2 MOS (m):", value=2.0, step=0.5)
        with d4:
            prop_bua = st.number_input("Proposed Total BUA (sq m):", value=300.0, step=10.0)

        check_btn = st.form_submit_button("🔍 Run Full Compliance Audit (योजना जांचें)", type="primary")

    if check_btn:
        proposed_plan = {
            "plot_area_sqm": p_area,
            "road_width_m": p_road,
            "building_type": p_type,
            "structure_type": p_layout,
            "height_m": p_height,
            "floors": p_floors,
            "proposed_front_mos_m": prop_front,
            "proposed_rear_mos_m": prop_rear,
            "proposed_side_mos_1_m": prop_side1,
            "proposed_side_mos_2_m": prop_side2,
            "proposed_builtup_sqm": prop_bua
        }
        report = check_building_plan(proposed_plan)

        if report["status"] == "COMPLIANT":
            st.success(f"### ✅ {report['summary']}")
        else:
            st.error(f"### ❌ {report['summary']}")

        col_v1, col_v2 = st.columns(2)
        with col_v1:
            st.markdown(f"#### ⚠️ Violations ({report['violations_count']}):")
            if report["violations"]:
                for v in report["violations"]:
                    st.error(f"**{v['rule']}**: {v['issue']}")
            else:
                st.info("No violations detected!")

        with col_v2:
            st.markdown(f"#### ℹ️ Additional Norms ({report['warnings_count']}):")
            for w in report["warnings"]:
                st.warning(f"**{w['rule']}**: {w['issue']}")

# -------------------------------------------------------------
# FEATURE 4: RULE AMENDMENT TRACKER
# -------------------------------------------------------------
elif feature.startswith("📢"):
    st.subheader(f"📢 {strings['modules'][3]}")
    st.caption("Official Gazette notifications tracked against MP Bhumi Vikas Rules 2012.")

    amendments = get_all_amendments()
    for am in amendments:
        status_color = "#ef4444" if am.get("warning_level") == "CRITICAL" else "#0284c7"
        with st.expander(f"📌 {am['title']} ({am['date']})", expanded=True):
            st.markdown(f"<span style='color:{status_color}; font-weight:700;'>Gazette No: {am['gazette_no']}</span>", unsafe_allow_html=True)
            st.write(f"**Affected Rules:** {', '.join(am['affected_rules'])}")
            st.write(f"**Key Changes:** {am['key_changes']}")
            st.markdown(f"[Official Source / Notification Link]({am['source_url']})")

# -------------------------------------------------------------
# FEATURE 5: VOICE-BASED ASSISTANT (Minimalist Alexa / Google Style)
# -------------------------------------------------------------
elif feature.startswith("🎙️"):
    st.subheader(f"🎙️ {strings['voice_title']}")
    st.caption(strings['voice_sub'])

    # Clean centered circular mic interface (Google Assistant / Alexa style)
    st.markdown('<div class="voice-orb-wrapper">', unsafe_allow_html=True)
    c_sp1, c_sp2, c_sp3 = st.columns([2, 1, 2])
    with c_sp2:
        spoken_text = speech_to_text(
            language="hi-IN" if current_lang == "hi" else "en-IN",
            start_prompt="🎙️ Tap to Speak",
            stop_prompt="⏹️ Listening... Click to Send",
            just_once=True,
            use_container_width=True,
            key="alexa_minimal_mic"
        )
    st.markdown('</div>', unsafe_allow_html=True)

    # Process spoken question
    if spoken_text and spoken_text.strip():
        st.session_state["v_active_query"] = spoken_text.strip()
        st.session_state["v_should_compute"] = True
        
        # Automatic language switching on voice
        detected_lang = detect_language(spoken_text)
        if detected_lang != current_lang:
            st.session_state["user_prefs"]["language"] = detected_lang
            save_user_preferences(current_user["user_id"], st.session_state["user_prefs"])
            st.rerun()

    active_q = st.session_state.get("v_active_query", "")
    if active_q:
        st.info(f"🎙️ **{'पूछा गया सवाल (Spoken Query)' if current_lang == 'hi' else 'Spoken Query'}**: \"{active_q}\"")

    if st.session_state.pop("v_should_compute", False) and active_q:
        with st.spinner("उत्तर खोजा जा रहा है..." if current_lang == "hi" else "Searching official rules..."):
            ans = answer_question(active_q)
            st.session_state["v_last_ans"] = ans
            try:
                tts_lang = "hi" if ans["language"] == "hi" else "en"
                tts = gTTS(text=ans['answer'], lang=tts_lang)
                audio_buffer = io.BytesIO()
                tts.write_to_fp(audio_buffer)
                st.session_state["v_last_audio"] = audio_buffer.getvalue()
            except Exception as e:
                st.session_state["v_last_audio"] = None

    # Persistent Display: Both Written Text and Voice Playback
    if "v_last_ans" in st.session_state:
        ans = st.session_state["v_last_ans"]

        if ans.get("amendment_warning"):
            st.markdown(f"""
            <div class="warning-banner">
                ⚠️ <b>AMENDMENT ALERT:</b> {ans['amendment_warning']}
            </div>
            """, unsafe_allow_html=True)

        # 1. Voice Playback (Plays automatically)
        if st.session_state.get("v_last_audio"):
            st.markdown(f"#### 🎧 {'ऑडियो उत्तर (Voice Response):' if current_lang == 'hi' else 'Voice Response:'}")
            st.audio(st.session_state["v_last_audio"], format="audio/mp3", autoplay=True)

        # 2. Written Text Output
        st.success(f"### 📢 {'लिखित उत्तर (Written Answer):' if current_lang == 'hi' else 'Written Answer:'}")
        st.write(ans['answer'])

        # Verified Citations
        if ans.get("citations"):
            st.markdown(f"#### {strings['official_citations']}")
            for cit in ans["citations"]:
                st.info(f"**{cit['rule_number']}** ({cit['page_range']}): \"{cit['exact_quote']}\"")

# -------------------------------------------------------------
# FEATURE 6: RULE COMPARISON DASHBOARD
# -------------------------------------------------------------
elif feature.startswith("📊"):
    st.subheader(f"📊 {strings['modules'][5]}")
    st.caption("Central reference tables for Municipal Officers at Bhopal Municipal Corporation.")

    tables = get_comparison_tables()
    t_tab1, t_tab2 = st.tabs(["🛣️ Setbacks by Road Width", "💰 Rule 21 Fee Slabs"])

    with t_tab1:
        st.markdown("#### 🛣️ Setback & Height Norms Across Road Widths:")
        st.table(tables["setback_comparison"])

    with t_tab2:
        st.markdown("#### 💰 Building Permission Fees (Rule 21(3)(b)):")
        st.table(tables["fee_slabs_rule_21"])

# -------------------------------------------------------------
# FEATURE 7: AI VERIFICATION SYSTEM
# -------------------------------------------------------------
elif feature.startswith("🛡️"):
    st.subheader(f"🛡️ {strings['modules'][6]}")
    st.caption("Ensuring zero hallucinations: Every citation must be a verified exact substring of the MP Bhumi Vikas Rules text.")

    st.markdown("""
    <div style="background:#1e293b; border:1px solid #334155; padding:16px; border-radius:10px; margin-bottom:16px;">
        <b>Verification Contract:</b><br>
        1. <b>Exact Substring Match</b>: The quote must strictly exist in the rule text after whitespace normalization.<br>
        2. <b>Zero Hallucination Tolerance</b>: If an unanswerable question is asked, the system outputs <code>found: false</code>.<br>
        3. <b>Deterministic Math</b>: Fees and setbacks are computed by Python code, not guessed by the model.
    </div>
    """, unsafe_allow_html=True)

    if os.path.exists(os.path.join(PROJECT_DIR, "data", "eval_results.json")):
        with open(os.path.join(PROJECT_DIR, "data", "eval_results.json"), "r", encoding="utf-8") as f:
            eval_data = json.load(f)

        c1, c2, c3 = st.columns(3)
        c1.metric("Benchmark Questions", eval_data["total"])
        c2.metric("Tests Passed", eval_data["passed"])
        c3.metric("Verification Accuracy", f"{eval_data['accuracy_pct']}%")

        st.markdown("#### Detailed Benchmark Test Results:")
        for r in eval_data["results"]:
            icon = "✅" if r["passed"] else "❌"
            with st.expander(f"{icon} [{r['id']}] {r['question'][:70]}..."):
                st.write(f"**Passed**: {r['passed']}")
                st.write(f"**Notes**: {'; '.join(r['notes'])}")
                st.json(r["response"])
    else:
        st.info("Run `python eval.py` to view full benchmark audit logs.")

# -------------------------------------------------------------
# FEATURE 8: USER SETTINGS & PREFERENCES
# -------------------------------------------------------------
elif feature.startswith("⚙️"):
    st.subheader(f"⚙️ {strings['modules'][7]}")
    st.caption("Customize your language, theme, and audio playback settings. Preferences are automatically saved.")

    prefs = st.session_state.get("user_prefs", {})

    with st.form("settings_pref_form"):
        st.markdown("#### 1️⃣ " + ("पसंदीदा भाषा (Default Language):" if current_lang == "hi" else "Default Language:"))
        p_lang = st.radio(
            "Language",
            ["hi", "en"],
            format_func=lambda x: "🇮🇳 Hindi (हिंदी) - सभी नियम, प्रश्न व गणनाएं हिंदी में" if x == "hi" else "🇬🇧 English - Standard English Interface",
            index=0 if prefs.get("language", "hi") == "hi" else 1,
            label_visibility="collapsed"
        )

        st.markdown("#### 2️⃣ " + strings["theme_toggle"])
        p_theme = st.radio(
            "Theme",
            ["dark", "light"],
            format_func=lambda x: strings["theme_dark"] if x == "dark" else strings["theme_light"],
            index=0 if prefs.get("theme", "dark") == "dark" else 1,
            label_visibility="collapsed"
        )

        st.markdown("#### 3️⃣ Audio & Voice Assistant Settings")
        p_audio = st.checkbox(
            "आवाज सहायक में उत्तर आने पर स्वतः ऑडियो प्लेबैक चालू रखें (Autoplay voice response)" if current_lang == "hi" else "Autoplay voice response in Voice Assistant",
            value=prefs.get("auto_voice_playback", True)
        )

        st.markdown("---")
        save_submitted = st.form_submit_button("💾 Save Preferences (प्राथमिकताएं सुरक्षित करें)", type="primary")

        if save_submitted:
            updated_prefs = {
                "language": p_lang,
                "theme": p_theme,
                "auto_voice_playback": p_audio
            }
            save_user_preferences(current_user["user_id"], updated_prefs)
            st.session_state["user_prefs"] = updated_prefs
            st.success("✅ प्राथमिकताएं सफलतापूर्वक सुरक्षित कर ली गईं!" if current_lang == "hi" else "✅ Preferences saved successfully!")
            st.rerun()

    st.markdown("#### 👤 " + ("सक्रिय उपयोगकर्ता प्रोफाइल (Active Profile)" if current_lang == "hi" else "Active Officer Profile"))
    col_p1, col_p2 = st.columns(2)
    with col_p1:
        st.info(f"""
        **उपयोगकर्ता (User ID):** `{current_user.get('user_id')}`<br>
        **पहचान (Identifier):** `{current_user.get('identifier')}`<br>
        **पद (Role):** {current_user.get('role')}<br>
        **संगठन (Org):** {current_user.get('organization')}
        """)
    with col_p2:
        st.info(f"""
        **सक्रिय थीम (Active Theme):** `{prefs.get('theme')}`<br>
        **सक्रिय भाषा (Active Language):** `{'Hindi (हिंदी)' if prefs.get('language') == 'hi' else 'English'}`<br>
        **ऑडियो ऑटोप्ले (Audio Autoplay):** `{prefs.get('auto_voice_playback')}`
        """)
