import os
import sys
import json
import io
import streamlit as st
import streamlit.components.v1 as components
from gtts import gTTS

# Setup path
PROJECT_DIR = os.path.abspath(os.path.dirname(__file__))
if PROJECT_DIR not in sys.path:
    sys.path.insert(0, PROJECT_DIR)

from src.agent import answer_question, VERSION_INFO, DISCLAIMER_EN, DISCLAIMER_HI, extract_parameters
from src.calculators import calculate_comprehensive_building_plan
from src.checker import check_building_plan
from src.tracker import get_all_amendments, get_comparison_tables

st.set_page_config(
    page_title="Bhumi Vikas Sahayak | भूमि विकास सहायक",
    page_icon="🏛️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for high-impact professional aesthetic
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(135deg, #1e3a8a 0%, #0284c7 100%);
        color: white;
        padding: 24px;
        border-radius: 12px;
        margin-bottom: 20px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
    }
    .version-tag {
        background-color: #fef08a;
        color: #854d0e;
        padding: 4px 10px;
        border-radius: 6px;
        font-size: 0.85rem;
        font-weight: 600;
        display: inline-block;
        margin-top: 8px;
    }
    .warning-banner {
        background-color: #fef2f2;
        border-left: 5px solid #ef4444;
        padding: 14px 18px;
        border-radius: 8px;
        color: #991b1b;
        margin-bottom: 18px;
        font-weight: 500;
    }
    .citation-card {
        background-color: #f8fafc;
        border: 1px solid #e2e8f0;
        border-left: 4px solid #0284c7;
        padding: 14px 18px;
        border-radius: 8px;
        margin-top: 10px;
    }
    .verified-badge {
        background-color: #dcfce7;
        color: #166534;
        font-size: 0.75rem;
        font-weight: 700;
        padding: 2px 8px;
        border-radius: 9999px;
        display: inline-block;
        margin-bottom: 6px;
    }
    .disclaimer-box {
        background-color: #f1f5f9;
        border: 1px dashed #cbd5e1;
        padding: 12px;
        border-radius: 8px;
        color: #475569;
        font-size: 0.85rem;
        margin-top: 24px;
    }
</style>
""", unsafe_allow_html=True)

# App Header
st.markdown(f"""
<div class="main-header">
    <h1 style="margin:0; font-size: 2.2rem;">🏛️ Bhumi Vikas Sahayak (भूमि विकास सहायक)</h1>
    <p style="margin:4px 0 0 0; opacity: 0.9; font-size: 1.1rem;">
        Building Permission AI Assistant & Verification Engine | Bhopal Municipal Corporation
    </p>
    <div class="version-tag">📌 {VERSION_INFO}</div>
</div>
""", unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.image("https://img.icons8.com/fluency/96/city-buildings.png", width=72)
    st.title("Navigation & Tools")
    feature = st.radio(
        "Select Module:",
        [
            "💬 1. AI Chatbot (AI सहायक)",
            "📐 2. Smart Calculator (स्मार्ट कैलकुलेटर)",
            "📋 3. Building Plan Checker (योजना परीक्षक)",
            "📢 4. Amendment Tracker (संशोधन ट्रैकर)",
            "🎙️ 5. Voice Assistant (आवाज सहायक)",
            "📊 6. Rule Comparison Dashboard (तुलना डैशबोर्ड)",
            "🛡️ 7. AI Verification System (सत्यापन प्रणाली)"
        ]
    )

    st.markdown("---")
    st.markdown("### 🏢 भोपाल नगर निगम (BMC)")
    st.info("Designed specifically for Building Permission Clerks, Architects, and Citizens of Bhopal.")

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

    # Query Input Box
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
# -------------------------------------------------------------
# FEATURE 5: VOICE-BASED HINDI ASSISTANT
# -------------------------------------------------------------
elif feature.startswith("🎙️"):
    st.subheader("🎙️ Voice-Based Hindi Assistant (आवाज सहायक - हिंदी एवं अंग्रेजी)")
    st.caption("Clerks and citizens can speak their questions in Hindi and receive spoken answers with verified rule citations.")

    st.markdown("#### 1️⃣ माइक से बोलकर प्रश्न पूछें (Speak Hindi Question):")

    # Speech Recognition HTML Component
    mic_html = """
    <div style="background: linear-gradient(135deg, #f1f5f9 0%, #e2e8f0 100%); padding: 22px; border-radius: 12px; border: 1px solid #cbd5e1; text-align: center; font-family: sans-serif;">
        <button id="micBtn" onclick="toggleRecognition()" style="background: #dc2626; color: white; border: none; padding: 14px 28px; border-radius: 50px; font-size: 1.15rem; cursor: pointer; font-weight: 700; box-shadow: 0 4px 6px rgba(220,38,38,0.3); transition: all 0.2s;">
            🎙️ माइक चालू करें (Click to Speak)
        </button>
        <div id="statusIndicator" style="margin-top: 14px; font-weight: 600; color: #475569; font-size: 1rem;">
            माइक बटन दबाएं और हिंदी या अंग्रेजी में अपना सवाल बोलें...
        </div>
        <div id="transcriptBox" style="margin-top: 12px; background: white; border: 1px solid #cbd5e1; border-radius: 8px; padding: 12px; min-height: 50px; font-size: 1.05rem; color: #1e293b; text-align: left;">
            (आपकी बोली हुई बात यहाँ दिखाई देगी...)
        </div>
        <div style="margin-top: 10px;">
            <button onclick="copyToClipboard()" style="background: #2563eb; color: white; border: none; padding: 8px 16px; border-radius: 6px; font-size: 0.9rem; cursor: pointer;">
                📋 टेक्स्ट कॉपी करें (Copy Question)
            </button>
        </div>
    </div>

    <script>
    var recognition = null;
    var isListening = false;

    if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
        var SpeechRec = window.SpeechRecognition || window.webkitSpeechRecognition;
        recognition = new SpeechRec();
        recognition.continuous = false;
        recognition.interimResults = true;
        recognition.lang = 'hi-IN';

        recognition.onstart = function() {
            isListening = true;
            document.getElementById('micBtn').style.background = '#16a34a';
            document.getElementById('micBtn').innerText = '🔴 सुन रहा हूँ... (Listening)';
            document.getElementById('statusIndicator').innerText = 'आवाज रिकॉर्ड हो रही है, कृपया अपना प्रश्न बोलें...';
        };

        recognition.onresult = function(event) {
            var finalTranscript = '';
            for (var i = event.resultIndex; i < event.results.length; ++i) {
                finalTranscript += event.results[i][0].transcript;
            }
            document.getElementById('transcriptBox').innerText = finalTranscript;
        };

        recognition.onerror = function(event) {
            isListening = false;
            document.getElementById('micBtn').style.background = '#dc2626';
            document.getElementById('micBtn').innerText = '🎙️ माइक चालू करें (Click to Speak)';
            document.getElementById('statusIndicator').innerText = 'माइक्रोफोन एरर: ' + event.error + ' (कृपया माइक्रोफोन परमिशन चेक करें)';
        };

        recognition.onend = function() {
            isListening = false;
            document.getElementById('micBtn').style.background = '#dc2626';
            document.getElementById('micBtn').innerText = '🎙️ फिर से बोलें (Click to Speak Again)';
            document.getElementById('statusIndicator').innerText = 'रिकॉर्डिंग समाप्त! नीचे दिए गए बॉक्स में प्रश्न पेस्ट/टाइप करके उत्तर सुनें।';
        };
    } else {
        document.getElementById('statusIndicator').innerText = 'नोट: यह ब्राउज़र वेब स्पीच को सपोर्ट नहीं करता। कृपया Google Chrome या Edge का उपयोग करें।';
    }

    function toggleRecognition() {
        if (!recognition) {
            alert('Speech recognition is not supported in this browser. Please use Chrome or Edge.');
            return;
        }
        if (isListening) {
            recognition.stop();
        } else {
            recognition.start();
        }
    }

    function copyToClipboard() {
        var text = document.getElementById('transcriptBox').innerText;
        if (text && text.indexOf('(आपकी') === -1) {
            navigator.clipboard.writeText(text);
            alert('प्रश्न कॉपी हो गया! अब नीचे इनपुट बॉक्स में पेस्ट कर सकते हैं।');
        } else {
            alert('पहले माइक बटन दबाकर कुछ बोलें!');
        }
    }
    </script>
    """
    components.html(mic_html, height=230)

    st.markdown("#### 2️⃣ प्रश्न की पुष्टि करें या टाइप करें (Verify/Type Question):")

    # Quick voice sample buttons
    col_v1, col_v2, col_v3 = st.columns(3)
    with col_v1:
        if st.button("🗣️ उदाहरण 1: 15m सड़क पर 300 वर्ग मीटर"):
            st.session_state["v_query_input"] = "15 मीटर चौड़ी सड़क पर 300 वर्ग मीटर के आवासीय प्लॉट के लिए सामने कितना खुला स्थान छोड़ना होगा?"
    with col_v2:
        if st.button("🗣️ उदाहरण 2: फार्म हाउस FAR व ऊंचाई"):
            st.session_state["v_query_input"] = "कृषि क्षेत्र में फार्म हाउस के लिए न्यूनतम भूखंड और अधिकतम FAR कितना अनुमत है?"
    with col_v3:
        if st.button("🗣️ उदाहरण 3: 250 sqm दुकान की फीस"):
            st.session_state["v_query_input"] = "250 वर्ग मीटर बिल्ट-अप एरिया की दुकान के लिए अनुमति शुल्क कितना देय होगा?"

    default_v = st.session_state.get("v_query_input", "15 मीटर चौड़ी सड़क पर 300 वर्ग मीटर के आवासीय प्लॉट के लिए सामने कितना खुला स्थान छोड़ना होगा?")
    v_query = st.text_input("Question for Voice Assistant:", value=default_v)

    if st.button("🔊 Answer & Read Aloud in Hindi (उत्तर निकालें व सुनें)", type="primary"):
        if v_query.strip():
            with st.spinner("उत्तर खोजा जा रहा है और आवाज तैयार हो रही है..."):
                ans = answer_question(v_query)

            st.success(f"### 📢 उत्तर (Response):")
            st.write(ans['answer'])

            # Generate and Play Native Audio via gTTS
            try:
                tts_lang = "hi" if ans["language"] == "hi" else "en"
                tts = gTTS(text=ans['answer'], lang=tts_lang)
                audio_buffer = io.BytesIO()
                tts.write_to_fp(audio_buffer)
                audio_bytes = audio_buffer.getvalue()

                st.markdown("#### 🎧 ऑडियो सुनें (Listen Spoken Audio):")
                st.audio(audio_bytes, format="audio/mp3", autoplay=True)
            except Exception as e:
                st.info("Browser Web Speech Playback fallback:")
                clean_speech = ans['answer'].replace('"', '\\"').replace('\n', ' ')
                components.html(f"""
                <script>
                    var msg = new SpeechSynthesisUtterance("{clean_speech}");
                    msg.lang = "{'hi-IN' if ans['language'] == 'hi' else 'en-US'}";
                    window.speechSynthesis.speak(msg);
                </script>
                """, height=0)

            if ans.get("citations"):
                st.markdown("#### 📜 आधिकारिक नियम (Verified Citations):")
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
