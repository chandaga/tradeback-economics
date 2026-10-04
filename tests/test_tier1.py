"""
Verification and Test Suite for Tier 1 Break-Even Solver and Tornado Analysis.
"""

import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.assumptions import get_default_assumptions
from src.tier0_engine import calculate_tier0_economics
from src.tier1_breakeven import (
    solve_breakeven_recovery,
    solve_breakeven_delta_f,
    solve_max_affordable_credit_pct,
    solve_max_tolerable_processing_cost,
    generate_breakeven_isocline,
    run_tornado_sensitivity,
    answer_section17_questions
)

def test_tier1_solver():
    defaults = get_default_assumptions()
    res = calculate_tier0_economics(defaults)
    
    print("\n" + "="*85)
    print("             TIER 1 BREAK-EVEN SURFACE & STRATEGIC SENSITIVITY REPORT")
    print("="*85)
    
    # 1. The 5 Deal-Breaker Thresholds
    min_rec_zero_uplift = solve_breakeven_recovery(0.0)
    min_uplift_zero_rec = solve_breakeven_delta_f(0.0)
    max_credit = solve_max_affordable_credit_pct()
    max_qc = solve_max_tolerable_processing_cost()
    
    print("\n--- 1. THE 5 DEAL-BREAKER BOUNDARY THRESHOLDS (INVESTOR PITCH METRICS) ---")
    print(f"1. Min Net Recovery Required if Uplift = 0 (Δf=0.0) : ₹{min_rec_zero_uplift:.2f} / return")
    print(f"2. Min Causal Uplift Required if Recovery = ₹0.0   : +{min_uplift_zero_rec:.2f} orders/year")
    print(f"3. Maximum Economically Affordable Credit %         : {max_credit*100:.1f}% of AOV (₹{defaults['aov']*max_credit:.1f})")
    print(f"4. Maximum Tolerable QC & Sanitization Cost         : ₹{max_qc:.2f} / garment")
    print(f"5. Current Net Accretion at Base Operating Point    : +₹{res.delta_contribution_tradeback:.2f} / acquired customer")
    
    # 2. 2D Break-Even Isocline
    print("\n--- 2. 2D BREAK-EVEN ISOCLINE (Δf_causal vs. Required Net Recovery E[R_net]) ---")
    print(f"{'Causal Frequency Uplift (Δf)':<32} | {'Required Net Recovery (₹)':<25} | {'Strategic Regime'}")
    print("-" * 80)
    isocline = generate_breakeven_isocline()
    for pt in isocline:
        df = pt["causal_frequency_uplift"]
        rec = pt["required_net_recovery"]
        if df == 0.0:
            regime = "Pure Resale Model (Zero behavioral change)"
        elif rec <= 0.0:
            regime = "Pure Loyalty Scheme (Tolerates negative salvage)"
        else:
            regime = "Hybrid Circularity (Balanced uplift & salvage)"
        print(f"+{df:<31.2f} | ₹{rec:<24.2f} | {regime}")
        
    # 3. Global Tornado Sensitivity Ranking
    print("\n--- 3. GLOBAL TORNADO SENSITIVITY RANKING (TOP 12 VARIABLES) ---")
    print(f"{'Rank':<5} | {'Variable':<32} | {'Range Tested':<20} | {'3-Yr ΔCM Swing':<15}")
    print("-" * 80)
    tornado = run_tornado_sensitivity()
    for i, t in enumerate(tornado, 1):
        rng_str = f"{t['min_val']}{t['unit']} - {t['max_val']}{t['unit']}"
        print(f"#{i:<4} | {t['display_name']:<32} | {rng_str:<20} | ₹{t['swing_range']:<14.2f}")
        
    # 4. Answers to Section 17 Questions
    print("\n--- 4. DIRECT ANSWERS TO THE 10 SECTION 17 BUSINESS QUESTIONS ---")
    q_ans = answer_section17_questions()
    print(f"Q1 (Min recovery at 20% credit & base uplift) : ₹{q_ans['Q1_min_net_recovery_at_20pct_credit']:.2f}")
    print(f"Q2 (Required uplift if net recovery is ₹250)   : +{q_ans['Q2_req_freq_uplift_if_recovery_250']:.2f} orders/yr (Actually accretive even at negative uplift!)")
    print(f"Q3 (Works with only 10% uplift / +0.25 orders): {'YES (+₹' + str(q_ans['Q3_delta_cm']) + ')' if q_ans['Q3_works_with_10pct_freq_uplift'] else 'NO'}")
    print(f"Q4 (Works if only 40% garments resold)        : {'YES (+₹' + str(q_ans['Q4_delta_cm']) + ')' if q_ans['Q4_works_with_40pct_resale'] else 'NO'}")
    print(f"Q5 (Max affordable credit %)                  : {q_ans['Q5_max_affordable_credit_pct']}% of AOV")
    print(f"Q6 (Min resale probability required)          : {q_ans['Q6_min_resale_prob_pct']}%")
    print(f"Q7 (Max tolerable processing cost)            : ₹{q_ans['Q7_max_tolerable_qc_cost']:.2f}")
    print(f"Q8 (Retention sensitivity)                    : {q_ans['Q8_retention_sensitivity']}")
    print(f"Q10 (TradeBack superiority vs. ₹200 Coupon)   : +₹{q_ans['Q10_tradeback_vs_coupon_superiority']:.2f} / customer")
    print("="*85 + "\n")

    # Assertions
    assert round(min_rec_zero_uplift, 2) == 215.00, f"Expected 215.00, got {min_rec_zero_uplift}"
    assert round(min_uplift_zero_rec, 2) in (0.45, 0.46), f"Expected 0.45 or 0.46, got {min_uplift_zero_rec}"
    assert round(max_credit * 100, 1) == 26.5, f"Expected 26.5, got {max_credit*100}"
    assert round(max_qc, 2) == 128.98, f"Expected 128.98, got {max_qc}"
    print("ALL TIER 1 CANONICAL ASSERTIONS PASSED!")

if __name__ == "__main__":
    test_tier1_solver()
