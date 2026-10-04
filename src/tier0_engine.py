"""
Tier 0 Deterministic Unit Economics Engine.

Implements transparent, closed-form 36-month customer lifecycle accounting
for:
- System A: Conventional Baseline D2C
- System B: TradeBack Model (Partitioned Cohort, Zero Breakage, Stranded Ceiling, Blended RTO Cascade)
- System C: Benchmark Promotional Coupon / Ad Incentive

References:
- docs/ARCHITECTURE_1PAGER.md
- docs/DECISION_LOG.md (ADR-001 through ADR-006)
"""

from dataclasses import dataclass
from typing import Dict, Any
from src.assumptions import get_default_assumptions

@dataclass
class UnitEconomicsResult:
    # 36-Month Order Counts
    n_orders_base: float
    n_orders_adopter: float
    n_orders_cohort: float
    n_eligible_repeats_adopter: float
    n_returns_adopter: float
    n_returns_cohort: float
    
    # Financial Totals per Acquired Customer (36 Months)
    ltc_baseline: float
    ltc_adopter: float
    ltc_cohort_tradeback: float
    ltc_benchmark_promo: float
    
    # Accretion Metrics
    delta_contribution_tradeback: float  # Cohort B - Baseline A
    delta_contribution_promo: float      # Promo C - Baseline A
    tradeback_vs_promo_delta: float      # Cohort B - Promo C
    
    # LTV/CAC Ratios
    ltv_cac_baseline: float
    ltv_cac_tradeback: float
    ltv_cac_promo: float
    
    # Itemized Breakdown for Adopter (per Adopter Customer over 36 Mo)
    adopter_gross_product_margin: float
    adopter_fulfillment_cost: float
    adopter_salvage_recovery_net: float
    adopter_ad_savings: float
    adopter_credit_cost: float
    adopter_cannibalization_loss: float
    adopter_repeat_ad_cac_paid: float
    
    # Unit Item Metrics (Per Return / Per Order)
    blended_collection_cost: float
    unit_net_salvage_recovery: float
    unit_tradeback_credit: float

def compute_blended_collection_cost(params: Dict[str, float]) -> float:
    """
    Computes blended reverse logistics cost per return factoring in doorstep swap
    failure rate and RTO freight burn cascade (ADR-003).
    
    Formula:
    C_collection = C_swap + P_fail * [C_standalone + P_rto * (C_forward + C_rto_freight)]
    """
    c_swap = params["doorstep_swap_cost"]
    p_fail = params["swap_failure_rate"]
    c_standalone = params["standalone_reverse_cost"]
    p_rto = params["swap_fail_rto_rate"]
    rto_burn = params["rto_freight_burn"]
    
    blended_cost = c_swap + p_fail * (c_standalone + p_rto * rto_burn)
    return blended_cost

def compute_unit_net_salvage_recovery(params: Dict[str, float]) -> float:
    """
    Computes expected net salvage cash per returned garment E[R_net] across all 5 routes,
    accounting for trend depreciation, collection friction, QC, and GST leakage (ADR-006).
    
    Formula:
    E[R_net] = sum_k(P_k * [V_gross,k * (1 - d_trend)^(t_hold/30)]) - C_collection - C_QC - Tax_GST
    """
    t_hold = params["inventory_holding_days"]
    d_trend = params["monthly_trend_depreciation"]
    depreciation_factor = (1.0 - d_trend) ** (t_hold / 30.0)
    
    # Gross recovery weighted across routes
    b2b_rec = params["b2b_route_prob"] * (params["b2b_gross_price"] * depreciation_factor)
    d2c_rec = params["d2c_route_prob"] * (params["d2c_gross_price"] * depreciation_factor)
    upcycle_rec = params["upcycle_route_prob"] * (params["upcycle_gross_price"] * depreciation_factor)
    recycle_rec = params["recycle_route_prob"] * (params["recycle_gross_price"] * depreciation_factor)
    writeoff_rec = params["writeoff_route_prob"] * 0.0
    
    expected_gross_recovery = b2b_rec + d2c_rec + upcycle_rec + recycle_rec + writeoff_rec
    
    # Reverse logistics, QC and Tax
    c_collection = compute_blended_collection_cost(params)
    c_qc = params["qc_inspection_cost"]
    gst_leakage = expected_gross_recovery * params["effective_gst_leakage"]
    
    net_recovery = expected_gross_recovery - c_collection - c_qc - gst_leakage
    return net_recovery

