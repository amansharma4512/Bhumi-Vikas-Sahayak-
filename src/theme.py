"""
Theme and Localization Engine for Bhumi Vikas Sahayak.
Provides:
- Dynamic CSS styling for Light Mode (White / Royal Blue) and Dark Mode (Black / Deep Slate)
- Bilingual string dictionary for Hindi and English interfaces
"""

def get_theme_css(theme: str = "light") -> str:
    """
    Generate responsive CSS styling for Light or Dark theme.
    """
    if theme == "dark":
        return """
        <style>
            /* Dark Theme Global Palette */
            .stApp {
                background-color: #0b1120 !important;
                color: #f1f5f9 !important;
            }
            [data-testid="stSidebar"] {
                background-color: #0f172a !important;
                color: #f1f5f9 !important;
                border-right: 1px solid #1e293b !important;
            }
            [data-testid="stSidebar"] * {
                color: #f1f5f9 !important;
            }
            .main-header {
                background: linear-gradient(135deg, #0f172a 0%, #1e3a8a 100%) !important;
                color: #ffffff !important;
                padding: 22px;
                border-radius: 12px;
                margin-bottom: 20px;
                border: 1px solid #334155;
                box-shadow: 0 4px 15px rgba(0, 0, 0, 0.4);
            }
            .auth-card {
                background: #1e293b !important;
                border: 1px solid #334155 !important;
                border-radius: 12px;
                padding: 24px;
                box-shadow: 0 10px 25px rgba(0,0,0,0.5);
                color: #f1f5f9 !important;
            }
            .citation-card {
                background-color: #1e293b !important;
                border: 1px solid #334155 !important;
                border-left: 4px solid #38bdf8 !important;
                padding: 14px 18px;
                border-radius: 8px;
                margin-top: 10px;
                color: #e2e8f0 !important;
            }
            .citation-card blockquote {
                color: #cbd5e1 !important;
                border-left: 3px solid #64748b !important;
            }
            .warning-banner {
                background-color: #3b1111 !important;
                border-left: 5px solid #ef4444 !important;
                padding: 14px 18px;
                border-radius: 8px;
                color: #fca5a5 !important;
                margin-bottom: 18px;
                font-weight: 500;
            }
            .verified-badge {
                background-color: #064e3b !important;
                color: #6ee7b7 !important;
                font-size: 0.75rem;
                font-weight: 700;
                padding: 3px 9px;
                border-radius: 9999px;
                display: inline-block;
                margin-bottom: 6px;
                border: 1px solid #059669;
            }
            .disclaimer-box {
                background-color: #1e293b !important;
                border: 1px dashed #475569 !important;
                padding: 12px;
                border-radius: 8px;
                color: #94a3b8 !important;
                font-size: 0.85rem;
                margin-top: 24px;
            }
            .user-badge {
                background-color: #1e293b;
                border: 1px solid #334155;
                padding: 10px 14px;
                border-radius: 8px;
                margin-bottom: 15px;
            }
            /* Dark Input & Select Styling */
            input, textarea, select {
                background-color: #1e293b !important;
                color: #ffffff !important;
                border-color: #475569 !important;
            }
            div[data-baseweb="select"] {
                background-color: #1e293b !important;
                color: #ffffff !important;
            }
            div[data-testid="stMetricValue"] {
                color: #38bdf8 !important;
            }
            .version-tag {
                background-color: #451a03 !important;
                color: #fde68a !important;
                padding: 4px 10px;
                border-radius: 6px;
                font-size: 0.85rem;
                font-weight: 600;
                display: inline-block;
                margin-top: 8px;
                border: 1px solid #78350f;
            }
        </style>
        """
    else:
        return """
        <style>
            /* Light Theme Global Palette */
            .stApp {
                background-color: #f8fafc !important;
                color: #0f172a !important;
            }
            [data-testid="stSidebar"] {
                background-color: #ffffff !important;
                color: #0f172a !important;
                border-right: 1px solid #e2e8f0 !important;
            }
            .main-header {
                background: linear-gradient(135deg, #1e3a8a 0%, #0284c7 100%) !important;
                color: white !important;
                padding: 22px;
                border-radius: 12px;
                margin-bottom: 20px;
                box-shadow: 0 4px 12px -1px rgba(0, 0, 0, 0.12);
            }
            .auth-card {
                background: #ffffff !important;
                border: 1px solid #e2e8f0 !important;
                border-radius: 12px;
                padding: 24px;
                box-shadow: 0 8px 20px rgba(0,0,0,0.06);
            }
            .citation-card {
                background-color: #f8fafc !important;
                border: 1px solid #e2e8f0 !important;
                border-left: 4px solid #0284c7 !important;
                padding: 14px 18px;
                border-radius: 8px;
                margin-top: 10px;
                color: #1e293b !important;
            }
            .citation-card blockquote {
                color: #334155 !important;
                border-left: 3px solid #94a3b8 !important;
            }
            .warning-banner {
                background-color: #fef2f2 !important;
                border-left: 5px solid #ef4444 !important;
                padding: 14px 18px;
                border-radius: 8px;
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
                padding: 12px;
                border-radius: 8px;
                color: #475569 !important;
                font-size: 0.85rem;
                margin-top: 24px;
            }
            .user-badge {
                background-color: #f1f5f9;
                border: 1px solid #e2e8f0;
                padding: 10px 14px;
                border-radius: 8px;
                margin-bottom: 15px;
            }
            .version-tag {
                background-color: #fef08a !important;
                color: #854d0e !important;
                padding: 4px 10px;
                border-radius: 6px;
                font-size: 0.85rem;
                font-weight: 600;
                display: inline-block;
                margin-top: 8px;
            }
        </style>
        """


