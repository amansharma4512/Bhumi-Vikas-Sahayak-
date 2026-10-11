"""
Rule Amendment Tracker & Comparison Dashboard Module.
Tracks government gazette notifications, highlights changed rules, setbacks, fees,
and provides Old vs New comparison tables for Municipal Corporation Officers.
"""

AMENDMENTS_HISTORY = [
    {
        "date": "28 August 2026",
        "gazette_ref": "Government of Madhya Pradesh Urban Development Notification",
        "rule_affected": "Rule 2(5)(c)",
        "subject": "Deemed building permission for plots up to 500 sq m",
        "change_type": "Critical Amendment Overlay",
        "summary": "Local bodies authorised to issue deemed/instant building permission for plots up to 500 sq m in developed central areas as per landuse permissibility.",
        "old_provision": "Permissions for plots above 186/300 sq m required multi-step scrutiny and Building Officer sanction.",
        "new_provision": "Deemed sanction extended to plots up to 500 sq m with affidavit and online fee payment.",
        "source_url": "https://teamleaseregtech.com/updates/article/59469/government-of-madhya-pradesh-amendment-to-land-development-rules"
    },
    {
        "date": "06 March 2025",
        "gazette_ref": "M.P. Rajpatra (Asadharan) S.N. 72, 73, 74",
        "rule_affected": "Rule 2(7)(a), Rule 2(55)(a), Rule 42, Rule 48, Rule 53(C), Rule 93(a)",
        "subject": "Base FAR, Premium FAR, EV Charging Norms & Dual Piping",
        "change_type": "Major Consolidation",
        "summary": "Introduced Base FAR and Premium FAR definitions (up to 25% extra FAR). Added EV charging station development standards. Mandatory dual water piping system for projects with STP.",
        "old_provision": "Single standard FAR without distinct Base/Premium tiers. No EV charging station dedicated norms. Single plumbing line.",
        "new_provision": "Premium FAR up to 25% over Base FAR. Table 5-A EV station norms. Mandatory dual plumbing (potable + treated/rainwater).",
        "source_url": "https://mptownplan.gov.in/NewsPDF/bvn06032025E.pdf"
    },
    {
        "date": "20 June 2024",
        "gazette_ref": "M.P. Rajpatra Part-4 (Ga) No. 26, Page 850",
        "rule_affected": "Rule 12-A",
        "subject": "Instant/Deemed Building Approval for Residential Plots up to 186 sqm",
        "change_type": "New Rule Insertion",
        "summary": "Inserted Rule 12-A permitting deemed sanction upon submission of application (Appendix A-2(2)), affidavit (Appendix A-2(3)), and fees for residential plots up to 186 sqm.",
        "old_provision": "All residential plots required standard inspection before building permission could be issued.",
        "new_provision": "Submission of form and affidavit with fee acts as a deemed sanction itself without upfront site inspection.",
        "source_url": "https://mptownplan.gov.in"
    },
    {
        "date": "22 August 2022",
        "gazette_ref": "M.P. Rajpatra Part-4 (Ga) No. 34, Pages 689-690",
        "rule_affected": "Rule 24(1)(b)",
        "subject": "Permissible Deviation in Sanctioned Plan",
        "change_type": "Tolerance Limit Amendment",
        "summary": "Substituted clause (b) of Rule 24(1) allowing compounding/deviation up to 30% of the permissible FAR.",
        "old_provision": "Earlier limit was restricted to 10% deviation in FAR.",
        "new_provision": "Deviation permissible up to 30% of the permissible FAR subject to compounding fees.",
        "source_url": "https://mptownplan.gov.in"
    },
    {
        "date": "28 September 2020",
        "gazette_ref": "M.P. Rajpatra (Asadharan) S.N. 710, Pages 12-23",
        "rule_affected": "Rule 6(3), Rule 26, Rule 83, Rule 87(4)",
        "subject": "Architect Licensing & Lift/Fire Safety Regulations",
        "change_type": "Safety and Delegated Authority",
        "summary": "Authorised Architects permitted to issue permissions up to 300 sqm. Mandatory annual fire audits (Rule 87(4)) and lift safety certificates (Rule 83).",
        "old_provision": "Only municipal building officer could approve plans. Annual fire audit submission not strictly codified.",
        "new_provision": "Registered architects with 10 years experience can sanction up to 300 sqm. Mandatory annual fire audit by 30 June.",
        "source_url": "https://mptownplan.gov.in"
    }
]

