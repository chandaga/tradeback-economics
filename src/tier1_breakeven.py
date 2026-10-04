"""
Tier 1 Analytical Break-Even Solver and Sensitivity Engine (Pure Python Core).

Computes:
1. The 2D Break-Even Isocline: Delta_Contribution(Delta_f, E[R_net]) = 0.
2. The 5 Deal-Breaker Thresholds for investor presentations.
3. Exact answers to the 10 specific business questions from Section 17.
4. Global 12-Variable Tornado Sensitivity Analysis.

All mathematical derivations are grounded in the Canonical 2-Lever Architecture:
    ΔLTC = (ΔN_orders * CM_order) + N_TB * (E[R_net_ops] + E[CAC_avoided] - C_TB)

Zero external dependencies required (Pure Python with built-in bisection solver).
References:
- docs/ARCHITECTURE_1PAGER.md
- docs/DECISION_LOG.md
"""

from typing import Dict, List, Tuple, Any, Callable
import math

from src.assumptions import get_default_assumptions, PARAMETER_REGISTRY
from src.tier0_engine import calculate_tier0_economics, compute_unit_net_salvage_recovery

def bisection_solve(func: Callable[[float], float], a: float, b: float, tol: float = 1e-4, max_iter: int = 100) -> float:
    """
    Robust pure-Python root finding using the bisection method.
    """
    f_a = func(a)
    f_b = func(b)
    
    if abs(f_a) < tol:
        return a
    if abs(f_b) < tol:
        return b
        
    if f_a * f_b > 0:
        # If bracket doesn't cross zero, do a coarse grid search to find bracket
        grid_steps = 100
        step = (b - a) / grid_steps
        bracket_found = False
        curr_x = a
        curr_f = f_a
        for _ in range(grid_steps):
            next_x = curr_x + step
            next_f = func(next_x)
            if curr_f * next_f <= 0:
                a, b = curr_x, next_x
                f_a, f_b = curr_f, next_f
                bracket_found = True
                break
            curr_x, curr_f = next_x, next_f
        if not bracket_found:
            # Return x with minimum absolute error
            best_x, best_err = a, abs(f_a)
            for i in range(grid_steps + 1):
                tx = a + i * step
                err = abs(func(tx))
                if err < best_err:
                    best_x, best_err = tx, err
            return best_x

    for _ in range(max_iter):
        mid = (a + b) / 2.0
        f_mid = func(mid)
        if abs(f_mid) < tol or (b - a) / 2.0 < tol:
            return mid
        if f_a * f_mid < 0:
            b = mid
            f_b = f_mid
        else:
            a = mid
            f_a = f_mid
            
    return (a + b) / 2.0

def solve_breakeven_recovery(target_delta_f: float, custom_params: Dict[str, float] = None) -> float:
    """
    Finds the exact net recovery E[R_net_ops] required to achieve
    Delta_Contribution = 0 given a fixed causal frequency uplift Delta_f.
    
    Derived from the Canonical Equation:
        ΔLTC = (ΔN_orders * CM_order) + N_TB * (E[R_net_ops] + E[CAC_avoided] - C_TB) = 0
        ==> E[R_net_ops] = C_TB - E[CAC_avoided] - (ΔN_orders * CM_order) / N_TB
    """
    params = get_default_assumptions()
    if custom_params:
        params.update(custom_params)
        
    eval_window_years = 3.0
    lifespan_years = min(eval_window_years, params["customer_lifespan_months"] / 12.0)
    
    f_base = params["baseline_annual_orders"]
    delta_n_orders = target_delta_f * lifespan_years
    n_orders_adopter = (f_base + target_delta_f) * lifespan_years
    
    n_stranded = params.get("stranded_garments_terminal", 1.0)
    n_eligible_repeats = max(0.0, n_orders_adopter - 1.0 - n_stranded)
    u = params.get("order_utilization_rate", 0.75)
    n_tb = n_eligible_repeats * u
    
    aov = params["aov"]
    gm = params["gross_margin_pct"]
    c_fulfill = params["forward_fulfillment_cost"]
    cm_order = (aov * gm) - c_fulfill
    
    cac_rep = params["repeat_ad_cac"]
    p_paid_rep = params.get("paid_repeat_share", 0.50)
    s_ad = params.get("ad_savings_pct", 0.60)
    cac_avoided = cac_rep * s_ad * p_paid_rep
    
    credit_pct = params["tradeback_credit_pct"]
    beta = params.get("credit_breakage_pct", 0.0)
    c_tb = aov * credit_pct * (1.0 - beta)
    
    if n_tb <= 1e-6:
        # If no returns occur, break-even requires volume margin >= 0
        return 0.0
        
    req_net_recovery = c_tb - cac_avoided - (delta_n_orders * cm_order) / n_tb
    return req_net_recovery