I18N = {
    "hi": {
        "title": "🏛️ Bhumi Vikas Sahayak (भूमि विकास सहायक)",
        "subtitle": "भवन अनुज्ञा नियम व सत्यापन प्रणाली | भोपाल नगर निगम (Bhopal Municipal Corporation)",
        "sidebar_nav": "मॉड्यूल चयन (Navigation):",
        "modules": [
            "💬 1. AI चैटबॉट (AI Chatbot)",
            "📐 2. स्मार्ट कैलकुलेटर (Smart Calculator)",
            "📋 3. भवन योजना परीक्षक (Plan Checker)",
            "📢 4. संशोधन ट्रैकर (Amendment Tracker)",
            "🎙️ 5. आवाज सहायक (Voice Assistant)",
            "📊 6. नियम तुलना डैशबोर्ड (Comparison Dashboard)",
            "🛡️ 7. AI सत्यापन प्रणाली (Verification System)",
            "⚙️ 8. सेटिंग्स व प्राथमिकताएं (Settings & Preferences)"
        ],
        "logged_in_as": "अधिकृत अधिकारी",
        "role": "पद",
        "department": "शाखा",
        "logout": "🚪 लॉग आउट (Logout)",
        "save_prefs": "💾 प्राथमिकताएं सुरक्षित करें (Save Preferences)",
        "prefs_saved": "✅ आपकी भाषा व थीम प्राथमिकताएं सफलतापूर्वक सुरक्षित कर ली गई हैं!",
        "lang_select": "डिफ़ॉल्ट भाषा (Preferred Language):",
        "theme_select": "डिफ़ॉल्ट थीम (Preferred Theme):",
        "theme_light": "☀️ लाइट मोड (Light Mode - श्वेत/White)",
        "theme_dark": "🌙 डार्क मोड (Dark Mode - श्याम/Black)",
        "auto_audio_label": "उत्तर का स्वतः ऑडियो प्लेबैक चालू रखें (Autoplay Hindi Voice)",
    },
    "en": {
        "title": "🏛️ Bhumi Vikas Sahayak",
        "subtitle": "Building Permission AI Assistant & Verification Engine | Bhopal Municipal Corporation",
        "sidebar_nav": "Select Module:",
        "modules": [
            "💬 1. AI Chatbot",
            "📐 2. Smart Calculator",
            "📋 3. Building Plan Checker",
            "📢 4. Rule Amendment Tracker",
            "🎙️ 5. Voice Assistant",
            "📊 6. Rule Comparison Dashboard",
            "🛡️ 7. AI Verification System",
            "⚙️ 8. User Settings & Preferences"
        ],
        "logged_in_as": "Authorized Officer",
        "role": "Role",
        "department": "Department",
        "logout": "🚪 Logout",
        "save_prefs": "💾 Save Preferences",
        "prefs_saved": "✅ Your language and theme preferences have been saved successfully!",
        "lang_select": "Default Language:",
        "theme_select": "Default Theme:",
        "theme_light": "☀️ Light Mode (White)",
        "theme_dark": "🌙 Dark Mode (Black/Dark Slate)",
        "auto_audio_label": "Enable automatic voice read-aloud (Spoken Audio)",
    }
}


def get_strings(lang: str = "hi") -> dict:
    """Return UI strings in user's preferred language."""
    return I18N.get(lang, I18N["hi"])
