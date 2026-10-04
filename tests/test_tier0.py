"""
Verification and Test Suite for Tier 0 Deterministic Engine.
"""

import sys
import os

# Add project root to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.assumptions import get_default_assumptions
from src.tier0_engine import calculate_tier0_economics, compute_blended_collection_cost, compute_unit_net_salvage_recovery

def test_tier0_baseline_and_tradeback():
    defaults = get_default_assumptions()
    res = calculate_tier0_economics(defaults)
    
    print("\n" + "="*80)
    print("           TIER 0 UNIT ECONOMICS REPORT (PER ACQUIRED CUSTOMER - 36 MONTHS)")
    print("="*80)
    
    print("\n--- 1. ORDER & RETURN COUNTS ---")
    print(f"Baseline Customer Orders (f=2.5, L=18mo)      : {res.n_orders_base:.2f} orders")
    print(f"TradeBack Adopter Orders (f=3.0, L=18mo)      : {res.n_orders_adopter:.2f} orders")
    print(f"Adopter Eligible Repeat Orders                : {res.n_eligible_repeats_adopter:.2f} orders")
    print(f"Adopter TradeBack Returns (N_TB = 2.50 * 0.75): {res.n_returns_adopter:.3f} returns")
    print(f"Cohort Blended Orders (Adoption = 40%)        : {res.n_orders_cohort:.2f} orders")
    print(f"Cohort Blended Returns                        : {res.n_returns_cohort:.3f} returns")
    
    print("\n--- 2. CANONICAL 2-LEVER DECOMPOSITION ---")
    print(f"Order Contribution Margin (CM_order)          : ₹{res.cm_order:.2f} / order")
    print(f"Incremental Orders per Adopter (ΔN_orders)    : +{res.delta_n_orders:.2f} orders")
    print(f"Lever 1: Incremental Volume Margin            : +₹{res.incremental_volume_margin:.2f} / adopter")
    print(f"True Net Salvage Recovery E[R_net_ops]         : ₹{res.unit_net_salvage_recovery:.2f} / return")
    print(f"Avoided Reacquisition CAC (E[CAC_avoided])    : ₹{res.cac_avoided:.2f} / return")
    print(f"TradeBack Credit Cost Paid (C_TB = 20%)       : -₹{res.unit_tradeback_credit:.2f} / return")
    print(f"Circular Unit Spread                          : ₹{res.circular_unit_spread:.2f} / return")
    print(f"Lever 2: Net Unit Circular Balance            : ₹{res.net_unit_circular_balance:.2f} / adopter")
    print(f"Incremental Adopter Contribution (ΔLTC_adopter): +₹{res.delta_ltc_adopter:.2f} / adopter")
    
    print("\n--- 3. ADOPTER FINANCIAL BREAKDOWN (36 MONTHS) ---")
    print(f"(+) Gross Product Revenue Margin              : ₹{res.adopter_gross_product_margin:.2f}")
    print(f"(-) Forward Fulfillment Freight               : -₹{res.adopter_fulfillment_cost:.2f}")
    print(f"(+) Net Garment Salvage Cash Collected        : ₹{res.adopter_salvage_recovery_net:.2f}")
    print(f"(-) TradeBack Credit Cost Given               : -₹{res.adopter_credit_cost:.2f}")
    print(f"(-) Repeat Marketing / CRM Spend Paid         : -₹{res.adopter_repeat_ad_cac_paid:.2f}")
    print(f"(-) Upfront Customer Acquisition Cost (CAC)   : -₹{defaults['cac']:.2f}")
    print(f"(=) Net 36-Month Adopter Lifetime Contribution: ₹{res.ltc_adopter:.2f}")
    
    print("\n--- 4. COHORT-LEVEL LIFETIME CONTRIBUTION & BENCHMARKS ---")
    print(f"System A: Baseline Conventional D2C Customer  : ₹{res.ltc_baseline:.2f}  (LTV/CAC: {res.ltv_cac_baseline:.2f}x)")
    print(f"System B: TradeBack Model Cohort (40% adopt)  : ₹{res.ltc_cohort_tradeback:.2f}  (LTV/CAC: {res.ltv_cac_tradeback:.2f}x)")
    print(f"System C: Benchmark Promo Coupon (₹200 coupon): ₹{res.ltc_benchmark_promo:.2f}  (LTV/CAC: {res.ltv_cac_promo:.2f}x)")
    
    print("\n--- 5. STRATEGIC ACCRETION SUMMARY ---")
    print(f"TradeBack Net Accretion over Baseline (ΔCM)   : ₹{res.delta_contribution_tradeback:.2f} / customer")
    print(f"Promo Coupon Net Accretion over Baseline (ΔCM): ₹{res.delta_contribution_promo:.2f} / customer")
    print(f"TradeBack Advantage over Promo Coupon (B - C) : ₹{res.tradeback_vs_promo_delta:.2f} / customer")
    print("="*80 + "\n")
    
    # Assertions for Canonical Architecture
    assert res.cm_order == 580.0, "CM_order must be 580.0"
    assert res.delta_n_orders == 0.75, "Incremental orders must be 0.75"
    assert res.n_returns_adopter == 1.875, "N_TB must be 1.875"
    assert res.unit_net_salvage_recovery == 66.98, "E[R_net_ops] must be 66.98"
    assert res.cac_avoided == 45.00, "Avoided CAC must be 45.00"
    assert res.circular_unit_spread == -148.02, "Circular unit spread must be -148.02"
    assert res.delta_ltc_adopter == 157.46, "Delta LTC adopter must be 157.46"
    assert res.ltc_baseline == 1568.75, "Baseline LTC must be 1568.75"
    assert res.ltc_adopter == 1726.21, "Adopter LTC must be 1726.21"
    assert res.ltc_cohort_tradeback == 1631.74, "Cohort LTC must be 1631.74"
    assert res.ltc_benchmark_promo == 1525.75, "Promo LTC must be 1525.75"
    assert res.tradeback_vs_promo_delta in (105.98, 105.99), "TradeBack vs Promo delta must be ~105.98"
    print("ALL TIER 0 CANONICAL ASSERTIONS PASSED!")

if __name__ == "__main__":
    test_tier0_baseline_and_tradeback()