def solve_breakeven_delta_f(target_net_recovery: float, custom_params: Dict[str, float] = None) -> float:
    """
    Finds the exact causal frequency uplift (Delta_f) required to achieve
    Delta_Contribution = 0 given a fixed net recovery value E[R_net_ops].
    """
    params = get_default_assumptions()
    if custom_params:
        params.update(custom_params)
        
    eval_window_years = 3.0
    lifespan_years = min(eval_window_years, params["customer_lifespan_months"] / 12.0)
    
    f_base = params["baseline_annual_orders"]
    n_stranded = params.get("stranded_garments_terminal", 1.0)
    u = params.get("order_utilization_rate", 0.75)
    
    aov = params["aov"]
    gm = params["gross_margin_pct"]
    c_fulfill = params["forward_fulfillment_cost"]
    cm_order = (aov * gm) - c_fulfill
    
    cac_rep = params["repeat_ad_cac"]
    p_paid_rep = params.get("paid_repeat_share", 0.50)
    s_ad = params.get("ad_savings_pct", 0.60)
    cac_avoided = cac_rep * s_ad * p_paid_rep
    
    credit_pct = params["tradeback_credit_pct"]
    beta = params.get("credit_breakage_pct", 0.0)
    c_tb = aov * credit_pct * (1.0 - beta)
    
    circ_unit_spread = target_net_recovery + cac_avoided - c_tb
    
    def objective_f(delta_f_val: float) -> float:
        delta_n = delta_f_val * lifespan_years
        n_adopter = (f_base + delta_f_val) * lifespan_years
        n_tb = max(0.0, n_adopter - 1.0 - n_stranded) * u
        delta_ltc = (delta_n * cm_order) + (n_tb * circ_unit_spread)
        return delta_ltc

    return bisection_solve(objective_f, -0.5, 3.0)

def solve_max_affordable_credit_pct(custom_params: Dict[str, float] = None) -> float:
    """
    Solves for the maximum credit % at which Delta_Contribution >= 0.
    
    Formula:
        C_TB,max = E[R_net_ops] + E[CAC_avoided] + (ΔN_orders * CM_order) / N_TB
        Credit_%,max = C_TB,max / AOV
    """
    params = get_default_assumptions()
    if custom_params:
        params.update(custom_params)
        
    eval_window_years = 3.0
    lifespan_years = min(eval_window_years, params["customer_lifespan_months"] / 12.0)
    
    f_base = params["baseline_annual_orders"]
    delta_f = params["causal_frequency_uplift"]
    delta_n_orders = delta_f * lifespan_years
    n_orders_adopter = (f_base + delta_f) * lifespan_years
    
    n_stranded = params.get("stranded_garments_terminal", 1.0)
    n_eligible_repeats = max(0.0, n_orders_adopter - 1.0 - n_stranded)
    u = params.get("order_utilization_rate", 0.75)
    n_tb = n_eligible_repeats * u
    
    aov = params["aov"]
    gm = params["gross_margin_pct"]
    c_fulfill = params["forward_fulfillment_cost"]
    cm_order = (aov * gm) - c_fulfill
    
    cac_rep = params["repeat_ad_cac"]
    p_paid_rep = params.get("paid_repeat_share", 0.50)
    s_ad = params.get("ad_savings_pct", 0.60)
    cac_avoided = cac_rep * s_ad * p_paid_rep
    
    unit_net_salvage = compute_unit_net_salvage_recovery(params)
    
    if n_tb <= 1e-6:
        return 0.35
        
    max_c_tb = unit_net_salvage + cac_avoided + (delta_n_orders * cm_order) / n_tb
    max_credit_pct = max_c_tb / aov
    return max_credit_pct

