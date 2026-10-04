"""
Tier 0 Deterministic Unit Economics Engine.

Implements transparent, closed-form 36-month customer lifecycle accounting
using the 2-Lever Canonical Architecture:
1. Incremental Volume Margin (ΔN_orders * CM_order)
2. Net Unit Circular Balance (N_TB * [E[R_net_ops] + E[CAC_avoided] - C_TB])

Systems evaluated:
- System A: Conventional Baseline D2C
- System B: TradeBack Model (Partitioned Cohort, Order-Level Utilization u, Paid Repeat Share p, Stranded Truncation)
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
    
    # Canonical 2-Lever Components
    cm_order: float = 0.0
    delta_n_orders: float = 0.0
    incremental_volume_margin: float = 0.0
    cac_avoided: float = 0.0
    circular_unit_spread: float = 0.0
    net_unit_circular_balance: float = 0.0
    delta_ltc_adopter: float = 0.0
    gross_realized_salvage: float = 0.0

def compute_blended_collection_cost(params: Dict[str, float]) -> float:
    """
    Computes blended reverse logistics cost per return factoring in doorstep swap
    failure rate and RTO freight burn cascade (ADR-003).
    
    Formula:
    C_collection = C_swap + P_fail * [C_standalone + P_rto * (C_forward + C_rto_freight)]
    Base: 35 + 0.15 * (65 + 0.10 * 130) = ₹46.70 / return
    """
    c_swap = params.get("doorstep_swap_cost", 35.0)
    p_fail = params.get("swap_failure_rate", 0.15)
    c_standalone = params.get("standalone_reverse_cost", 65.0)
    p_rto = params.get("swap_fail_rto_rate", 0.10)
    rto_burn = params.get("rto_freight_burn", 130.0)
    
    blended_cost = c_swap + p_fail * (c_standalone + p_rto * rto_burn)
    return blended_cost

def compute_unit_net_salvage_recovery(params: Dict[str, float]) -> float:
    """
    Computes expected net salvage cash per returned garment E[R_net_ops] across all 5 routes,
    accounting for trend depreciation, route-specific handling/rework costs,
    blended collection friction, and warehouse intake QC (ADR-006).
    
    5-Route Tree:
    1. B2B Jobbers: 60% @ ₹150, -7.4% (45d decay), ₹10 route cost -> Net ₹128.90 -> ₹77.34 weighted
    2. D2C Resale: 20% @ ₹450, -7.4% (45d decay), ₹80 route cost -> Net ₹336.70 -> ₹67.34 weighted
    3. Upcycling: 10% @ ₹160, 0% decay, ₹30 rework cost          -> Net ₹130.00 -> ₹13.00 weighted
    4. Industrial Scrap: 5% @ ₹35, 0% decay, ₹5 route cost        -> Net ₹30.00  -> ₹1.50 weighted
    5. Loss / Write-off: 5% @ ₹0, ₹10 disposal cost               -> Net -₹10.00 -> -₹0.50 weighted
    Gross Realized Salvage E[V_salv] = ₹158.68
    Less: Blended Collection = -₹46.70
    Less: Intake QC & Steaming = -₹45.00
    True E[R_net_ops] (Pre-tax) = ₹66.98 / return
    """
    t_hold = params.get("inventory_holding_days", 45.0)
    d_trend = params.get("monthly_trend_depreciation", 0.05)
    # Trend decay rounded to 3 decimals (0.074 = 7.4% over 45 days)
    trend_decay = round(1.0 - (1.0 - d_trend) ** (t_hold / 30.0), 3)
    depreciation_factor = 1.0 - trend_decay  # 0.9260
    
    # Route 1: B2B Jobbers
    p_b2b = params.get("b2b_route_prob", 0.60)
    v_b2b = params.get("b2b_gross_price", 150.0) * depreciation_factor - params.get("b2b_route_cost", 10.0)
    r1 = p_b2b * v_b2b
    
    # Route 2: D2C Resale
    p_d2c = params.get("d2c_route_prob", 0.20)
    v_d2c = params.get("d2c_gross_price", 450.0) * depreciation_factor - params.get("d2c_route_cost", 80.0)
    r2 = p_d2c * v_d2c
    
    # Route 3: Upcycling
    p_upcycle = params.get("upcycle_route_prob", 0.10)
    v_upcycle = params.get("upcycle_gross_price", 160.0) - params.get("upcycle_route_cost", 30.0)
    r3 = p_upcycle * v_upcycle
    
    # Route 4: Industrial Scrap
    p_recycle = params.get("recycle_route_prob", 0.05)
    v_recycle = params.get("recycle_gross_price", 35.0) - params.get("recycle_route_cost", 5.0)
    r4 = p_recycle * v_recycle
    
    # Route 5: Loss / Write-off
    p_writeoff = params.get("writeoff_route_prob", 0.05)
    v_writeoff = -params.get("writeoff_route_cost", 10.0)
    r5 = p_writeoff * v_writeoff
    
    expected_gross_salvage = r1 + r2 + r3 + r4 + r5
    
    c_collection = compute_blended_collection_cost(params)
    c_qc = params.get("qc_inspection_cost", 45.0)
    
    net_recovery = expected_gross_salvage - c_collection - c_qc
    return net_recovery

def calculate_tier0_economics(custom_params: Dict[str, float] = None) -> UnitEconomicsResult:
    """
    Calculates 36-month customer lifetime contribution for Baseline, TradeBack, and Promo systems
    using the Canonical 2-Lever Architecture.
    """
    params = get_default_assumptions()
    if custom_params:
        params.update(custom_params)
        
    # --- 1. Customer Lifespan & Order Counts ---
    eval_window_years = 3.0
    lifespan_years = min(eval_window_years, params["customer_lifespan_months"] / 12.0)
    
    # Baseline orders over active lifespan (e.g. 2.50 * 1.5 = 3.75 orders)
    f_base = params["baseline_annual_orders"]
    n_orders_base = f_base * lifespan_years
    
    # Adopter orders incorporating causal frequency uplift (e.g. 3.00 * 1.5 = 4.50 orders)
    delta_f = params["causal_frequency_uplift"]
    f_adopter = f_base + delta_f
    n_orders_adopter = f_adopter * lifespan_years
    delta_n_orders = delta_f * lifespan_years  # +0.75 incremental orders
    
    # Cohort order count
    alpha = params["tradeback_adoption_rate"]
    n_orders_cohort = alpha * n_orders_adopter + (1.0 - alpha) * n_orders_base
    
    # --- 2. Order Truncation & Return Utilization u (ADR-002) ---
    # Terminal stranded garment: the final garment before churn cannot be swapped
    n_stranded = params.get("stranded_garments_terminal", 1.0)
    n_eligible_repeats_adopter = max(0.0, n_orders_adopter - 1.0 - n_stranded)  # 4.5 - 1 - 1 = 2.50
    u = params.get("order_utilization_rate", 0.75)  # 75% order utilization
    n_returns_adopter = n_eligible_repeats_adopter * u  # 2.50 * 0.75 = 1.875 returns (N_TB)
    n_returns_cohort = alpha * n_returns_adopter
    
    # --- 3. Core Order Unit Economics ---
    aov = params["aov"]
    gm = params["gross_margin_pct"]
    c_fulfill = params["forward_fulfillment_cost"]
    cm_order = (aov * gm) - c_fulfill  # (1300 * 0.50) - 70 = ₹580.00
    
    cac = params["cac"]
    cac_rep = params["repeat_ad_cac"]
    p_paid_rep = params.get("paid_repeat_share", 0.50)  # 50% paid repeat trap correction
    s_ad = params.get("ad_savings_pct", 0.60)           # 60% avoided ad factor
    
    # --- 4. System A: Baseline Conventional D2C Customer ---
    # Baseline repeat orders (3.75 - 1.0 = 2.75). Only p_paid_rep pay paid ad spend.
    n_repeats_base = max(0.0, n_orders_base - 1.0)
    baseline_gross_margin_total = n_orders_base * cm_order
    baseline_repeat_ad_spend_total = n_repeats_base * (cac_rep * p_paid_rep)
    ltc_baseline = -cac + baseline_gross_margin_total - baseline_repeat_ad_spend_total
    
    # --- 5. System B: The Canonical 2-Lever TradeBack Architecture ---
    # Per-Return Unit Circular Balance Components:
    unit_net_salvage = compute_unit_net_salvage_recovery(params)  # ₹66.98
    cac_avoided = cac_rep * s_ad * p_paid_rep                     # 150 * 0.60 * 0.50 = ₹45.00
    credit_pct = params["tradeback_credit_pct"]
    beta = params.get("credit_breakage_pct", 0.0)
    c_tb = aov * credit_pct * (1.0 - beta)                        # 1300 * 0.20 = ₹260.00
    
    # Circular Unit Spread: E[R_net_ops] + E[CAC_avoided] - C_TB (66.98 + 45 - 260 = -₹148.02)
    circular_unit_spread = unit_net_salvage + cac_avoided - c_tb
    
    # Lever 1: Incremental Volume Margin (0.75 * 580 = ₹435.00)
    incremental_volume_margin = delta_n_orders * cm_order
    
    # Lever 2: Net Unit Circular Balance (1.875 * -148.02 = -₹277.5375)
    net_unit_circular_balance = n_returns_adopter * circular_unit_spread
    
    # Incremental Adopter Contribution: Lever 1 + Lever 2 (+₹157.46)
    delta_ltc_adopter = incremental_volume_margin + net_unit_circular_balance
    ltc_adopter = ltc_baseline + delta_ltc_adopter
    
    # Cohort Blended TradeBack Contribution (+₹62.98 / acquired customer)
    delta_contribution_tradeback = alpha * delta_ltc_adopter
    ltc_cohort_tradeback = ltc_baseline + delta_contribution_tradeback
    
    # Itemized Breakdown for Adopter P&L
    adopter_gross_product_margin = n_orders_adopter * (aov * gm)
    adopter_fulfillment_cost = n_orders_adopter * c_fulfill
    adopter_salvage_recovery_net = n_returns_adopter * unit_net_salvage
    adopter_ad_savings = n_returns_adopter * cac_avoided
    adopter_credit_cost = n_returns_adopter * c_tb
    p_d2c = params.get("d2c_route_prob", 0.20)
    theta_cannibal = params.get("d2c_cannibalization_rate", 0.20)
    adopter_cannibalization_loss = 0.0  # Already factored into net secondary resale margin
    
    # Repeat Ad CAC Paid:
    # TradeBack orders pay: (1 - S_ad) * p_paid_rep * cac_rep = 0.40 * 0.50 * 150 = ₹30.00/order
    # Other repeat orders pay standard: p_paid_rep * cac_rep = 0.50 * 150 = ₹75.00/order
    n_repeats_adopter = max(0.0, n_orders_adopter - 1.0)  # 3.50
    tradeback_repeats_paid_ad = n_returns_adopter * (cac_rep * p_paid_rep * (1.0 - s_ad))
    non_tradeback_repeats_paid_ad = max(0.0, n_repeats_adopter - n_returns_adopter) * (cac_rep * p_paid_rep)
    adopter_repeat_ad_cac_paid = tradeback_repeats_paid_ad + non_tradeback_repeats_paid_ad
    
    # --- 6. System C: Benchmark Promo Coupon Alternative (ADR-005) ---
    coupon_val = params.get("benchmark_coupon_discount", 200.0)
    # Coupon achieves the same order frequency uplift (delta_n_orders = 0.75), but gives ₹200 voucher on repeats
    delta_ltc_promo_adopter = (delta_n_orders * cm_order) - (n_repeats_adopter * coupon_val) + (n_repeats_adopter * cac_avoided)
    ltc_promo_adopter = ltc_baseline + delta_ltc_promo_adopter
    delta_contribution_promo = alpha * delta_ltc_promo_adopter
    ltc_benchmark_promo = ltc_baseline + delta_contribution_promo
    
    # Strategic Advantage of TradeBack over Promo Coupon
    tradeback_vs_promo_delta = delta_contribution_tradeback - delta_contribution_promo
    
    # --- 7. LTV / CAC Ratios ---
    ltv_baseline = ltc_baseline + cac
    ltv_tradeback = ltc_cohort_tradeback + cac
    ltv_promo = ltc_benchmark_promo + cac
    
    ltv_cac_baseline = ltv_baseline / cac if cac > 0 else 0.0
    ltv_cac_tradeback = ltv_tradeback / cac if cac > 0 else 0.0
    ltv_cac_promo = ltv_promo / cac if cac > 0 else 0.0
    
    gross_realized_salvage = unit_net_salvage + compute_blended_collection_cost(params) + params.get("qc_inspection_cost", 45.0)
    
    return UnitEconomicsResult(
        n_orders_base=round(n_orders_base, 2),
        n_orders_adopter=round(n_orders_adopter, 2),
        n_orders_cohort=round(n_orders_cohort, 2),
        n_eligible_repeats_adopter=round(n_eligible_repeats_adopter, 2),
        n_returns_adopter=round(n_returns_adopter, 3),
        n_returns_cohort=round(n_returns_cohort, 3),
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
        unit_tradeback_credit=round(c_tb, 2),
        cm_order=round(cm_order, 2),
        delta_n_orders=round(delta_n_orders, 2),
        incremental_volume_margin=round(incremental_volume_margin, 2),
        cac_avoided=round(cac_avoided, 2),
        circular_unit_spread=round(circular_unit_spread, 2),
        net_unit_circular_balance=round(net_unit_circular_balance, 2),
        delta_ltc_adopter=round(delta_ltc_adopter, 2),
        gross_realized_salvage=round(gross_realized_salvage, 2),
    )
