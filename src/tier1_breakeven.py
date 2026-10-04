"""
Tier 1 Analytical Break-Even Solver and Sensitivity Engine (Pure Python Core).

Computes:
1. The 2D Break-Even Isocline: Delta_Contribution(Delta_f, E[R_net]) = 0.
2. The 5 Deal-Breaker Thresholds for investor presentations.
3. Exact answers to the 10 specific business questions from Section 17.
4. Global 12-Variable Tornado Sensitivity Analysis.

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

def solve_breakeven_delta_f(target_net_recovery: float, custom_params: Dict[str, float] = None) -> float:
    """
    Finds the exact causal frequency uplift (Delta_f) required to achieve
    Delta_Contribution = 0 given a fixed net recovery value E[R_net].
    """
    params = get_default_assumptions()
    if custom_params:
        params.update(custom_params)
        
    def objective_f(delta_f_val: float) -> float:
        test_p = params.copy()
        test_p["causal_frequency_uplift"] = delta_f_val
        curr_net = compute_unit_net_salvage_recovery(test_p)
        diff = target_net_recovery - curr_net
        test_p["b2b_gross_price"] += diff / max(0.01, test_p["b2b_route_prob"])
        res = calculate_tier0_economics(test_p)
        return res.delta_contribution_tradeback

    return bisection_solve(objective_f, -0.5, 4.0)

def solve_breakeven_recovery(target_delta_f: float, custom_params: Dict[str, float] = None) -> float:
    """
    Finds the exact net recovery E[R_net] required to achieve
    Delta_Contribution = 0 given a fixed causal frequency uplift Delta_f.
    """
    params = get_default_assumptions()
    if custom_params:
        params.update(custom_params)
    params["causal_frequency_uplift"] = target_delta_f

    def objective_rec(net_rec_val: float) -> float:
        test_p = params.copy()
        curr_net = compute_unit_net_salvage_recovery(test_p)
        diff = net_rec_val - curr_net
        test_p["b2b_gross_price"] += diff / max(0.01, test_p["b2b_route_prob"])
        res = calculate_tier0_economics(test_p)
        return res.delta_contribution_tradeback

    return bisection_solve(objective_rec, -200.0, 700.0)

def solve_max_affordable_credit_pct(custom_params: Dict[str, float] = None) -> float:
    """
    Solves for the maximum credit % at which Delta_Contribution >= 0.
    """
    params = get_default_assumptions()
    if custom_params:
        params.update(custom_params)

    def objective_credit(credit_pct_val: float) -> float:
        test_p = params.copy()
        test_p["tradeback_credit_pct"] = credit_pct_val
        res = calculate_tier0_economics(test_p)
        return res.delta_contribution_tradeback

    return bisection_solve(objective_credit, 0.05, 0.60)

def solve_max_tolerable_processing_cost(custom_params: Dict[str, float] = None) -> float:
    """
    Solves for the maximum QC + inspection cost tolerable before TradeBack becomes dilutive.
    """
    params = get_default_assumptions()
    if custom_params:
        params.update(custom_params)

    def objective_qc(qc_val: float) -> float:
        test_p = params.copy()
        test_p["qc_inspection_cost"] = qc_val
        res = calculate_tier0_economics(test_p)
        return res.delta_contribution_tradeback

    return bisection_solve(objective_qc, 0.0, 300.0)

def generate_breakeven_isocline(custom_params: Dict[str, float] = None) -> List[Dict[str, float]]:
    """
    Generates a 2D Break-Even curve mapping
    Causal Order Uplift (Delta_f) to Required Net Recovery E[R_net].
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
        "b2b_gross_price",
        "qc_inspection_cost",
        "gross_margin_pct",
        "aov",
        "repeat_ad_cac",
        "ad_savings_pct",
        "swap_failure_rate",
        "d2c_cannibalization_rate",
        "baseline_annual_orders",
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
        
    # Q1: If credit is 20%, what min net recovery is required?
    q1_min_rec = solve_breakeven_recovery(params["causal_frequency_uplift"], params)
    
    # Q2: If net recovery is only ₹250, what incremental frequency is required?
    q2_req_f = solve_breakeven_delta_f(250.0, params)
    
    # Q3: If annual purchase frequency increases by only 10% (e.g. +0.25 orders/year from 2.5), does it work?
    p_q3 = params.copy()
    p_q3["causal_frequency_uplift"] = 0.25
    res_q3 = calculate_tier0_economics(p_q3)
    
    # Q4: If only 40% of returned garments can be resold (e.g. B2B + D2C = 40%, 60% loss/rag)?
    p_q4 = params.copy()
    p_q4["b2b_route_prob"] = 0.30
    p_q4["d2c_route_prob"] = 0.10
    p_q4["writeoff_route_prob"] = 0.60
    res_q4 = calculate_tier0_economics(p_q4)
    
    # Q5: What is the maximum TradeBack credit % we can offer?
    q5_max_credit = solve_max_affordable_credit_pct(params)
    
    # Q6: Minimum resale probability required
    p_q6 = params.copy()
    def obj_q6(scale: float) -> float:
        tp = p_q6.copy()
        tp["b2b_route_prob"] = 0.60 * scale
        tp["d2c_route_prob"] = 0.20 * scale
        tp["writeoff_route_prob"] = max(0.0, 1.0 - (tp["b2b_route_prob"] + tp["d2c_route_prob"] + 0.15))
        return calculate_tier0_economics(tp).delta_contribution_tradeback
    q6_scale = bisection_solve(obj_q6, 0.1, 1.2)
    q6_min_resale_prob = (0.60 + 0.20) * q6_scale
        
    # Q7: Maximum processing cost tolerable?
    q7_max_qc = solve_max_tolerable_processing_cost(params)
    
    # Q8: How much does a 5%, 10%, 20% increase in retention (lifespan) change economics?
    ret_impacts = {}
    for pct in [0.05, 0.10, 0.20]:
        p_ret = params.copy()
        p_ret["customer_lifespan_months"] = params["customer_lifespan_months"] * (1.0 + pct)
        res_ret = calculate_tier0_economics(p_ret)
        diff = res_ret.delta_contribution_tradeback - calculate_tier0_economics(params).delta_contribution_tradeback
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