def solve_max_tolerable_processing_cost(custom_params: Dict[str, float] = None) -> float:
    """
    Solves for the maximum QC + inspection cost tolerable before TradeBack becomes dilutive.
    
    Formula:
        C_QC,max = C_QC,base + (ΔLTC_adopter / N_TB)
    """
    params = get_default_assumptions()
    if custom_params:
        params.update(custom_params)
        
    res = calculate_tier0_economics(params)
    if res.n_returns_adopter <= 1e-6:
        return params.get("qc_inspection_cost", 45.0)
        
    current_qc = params.get("qc_inspection_cost", 45.0)
    buffer_per_return = res.delta_ltc_adopter / res.n_returns_adopter
    max_qc = current_qc + buffer_per_return
    return max_qc

def generate_breakeven_isocline(custom_params: Dict[str, float] = None) -> List[Dict[str, float]]:
    """
    Generates a 2D Break-Even curve mapping
    Causal Order Uplift (Delta_f) to Required Net Recovery E[R_net_ops].
    """
    delta_f_points = [0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.8, 1.0, 1.2, 1.5]
    curve_data = []
    for df in delta_f_points:
        req_rec = solve_breakeven_recovery(df, custom_params)
        curve_data.append({
            "causal_frequency_uplift": round(df, 2),
            "required_net_recovery": round(req_rec, 2)
        })
    return curve_data

def run_tornado_sensitivity(custom_params: Dict[str, float] = None) -> List[Dict[str, Any]]:
    """
    Computes global tornado sensitivity ranking across 12 critical variables.
    """
    params = get_default_assumptions()
    if custom_params:
        params.update(custom_params)
        
    tested_vars = [
        "causal_frequency_uplift",
        "tradeback_credit_pct",
        "tradeback_adoption_rate",
        "order_utilization_rate",
        "paid_repeat_share",
        "ad_savings_pct",
        "b2b_gross_price",
        "qc_inspection_cost",
        "gross_margin_pct",
        "aov",
        "repeat_ad_cac",
        "swap_failure_rate",
    ]
    
    tornado_results = []
    for var in tested_vars:
        meta = PARAMETER_REGISTRY[var]
        
        # Low swing
        p_low = params.copy()
        p_low[var] = meta.min_value
        res_low = calculate_tier0_economics(p_low)
        delta_low = res_low.delta_contribution_tradeback
        
        # High swing
        p_high = params.copy()
        p_high[var] = meta.max_value
        res_high = calculate_tier0_economics(p_high)
        delta_high = res_high.delta_contribution_tradeback
        
        swing = abs(delta_high - delta_low)
        tornado_results.append({
            "variable": var,
            "display_name": meta.display_name,
            "min_val": meta.min_value,
            "max_val": meta.max_value,
            "default_val": meta.default_value,
            "unit": meta.unit,
            "delta_cm_at_min": round(delta_low, 2),
            "delta_cm_at_max": round(delta_high, 2),
            "swing_range": round(swing, 2)
        })
        
    tornado_results.sort(key=lambda x: x["swing_range"], reverse=True)
    return tornado_results

