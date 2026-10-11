"""
Deterministic Mathematical & Rule-based Calculators for MP Bhumi Vikas Rules, 2012.
All arithmetic, setback lookups, fee calculations, and limit verifications are executed in Python, NEVER by LLM.
"""

def calculate_front_mos(road_width_m, building_type="residential", height_m=None):
    """
    Calculate required Front Marginal Open Space (FMOS).
    Rule 56(1)(a) for residential height <= 12.5m.
    Rule 42(1) Table 4 for height 12.5m - 30m.
    """
    if height_m is not None and height_m > 12.5:
        if road_width_m >= 24.0:
            return {
                "front_mos_meters": 12.0,
                "rule_citation": "Rule 42(1) Table No. 4 S.No. 3",
                "page": 58,
                "quote": "24 m. & above 2000 sq. m. 30 m. 1:2.0 -] Up to 30 meters 12.00 m. 7.5 m."
            }
        elif road_width_m >= 18.0:
            return {
                "front_mos_meters": 9.0,
                "rule_citation": "Rule 42(1) Table No. 4 S.No. 2",
                "page": 58,
                "quote": "18 m. & above 1500 sq. m. 21 m. 1:1.75 - Up to 24 meters 9.0 6.0"
            }
        elif road_width_m >= 12.0:
            return {
                "front_mos_meters": 7.5,
                "rule_citation": "Rule 42(1) Table No. 4 S.No. 1",
                "page": 58,
                "quote": "12.0 m. and above 1000 sq. m. 18 m. 1:1.50 - Up to 18 meters 7.5 6.0"
            }
        else:
            return {
                "front_mos_meters": 7.5,
                "rule_citation": "Rule 42(1) Table No. 4",
                "page": 58,
                "warning": "Buildings above 12.5m require road width of at least 12.0m."
            }

    # Standard Rule 56(1)(a) for height <= 12.5m
    if road_width_m <= 9.0:
        return {
            "front_mos_meters": 3.0,
            "rule_citation": "Rule 56(1)(a) Table Item 1",
            "page": 77,
            "quote": "Up to 9.0 meters 3.0 meters"
        }
    elif road_width_m <= 12.0:
        return {
            "front_mos_meters": 3.6,
            "rule_citation": "Rule 56(1)(a) Table Item 2",
            "page": 77,
            "quote": "More than 9.0 meters and up to 12 meters 3.6 meters"
        }
    elif road_width_m <= 18.0:
        return {
            "front_mos_meters": 4.5,
            "rule_citation": "Rule 56(1)(a) Table Item 3",
            "page": 77,
            "quote": "More than 12.0 meters and up to 18 meters 4.5 meters"
        }
    else:
        return {
            "front_mos_meters": 6.0,
            "rule_citation": "Rule 56(1)(a) Table Item 4",
            "page": 77,
            "quote": "Above 18 meters 6.0 meters"
        }

def calculate_rear_mos(plot_area_sqm, height_m=None):
    """
    Calculate required Rear Marginal Open Space (RMOS).
    Rule 56(2)(a) for residential height <= 12.5m.
    """
    if height_m is not None and height_m > 12.5:
        if height_m <= 24.0:
            return {
                "rear_mos_meters": 6.0,
                "rule_citation": "Rule 42(1) Table No. 4",
                "page": 58,
                "quote": "Sides/ rear in MOS in meters 6.0"
            }
        else:
            return {
                "rear_mos_meters": 7.5,
                "rule_citation": "Rule 42(1) Table No. 4",
                "page": 58,
                "quote": "Sides/ rear in MOS in meters 7.5 m."
            }

    if plot_area_sqm <= 40.0:
        return {
            "rear_mos_meters": 0.0,
            "rule_citation": "Rule 56(2)(a) Table Item 1",
            "page": 78,
            "quote": "Up to 40.00 Nil"
        }
    elif plot_area_sqm <= 150.0:
        return {
            "rear_mos_meters": 1.50,
            "rule_citation": "Rule 56(2)(a) Table Item 2",
            "page": 78,
            "quote": "Above 40.00 and up to 150.00 1.50"
        }
    elif plot_area_sqm <= 225.0:
        return {
            "rear_mos_meters": 2.50,
            "rule_citation": "Rule 56(2)(a) Table Item 3",
            "page": 78,
            "quote": "Above 150 and up to 225.00 2.50"
        }
    else:
        return {
            "rear_mos_meters": 3.00,
            "rule_citation": "Rule 56(2)(a) Table Item 4",
            "page": 78,
            "quote": "Above 225.00 3.00"
        }

