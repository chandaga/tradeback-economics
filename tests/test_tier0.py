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
    print(f"Adopter TradeBack Returns (Stranded Truncated): {res.n_returns_adopter:.2f} returns")
    print(f"Cohort Blended Orders (Adoption = 40%)        : {res.n_orders_cohort:.2f} orders")
    print(f"Cohort Blended Returns                        : {res.n_returns_cohort:.2f} returns")
    
    print("\n--- 2. PER-UNIT REVERSE LOGISTICS & SALVAGE METRICS ---")
    print(f"Blended Doorstep Swap + RTO Cascade Cost      : ₹{res.blended_collection_cost:.2f} / return")
    print(f"Expected Net Salvage Recovery E[R_net]         : ₹{res.unit_net_salvage_recovery:.2f} / return")
    print(f"TradeBack Credit Paid at Checkout (20%)       : ₹{res.unit_tradeback_credit:.2f} / return")
    
    print("\n--- 3. ADOPTER FINANCIAL BREAKDOWN (36 MONTHS) ---")
    print(f"(+) Gross Product Revenue Margin              : ₹{res.adopter_gross_product_margin:.2f}")
    print(f"(-) Forward Fulfillment Freight               : -₹{res.adopter_fulfillment_cost:.2f}")
    print(f"(+) Net Garment Salvage Cash Collected        : ₹{res.adopter_salvage_recovery_net:.2f}")
    print(f"(-) TradeBack Credit Cost Given               : -₹{res.adopter_credit_cost:.2f}")
    print(f"(-) D2C Cannibalization Lost Margin           : -₹{res.adopter_cannibalization_loss:.2f}")
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
    
    # Assertions
    assert res.n_orders_adopter > res.n_orders_base, "Adopter must have more orders due to causal uplift"
    assert res.n_returns_adopter <= res.n_eligible_repeats_adopter, "Returns cannot exceed eligible repeats"
    assert res.blended_collection_cost > defaults["doorstep_swap_cost"], "Blended logistics must exceed base swap"
    
if __name__ == "__main__":
    test_tier0_baseline_and_tradeback()
