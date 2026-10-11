import os
import sys
import json
import streamlit as st

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
elif feature.startswith("🎙️"):
    st.subheader("🎙️ Voice-Based Hindi Assistant (आवाज सहायक)")
    st.caption("Clerks and citizens speak questions in Hindi and receive spoken answers with verified rule citations.")

    # Voice input component using HTML5 Speech Recognition & Synthesis
    st.markdown("""
    <div style="background: #f8fafc; padding: 20px; border-radius: 12px; border: 1px solid #cbd5e1; text-align: center;">
        <button id="micBtn" onclick="startDictation()" style="background: #ef4444; color: white; border: none; padding: 12px 24px; border-radius: 50px; font-size: 1.1rem; cursor: pointer; font-weight: 600;">
            🎙️ बोलकर प्रश्न पूछें (Click to Speak Hindi)
        </button>
        <p id="transcriptText" style="margin-top: 14px; font-weight: 500; color: #1e293b;">माइक बटन दबाएं और हिंदी में अपना प्रश्न बोलें...</p>
    </div>

    <script>
    function startDictation() {
        if (window.hasOwnProperty('webkitSpeechRecognition')) {
            var recognition = new webkitSpeechRecognition();
            recognition.continuous = false;
            recognition.interimResults = false;
            recognition.lang = "hi-IN";
            recognition.start();

            document.getElementById('micBtn').innerText = "🔴 सुन रहा हूँ... (Listening)";
            recognition.onresult = function(e) {
                var spoken = e.results[0][0].transcript;
                document.getElementById('transcriptText').innerText = "आपने कहा: " + spoken;
                document.getElementById('micBtn').innerText = "🎙️ फिर से बोलें (Speak Again)";
                // Speak response back
                var msg = new SpeechSynthesisUtterance("आपका प्रश्न दर्ज किया गया है: " + spoken);
                msg.lang = 'hi-IN';
                window.speechSynthesis.speak(msg);
            };
            recognition.onerror = function(e) {
                recognition.stop();
                document.getElementById('micBtn').innerText = "🎙️ बोलकर प्रश्न पूछें";
            };
        } else {
            alert("Speech recognition not supported in this browser. Please use Google Chrome or Edge.");
        }
    }
    </script>
    """, unsafe_allow_html=True)

    v_query = st.text_input("Spoken / Typed Hindi Question (या यहाँ टाइप करें):", value="15 मीटर सड़क पर 300 वर्ग मीटर आवासीय प्लॉट के लिए सामने कितना खुला स्थान छोड़ना होगा?")
    if st.button("🔊 Answer & Read Aloud (उत्तर सुनें)", type="primary"):
        with st.spinner("उत्तर तैयार किया जा रहा है..."):
            ans = answer_question(v_query)
        st.success(f"**उत्तर**: {ans['answer']}")
        if ans.get("citations"):
            for cit in ans["citations"]:
                st.info(f"📜 **{cit['rule_number']}** ({cit['page_range']}): \"{cit['exact_quote']}\"")

        # Read aloud in Hindi using Web Speech
        clean_speech = ans['answer'].replace('"', '\\"').replace('\n', ' ')
        st.markdown(f"""
        <script>
            var msg = new SpeechSynthesisUtterance("{clean_speech}");
            msg.lang = "hi-IN";
            window.speechSynthesis.speak(msg);
        </script>
        """, unsafe_allow_html=True)

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