def calculate_side_mos(development_type="detached", frontage_m=None, height_m=None):
    """
    Calculate Side Marginal Open Space (SMOS).
    Rule 56(3).
    """
    dev = development_type.lower()
    if "row" in dev:
        return {
            "side_mos_meters": 0.0,
            "rule_citation": "Rule 56(3)(iii)",
            "page": 78,
            "quote": "For row-type buildings, no side open space is required."
        }
    elif "semi" in dev:
        side = 3.0
        quote = "For semi-detached building there shall be a minimum side open space of 3.0 meters on one side."
        if height_m is not None and height_m <= 10.0 and frontage_m is not None and frontage_m <= 10.0:
            side = 2.5
            quote = "For Semi-detached building up to 10 meters in height on plots with a frontage up to 10 meters, the side open space may be reduced to 2.5 meters."
        return {
            "side_mos_meters": side,
            "one_side_only": True,
            "rule_citation": "Rule 56(3)(ii)",
            "page": 78,
            "quote": quote
        }
    else:
        # Detached
        side = 3.0
        quote = "For detached buildings there shall be minimum side open spaces of 3 meters on both the sides"
        if height_m is not None and height_m <= 7.0 and frontage_m is not None and frontage_m < 12.0:
            return {
                "side_mos_meters": 3.0,
                "reduced_side_mos_meters": 1.5,
                "both_sides": True,
                "rule_citation": "Rule 56(3)(i) Proviso",
                "page": 78,
                "quote": "for detached residential building up to 7 meters in height on plots with a frontage less than 12 meters, one of the sides open space may be reduced to 1.5 meters."
            }
        return {
            "side_mos_meters": side,
            "both_sides": True,
            "rule_citation": "Rule 56(3)(i)",
            "page": 78,
            "quote": quote
        }

def calculate_far_and_area(plot_area_sqm, building_type="residential", category=None):
    """
    Calculate permissible FAR and maximum built-up area.
    Rule 61, Table 8.
    """
    btype = building_type.lower()
    if "farm" in btype:
        far = 0.10
        citation = "Rule 17(b)"
        page = 34
        quote = "Maximum F.A.R. shall be 0.10;"
    elif "commercial" in btype or "mercantile" in btype or "shop" in btype:
        cat = (category or "").lower()
        if "city centre" in cat:
            far = 2.50
        elif "sub" in cat:
            far = 2.00
        elif "community" in cat:
            far = 1.75
        elif "local" in cat:
            far = 1.50
        else:
            far = 1.25  # Convenience Shopping Centre
        citation = "Rule 61 Table 8 Item 2"
        page = 83
        quote = "Commercial 2.50 City Centre"
    elif "public" in btype or "institutional" in btype:
        far = 1.00
        citation = "Rule 61 Table 8 Item 3"
        page = 83
        quote = "Public Semi-public 1.00"
    else:
        # Residential
        far = 1.25
        citation = "Rule 61 Table 8 Item 1"
        page = 83
        quote = "Resdential 1.25"

    max_builtup = plot_area_sqm * far
    return {
        "base_far": far,
        "max_builtup_area_sqm": round(max_builtup, 2),
        "rule_citation": citation,
        "page": page,
        "quote": quote
    }

def calculate_permission_fees(builtup_area_sqm, building_type="residential", is_high_rise=False):
    """
    Calculate Application Fee and Permission Fee.
    Rule 21(2)(ii) & Rule 21(3)(b).
    """
    btype = building_type.lower()
    # Application Fee: Rs. 1.00 per sq m of proposed built-up area
    app_fee = round(builtup_area_sqm * 1.0, 2)
    app_fee_citation = "Rule 21(2)(ii)"
    app_fee_quote = "for the Building Permission Rs 1.00 per Square meter of the proposed built-up area."

    if is_high_rise:
        if "commercial" in btype or "shop" in btype or "industrial" in btype:
            rate = 20.0  # Rs 10 + 100%
            perm_fee = builtup_area_sqm * rate
            citation = "Rule 21(3)(c) Item 2"
            quote = "Fees as prescribed in item No. 1 with additional charges of 100% of amount of fees."
        else:
            rate = 10.0
            perm_fee = builtup_area_sqm * rate
            citation = "Rule 21(3)(c) Item 1"
            quote = "Rs. 10.00 per square meter of the built up area."
        return {
            "application_fee": app_fee,
            "permission_fee": round(perm_fee, 2),
            "total_fee": round(app_fee + perm_fee, 2),
            "app_fee_citation": app_fee_citation,
            "perm_fee_citation": citation,
            "perm_fee_quote": quote,
            "page": 37
        }

    # Standard residential table lookup (Rule 21(3)(b) Item 1)
    # 0-75: 750, 76-125: 1250, 126-200: 2000, 201-300: 3000, 301-400: 4000,
    # 401-600: 6000, 601-750: 7500, 751-1000: 10000, 1001-1250: 12500,
    # 1251-1500: 15000, 1501-2000: 20000, 2001-2500: 25000, >2500: 50000
    fee_slabs = [
        (75, 750, "0 75 750"),
        (125, 1250, "76 125 1,250"),
        (200, 2000, "126 200 2,000"),
        (300, 3000, "201 300 3,000"),
        (400, 4000, "301 400 4,000"),
        (600, 6000, "401 600 6,000"),
        (750, 7500, "601 750 7,500"),
        (1000, 10000, "751 1,000 10,000"),
        (1250, 12500, "1,001 1,250 12,500"),
        (1500, 15000, "1,251 1,500 15,000"),
        (2000, 20000, "1,501 2,000 20,000"),
        (2500, 25000, "2,001 2,500 25,000"),
        (float('inf'), 50000, "above 2500 50,000")
    ]

    base_fee = 750
    slab_quote = "0 75 750"
    for max_area, fee, q in fee_slabs:
        if builtup_area_sqm <= max_area:
            base_fee = fee
            slab_quote = q
            break

    if "commercial" in btype or "shop" in btype or "trade" in btype:
        perm_fee = base_fee * 1.5  # 50% extra
        citation = "Rule 21(3)(b) Item 2"
        quote = "Fees as prescribed in item No. 1 together with additional charge of 50% of such amount of fees."
    else:
        perm_fee = base_fee
        citation = "Rule 21(3)(b) Item 1"
        quote = slab_quote

    return {
        "application_fee": app_fee,
        "permission_fee": round(perm_fee, 2),
        "total_fee": round(app_fee + perm_fee, 2),
        "app_fee_citation": app_fee_citation,
        "app_fee_quote": app_fee_quote,
        "perm_fee_citation": citation,
        "perm_fee_quote": quote,
        "page": 36
    }