COMPARISON_TABLES = {
    "setback_comparison": [
        {"Road Width": "Up to 9.0 m", "Residential Front MOS": "3.0 m", "Buildings > 12.5m (Rule 42)": "Not Permitted (Min 12m road)", "High Rise (>30m)": "Not Permitted (Min 30m road)"},
        {"Road Width": "9.0 m to 12.0 m", "Residential Front MOS": "3.6 m", "Buildings > 12.5m (Rule 42)": "Not Permitted", "High Rise (>30m)": "Not Permitted"},
        {"Road Width": "12.0 m to 18.0 m", "Residential Front MOS": "4.5 m", "Buildings > 12.5m (Rule 42)": "7.5 m (Max Ht 18m)", "High Rise (>30m)": "Not Permitted"},
        {"Road Width": "18.0 m to 24.0 m", "Residential Front MOS": "6.0 m", "Buildings > 12.5m (Rule 42)": "9.0 m (Max Ht 24m)", "High Rise (>30m)": "Not Permitted"},
        {"Road Width": "24.0 m to 30.0 m", "Residential Front MOS": "6.0 m", "Buildings > 12.5m (Rule 42)": "12.0 m (Max Ht 30m)", "High Rise (>30m)": "Not Permitted"},
        {"Road Width": "30.0 m and above", "Residential Front MOS": "6.0 m", "Buildings > 12.5m (Rule 42)": "12.0 m", "High Rise (>30m)": "15.0 m (Ht up to 45m)"}
    ],
    "fee_slabs_rule_21": [
        {"Built-up Area Slab": "0 to 75 sq m", "Residential Permission Fee": "Rs. 750", "Commercial (+50%)": "Rs. 1,125", "Application Fee Rate": "Rs. 1.00 / sq m"},
        {"Built-up Area Slab": "76 to 125 sq m", "Residential Permission Fee": "Rs. 1,250", "Commercial (+50%)": "Rs. 1,875", "Application Fee Rate": "Rs. 1.00 / sq m"},
        {"Built-up Area Slab": "126 to 200 sq m", "Residential Permission Fee": "Rs. 2,000", "Commercial (+50%)": "Rs. 3,000", "Application Fee Rate": "Rs. 1.00 / sq m"},
        {"Built-up Area Slab": "201 to 300 sq m", "Residential Permission Fee": "Rs. 3,000", "Commercial (+50%)": "Rs. 4,500", "Application Fee Rate": "Rs. 1.00 / sq m"},
        {"Built-up Area Slab": "301 to 400 sq m", "Residential Permission Fee": "Rs. 4,000", "Commercial (+50%)": "Rs. 6,000", "Application Fee Rate": "Rs. 1.00 / sq m"},
        {"Built-up Area Slab": "401 to 600 sq m", "Residential Permission Fee": "Rs. 6,000", "Commercial (+50%)": "Rs. 9,000", "Application Fee Rate": "Rs. 1.00 / sq m"},
        {"Built-up Area Slab": "601 to 750 sq m", "Residential Permission Fee": "Rs. 7,500", "Commercial (+50%)": "Rs. 11,250", "Application Fee Rate": "Rs. 1.00 / sq m"},
        {"Built-up Area Slab": "751 to 1,000 sq m", "Residential Permission Fee": "Rs. 10,000", "Commercial (+50%)": "Rs. 15,000", "Application Fee Rate": "Rs. 1.00 / sq m"},
        {"Built-up Area Slab": "Above 2,500 sq m", "Residential Permission Fee": "Rs. 50,000", "Commercial (+50%)": "Rs. 75,000", "Application Fee Rate": "Rs. 1.00 / sq m"}
    ]
}

def get_all_amendments():
    return AMENDMENTS_HISTORY

def get_comparison_tables():
    return COMPARISON_TABLES