def calculate_tier0_economics(custom_params: Dict[str, float] = None) -> UnitEconomicsResult:
    """
    Calculates 36-month customer lifetime contribution for Baseline, TradeBack, and Promo systems.
    """
    params = get_default_assumptions()
    if custom_params:
        params.update(custom_params)
        
    # --- 1. Customer Lifespan & Order Counts ---
    # Lifespan in years (clamped to max 36 months / 3.0 years evaluation window)
    eval_window_years = 3.0
    lifespan_years = min(eval_window_years, params["customer_lifespan_months"] / 12.0)
    
    # Baseline orders over 36 months
    f_base = params["baseline_annual_orders"]
    n_orders_base = f_base * lifespan_years
    
    # Adopter orders over 36 months (incorporates causal frequency uplift)
    delta_f = params["causal_frequency_uplift"]
    f_adopter = f_base + delta_f
    n_orders_adopter = f_adopter * lifespan_years
    
    # Cohort order count
    alpha = params["tradeback_adoption_rate"]
    n_orders_cohort = alpha * n_orders_adopter + (1.0 - alpha) * n_orders_base
    
    # --- 2. Stranded Garment Truncation for Adopter (ADR-002) ---
    n_eligible_repeats_adopter = max(0.0, n_orders_adopter - 1.0)
    n_stranded = params["stranded_garments_terminal"]
    n_returns_adopter = max(0.0, n_orders_adopter - 1.0 - n_stranded)
    n_returns_cohort = alpha * n_returns_adopter
    
    # --- 3. System A: Baseline Conventional D2C Customer ---
    # Every order yields (AOV * GM - C_fulfill). Repeat orders pay full M_base.
    aov = params["aov"]
    gm = params["gross_margin_pct"]
    c_fulfill = params["forward_fulfillment_cost"]
    cac = params["cac"]
    m_base = params["repeat_ad_cac"]
    
    unit_product_margin = (aov * gm) - c_fulfill
    baseline_gross_margin_total = n_orders_base * unit_product_margin
    baseline_repeat_ad_spend_total = max(0.0, n_orders_base - 1.0) * m_base
    ltc_baseline = -cac + baseline_gross_margin_total - baseline_repeat_ad_spend_total
    
    # --- 4. System B: TradeBack Adopter Economics (ADR-001, ADR-002, ADR-004) ---
    # 4a. Gross Product Margin across ALL orders
    adopter_gross_product_margin = n_orders_adopter * (aov * gm)
    adopter_fulfillment_cost = n_orders_adopter * c_fulfill
    
    # 4b. Net Salvage Recovery on non-stranded returns
    unit_net_salvage = compute_unit_net_salvage_recovery(params)
    adopter_salvage_recovery_net = n_returns_adopter * unit_net_salvage
    
    # 4c. Avoided Repeat Ad Spend (S_ad applied to returns)
    s_ad = params["ad_savings_pct"]
    adopter_ad_savings = n_returns_adopter * (m_base * s_ad)
    
    # 4d. TradeBack Credit Cost (Accounts for configurable breakage beta)
    credit_pct = params["tradeback_credit_pct"]
    beta = params.get("credit_breakage_pct", 0.0)
    unit_credit = aov * credit_pct
    adopter_credit_cost = n_returns_adopter * unit_credit * (1.0 - beta)
    
    # 4e. Cannibalization Loss on D2C clearance route
    p_d2c = params["d2c_route_prob"]
    theta_cannibal = params["d2c_cannibalization_rate"]
    adopter_cannibalization_loss = n_returns_adopter * p_d2c * theta_cannibal * (aov * gm)
    
    # 4f. Paid Repeat Ad Spend for orders that did NOT use TradeBack
    # Total repeat orders = n_eligible_repeats_adopter. Of these, n_returns used TradeBack.
    # Orders using TradeBack pay (1 - S_ad) * m_base; other repeat orders pay full m_base.
    tradeback_repeats_paid_ad = n_returns_adopter * (m_base * (1.0 - s_ad))
    non_tradeback_repeats_paid_ad = max(0.0, n_eligible_repeats_adopter - n_returns_adopter) * m_base
    adopter_repeat_ad_cac_paid = tradeback_repeats_paid_ad + non_tradeback_repeats_paid_ad
    
    # Net Adopter Lifetime Contribution
    ltc_adopter = (
        -cac
        + adopter_gross_product_margin
        - adopter_fulfillment_cost
        + adopter_salvage_recovery_net
        - adopter_credit_cost
        - adopter_cannibalization_loss
        - adopter_repeat_ad_cac_paid
    )
    
    # Cohort Blended TradeBack Contribution (ADR-004)
    ltc_cohort_tradeback = alpha * ltc_adopter + (1.0 - alpha) * ltc_baseline
    delta_contribution_tradeback = ltc_cohort_tradeback - ltc_baseline
    
    # --- 5. System C: Benchmark Promo Coupon Alternative (ADR-005) ---
    # Assume coupon achieves the exact same order frequency as TradeBack (f_adopter),
    # but instead of TradeBack credit and reverse logistics, gives flat coupon discount on repeats.
    coupon_val = params["benchmark_coupon_discount"]
    promo_gross_product_margin = n_orders_adopter * unit_product_margin
    promo_discount_total = max(0.0, n_orders_adopter - 1.0) * coupon_val
    promo_ad_spend_total = max(0.0, n_orders_adopter - 1.0) * (m_base * (1.0 - s_ad))
    ltc_promo_adopter = -cac + promo_gross_product_margin - promo_discount_total - promo_ad_spend_total
    ltc_benchmark_promo = alpha * ltc_promo_adopter + (1.0 - alpha) * ltc_baseline
    delta_contribution_promo = ltc_benchmark_promo - ltc_baseline
    
    tradeback_vs_promo_delta = ltc_cohort_tradeback - ltc_benchmark_promo
    
    # --- 6. LTV / CAC Ratios ---
    # LTV here is 36-Month Net Contribution before CAC
    ltv_baseline = ltc_baseline + cac
    ltv_tradeback = ltc_cohort_tradeback + cac
    ltv_promo = ltc_benchmark_promo + cac
    
    ltv_cac_baseline = ltv_baseline / cac if cac > 0 else 0.0
    ltv_cac_tradeback = ltv_tradeback / cac if cac > 0 else 0.0
    ltv_cac_promo = ltv_promo / cac if cac > 0 else 0.0
    
    return UnitEconomicsResult(
        n_orders_base=round(n_orders_base, 2),
        n_orders_adopter=round(n_orders_adopter, 2),
        n_orders_cohort=round(n_orders_cohort, 2),
        n_eligible_repeats_adopter=round(n_eligible_repeats_adopter, 2),
        n_returns_adopter=round(n_returns_adopter, 2),
        n_returns_cohort=round(n_returns_cohort, 2),
        ltc_baseline=round(ltc_baseline, 2),
        ltc_adopter=round(ltc_adopter, 2),
        ltc_cohort_tradeback=round(ltc_cohort_tradeback, 2),
        ltc_benchmark_promo=round(ltc_benchmark_promo, 2),
        delta_contribution_tradeback=round(delta_contribution_tradeback, 2),
        delta_contribution_promo=round(delta_contribution_promo, 2),
        tradeback_vs_promo_delta=round(tradeback_vs_promo_delta, 2),
        ltv_cac_baseline=round(ltv_cac_baseline, 2),
        ltv_cac_tradeback=round(ltv_cac_tradeback, 2),
        ltv_cac_promo=round(ltv_cac_promo, 2),
        adopter_gross_product_margin=round(adopter_gross_product_margin, 2),
        adopter_fulfillment_cost=round(adopter_fulfillment_cost, 2),
        adopter_salvage_recovery_net=round(adopter_salvage_recovery_net, 2),
        adopter_ad_savings=round(adopter_ad_savings, 2),
        adopter_credit_cost=round(adopter_credit_cost, 2),
        adopter_cannibalization_loss=round(adopter_cannibalization_loss, 2),
        adopter_repeat_ad_cac_paid=round(adopter_repeat_ad_cac_paid, 2),
        blended_collection_cost=round(compute_blended_collection_cost(params), 2),
        unit_net_salvage_recovery=round(unit_net_salvage, 2),
        unit_tradeback_credit=round(unit_credit, 2),
    )
