"""
Building Plan Checker Module.
Compares proposed building plan specifications against official MP Bhumi Vikas Rules, 2012.
Flags violations in Front MOS, Rear MOS, Side MOS, FAR, Height, and Fees before submission.
"""

from src.calculators import (
    calculate_front_mos,
    calculate_rear_mos,
    calculate_side_mos,
    calculate_far_and_area,
    calculate_permission_fees
)

def check_building_plan(plan_data):
    """
    plan_data: {
        'plot_area_sqm': float,
        'road_width_m': float,
        'building_type': 'residential' | 'commercial' | 'farm house',
        'development_type': 'detached' | 'semi-detached' | 'row-type',
        'proposed_front_mos_m': float,
        'proposed_rear_mos_m': float,
        'proposed_side_mos_m': float,
        'proposed_builtup_sqm': float,
        'proposed_height_m': float
    }
    """
    violations = []
    passes = []

    plot_area = float(plan_data.get("plot_area_sqm", 0.0))
    road_width = float(plan_data.get("road_width_m", 0.0))
    btype = plan_data.get("building_type", "residential")
    dev_type = plan_data.get("development_type", "detached")
    prop_height = float(plan_data.get("proposed_height_m", 0.0)) if plan_data.get("proposed_height_m") else 10.0

    # 1. Check Front Setback
    req_front = calculate_front_mos(road_width, btype, prop_height)
    prop_front = float(plan_data.get("proposed_front_mos_m", 0.0))
    if prop_front < req_front["front_mos_meters"]:
        violations.append({
            "parameter": "Front Open Space (FMOS)",
            "proposed": f"{prop_front} m",
            "required": f">= {req_front['front_mos_meters']} m",
            "deficit": f"{round(req_front['front_mos_meters'] - prop_front, 2)} m deficient",
            "rule": req_front["rule_citation"],
            "severity": "CRITICAL"
        })
    else:
        passes.append({
            "parameter": "Front Open Space (FMOS)",
            "proposed": f"{prop_front} m",
            "required": f">= {req_front['front_mos_meters']} m",
            "rule": req_front["rule_citation"]
        })

    # 2. Check Rear Setback
    req_rear = calculate_rear_mos(plot_area, prop_height)
    prop_rear = float(plan_data.get("proposed_rear_mos_m", 0.0))
    if prop_rear < req_rear["rear_mos_meters"]:
        violations.append({
            "parameter": "Rear Open Space (RMOS)",
            "proposed": f"{prop_rear} m",
            "required": f">= {req_rear['rear_mos_meters']} m",
            "deficit": f"{round(req_rear['rear_mos_meters'] - prop_rear, 2)} m deficient",
            "rule": req_rear["rule_citation"],
            "severity": "CRITICAL"
        })
    else:
        passes.append({
            "parameter": "Rear Open Space (RMOS)",
            "proposed": f"{prop_rear} m",
            "required": f">= {req_rear['rear_mos_meters']} m",
            "rule": req_rear["rule_citation"]
        })

    # 3. Check Side Setback
    req_side = calculate_side_mos(dev_type, height_m=prop_height)
    prop_side = float(plan_data.get("proposed_side_mos_m", 0.0))
    if prop_side < req_side["side_mos_meters"]:
        violations.append({
            "parameter": "Side Open Space (SMOS)",
            "proposed": f"{prop_side} m",
            "required": f">= {req_side['side_mos_meters']} m",
            "deficit": f"{round(req_side['side_mos_meters'] - prop_side, 2)} m deficient",
            "rule": req_side["rule_citation"],
            "severity": "CRITICAL"
        })
    else:
        passes.append({
            "parameter": "Side Open Space (SMOS)",
            "proposed": f"{prop_side} m",
            "required": f">= {req_side['side_mos_meters']} m",
            "rule": req_side["rule_citation"]
        })

    # 4. Check FAR & Built-up Area
    far_info = calculate_far_and_area(plot_area, btype)
    prop_builtup = float(plan_data.get("proposed_builtup_sqm", 0.0))
    if prop_builtup > far_info["max_builtup_area_sqm"]:
        violations.append({
            "parameter": "Total Built-up Area (FAR Limit)",
            "proposed": f"{prop_builtup} sq m",
            "required": f"<= {far_info['max_builtup_area_sqm']} sq m (FAR {far_info['base_far']})",
            "excess": f"{round(prop_builtup - far_info['max_builtup_area_sqm'], 2)} sq m excess",
            "rule": far_info["rule_citation"],
            "severity": "HIGH"
        })
    else:
        passes.append({
            "parameter": "Total Built-up Area (FAR Limit)",
            "proposed": f"{prop_builtup} sq m",
            "required": f"<= {far_info['max_builtup_area_sqm']} sq m (FAR {far_info['base_far']})",
            "rule": far_info["rule_citation"]
        })

    # 5. Calculate Official Applicable Fees
    fees = calculate_permission_fees(prop_builtup, btype)

    # 6. Environmental & Fast Track Checks
    trees_needed = int(plot_area // 100) if plot_area >= 100 else 0
    rwh_mandatory = (plot_area > 140.0)
    instant_eligible = (btype.lower() == "residential" and plot_area <= 186.0)

    is_compliant = len(violations) == 0

    return {
        "status": "APPROVED" if is_compliant else "VIOLATIONS_FOUND",
        "is_compliant": is_compliant,
        "violations_count": len(violations),
        "passes_count": len(passes),
        "violations": violations,
        "compliant_checks": passes,
        "applicable_fees": fees,
        "advisory": {
            "trees_required": trees_needed,
            "rainwater_harvesting_mandatory": rwh_mandatory,
            "instant_deemed_eligible": instant_eligible
        }
    }
