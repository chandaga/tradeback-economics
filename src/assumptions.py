"""
TradeBack Economics & Customer Lifecycle Model: Assumptions Registry.

Single source of truth for all baseline parameters, operational levers,
and taxonomy classifications.

Taxonomy Tiers:
- [Observed]: Empirical company/market data.
- [External Benchmark]: Credible Indian e-commerce / D2C benchmarks (e.g., Meesho, Urbanic, Nykaa).
- [Management Assumption]: Founding team policy choice.
- [Model Assumption]: Structural modeling choice or proxy.
- [Unknown]: High uncertainty parameter to be experimentally validated in a pilot.
"""

from dataclasses import dataclass, field
from typing import Dict, Any, List

@dataclass
class ParameterMeta:
    name: str
    display_name: str
    default_value: float
    min_value: float
    max_value: float
    unit: str
    taxonomy_tier: str
    source_description: str
    adr_reference: str = ""

# Complete Parameter Registry with Metadata
PARAMETER_REGISTRY: Dict[str, ParameterMeta] = {
    # Group 1: Baseline Customer Economics
    "aov": ParameterMeta(
        name="aov",
        display_name="Average Order Value (AOV)",
        default_value=1300.0,
        min_value=900.0,
        max_value=1800.0,
        unit="₹",
        taxonomy_tier="[External Benchmark]",
        source_description="Indian fast-fashion mid-market standard (Urbanic, Snitch, Westside online).",
    ),
    "gross_margin_pct": ParameterMeta(
        name="gross_margin_pct",
        display_name="Gross Margin %",
        default_value=0.50,
        min_value=0.40,
        max_value=0.65,
        unit="%",
        taxonomy_tier="[External Benchmark]",
        source_description="Fast-fashion D2C average after garment manufacturing COGS and inbound freight.",
    ),
    "cac": ParameterMeta(
        name="cac",
        display_name="Customer Acquisition Cost (CAC)",
        default_value=400.0,
        min_value=250.0,
        max_value=700.0,
        unit="₹",
        taxonomy_tier="[External Benchmark]",
        source_description="Blended paid social CAC across Meta & Google in India for fashion.",
    ),
    "baseline_annual_orders": ParameterMeta(
        name="baseline_annual_orders",
        display_name="Baseline Annual Orders (f_base)",
        default_value=2.5,
        min_value=1.5,
        max_value=4.0,
        unit="orders/year",
        taxonomy_tier="[External Benchmark]",
        source_description="Standard Indian fashion e-commerce repeat purchasing frequency.",
    ),
    "customer_lifespan_months": ParameterMeta(
        name="customer_lifespan_months",
        display_name="Customer Lifespan",
        default_value=18.0,
        min_value=12.0,
        max_value=36.0,
        unit="months",
        taxonomy_tier="[Management Assumption]",
        source_description="Typical active lifespan before non-contractual churn.",
    ),
    "repeat_ad_cac": ParameterMeta(
        name="repeat_ad_cac",
        display_name="Repeat Ad CAC (M_base)",
        default_value=150.0,
        min_value=50.0,
        max_value=250.0,
        unit="₹/order",
        taxonomy_tier="[External Benchmark]",
        source_description="Blended retargeting ad spend (Meta DPA + Google) + CRM tools per repeat purchase.",
    ),
    "forward_fulfillment_cost": ParameterMeta(
        name="forward_fulfillment_cost",
        display_name="Forward Fulfillment Cost",
        default_value=70.0,
        min_value=50.0,
        max_value=100.0,
        unit="₹/order",
        taxonomy_tier="[Observed]",
        source_description="Standard forward delivery courier (Shiprocket/Delhivery) + warehouse pack cost.",
    ),

    # Group 2: TradeBack Policy & Customer Levers
    "tradeback_adoption_rate": ParameterMeta(
        name="tradeback_adoption_rate",
        display_name="TradeBack Adoption Rate (α)",
        default_value=0.40,
        min_value=0.10,
        max_value=0.80,
        unit="%",
        taxonomy_tier="[Unknown]",
        source_description="Target participation rate among eligible customers. Must validate in pilot.",
        adr_reference="ADR-004",
    ),
    "tradeback_credit_pct": ParameterMeta(
        name="tradeback_credit_pct",
        display_name="TradeBack Credit %",
        default_value=0.20,
        min_value=0.10,
        max_value=0.35,
        unit="%",
        taxonomy_tier="[Management Assumption]",
        source_description="Store credit issued at checkout as a % of original garment purchase price.",
        adr_reference="ADR-001",
    ),
    "causal_frequency_uplift": ParameterMeta(
        name="causal_frequency_uplift",
        display_name="Causal Frequency Uplift (Δf_causal)",
        default_value=0.50,
        min_value=0.0,
        max_value=1.5,
        unit="orders/year",
        taxonomy_tier="[Unknown]",
        source_description="True incremental annual purchases caused strictly by TradeBack credit incentive.",
        adr_reference="ADR-002",
    ),
    "ad_savings_pct": ParameterMeta(
        name="ad_savings_pct",
        display_name="Repeat Ad Savings % (S_ad)",
        default_value=0.80,
        min_value=0.40,
        max_value=1.00,
        unit="%",
        taxonomy_tier="[Management Assumption]",
        source_description="Share of M_base avoided because TradeBack notification replaces paid retargeting.",
    ),
    "credit_breakage_pct": ParameterMeta(
        name="credit_breakage_pct",
        display_name="Credit Breakage Rate (β)",
        default_value=0.0,
        min_value=0.0,
        max_value=0.30,
        unit="%",
        taxonomy_tier="[Model Assumption]",
        source_description="Strictly 0.0 because credit is selected and applied instantly at replacement checkout.",
        adr_reference="ADR-001",
    ),
    "stranded_garments_terminal": ParameterMeta(
        name="stranded_garments_terminal",
        display_name="Terminal Stranded Garments (N_stranded)",
        default_value=1.0,
        min_value=1.0,
        max_value=2.0,
        unit="garments",
        taxonomy_tier="[Model Assumption]",
        source_description="Last garments bought before churn that are permanently stranded in closets.",
        adr_reference="ADR-002",
    ),

    # Group 3: Reverse Logistics & Inspection Friction
    "doorstep_swap_cost": ParameterMeta(
        name="doorstep_swap_cost",
        display_name="Base Doorstep Swap Cost",
        default_value=35.0,
        min_value=25.0,
        max_value=50.0,
        unit="₹/return",
        taxonomy_tier="[External Benchmark]",
        source_description="Carrier contract fee for courier reverse pickup during forward delivery.",
        adr_reference="ADR-003",
    ),
    "swap_failure_rate": ParameterMeta(
        name="swap_failure_rate",
        display_name="Doorstep Swap Failure Rate",
        default_value=0.15,
        min_value=0.05,
        max_value=0.30,
        unit="%",
        taxonomy_tier="[External Benchmark]",
        source_description="Share of doorstep handovers that fail (customer unavailable/unready).",
        adr_reference="ADR-003",
    ),
    "standalone_reverse_cost": ParameterMeta(
        name="standalone_reverse_cost",
        display_name="Standalone Reverse Courier Cost",
        default_value=65.0,
        min_value=45.0,
        max_value=90.0,
        unit="₹/return",
        taxonomy_tier="[Observed]",
        source_description="Dedicated reverse courier fee when doorstep swap fails.",
        adr_reference="ADR-003",
    ),
    "swap_fail_rto_rate": ParameterMeta(
        name="swap_fail_rto_rate",
        display_name="Swap Fail RTO Rate",
        default_value=0.10,
        min_value=0.0,
        max_value=0.25,
        unit="%",
        taxonomy_tier="[External Benchmark]",
        source_description="Fraction of failed swaps that result in the forward parcel turning into RTO.",
        adr_reference="ADR-003",
    ),
    "rto_freight_burn": ParameterMeta(
        name="rto_freight_burn",
        display_name="RTO Forward + Reverse Freight Burn",
        default_value=130.0,
        min_value=100.0,
        max_value=180.0,
        unit="₹/RTO",
        taxonomy_tier="[External Benchmark]",
        source_description="Total forward (₹70) + return freight (₹60) wasted when forward parcel RTOs.",
        adr_reference="ADR-003",
    ),
    "qc_inspection_cost": ParameterMeta(
        name="qc_inspection_cost",
        display_name="QC & Sanitization Cost",
        default_value=45.0,
        min_value=25.0,
        max_value=80.0,
        unit="₹/garment",
        taxonomy_tier="[Observed]",
        source_description="Warehouse labor to unbox, inspect, steam-sanitize, and barcode grade.",
    ),

    # Group 4: Recovery Routes & Secondary Market
    "b2b_route_prob": ParameterMeta(
        name="b2b_route_prob",
        display_name="Route 1: B2B Jobber Probability",
        default_value=0.60,
        min_value=0.30,
        max_value=0.80,
        unit="%",
        taxonomy_tier="[External Benchmark]",
        source_description="Share of garments sold in bulk lots to offline discount jobbers.",
        adr_reference="ADR-006",
    ),
    "b2b_gross_price": ParameterMeta(
        name="b2b_gross_price",
        display_name="B2B Jobber Gross Price",
        default_value=150.0,
        min_value=80.0,
        max_value=250.0,
        unit="₹/garment",
        taxonomy_tier="[External Benchmark]",
        source_description="Cash salvage received per garment from offline liquidation lots.",
        adr_reference="ADR-006",
    ),
    "d2c_route_prob": ParameterMeta(
        name="d2c_route_prob",
        display_name="Route 2: D2C Clearance Portal Probability",
        default_value=0.20,
        min_value=0.0,
        max_value=0.40,
        unit="%",
        taxonomy_tier="[Management Assumption]",
        source_description="Share of Grade A garments resold online on a refurbished clearance portal.",
    ),
    "d2c_gross_price": ParameterMeta(
        name="d2c_gross_price",
        display_name="D2C Clearance Gross Price",
        default_value=450.0,
        min_value=250.0,
        max_value=700.0,
        unit="₹/garment",
        taxonomy_tier="[External Benchmark]",
        source_description="Selling price on refurbished portal.",
    ),
    "d2c_cannibalization_rate": ParameterMeta(
        name="d2c_cannibalization_rate",
        display_name="D2C Cannibalization Rate (θ_cannibal)",
        default_value=0.20,
        min_value=0.0,
        max_value=0.40,
        unit="%",
        taxonomy_tier="[Model Assumption]",
        source_description="Fraction of D2C clearance buyers who would have bought a full-price new item.",
    ),
    "upcycle_route_prob": ParameterMeta(
        name="upcycle_route_prob",
        display_name="Route 3: Upcycle / Redesign Probability",
        default_value=0.10,
        min_value=0.0,
        max_value=0.20,
        unit="%",
        taxonomy_tier="[Management Assumption]",
        source_description="Share of garments redesigned or remanufactured.",
    ),
    "upcycle_gross_price": ParameterMeta(
        name="upcycle_gross_price",
        display_name="Upcycle Gross Recovery",
        default_value=120.0,
        min_value=50.0,
        max_value=200.0,
        unit="₹/garment",
        taxonomy_tier="[Management Assumption]",
        source_description="Net value recovered per upcycled item after rework cost.",
    ),
    "recycle_route_prob": ParameterMeta(
        name="recycle_route_prob",
        display_name="Route 4: Industrial Rag Recycling Probability",
        default_value=0.05,
        min_value=0.0,
        max_value=0.15,
        unit="%",
        taxonomy_tier="[External Benchmark]",
        source_description="Share of garments sent to shredding / industrial rag recyclers.",
    ),
    "recycle_gross_price": ParameterMeta(
        name="recycle_gross_price",
        display_name="Recycling Salvage Price",
        default_value=15.0,
        min_value=5.0,
        max_value=30.0,
        unit="₹/garment",
        taxonomy_tier="[External Benchmark]",
        source_description="Scrap price per kg from textile shredders.",
    ),
    "writeoff_route_prob": ParameterMeta(
        name="writeoff_route_prob",
        display_name="Route 5: Unsalvageable Write-off Probability",
        default_value=0.05,
        min_value=0.0,
        max_value=0.15,
        unit="%",
        taxonomy_tier="[Model Assumption]",
        source_description="Damaged / stained garments with zero recovery value.",
    ),

    # Group 5: Inventory Holding Delay & GST
    "inventory_holding_days": ParameterMeta(
        name="inventory_holding_days",
        display_name="Inventory Holding Days (t_hold)",
        default_value=45.0,
        min_value=15.0,
        max_value=90.0,
        unit="days",
        taxonomy_tier="[Model Assumption]",
        source_description="Average delay from customer pickup to secondary market cash collection.",
    ),
    "monthly_trend_depreciation": ParameterMeta(
        name="monthly_trend_depreciation",
        display_name="Monthly Trend Depreciation Rate",
        default_value=0.05,
        min_value=0.02,
        max_value=0.10,
        unit="%/month",
        taxonomy_tier="[Model Assumption]",
        source_description="Fast-fashion trend obsolescence discount per 30 days of storage.",
    ),
    "effective_gst_leakage": ParameterMeta(
        name="effective_gst_leakage",
        display_name="Effective GST Leakage %",
        default_value=0.08,
        min_value=0.05,
        max_value=0.12,
        unit="%",
        taxonomy_tier="[External Benchmark]",
        source_description="Net un-recovered tax friction under Indian GST Margin Scheme.",
    ),

    # Group 6: Benchmark System C (Promo Coupon Alternative)
    "benchmark_coupon_discount": ParameterMeta(
        name="benchmark_coupon_discount",
        display_name="System C: Coupon Discount Value",
        default_value=200.0,
        min_value=100.0,
        max_value=300.0,
        unit="₹/order",
        taxonomy_tier="[Management Assumption]",
        source_description="Instant discount voucher given on repeat purchase in System C.",
        adr_reference="ADR-005",
    ),
}

def get_default_assumptions() -> Dict[str, float]:
    """Returns a clean key-value dictionary of all default parameters."""
    return {k: meta.default_value for k, meta in PARAMETER_REGISTRY.items()}
