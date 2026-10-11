"""
Theme and Localization Engine for Bhumi Vikas Sahayak.
Provides:
- Natural, comfortable Dark Grey palette (charcoal-slate #1e2227, non-artificial, executive look)
- Dignified Light Palette (pure white #f8fafc with royal green/blue government styling)
- Alexa / Google Assistant style minimalist circular microphone styling
- Complete bilingual dictionary for automatic language switching (Hindi & English)
"""

def get_theme_css(theme: str = "dark") -> str:
    """
    Generate clean, natural, eye-friendly CSS styling.
    """
    if theme == "dark":
        return """
        <style>
            /* Natural, Comfortable Dark Grey Palette (No pitch black) */
            .stApp {
                background-color: #1e2227 !important;
                color: #e2e8f0 !important;
                font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif !important;
            }
            [data-testid="stSidebar"] {
                background-color: #242930 !important;
                color: #e2e8f0 !important;
                border-right: 1px solid #333a44 !important;
            }
            [data-testid="stSidebar"] * {
                color: #e2e8f0 !important;
            }
            .main-header {
                background: linear-gradient(135deg, #1e3a24 0%, #243428 50%, #1e293b 100%) !important;
                color: #ffffff !important;
                padding: 22px 26px;
                border-radius: 14px;
                margin-bottom: 20px;
                border: 1px solid #36423a;
                box-shadow: 0 4px 16px rgba(0, 0, 0, 0.25);
            }
            .auth-card {
                background: #262b32 !important;
                border: 1px solid #3a414d !important;
                border-radius: 14px;
                padding: 28px;
                box-shadow: 0 8px 24px rgba(0, 0, 0, 0.2);
                color: #e2e8f0 !important;
            }
            .citation-card {
                background-color: #262b32 !important;
                border: 1px solid #3a414d !important;
                border-left: 4px solid #16a34a !important;
                padding: 14px 18px;
                border-radius: 10px;
                margin-top: 10px;
                color: #e2e8f0 !important;
            }
            .citation-card blockquote {
                color: #cbd5e1 !important;
                border-left: 3px solid #4b5563 !important;
            }
            .warning-banner {
                background-color: #382424 !important;
                border-left: 5px solid #ef4444 !important;
                padding: 14px 18px;
                border-radius: 10px;
                color: #fca5a5 !important;
                margin-bottom: 18px;
                font-weight: 500;
            }
            .verified-badge {
                background-color: #143522 !important;
                color: #86efac !important;
                font-size: 0.75rem;
                font-weight: 600;
                padding: 3px 10px;
                border-radius: 9999px;
                display: inline-block;
                margin-bottom: 6px;
                border: 1px solid #1e5631;
            }
            .disclaimer-box {
                background-color: #242930 !important;
                border: 1px dashed #404856 !important;
                padding: 14px;
                border-radius: 10px;
                color: #94a3b8 !important;
                font-size: 0.85rem;
                margin-top: 24px;
            }
            .user-badge {
                background-color: #292f38;
                border: 1px solid #3a424e;
                padding: 12px 14px;
                border-radius: 10px;
                margin-bottom: 15px;
            }
            /* Natural Slate/Grey Form Elements */
            input, textarea, select {
                background-color: #292f38 !important;
                color: #ffffff !important;
                border-color: #3e4754 !important;
                border-radius: 8px !important;
            }
            div[data-baseweb="select"] {
                background-color: #292f38 !important;
                color: #ffffff !important;
            }
            div[data-testid="stMetricValue"] {
                color: #4ade80 !important;
            }
            .version-tag {
                background-color: #3b2c15 !important;
                color: #fef08a !important;
                padding: 4px 10px;
                border-radius: 6px;
                font-size: 0.82rem;
                font-weight: 600;
                display: inline-block;
                margin-top: 8px;
                border: 1px solid #60461f;
            }
            /* Clean Minimalist Voice Assistant Styling */
            .voice-orb-wrapper {
                text-align: center;
                padding: 20px 0 10px 0;
            }
        </style>
        """
    else:
        return """
        <style>
            /* Light Theme Palette */
            .stApp {
                background-color: #f8fafc !important;
                color: #0f172a !important;
                font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif !important;
            }
            [data-testid="stSidebar"] {
                background-color: #ffffff !important;
                color: #0f172a !important;
                border-right: 1px solid #e2e8f0 !important;
            }
            .main-header {
                background: linear-gradient(135deg, #1e5631 0%, #15803d 50%, #1e3a8a 100%) !important;
                color: white !important;
                padding: 22px 26px;
                border-radius: 14px;
                margin-bottom: 20px;
                box-shadow: 0 4px 14px -1px rgba(0, 0, 0, 0.1);
            }
            .auth-card {
                background: #ffffff !important;
                border: 1px solid #e2e8f0 !important;
                border-radius: 14px;
                padding: 28px;
                box-shadow: 0 8px 24px rgba(0,0,0,0.06);
            }
            .citation-card {
                background-color: #ffffff !important;
                border: 1px solid #e2e8f0 !important;
                border-left: 4px solid #16a34a !important;
                padding: 14px 18px;
                border-radius: 10px;
                margin-top: 10px;
                color: #1e293b !important;
                box-shadow: 0 2px 6px rgba(0,0,0,0.03);
            }
            .citation-card blockquote {
                color: #334155 !important;
                border-left: 3px solid #94a3b8 !important;
            }
            .warning-banner {
                background-color: #fef2f2 !important;
                border-left: 5px solid #ef4444 !important;
                padding: 14px 18px;
                border-radius: 10px;
                color: #991b1b !important;
                margin-bottom: 18px;
                font-weight: 500;
            }
            .verified-badge {
                background-color: #dcfce7 !important;
                color: #166534 !important;
                font-size: 0.75rem;
                font-weight: 700;
                padding: 3px 9px;
                border-radius: 9999px;
                display: inline-block;
                margin-bottom: 6px;
            }
            .disclaimer-box {
                background-color: #f1f5f9 !important;
                border: 1px dashed #cbd5e1 !important;
                padding: 14px;
                border-radius: 10px;
                color: #475569 !important;
                font-size: 0.85rem;
                margin-top: 24px;
            }
            .user-badge {
                background-color: #f8fafc;
                border: 1px solid #e2e8f0;
                padding: 12px 14px;
                border-radius: 10px;
                margin-bottom: 15px;
            }
            .version-tag {
                background-color: #fef08a !important;
                color: #854d0e !important;
                padding: 4px 10px;
                border-radius: 6px;
                font-size: 0.82rem;
                font-weight: 600;
                display: inline-block;
                margin-top: 8px;
            }
        </style>
        """


