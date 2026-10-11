import os
import sys
import json
import io
import streamlit as st
import streamlit.components.v1 as components
from gtts import gTTS
from streamlit_mic_recorder import speech_to_text

# Setup path
PROJECT_DIR = os.path.abspath(os.path.dirname(__file__))
if PROJECT_DIR not in sys.path:
    sys.path.insert(0, PROJECT_DIR)

from src.agent import answer_question, VERSION_INFO, DISCLAIMER_EN, DISCLAIMER_HI, extract_parameters
from src.calculators import calculate_comprehensive_building_plan
from src.checker import check_building_plan
from src.tracker import get_all_amendments, get_comparison_tables
from src.auth import (
    authenticate_password,
    generate_otp,
    verify_otp,
    get_user_preferences,
    save_user_preferences,
    DEMO_EMAIL,
    DEMO_USER_ID,
    DEMO_PASSWORD_PLAIN
)
from src.theme import get_theme_css, get_strings

st.set_page_config(
    page_title="Bhumi Vikas Sahayak | भूमि विकास सहायक",
    page_icon="🏛️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize Session State
if "auth_user" not in st.session_state:
    st.session_state["auth_user"] = None

if "user_prefs" not in st.session_state:
    st.session_state["user_prefs"] = {
        "language": "hi",
        "theme": "light",
        "auto_voice_playback": True
    }

current_theme = st.session_state["user_prefs"].get("theme", "light")
current_lang = st.session_state["user_prefs"].get("language", "hi")
strings = get_strings(current_lang)

# Apply dynamic CSS based on Active Theme
st.markdown(get_theme_css(current_theme), unsafe_allow_html=True)

# -------------------------------------------------------------
# LOGIN PORTAL (Displayed when not logged in)
# -------------------------------------------------------------
if not st.session_state.get("auth_user"):
    st.markdown(f"""
    <div class="main-header" style="text-align: center;">
        <h1 style="margin:0; font-size: 2.2rem;">🏛️ भोपाल नगर निगम (Bhopal Municipal Corporation)</h1>
        <h3 style="margin:6px 0 0 0; font-weight: 500; opacity: 0.95;">भवन अनुज्ञा शाखा (Building Permission Directorate)</h3>
        <p style="margin:6px 0 0 0; opacity: 0.85;">भूमि विकास सहायक — सुरक्षित अधिकृत प्रवेश द्वार (Secure Authentication Gateway)</p>
        <div class="version-tag">📌 {VERSION_INFO}</div>
    </div>
    """, unsafe_allow_html=True)

    # Demo credentials callout banner
    st.markdown(f"""
    <div style="background: linear-gradient(135deg, #eff6ff 0%, #dbeafe 100%); border: 2px solid #3b82f6; border-radius: 12px; padding: 18px 22px; margin-bottom: 20px; color: #1e3a8a;">
        <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 12px;">
            <div>
                <h4 style="margin:0; color:#1d4ed8; font-size: 1.15rem;">🔑 परीक्षक / डेमो खाता (Evaluator Demo Account):</h4>
                <div style="margin-top: 6px; font-size: 0.95rem;">
                    <b>ईमेल / यूजरनेम:</b> <code>{DEMO_EMAIL}</code> &nbsp;|&nbsp; 
                    <b>पासवर्ड:</b> <code>{DEMO_PASSWORD_PLAIN}</code> &nbsp;|&nbsp; 
                    <b>पद:</b> Senior Building Permission Clerk (Ward 14)
                </div>
                <div style="margin-top: 4px; font-size: 0.85rem; color: #2563eb;">
                    💡 <i>OTP लॉगिन के लिए किसी भी 10-अंकीय फोन नंबर या ईमेल पर कोड मांगें (त्वरित परीक्षण कोड: <code>123456</code>)।</i>
                </div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    c_q1, c_q2, c_q3 = st.columns([1, 2, 1])
    with c_q2:
        if st.button("🚀 1-Click Instant Demo Login (तुरंत डेमो लॉगिन करें)", type="primary", use_container_width=True):
            user = authenticate_password(DEMO_EMAIL, DEMO_PASSWORD_PLAIN)
            if user:
                st.session_state["auth_user"] = user
                st.session_state["user_prefs"] = get_user_preferences(user["user_id"])
                st.toast("डेमो लॉगिन सफल! प्रवेश किया जा रहा है...")
                st.rerun()

    st.markdown("---")

    auth_tab1, auth_tab2, auth_tab3 = st.tabs([
        "📱 फोन / ईमेल OTP लॉगिन (Phone/Email OTP)",
        "🔑 डेमो पासवर्ड लॉगिन (Password Login)",
        "⚙️ प्रवेश पूर्व सेटिंग्स (Initial Setup Preferences)"
    ])

    with auth_tab1:
        st.markdown("#### 📱 OTP आधारित सुरक्षित लॉगिन (OTP Verification):")
        st.caption("अपने 10-अंकीय मोबाइल नंबर या आधिकारिक ईमेल पते से लॉगिन करें।")

        dest_col, send_col = st.columns([3, 1])
        with dest_col:
            login_dest = st.text_input(
                "मोबाइल नंबर या ईमेल पता दर्ज करें (Mobile / Email):",
                placeholder="उदा. 9876543210 या clerk@bhopal.gov.in",
                key="login_dest_input"
            )
        with send_col:
            st.write("&nbsp;")
            if st.button("📩 OTP भेजें (Send OTP)", use_container_width=True):
                if login_dest.strip():
                    otp, msg = generate_otp(login_dest.strip())
                    st.session_state["active_otp_dest"] = login_dest.strip()
                    st.session_state["last_sent_otp"] = otp
                    st.session_state["otp_sent"] = True
                    st.toast("OTP सफलता से भेजा गया!")
                else:
                    st.error("कृपया वैध फोन नंबर या ईमेल पता दर्ज करें!")

        if st.session_state.get("otp_sent"):
            st.info(f"📲 **[BMC SMS/Email Gateway Notification]**: सत्यापन कोड (OTP) भेजा गया: `{st.session_state.get('last_sent_otp')}` (त्वरित परीक्षण कोड: `123456`)")

            c_otp, c_verify = st.columns([2, 2])
            with c_otp:
                entered_otp = st.text_input("6-अंकीय OTP दर्ज करें (Enter 6-digit OTP):", max_chars=6, key="otp_verify_input")
            with c_verify:
                st.write("&nbsp;")
                if st.button("✅ OTP सत्यापित करें व लॉगिन करें (Verify & Login)", type="primary", use_container_width=True):
                    dest = st.session_state.get("active_otp_dest", login_dest)
                    ok, user, msg = verify_otp(dest, entered_otp)
                    if ok:
                        st.session_state["auth_user"] = user
                        st.session_state["user_prefs"] = get_user_preferences(user["user_id"])
                        st.success(f"{msg} स्वागत है!")
                        st.rerun()
                    else:
                        st.error(msg)

    with auth_tab2:
        st.markdown("#### 🔑 पासवर्ड आधारित अधिकृत लॉगिन (Officer Password Login):")
        with st.form("pwd_login_form"):
            c_u, c_p = st.columns(2)
            with c_u:
                username_input = st.text_input("यूजरनेम या ईमेल (Username/Email):", value=DEMO_EMAIL)
            with c_p:
                pwd_input = st.text_input("पासवर्ड (Password):", type="password", value=DEMO_PASSWORD_PLAIN)

            submit_pwd = st.form_submit_button("🔐 लॉगिन करें (Sign In)", type="primary", use_container_width=True)
            if submit_pwd:
                user = authenticate_password(username_input, pwd_input)
                if user:
                    st.session_state["auth_user"] = user
                    st.session_state["user_prefs"] = get_user_preferences(user["user_id"])
                    st.success(f"लॉगिन सफल! स्वागत है, {user['name']}!")
                    st.rerun()
                else:
                    st.error("अमान्य यूजरनेम या पासवर्ड! कृपया डेमो क्रेडेंशियल्स का उपयोग करें।")

    with auth_tab3:
        st.markdown("#### ⚙️ प्रवेश पूर्व सेटिंग्स (Initial Setup Preferences):")
        st.caption("लॉगिन करने से पहले अपनी पसंदीदा भाषा और थीम का चयन करें:")

        col_setup_lang, col_setup_theme = st.columns(2)
        with col_setup_lang:
            setup_lang = st.radio(
                "डिफ़ॉल्ट भाषा (Default Language):",
                ["hi", "en"],
                format_func=lambda x: "🇮🇳 Hindi (हिंदी)" if x == "hi" else "🇬🇧 English",
                index=0 if st.session_state["user_prefs"]["language"] == "hi" else 1
            )
        with col_setup_theme:
            setup_theme = st.radio(
                "डिफ़ॉल्ट थीम (Default Theme):",
                ["light", "dark"],
                format_func=lambda x: "☀️ Light Mode (श्वेत/White)" if x == "light" else "🌙 Dark Mode (श्याम/Black)",
                index=0 if st.session_state["user_prefs"]["theme"] == "light" else 1
            )

        if st.button("💾 प्राथमिकताएं लागू करें (Apply Preferences)"):
            st.session_state["user_prefs"]["language"] = setup_lang
            st.session_state["user_prefs"]["theme"] = setup_theme
            st.success("प्राथमिकताएं लागू हुईं!")
            st.rerun()

    st.stop()

# -------------------------------------------------------------
# AUTHENTICATED APP SCREEN
# -------------------------------------------------------------
current_user = st.session_state["auth_user"]

# App Header with Officer Status Bar
st.markdown(f"""
<div class="main-header">
    <div style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:10px;">
        <div>
            <h1 style="margin:0; font-size: 2.1rem;">{strings['title']}</h1>
            <p style="margin:4px 0 0 0; opacity: 0.9; font-size: 1.05rem;">
                {strings['subtitle']}
            </p>
            <div class="version-tag">📌 {VERSION_INFO}</div>
        </div>
        <div style="text-align:right; background:rgba(255,255,255,0.15); padding:10px 16px; border-radius:10px; border:1px solid rgba(255,255,255,0.2);">
            <div style="font-size:0.85rem; opacity:0.85;">{strings['logged_in_as']}</div>
            <div style="font-weight:700; font-size:1.05rem;">👤 {current_user.get('name')}</div>
            <div style="font-size:0.85rem; opacity:0.9;">🏢 {current_user.get('role')}</div>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# Sidebar with User Profile, Quick Settings, Navigation & Logout
with st.sidebar:
    st.image("https://img.icons8.com/fluency/96/city-buildings.png", width=64)
    st.markdown(f"### 🏢 {current_user.get('organization', 'भोपाल नगर निगम')}")

    # Officer Profile Chip
    st.markdown(f"""
    <div class="user-badge">
        <div style="font-weight:700; font-size:0.95rem;">👤 {current_user.get('name')}</div>
        <div style="font-size:0.8rem; color:#64748b;">{current_user.get('department')}</div>
        <div style="font-size:0.75rem; color:#0284c7; margin-top:3px;">● Active Session: Verified</div>
    </div>
    """, unsafe_allow_html=True)

    # Quick Theme & Language Toggles in Sidebar
    st.markdown("#### ⚙️ Quick Preferences")
    col_sb_lang, col_sb_theme = st.columns(2)
    with col_sb_lang:
        sb_lang = st.selectbox(
            "🌐 भाषा:",
            ["hi", "en"],
            format_func=lambda x: "हिंदी" if x == "hi" else "English",
            index=0 if current_lang == "hi" else 1,
            key="sb_quick_lang"
        )
    with col_sb_theme:
        sb_theme = st.selectbox(
            "🎨 थीम:",
            ["light", "dark"],
            format_func=lambda x: "☀️ Light" if x == "light" else "🌙 Dark",
            index=0 if current_theme == "light" else 1,
            key="sb_quick_theme"
        )

    # Reactive update if sidebar quick toggle changed
    if sb_lang != current_lang or sb_theme != current_theme:
        st.session_state["user_prefs"]["language"] = sb_lang
        st.session_state["user_prefs"]["theme"] = sb_theme
        save_user_preferences(current_user["user_id"], st.session_state["user_prefs"])
        st.rerun()

    st.markdown("---")
    st.markdown(f"#### {strings['sidebar_nav']}")
    feature = st.radio(
        strings['sidebar_nav'],
        strings['modules'],
        label_visibility="collapsed"
    )

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
    st.subheader("💬 AI Chatbot for Building Permission Rules")
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

    # Query Input Box with direct mic input
    col_input, col_mic = st.columns([3, 1])
    with col_mic:
        st.write("**माइक (Speak Directly):**")
        chat_spoken = speech_to_text(
            language="hi-IN",
            start_prompt="🎤 बोलें (Mic)",
            stop_prompt="⏹️ रोकें (Stop)",
            just_once=True,
            use_container_width=True,
            key="chat_mic_speech"
        )
        if chat_spoken and chat_spoken.strip():
            st.session_state["query_input"] = chat_spoken.strip()

    with col_input:
        default_q = st.session_state.get("query_input", "")
        query = st.text_input("Enter your question (प्रश्न दर्ज करें):", value=default_q, placeholder="e.g. My plot is 200 sq m on a 9 m road. How much front gap do I leave?")

    if st.button("🔍 Get Verified Answer (उत्तर प्राप्त करें)", type="primary") or query:
        if query.strip():
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
                st.markdown("#### 📜 Official Rulebook Citations & Evidence:")
                if response.get("citations"):
                    for cit in response["citations"]:
                        is_verif = cit.get("verified", False)
                        verif_badge = '<div class="verified-badge">✓ 100% VERIFIED QUOTE SUBSTRING</div>' if is_verif else '<div class="verified-badge" style="background:#fee2e2; color:#991b1b;">⚠️ PENDING AUDIT</div>'
                        st.markdown(f"""
                        <div class="citation-card">
                            {verif_badge}
                            <div style="font-weight: 700; color: #1e3a8a; font-size: 1.05rem;">{cit.get('rule_number')} &bull; {cit.get('page_range')}</div>
                            <blockquote style="margin: 8px 0 0 0; font-style: italic; color: #334155; border-left: 3px solid #94a3b8; padding-left: 10px;">
                                &ldquo;{cit.get('exact_quote')}&rdquo;
                            </blockquote>
                        </div>
                        """, unsafe_allow_html=True)

                # Show extracted numbers
                if response.get("extracted_numbers"):
                    with st.expander("🔢 Extracted Parameters (कोड द्वारा निकाले गए आंकड़े)"):
                        st.json(response["extracted_numbers"])
            else:
                st.warning(f"### {response['answer']}")
                st.info("The Bhumi Vikas Rules specifically govern land development and construction sanction standards. External municipal taxes, utility bills, or non-technical matters are outside its scope.")

            # Legal Disclaimer
            st.markdown(f"""
            <div class="disclaimer-box">
                {response.get('disclaimer', DISCLAIMER_EN)}
            </div>
            """, unsafe_allow_html=True)

# -------------------------------------------------------------
# FEATURE 2: SMART BUILDING CALCULATOR
# -------------------------------------------------------------
elif feature.startswith("📐"):
    st.subheader("📐 Smart Building Calculator (स्मार्ट कैलकुलेटर)")
    st.caption("Calculate setbacks, permissible FAR, maximum built-up area, and official municipal fees based on MP Bhumi Vikas Rules.")

    col1, col2, col3 = st.columns(3)
    with col1:
        plot_area = st.number_input("Plot Area (वर्ग मीटर / sq m):", min_value=10.0, max_value=50000.0, value=200.0, step=10.0)
        building_type = st.selectbox("Building Type (भवन का प्रकार):", ["residential", "commercial", "farm house", "public/institutional"])
    with col2:
        road_width = st.number_input("Front Road Width (सड़क की चौड़ाई - मीटर / m):", min_value=3.0, max_value=100.0, value=9.0, step=0.5)
        dev_type = st.selectbox("Development Type (विकास का प्रकार):", ["detached", "semi-detached", "row-type"])
    with col3:
        proposed_builtup = st.number_input("Proposed Built-up Area (वैकल्पिक निर्माण क्षेत्र):", min_value=0.0, max_value=100000.0, value=round(plot_area * 1.25, 2))
        prop_height = st.number_input("Proposed Building Height (ऊंचाई - मीटर):", min_value=0.0, max_value=120.0, value=10.0, step=1.0)

    if st.button("🚀 Calculate Norms (गणना करें)", type="primary"):
        calc = calculate_comprehensive_building_plan(
            plot_area_sqm=plot_area,
            road_width_m=road_width,
            building_type=building_type,
            development_type=dev_type,
            proposed_builtup_sqm=proposed_builtup,
            proposed_height_m=prop_height
        )

        st.markdown("### 📊 Calculation Summary:")
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Front Setback (FMOS)", f"{calc['setbacks']['front_mos_meters']} m")
        m2.metric("Rear Setback (RMOS)", f"{calc['setbacks']['rear_mos_meters']} m")
        m3.metric("Side Setback (SMOS)", f"{calc['setbacks']['side_mos_meters']} m")
        m4.metric("Permissible Base FAR", f"{calc['far']['base_far']}")

        f1, f2, f3, f4 = st.columns(4)
        f1.metric("Max Built-up Allowed", f"{calc['far']['max_permissible_builtup_sqm']} sq m")
        f2.metric("Application Fee", f"₹ {calc['fees']['application_fee']}")
        f3.metric("Permission Fee", f"₹ {calc['fees']['permission_fee']}")
        f4.metric("Total Municipal Fee", f"₹ {calc['fees']['total_fee']}")

        st.markdown("#### 🌿 Environmental & Fast-Track Compliances:")
        c1, c2, c3 = st.columns(3)
        with c1:
            st.info(f"🌳 **Tree Plantation**: {calc['environmental']['trees_required']} trees required on site ({calc['environmental']['tree_rule']})")
        with c2:
            rwh_status = "Mandatory (अनिवार्य)" if calc['environmental']['rainwater_harvesting_mandatory'] else "Optional"
            st.info(f"💧 **Rainwater Harvesting**: {rwh_status} ({calc['environmental']['rwh_rule']})")
        with c3:
            deemed = "Eligible (पात्र)" if calc['fast_track']['deemed_instant_approval_eligible'] else "Standard Scrutiny Required"
            st.info(f"⚡ **Rule 12-A Instant Deemed Approval**: {deemed}")

        if calc.get("amendment_warning"):
            st.warning("⚠️ **Amendment Overlay Alert**: Plots up to 500 sq m are subject to the 28 Aug 2026 amendment. Please verify local body jurisdiction and deemed sanction conditions.")

# -------------------------------------------------------------
# FEATURE 3: BUILDING PLAN CHECKER
# -------------------------------------------------------------
elif feature.startswith("📋"):
    st.subheader("📋 Building Plan Checker (योजना पूर्व-परीक्षण)")
    st.caption("Upload or test proposed architectural parameters before formal submission to prevent plan rejection at Bhopal Municipal Corporation.")

    col_p1, col_p2 = st.columns(2)
    with col_p1:
        st.markdown("#### 📐 Plot & Site Details:")
        c_plot = st.number_input("Plot Area (sq m):", value=200.0, step=10.0, key="c_plot")
        c_road = st.number_input("Road Width (m):", value=9.0, step=0.5, key="c_road")
        c_btype = st.selectbox("Occupancy:", ["residential", "commercial"], key="c_btype")
        c_dev = st.selectbox("Layout:", ["detached", "semi-detached", "row-type"], key="c_dev")
    with col_p2:
        st.markdown("#### 🏗️ Proposed Plan Details:")
        p_front = st.number_input("Proposed Front Open Space (m):", value=2.5, step=0.1, help="Try 2.5m on 9m road to see violation (3.0m required)")
        p_rear = st.number_input("Proposed Rear Open Space (m):", value=2.5, step=0.1)
        p_side = st.number_input("Proposed Side Open Space (m):", value=3.0, step=0.1)
        p_built = st.number_input("Proposed Total Built-up Area (sq m):", value=260.0, step=10.0, help="Try 260 sq m on 200 sq m plot to see FAR violation (max 250 sq m)")

    if st.button("🔍 Validate Building Plan (योजना की जांच करें)", type="primary"):
        plan_check = check_building_plan({
            "plot_area_sqm": c_plot,
            "road_width_m": c_road,
            "building_type": c_btype,
            "development_type": c_dev,
            "proposed_front_mos_m": p_front,
            "proposed_rear_mos_m": p_rear,
            "proposed_side_mos_m": p_side,
            "proposed_builtup_sqm": p_built
        })

        if plan_check["is_compliant"]:
            st.success("### ✅ PLAN STATUS: APPROVED (सभी नियम मानकों के अनुकूल)")
            st.balloons()
        else:
            st.error(f"### ❌ PLAN STATUS: {plan_check['violations_count']} VIOLATION(S) DETECTED (योजना में कमियां पाई गईं)")

        if plan_check["violations"]:
            st.markdown("#### ⚠️ Specific Violations Requiring Correction:")
            for v in plan_check["violations"]:
                st.error(f"**{v['parameter']}**: Proposed `{v['proposed']}` | Required `{v['required']}` &bull; Deficit: **{v.get('deficit') or v.get('excess')}** ({v['rule']})")

        if plan_check["compliant_checks"]:
            st.markdown("#### ✅ Compliant Parameters:")
            for p in plan_check["compliant_checks"]:
                st.write(f"- **{p['parameter']}**: Proposed `{p['proposed']}` meets requirement `{p['required']}` ({p['rule']})")

# -------------------------------------------------------------
# FEATURE 4: RULE AMENDMENT TRACKER
# -------------------------------------------------------------
elif feature.startswith("📢"):
    st.subheader("📢 Rule Amendment Tracker (संशोधन ट्रैकर)")
    st.caption("Automatic tracking of Madhya Pradesh Government Gazette notifications, comparing previous rules with new amendments.")

    st.markdown("""
    <div class="warning-banner">
        <b>🚨 CRITICAL OVERLAY NOTIFICATION (28 AUG 2026):</b><br>
        Madhya Pradesh Government Gazette Notification regarding <b>Rule 2(5)(c)</b>: Deemed building permissions now extended for plots up to 500 sq m in developed central areas.
        <br><a href="https://teamleaseregtech.com/updates/article/59469/government-of-madhya-pradesh-amendment-to-land-development-rules" target="_blank" style="color: #b91c1c; font-weight:700;">View Official Gazette Notification Link &rarr;</a>
    </div>
    """, unsafe_allow_html=True)

    amendments = get_all_amendments()
    for am in amendments:
        with st.expander(f"📅 {am['date']} — {am['subject']} ({am['rule_affected']})"):
            st.markdown(f"**Gazette Reference**: `{am['gazette_ref']}`")
            st.markdown(f"**Summary**: {am['summary']}")
            col_old, col_new = st.columns(2)
            with col_old:
                st.error(f"**Previous Rule (पुरानी व्यवस्था)**:\n{am['old_provision']}")
            with col_new:
                st.success(f"**Amended Rule (नया प्रावधान)**:\n{am['new_provision']}")
            st.markdown(f"[Official Source / Notification Link]({am['source_url']})")

# -------------------------------------------------------------
# FEATURE 5: VOICE-BASED HINDI ASSISTANT
# -------------------------------------------------------------
elif feature.startswith("🎙️"):
    st.subheader("🎙️ Direct Voice Command Assistant (सीधा आवाज सहायक)")
    st.caption("माइक बटन दबाकर सीधे बोलें। सिस्टम बिना किसी कॉपी-पेस्ट के आपकी आवाज को सीधे समझकर नियम व उत्तर बोलकर सुनाएगा।")

    # Quick instruction banner
    st.info("💡 **सीधा माइक निर्देश**: 1. भाषा चुनें ➔ 2. '🔴 माइक चालू करें' दबाएं ➔ 3. अपना प्रश्न बोलें ➔ 4. '⏹️ बोलना समाप्त' दबाएं। सिस्टम सीधे आपकी आवाज से उत्तर और ऑडियो तैयार करेगा!")

    st.markdown("#### 1️⃣ माइक से सीधा बोलें (Speak Directly via Mic):")

    col_vlang, col_vmic = st.columns([1, 2])
    with col_vlang:
        speech_lang = st.selectbox(
            "भाषा चुनें (Language):",
            ["hi-IN", "en-IN"],
            format_func=lambda x: "🇮🇳 Hindi (हिंदी/Hinglish)" if x == "hi-IN" else "🇬🇧 English",
            key="v_speech_lang_select"
        )
    with col_vmic:
        st.write("**माइक कमांड बटन (Click & Speak):**")
        spoken_text = speech_to_text(
            language=speech_lang,
            start_prompt="🔴 माइक चालू करें (Click to Speak)",
            stop_prompt="⏹️ बोलना समाप्त (Stop & Process)",
            just_once=True,
            use_container_width=True,
            key="direct_voice_assistant_mic"
        )

    # Initialize voice query state
    if "v_query_input" not in st.session_state:
        st.session_state["v_query_input"] = ""

    # Detect spoken voice directly
    if spoken_text and spoken_text.strip():
        st.session_state["v_query_input"] = spoken_text.strip()
        st.session_state["v_auto_run"] = True
        st.success(f"🎙️ **आवाज पहचानी गई (Recognized Voice)**: \"{spoken_text.strip()}\"")

    # Quick sample voice buttons
    st.markdown("#### 2️⃣ या उदाहरण प्रश्न चुनें (Or Pick a Sample):")
    col_v1, col_v2, col_v3 = st.columns(3)
    with col_v1:
        if st.button("🗣️ 15m सड़क पर 300 वर्ग मीटर", key="v_sample_btn1"):
            st.session_state["v_query_input"] = "15 मीटर चौड़ी सड़क पर 300 वर्ग मीटर के आवासीय प्लॉट के लिए सामने कितना खुला स्थान छोड़ना होगा?"
            st.session_state["v_auto_run"] = True
    with col_v2:
        if st.button("🗣️ फार्म हाउस न्यूनतम प्लॉट व FAR", key="v_sample_btn2"):
            st.session_state["v_query_input"] = "कृषि क्षेत्र में फार्म हाउस के लिए न्यूनतम भूखंड और अधिकतम FAR कितना अनुमत है?"
            st.session_state["v_auto_run"] = True
    with col_v3:
        if st.button("🗣️ 250 sqm दुकान की अनुमति फीस", key="v_sample_btn3"):
            st.session_state["v_query_input"] = "250 वर्ग मीटर बिल्ट-अप एरिया की दुकान के लिए अनुमति शुल्क कितना देय होगा?"
            st.session_state["v_auto_run"] = True

    # Active command box
    st.markdown("#### 3️⃣ सक्रिय कमांड (Active Voice Command):")
    v_query = st.text_input(
        "कमांड / प्रश्न:",
        value=st.session_state.get("v_query_input", ""),
        placeholder="माइक से बोलें या यहाँ टाइप करें..."
    )

    should_process = st.session_state.pop("v_auto_run", False) or st.button("🔊 Answer & Read Aloud (उत्तर निकालें व सुनें)", type="primary", key="v_process_btn")

    if should_process and v_query.strip():
        with st.spinner("आधिकारिक नियम खोजे जा रहे हैं और आवाज तैयार हो रही है..."):
            ans = answer_question(v_query)
            st.session_state["v_last_ans"] = ans
            try:
                tts_lang = "hi" if ans["language"] == "hi" else "en"
                tts = gTTS(text=ans['answer'], lang=tts_lang)
                audio_buffer = io.BytesIO()
                tts.write_to_fp(audio_buffer)
                st.session_state["v_last_audio"] = audio_buffer.getvalue()
            except Exception as e:
                st.session_state["v_last_audio"] = None

    # Render persisted answer & audio player
    if "v_last_ans" in st.session_state:
        ans = st.session_state["v_last_ans"]

        # Amendment warning banner if triggered
        if ans.get("amendment_warning"):
            st.markdown(f"""
            <div class="warning-banner">
                ⚠️ <b>AMENDMENT ALERT:</b> {ans['amendment_warning']}
                <br><a href="https://teamleaseregtech.com/updates/article/59469/government-of-madhya-pradesh-amendment-to-land-development-rules" target="_blank" style="color:#b91c1c; text-decoration: underline;">View Gazette Notification &rarr;</a>
            </div>
            """, unsafe_allow_html=True)

        st.success(f"### 📢 उत्तर (Response):")
        st.write(ans['answer'])

        # Native Audio player with Hindi playback
        if st.session_state.get("v_last_audio"):
            st.markdown("#### 🎧 ऑडियो उत्तर (Listen Spoken Audio):")
            st.audio(st.session_state["v_last_audio"], format="audio/mp3", autoplay=True)

        if ans.get("citations"):
            st.markdown("#### 📜 आधिकारिक नियम व उद्धरण (Verified Citations):")
            for cit in ans["citations"]:
                st.info(f"**{cit['rule_number']}** ({cit['page_range']}): \"{cit['exact_quote']}\"")

# -------------------------------------------------------------
# FEATURE 6: RULE COMPARISON DASHBOARD
# -------------------------------------------------------------
elif feature.startswith("📊"):
    st.subheader("📊 Rule Comparison Dashboard (नियम तुलना व तालिकाएं)")
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
    st.subheader("🛡️ AI Answer Verification System & Audit Engine")
    st.caption("Ensuring zero hallucinations: Every citation must be a verified exact substring of the MP Bhumi Vikas Rules text.")

    st.markdown("""
    <div style="background:#eff6ff; border:1px solid #bfdbfe; padding:16px; border-radius:8px; margin-bottom:16px;">
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
    st.subheader("⚙️ " + ("सेटिंग्स व प्राथमिकताएं (Settings & Preferences)" if current_lang == "hi" else "User Settings & Preferences"))
    st.caption("Customize your language, theme, and audio playback settings. Preferences are saved and automatically remembered when you log in again.")

    user = st.session_state["auth_user"]
    prefs = st.session_state.get("user_prefs", {})

    with st.form("settings_pref_form"):
        st.markdown("#### 1️⃣ " + strings["lang_select"])
        p_lang = st.radio(
            strings["lang_select"],
            ["hi", "en"],
            format_func=lambda x: "🇮🇳 Hindi (हिंदी) - सभी नियम, प्रश्न व गणनाएं हिंदी में" if x == "hi" else "🇬🇧 English - Standard English Interface",
            index=0 if prefs.get("language", "hi") == "hi" else 1,
            key="form_lang_choice"
        )

        st.markdown("#### 2️⃣ " + strings["theme_select"])
        p_theme = st.radio(
            strings["theme_select"],
            ["light", "dark"],
            format_func=lambda x: strings["theme_light"] if x == "light" else strings["theme_dark"],
            index=0 if prefs.get("theme", "light") == "light" else 1,
            key="form_theme_choice"
        )

        st.markdown("#### 3️⃣ Audio & Voice Assistant Settings")
        p_audio = st.checkbox(
            strings["auto_audio_label"],
            value=prefs.get("auto_voice_playback", True),
            key="form_audio_choice"
        )

        st.markdown("---")
        save_submitted = st.form_submit_button(strings["save_prefs"], type="primary")

        if save_submitted:
            updated_prefs = {
                "language": p_lang,
                "theme": p_theme,
                "auto_voice_playback": p_audio
            }
            save_user_preferences(user["user_id"], updated_prefs)
            st.session_state["user_prefs"] = updated_prefs
            st.success(strings["prefs_saved"])
            st.rerun()

    st.markdown("#### 👤 " + ("सक्रिय अधिकारी प्रोफाइल (Active Profile)" if current_lang == "hi" else "Active Officer Profile"))
    col_p1, col_p2 = st.columns(2)
    with col_p1:
        st.info(f"""
        **नाम (Name):** {user.get('name')}<br>
        **पद (Role):** {user.get('role')}<br>
        **शाखा (Department):** {user.get('department')}<br>
        **संगठन (Org):** {user.get('organization')}
        """)
    with col_p2:
        st.info(f"""
        **ईमेल (Email):** `{user.get('email', 'N/A')}`<br>
        **फोन (Phone):** `{user.get('phone', 'N/A')}`<br>
        **सक्रिय थीम (Active Theme):** `{prefs.get('theme')}`<br>
        **सक्रिय भाषा (Active Language):** `{'Hindi (हिंदी)' if prefs.get('language') == 'hi' else 'English'}`
        """)