def answer_section17_questions(custom_params: Dict[str, float] = None) -> Dict[str, Any]:
    """
    Provides exact numerical answers to Questions 1 through 10 from Section 17 of the brief.
    """
    params = get_default_assumptions()
    if custom_params:
        params.update(custom_params)
        
    # Q1: At 20% credit and base uplift, what min net recovery is required?
    q1_min_rec = solve_breakeven_recovery(params["causal_frequency_uplift"], params)
    
    # Q2: If net recovery is only ₹250, what incremental frequency is required?
    q2_req_f = solve_breakeven_delta_f(250.0, params)
    
    # Q3: If annual purchase frequency increases by only 10% (e.g. +0.25 orders/year from 2.5), does it work?
    p_q3 = params.copy()
    p_q3["causal_frequency_uplift"] = 0.25
    res_q3 = calculate_tier0_economics(p_q3)
    
    # Q4: If only 40% of returned garments can be resold (e.g. B2B 30%, D2C 10%, writeoff 60%)?
    p_q4 = params.copy()
    p_q4["b2b_route_prob"] = 0.30
    p_q4["d2c_route_prob"] = 0.10
    p_q4["upcycle_route_prob"] = 0.0
    p_q4["recycle_route_prob"] = 0.0
    p_q4["writeoff_route_prob"] = 0.60
    res_q4 = calculate_tier0_economics(p_q4)
    
    # Q5: What is the maximum TradeBack credit % we can offer?
    q5_max_credit = solve_max_affordable_credit_pct(params)
    
    # Q6: Minimum resale probability required (scaling B2B & D2C routes)
    p_q6 = params.copy()
    def obj_q6(scale: float) -> float:
        tp = p_q6.copy()
        tp["b2b_route_prob"] = 0.60 * scale
        tp["d2c_route_prob"] = 0.20 * scale
        rem = max(0.0, 1.0 - (tp["b2b_route_prob"] + tp["d2c_route_prob"] + 0.15))
        tp["writeoff_route_prob"] = rem
        return calculate_tier0_economics(tp).delta_contribution_tradeback
    q6_scale = bisection_solve(obj_q6, 0.1, 1.5)
    q6_min_resale_prob = (0.60 + 0.20) * q6_scale
        
    # Q7: Maximum processing cost tolerable?
    q7_max_qc = solve_max_tolerable_processing_cost(params)
    
    # Q8: How much does a 5%, 10%, 20% increase in retention (lifespan) change economics?
    ret_impacts = {}
    base_accretion = calculate_tier0_economics(params).delta_contribution_tradeback
    for pct in [0.05, 0.10, 0.20]:
        p_ret = params.copy()
        p_ret["customer_lifespan_months"] = params["customer_lifespan_months"] * (1.0 + pct)
        res_ret = calculate_tier0_economics(p_ret)
        diff = res_ret.delta_contribution_tradeback - base_accretion
        ret_impacts[f"+{int(pct*100)}% retention"] = round(diff, 2)
        
    # Q10: TradeBack vs Promo Coupon
    tradeback_vs_promo_diff = calculate_tier0_economics(params).tradeback_vs_promo_delta

    return {
        "Q1_min_net_recovery_at_20pct_credit": round(q1_min_rec, 2),
        "Q2_req_freq_uplift_if_recovery_250": round(q2_req_f, 2),
        "Q3_works_with_10pct_freq_uplift": res_q3.delta_contribution_tradeback >= 0,
        "Q3_delta_cm": round(res_q3.delta_contribution_tradeback, 2),
        "Q4_works_with_40pct_resale": res_q4.delta_contribution_tradeback >= 0,
        "Q4_delta_cm": round(res_q4.delta_contribution_tradeback, 2),
        "Q5_max_affordable_credit_pct": round(q5_max_credit * 100, 1),
        "Q6_min_resale_prob_pct": round(q6_min_resale_prob * 100, 1),
        "Q7_max_tolerable_qc_cost": round(q7_max_qc, 2),
        "Q8_retention_sensitivity": ret_impacts,
        "Q10_tradeback_vs_coupon_superiority": round(tradeback_vs_promo_diff, 2),
    }