I18N = {
    "hi": {
        "app_title": "भूमि विकास सहायक",
        "app_subtitle": "भवन अनुज्ञा नियम व गणना प्रणाली | भोपाल नगर निगम, मध्य प्रदेश",
        "tagline": "सही जानकारी • सरल प्रक्रिया • समृद्ध मध्यप्रदेश",
        "sidebar_nav": "मॉड्यूल का चयन करें:",
        "modules": [
            "💬 1. AI चैटबॉट (AI Chatbot)",
            "📐 2. स्मार्ट कैलकुलेटर (Smart Calculator)",
            "📋 3. भवन योजना परीक्षक (Plan Checker)",
            "📢 4. संशोधन ट्रैकर (Amendment Tracker)",
            "🎙️ 5. आवाज सहायक (Voice Assistant)",
            "📊 6. नियम तुलना डैशबोर्ड (Comparison Dashboard)",
            "🛡️ 7. AI सत्यापन प्रणाली (Verification System)",
            "⚙️ 8. सेटिंग्स (Settings)"
        ],
        "logged_in_as": "सक्रिय सत्र (Active Session)",
        "logout": "लॉग आउट (Logout)",
        "otp_title": "सुरक्षित लॉगिन (OTP Verification)",
        "login_sub": "अपने मोबाइल नंबर या आधिकारिक ईमेल पते से लॉगिन करें।",
        "choose_method": "लॉगिन माध्यम चुनें:",
        "phone_opt": "📱 मोबाइल नंबर (Mobile Number)",
        "email_opt": "📧 ईमेल पता (Email Address)",
        "enter_phone": "10-अंकीय मोबाइल नंबर दर्ज करें:",
        "enter_email": "ईमेल पता दर्ज करें:",
        "send_otp": "📩 OTP प्राप्त करें (Get OTP)",
        "enter_otp": "6-अंकीय OTP कोड दर्ज करें:",
        "verify_login": "✅ सत्यापित करें व प्रवेश करें (Verify & Login)",
        "query_placeholder": "अपना सवाल यहाँ पूछें... (उदा. 9 मीटर सड़क पर 200 वर्ग मीटर प्लॉट पर फ्रंट सेटबैक कितना होगा?)",
        "get_answer": "🔍 उत्तर प्राप्त करें",
        "official_citations": "📜 आधिकारिक नियम व उद्धरण:",
        "verif_badge": "✓ 100% सत्यापित नियम उद्धरण",
        "voice_title": "आवाज सहायक (Voice Assistant)",
        "voice_sub": "माइक आइकन पर क्लिक करके सीधे बोलें। उत्तर लिखित और आवाज दोनों में प्राप्त होगा।",
        "theme_toggle": "थीम (Theme):",
        "theme_dark": "🌙 डार्क मोड (Dark)",
        "theme_light": "☀️ लाइट मोड (Light)",
        "lang_name": "हिंदी (Hindi)",
    },
    "en": {
        "app_title": "Bhumi Vikas Sahayak",
        "app_subtitle": "Building Permission AI Assistant & Verification Engine | Bhopal Municipal Corporation, MP",
        "tagline": "Accurate Rules • Simple Process • Empowered Madhya Pradesh",
        "sidebar_nav": "Select Module:",
        "modules": [
            "💬 1. AI Chatbot",
            "📐 2. Smart Building Calculator",
            "📋 3. Building Plan Checker",
            "📢 4. Rule Amendment Tracker",
            "🎙️ 5. Voice Assistant",
            "📊 6. Rule Comparison Dashboard",
            "🛡️ 7. AI Verification System",
            "⚙️ 8. Settings & Preferences"
        ],
        "logged_in_as": "Active Session",
        "logout": "Logout",
        "otp_title": "Secure Login (OTP Verification)",
        "login_sub": "Log in using your registered mobile number or official email address.",
        "choose_method": "Choose Login Method:",
        "phone_opt": "📱 Mobile Number",
        "email_opt": "📧 Email Address",
        "enter_phone": "Enter 10-digit mobile number:",
        "enter_email": "Enter official email address:",
        "send_otp": "📩 Get OTP",
        "enter_otp": "Enter 6-digit OTP code:",
        "verify_login": "✅ Verify & Login",
        "query_placeholder": "Ask your question here... (e.g. My plot is 200 sq m on a 9 m road. How much front gap do I leave?)",
        "get_answer": "🔍 Get Verified Answer",
        "official_citations": "📜 Official Rulebook Citations:",
        "verif_badge": "✓ 100% VERIFIED QUOTE SUBSTRING",
        "voice_title": "Voice Assistant",
        "voice_sub": "Click the microphone to speak naturally. Get instant answers in voice and written text.",
        "theme_toggle": "Theme:",
        "theme_dark": "🌙 Dark Mode",
        "theme_light": "☀️ Light Mode",
        "lang_name": "English",
    }
}


def get_strings(lang: str = "hi") -> dict:
    return I18N.get(lang, I18N["hi"])