def calculate_electric_clearance(voltage_volts):
    """
    Calculate minimum vertical and horizontal distance from electric lines.
    Rule 52.
    """
    if voltage_volts <= 650:
        # Low and medium voltage
        return {
            "vertical_meters": 2.5,
            "horizontal_meters": 1.2,
            "rule_citation": "Rule 52(1) Table (a)",
            "page": 69,
            "quote": "Low and Medium voltage lines and service lines 2.5 1.2"
        }
    elif voltage_volts <= 33000:
        # High voltage
        return {
            "vertical_meters": 3.7,
            "horizontal_meters": 1.2,
            "rule_citation": "Rule 52(1) Table (b)",
            "page": 69,
            "quote": "High voltage lines up to and including 33000 volts 3.7 1.2"
        }
    else:
        # Extra high voltage
        return {
            "corridor_width_meters": 15.0,
            "open_each_side_meters": 7.5,
            "rule_citation": "Rule 52(1) Note",
            "page": 69,
            "quote": "clear horizontal corridor of 15 meters (7.5 meter open both side of centre line)"
        }

def calculate_comprehensive_building_plan(plot_area_sqm, road_width_m, building_type="residential", development_type="detached", proposed_builtup_sqm=None, proposed_height_m=None):
    """
    All-in-one Smart Building Calculator.
    Calculates setbacks, permissible FAR, max built-up area, fees, tree plantation, rainwater harvesting.
    """
    front_mos = calculate_front_mos(road_width_m, building_type, proposed_height_m)
    rear_mos = calculate_rear_mos(plot_area_sqm, proposed_height_m)
    side_mos = calculate_side_mos(development_type, height_m=proposed_height_m)
    far_info = calculate_far_and_area(plot_area_sqm, building_type)

    builtup = proposed_builtup_sqm if proposed_builtup_sqm is not None else far_info["max_builtup_area_sqm"]
    is_hr = (proposed_height_m is not None and proposed_height_m > 30.0)
    fees = calculate_permission_fees(builtup, building_type, is_high_rise=is_hr)

    # Ancillary requirements
    trees_required = int(plot_area_sqm // 100) if plot_area_sqm >= 100 else 0
    rainwater_harvesting = (plot_area_sqm > 140.0)
    deemed_approval_eligible = (building_type.lower() == "residential" and plot_area_sqm <= 186.0)

    # 28 Aug 2026 amendment warning for plots <= 500 sqm
    amendment_warning = (plot_area_sqm <= 500.0)

    return {
        "plot_area_sqm": plot_area_sqm,
        "road_width_m": road_width_m,
        "building_type": building_type,
        "development_type": development_type,
        "setbacks": {
            "front_mos_meters": front_mos["front_mos_meters"],
            "front_citation": front_mos["rule_citation"],
            "rear_mos_meters": rear_mos["rear_mos_meters"],
            "rear_citation": rear_mos["rule_citation"],
            "side_mos_meters": side_mos["side_mos_meters"],
            "side_citation": side_mos["rule_citation"]
        },
        "far": {
            "base_far": far_info["base_far"],
            "max_permissible_builtup_sqm": far_info["max_builtup_area_sqm"],
            "citation": far_info["rule_citation"]
        },
        "fees": fees,
        "environmental": {
            "trees_required": trees_required,
            "tree_rule": "Rule 67 (1 tree per 100 sq m if plot >= 100 sq m)",
            "rainwater_harvesting_mandatory": rainwater_harvesting,
            "rwh_rule": "Rule 81(4) (Mandatory for plot size > 140 sq m)"
        },
        "fast_track": {
            "deemed_instant_approval_eligible": deemed_approval_eligible,
            "rule": "Rule 12-A (Instant/deemed sanction for residential plots up to 186 sq m)"
        },
        "amendment_warning": amendment_warning
    }

if __name__ == "__main__":
    res = calculate_comprehensive_building_plan(200, 9, "residential")
    print("Comprehensive Calculator Test Result:")
    import pprint
    pprint.pprint(res)
