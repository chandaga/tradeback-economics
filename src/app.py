"""
Interactive Streamlit Dashboard for TradeBack Economics (Phase 1).

Allows founders and investors to simulate unit economics, break-even frontiers,
and sensitivity in real time.

Run with:
.venv/bin/streamlit run src/app.py
"""

import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px

from src.assumptions import PARAMETER_REGISTRY, get_default_assumptions
from src.advisor_knowledge import (
    get_parameter_advice,
    call_gemini_diligence_advisor,
    FOUNDATIONAL_LITERATURE_REGISTRY
)
from src.tier0_engine import calculate_tier0_economics, compute_blended_collection_cost, compute_unit_net_salvage_recovery
from src.tier1_breakeven import (
    solve_breakeven_recovery,
    solve_breakeven_delta_f,
    solve_max_affordable_credit_pct,
    solve_max_tolerable_processing_cost,
    generate_breakeven_isocline,
    run_tornado_sensitivity,
    answer_section17_questions
)

st.set_page_config(
    page_title="TradeBack Economics | Investor Lifecycle Model",
    page_icon="🔄",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Styling
st.markdown("""
<style>
    .metric-card {
        background-color: #f8f9fa;
        border-radius: 8px;
        padding: 16px;
        border-left: 5px solid #1f77b4;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    .metric-title { font-size: 13px; color: #6c757d; font-weight: 600; text-transform: uppercase; }
    .metric-value { font-size: 26px; font-weight: 700; color: #212529; margin: 4px 0; }
    .metric-sub { font-size: 12px; color: #28a745; font-weight: 500; }
    .metric-sub-neg { font-size: 12px; color: #dc3545; font-weight: 500; }
</style>
""", unsafe_allow_html=True)

# --- SIDEBAR CONTROLS (UNCLUTTERED DROPDOWN DESIGN) ---
st.sidebar.title("🎛️ Control Panel")

# 1. Preset Scenarios Dropdown
scenario = st.sidebar.selectbox(
    "📌 Load Scenario Preset:",
    [
        "🎯 Base Case (Real-World Indian D2C)",
        "🛡️ Conservative Stress-Test (High Friction)",
        "🚀 Optimistic Growth Case (High Uplift)",
        "⚙️ Custom Parameters"
    ],
    index=0
)

# Initialize parameters based on preset
defaults = get_default_assumptions()
custom_params = defaults.copy()

if scenario == "🛡️ Conservative Stress-Test (High Friction)":
    custom_params.update({
        "tradeback_adoption_rate": 0.25,
        "causal_frequency_uplift": 0.20,
        "tradeback_credit_pct": 0.25,
        "b2b_gross_price": 100.0,
        "swap_failure_rate": 0.25,
        "qc_inspection_cost": 65.0,
        "d2c_cannibalization_rate": 0.35,
        "credit_breakage_pct": 0.0,
    })
elif scenario == "🚀 Optimistic Growth Case (High Uplift)":
    custom_params.update({
        "tradeback_adoption_rate": 0.60,
        "causal_frequency_uplift": 0.90,
        "tradeback_credit_pct": 0.18,
        "b2b_gross_price": 180.0,
        "swap_failure_rate": 0.10,
        "qc_inspection_cost": 35.0,
        "ad_savings_pct": 0.90,
        "credit_breakage_pct": 0.05,
    })

# Store in session state for persistence
if "params" not in st.session_state or scenario != st.session_state.get("last_scenario"):
    st.session_state["params"] = custom_params.copy()
    st.session_state["last_scenario"] = scenario

# 2. Category Selector Dropdown to prevent clutter
st.sidebar.markdown("---")
category = st.sidebar.selectbox(
    "📂 Select Settings Category to Edit:",
    [
        "1. Core Customer Economics",
        "2. TradeBack Policy & Adoption",
        "3. Reverse Logistics & RTO Friction",
        "4. Secondary Salvage & Liquidation",
        "5. Inventory Delay, Tax & Promo"
    ],
    index=1
)

# Display ONLY the controls for the selected category
p = st.session_state["params"]

if category == "1. Core Customer Economics":
    st.sidebar.markdown("#### Baseline Business Levers")
    p["aov"] = st.sidebar.slider("AOV (₹)", 800.0, 2000.0, float(p["aov"]), step=50.0)
    p["gross_margin_pct"] = st.sidebar.slider("Gross Margin %", 0.30, 0.70, float(p["gross_margin_pct"]), step=0.01, format="%.2f")
    p["cac"] = st.sidebar.slider("Customer Acquisition Cost (₹)", 150.0, 800.0, float(p["cac"]), step=25.0)
    p["baseline_annual_orders"] = st.sidebar.slider("Baseline Orders/Year (f_base)", 1.0, 5.0, float(p["baseline_annual_orders"]), step=0.1)
    p["customer_lifespan_months"] = st.sidebar.slider("Active Lifespan (Months)", 6.0, 36.0, float(p["customer_lifespan_months"]), step=3.0)
    p["repeat_ad_cac"] = st.sidebar.slider("Repeat Retargeting CAC (M_base ₹)", 30.0, 300.0, float(p["repeat_ad_cac"]), step=10.0)
    p["forward_fulfillment_cost"] = st.sidebar.slider("Forward Fulfillment Freight (₹)", 40.0, 120.0, float(p["forward_fulfillment_cost"]), step=5.0)

elif category == "2. TradeBack Policy & Adoption":
    st.sidebar.markdown("#### TradeBack Customer & Credit Rules")
    p["tradeback_credit_pct"] = st.sidebar.slider("TradeBack Credit %", 0.05, 0.40, float(p["tradeback_credit_pct"]), step=0.01, format="%.2f")
    p["tradeback_adoption_rate"] = st.sidebar.slider("Adoption Rate % (α)", 0.05, 0.90, float(p["tradeback_adoption_rate"]), step=0.05, format="%.2f")
    p["causal_frequency_uplift"] = st.sidebar.slider("Causal Order Uplift (Δf orders/yr)", 0.0, 2.0, float(p["causal_frequency_uplift"]), step=0.05)
    p["ad_savings_pct"] = st.sidebar.slider("Repeat Ad Savings % (S_ad)", 0.0, 1.00, float(p["ad_savings_pct"]), step=0.05, format="%.2f")
    p["credit_breakage_pct"] = st.sidebar.slider("Credit Breakage % (β)", 0.0, 0.30, float(p["credit_breakage_pct"]), step=0.01, format="%.2f", help="Unredeemed expired credit %")
    p["stranded_garments_terminal"] = st.sidebar.slider("Stranded Garments at Churn", 0.0, 3.0, float(p["stranded_garments_terminal"]), step=0.5, help="Clothes left in closet when customer leaves")

elif category == "3. Reverse Logistics & RTO Friction":
    st.sidebar.markdown("#### Indian Reverse Supply Chain Friction")
    p["doorstep_swap_cost"] = st.sidebar.slider("Doorstep Swap Courier Cost (₹)", 20.0, 70.0, float(p["doorstep_swap_cost"]), step=5.0)
    p["swap_failure_rate"] = st.sidebar.slider("Doorstep Swap Failure Rate %", 0.0, 0.40, float(p["swap_failure_rate"]), step=0.01, format="%.2f")
    p["standalone_reverse_cost"] = st.sidebar.slider("Standalone Reverse Courier (₹)", 40.0, 100.0, float(p["standalone_reverse_cost"]), step=5.0)
    p["swap_fail_rto_rate"] = st.sidebar.slider("Failed Swap RTO Rate %", 0.0, 0.30, float(p["swap_fail_rto_rate"]), step=0.01, format="%.2f")
    p["rto_freight_burn"] = st.sidebar.slider("RTO Wasted Freight (₹)", 80.0, 220.0, float(p["rto_freight_burn"]), step=10.0)
    p["qc_inspection_cost"] = st.sidebar.slider("QC, Sanitization & Sorting (₹)", 15.0, 90.0, float(p["qc_inspection_cost"]), step=5.0)

elif category == "4. Secondary Salvage & Liquidation":
    st.sidebar.markdown("#### Liquidation Routes & Cannibalization")
    p["b2b_gross_price"] = st.sidebar.slider("Route 1: B2B Jobber Price (₹)", 50.0, 300.0, float(p["b2b_gross_price"]), step=10.0)
    p["b2b_route_prob"] = st.sidebar.slider("Route 1: B2B Allocation %", 0.10, 0.90, float(p["b2b_route_prob"]), step=0.05, format="%.2f")
    p["d2c_gross_price"] = st.sidebar.slider("Route 2: D2C Clearance Price (₹)", 200.0, 800.0, float(p["d2c_gross_price"]), step=25.0)
    p["d2c_route_prob"] = st.sidebar.slider("Route 2: D2C Allocation %", 0.0, 0.50, float(p["d2c_route_prob"]), step=0.05, format="%.2f")
    p["d2c_cannibalization_rate"] = st.sidebar.slider("D2C Cannibalization of New Items %", 0.0, 0.50, float(p["d2c_cannibalization_rate"]), step=0.05, format="%.2f")
    p["upcycle_gross_price"] = st.sidebar.slider("Route 3: Upcycle Salvage (₹)", 30.0, 250.0, float(p["upcycle_gross_price"]), step=10.0)
    p["upcycle_route_prob"] = st.sidebar.slider("Route 3: Upcycle Allocation %", 0.0, 0.30, float(p["upcycle_route_prob"]), step=0.05, format="%.2f")
    p["recycle_gross_price"] = st.sidebar.slider("Route 4: Rag Recycling (₹)", 5.0, 40.0, float(p["recycle_gross_price"]), step=5.0)
    p["recycle_route_prob"] = st.sidebar.slider("Route 4: Recycling %", 0.0, 0.20, float(p["recycle_route_prob"]), step=0.05, format="%.2f")
    p["writeoff_route_prob"] = st.sidebar.slider("Route 5: Unsalvageable Write-Off %", 0.0, 0.25, float(p["writeoff_route_prob"]), step=0.05, format="%.2f")

elif category == "5. Inventory Delay, Tax & Promo":
    st.sidebar.markdown("#### Working Capital, Depreciation & Promo Benchmark")
    p["inventory_holding_days"] = st.sidebar.slider("Inventory Holding Delay (Days)", 0.0, 90.0, float(p["inventory_holding_days"]), step=5.0)
    p["monthly_trend_depreciation"] = st.sidebar.slider("Monthly Trend Obsolescence %", 0.0, 0.15, float(p["monthly_trend_depreciation"]), step=0.01, format="%.2f")
    p["effective_gst_leakage"] = st.sidebar.slider("Effective GST Margin Leakage %", 0.0, 0.18, float(p["effective_gst_leakage"]), step=0.01, format="%.2f")
    p["benchmark_coupon_discount"] = st.sidebar.slider("System C: Promo Coupon Discount (₹)", 50.0, 400.0, float(p["benchmark_coupon_discount"]), step=25.0)

category_params = {
    "1. Core Customer Economics": [
        ("aov", "Average Order Value (AOV)"),
        ("gross_margin_pct", "Gross Margin %"),
        ("cac", "Customer Acquisition Cost (CAC)"),
        ("baseline_annual_orders", "Baseline Orders/Year"),
        ("customer_lifespan_months", "Active Customer Lifespan"),
        ("repeat_ad_cac", "Repeat Retargeting CAC"),
        ("forward_fulfillment_cost", "Forward Delivery Freight")
    ],
    "2. TradeBack Policy & Adoption": [
        ("tradeback_credit_pct", "TradeBack Credit %"),
        ("credit_breakage_pct", "Credit Breakage % (β)"),
        ("causal_frequency_uplift", "Causal Order Uplift (Δf)"),
        ("tradeback_adoption_rate", "Adoption Rate % (α)"),
        ("stranded_garments_terminal", "Stranded Garments at Churn"),
        ("ad_savings_pct", "Repeat Ad Savings %")
    ],
    "3. Reverse Logistics & RTO Friction": [
        ("swap_failure_rate", "Doorstep Swap Failure Rate %"),
        ("doorstep_swap_cost", "Base Doorstep Swap Cost"),
        ("qc_inspection_cost", "QC, Sanitization & Sorting"),
        ("standalone_reverse_cost", "Standalone Reverse Courier"),
        ("rto_freight_burn", "RTO Wasted Freight Burn")
    ],
    "4. Secondary Salvage & Liquidation": [
        ("b2b_gross_price", "B2B Jobber Price"),
        ("d2c_cannibalization_rate", "D2C Cannibalization Rate %"),
        ("d2c_gross_price", "D2C Clearance Price"),
        ("b2b_route_prob", "B2B Route Allocation %"),
        ("upcycle_gross_price", "Upcycle Recovery Value")
    ],
    "5. Inventory Delay, Tax & Promo": [
        ("inventory_holding_days", "Inventory Holding Delay (Days)"),
        ("monthly_trend_depreciation", "Monthly Trend Obsolescence %"),
        ("effective_gst_leakage", "Effective GST Margin Leakage"),
        ("benchmark_coupon_discount", "System C Promo Coupon Value")
    ]
}

param_options = category_params.get(category, [("tradeback_credit_pct", "TradeBack Credit %")])
param_keys = [k for k, _ in param_options]
param_labels = {k: lbl for k, lbl in param_options}

st.sidebar.markdown("---")
selected_inspect_key = st.sidebar.selectbox(
    "💡 Inspect Parameter with AI Advisor:",
    param_keys,
    format_func=lambda k: param_labels.get(k, k)
)

st.sidebar.markdown("---")
if st.sidebar.button("🔄 Reset to Default Parameters", use_container_width=True):
    st.session_state["params"] = defaults.copy()
    st.rerun()

custom_params = st.session_state["params"]

# --- CALCULATE CURRENT STATE ---
res = calculate_tier0_economics(custom_params)
q_ans = answer_section17_questions(custom_params)

# --- HEADER SECTION ---
st.title("🔄 TradeBack Economics & Customer Lifecycle Model")
st.markdown("**Phase 1 Deterministic Unit Economics & Break-Even Surface Engine** | Target Market: *AI-Native Fashion D2C (India)*")

# --- KPI METRICS ROW ---
col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-title">System A: Baseline D2C</div>
        <div class="metric-value">₹{res.ltc_baseline:,.0f}</div>
        <div class="metric-sub">LTV/CAC: {res.ltv_cac_baseline:.2f}x</div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    is_pos = res.delta_contribution_tradeback >= 0
    delta_class = "metric-sub" if is_pos else "metric-sub-neg"
    sign = "+" if is_pos else ""
    st.markdown(f"""
    <div class="metric-card" style="border-left-color: {'#28a745' if is_pos else '#dc3545'};">
        <div class="metric-title">System B: TradeBack</div>
        <div class="metric-value">₹{res.ltc_cohort_tradeback:,.0f}</div>
        <div class="{delta_class}">{sign}₹{res.delta_contribution_tradeback:.1f} vs Base ({res.ltv_cac_tradeback:.2f}x)</div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    is_promo_pos = res.delta_contribution_promo >= 0
    delta_p_class = "metric-sub" if is_promo_pos else "metric-sub-neg"
    st.markdown(f"""
    <div class="metric-card" style="border-left-color: #ff7f0e;">
        <div class="metric-title">System C: ₹200 Coupon</div>
        <div class="metric-value">₹{res.ltc_benchmark_promo:,.0f}</div>
        <div class="{delta_p_class}">{'+' if is_promo_pos else ''}₹{res.delta_contribution_promo:.1f} vs Base</div>
    </div>
    """, unsafe_allow_html=True)

with col4:
    tb_adv = res.tradeback_vs_promo_delta
    is_adv_pos = tb_adv >= 0
    adv_class = "metric-sub" if is_adv_pos else "metric-sub-neg"
    st.markdown(f"""
    <div class="metric-card" style="border-left-color: #6f42c1;">
        <div class="metric-title">TradeBack vs Coupon</div>
        <div class="metric-value">{'+' if is_adv_pos else ''}₹{tb_adv:.1f}</div>
        <div class="{adv_class}">Strategy Superiority</div>
    </div>
    """, unsafe_allow_html=True)

with col5:
    st.markdown(f"""
    <div class="metric-card" style="border-left-color: #17a2b8;">
        <div class="metric-title">Net Salvage Recovery</div>
        <div class="metric-value">₹{res.unit_net_salvage_recovery:.1f}</div>
        <div class="metric-sub">Blended Logistics: ₹{res.blended_collection_cost:.1f}</div>
    </div>
    """, unsafe_allow_html=True)

st.divider()

# --- AI ECONOMICS & DILIGENCE ADVISOR BOX ---
advice = get_parameter_advice(selected_inspect_key, custom_params[selected_inspect_key], custom_params)
param_curr_val = custom_params[selected_inspect_key]
param_meta = PARAMETER_REGISTRY.get(selected_inspect_key)
unit_str = f" {param_meta.unit}" if param_meta else ""

val_display = f"{param_curr_val * 100:.1f}%" if param_meta and param_meta.unit == "%" else f"{param_curr_val:.2f}{unit_str}"

with st.expander(f"🤖 AI Economics & Market Advisor: {advice['title']} (Selected Value: {val_display})", expanded=True):
    st.markdown(f"""
    <div style="background-color: #f8faff; border-radius: 8px; padding: 14px 18px; border: 1px solid #d0e2ff;">
        <div style="font-size: 14px; font-weight: 700; margin-bottom: 10px; padding: 8px 12px; background: white; border-radius: 6px; border-left: 4px solid #1f77b4; box-shadow: 0 1px 2px rgba(0,0,0,0.03);">
            {advice['status_message']}
        </div>
        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 14px; margin-top: 8px;">
            <div style="background: white; padding: 12px 14px; border-radius: 6px; border: 1px solid #eef2f7;">
                <div style="font-size: 11px; font-weight: 700; color: #6c757d; text-transform: uppercase;">🎓 Economic Theory & Mechanism</div>
                <div style="font-size: 13px; font-weight: 700; color: #1f77b4; margin: 2px 0;">{advice['theory']}</div>
                <div style="font-size: 12px; color: #495057; line-height: 1.45;">{advice['theory_detail']}</div>
            </div>
            <div style="background: white; padding: 12px 14px; border-radius: 6px; border: 1px solid #eef2f7;">
                <div style="font-size: 11px; font-weight: 700; color: #6c757d; text-transform: uppercase;">🇮🇳 Observed Indian Market Benchmark</div>
                <div style="font-size: 12px; color: #333; line-height: 1.45; margin-top: 4px;">{advice['india_benchmark']}</div>
            </div>
        </div>
        <div style="margin-top: 10px; padding: 8px 12px; background: #eef6fc; border-radius: 6px; font-size: 12px; color: #0b5394;">
            <strong>💼 Investor & Founder Takeaway:</strong> {advice['investor_verdict']}
        </div>
    </div>
    """, unsafe_allow_html=True)

    with st.expander("📚 View Curated Literature & Empirical Benchmark Context (Shared with Gemini)", expanded=False):
        st.markdown("*The dynamic advisor is provided with this curated academic literature and empirical market dataset to ground its diligence verdicts:*")
        for lit_k, lit_v in FOUNDATIONAL_LITERATURE_REGISTRY.items():
            st.markdown(f"**{lit_v['title']}**")
            for cit in lit_v["citations"]:
                st.markdown(f"- {cit}")
        st.info(f"📌 **Current Focus ({advice['title']}):** Grounded on *{advice['theory']}* with Indian benchmark: *{advice['india_benchmark']}*")

    st.markdown("---")
    st.markdown("#### ✨ Live Dynamic Diligence Advisor (*Powered by Google Gemini 3.5 Flash*)")
    col_gem1, col_gem2 = st.columns([3, 1])
    with col_gem1:
        user_q = st.text_input(
            f"Ask Gemini a custom diligence question about '{advice['title']}' (optional):",
            placeholder="e.g. How does this compare to Snitch or Urbanic return rates in Tier 2 cities?",
            key=f"user_q_{selected_inspect_key}"
        )
    with col_gem2:
        st.write("")
        st.write("")
        ask_btn = st.button("🧠 Call Gemini 3.5 Flash", key=f"btn_gem_{selected_inspect_key}", use_container_width=True)

    if ask_btn:
        econ_summary = {
            "delta_contribution_tradeback": res.delta_contribution_tradeback,
            "min_recovery_required": q_ans.get("Q1_min_net_recovery_at_20pct_credit", 0.0)
        }
        with st.spinner("🤖 Consulting Gemini 3.5 Flash on economic viability and market benchmarks..."):
            gemini_analysis = call_gemini_diligence_advisor(
                selected_inspect_key,
                custom_params[selected_inspect_key],
                custom_params,
                econ_summary,
                user_q
            )
            st.session_state[f"gemini_analysis_{selected_inspect_key}"] = gemini_analysis

    if f"gemini_analysis_{selected_inspect_key}" in st.session_state:
        st.markdown(f"**⚡ Gemini 3.5 Flash Investment Memo Critique for `{advice['title']}`:**")
        st.markdown(st.session_state[f"gemini_analysis_{selected_inspect_key}"])

# --- MAIN NAVIGATION TABS ---
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "📊 Financial Waterfall Comparison",
    "📈 2D Break-Even Isocline",
    "🌪️ Tornado Sensitivity Ranking",
    "🎯 Diligence Q&A (Section 17)",
    "📐 Model Architecture & Formulas",
    "📋 Assumptions & Taxonomy"
])

# --- TAB 1: FINANCIAL COMPARISON ---
with tab1:
    st.subheader("36-Month Lifetime Cash Flows per Acquired Customer")
    
    col_t1, col_t2 = st.columns([1, 1])
    
    with col_t1:
        # Comparison Bar Chart
        fig_bar = go.Figure()
        fig_bar.add_trace(go.Bar(
            name="36-Month Net Contribution (₹)",
            x=["Baseline D2C", "TradeBack Model", "₹200 Promo Coupon"],
            y=[res.ltc_baseline, res.ltc_cohort_tradeback, res.ltc_benchmark_promo],
            marker_color=["#1f77b4", "#2ca02c" if res.delta_contribution_tradeback >= 0 else "#d62728", "#ff7f0e"],
            text=[f"₹{res.ltc_baseline:,.0f}", f"₹{res.ltc_cohort_tradeback:,.0f}", f"₹{res.ltc_benchmark_promo:,.0f}"],
            textposition="auto"
        ))
        fig_bar.update_layout(
            title="36-Month Net Contribution per Customer",
            yaxis_title="Contribution Margin (₹)",
            template="plotly_white",
            height=360
        )
        st.plotly_chart(fig_bar, use_container_width=True)
        
    with col_t2:
        # Adopter Waterfall
        fig_waterfall = go.Figure(go.Waterfall(
            name="Adopter Cash Flow",
            orientation="v",
            measure=["absolute", "relative", "relative", "relative", "relative", "relative", "relative", "total"],
            x=["Gross Margin", "Fulfillment", "Salvage Cash", "Credit Paid", "Cannibalization", "Ad Spend Paid", "CAC", "Net LTC"],
            textposition="outside",
            text=[
                f"+₹{res.adopter_gross_product_margin:.0f}",
                f"-₹{res.adopter_fulfillment_cost:.0f}",
                f"+₹{res.adopter_salvage_recovery_net:.0f}",
                f"-₹{res.adopter_credit_cost:.0f}",
                f"-₹{res.adopter_cannibalization_loss:.0f}",
                f"-₹{res.adopter_repeat_ad_cac_paid:.0f}",
                f"-₹{custom_params['cac']:.0f}",
                f"₹{res.ltc_adopter:.0f}"
            ],
            y=[
                res.adopter_gross_product_margin,
                -res.adopter_fulfillment_cost,
                res.adopter_salvage_recovery_net,
                -res.adopter_credit_cost,
                -res.adopter_cannibalization_loss,
                -res.adopter_repeat_ad_cac_paid,
                -custom_params["cac"],
                0
            ],
            connector={"line": {"color": "rgb(63, 63, 63)"}},
        ))
        fig_waterfall.update_layout(
            title="TradeBack Adopter Unit Cashflow Waterfall (36 Months)",
            template="plotly_white",
            height=360
        )
        st.plotly_chart(fig_waterfall, use_container_width=True)

    # Detailed Table
    st.markdown("#### Itemized 36-Month Statement")
    df_statement = pd.DataFrame({
        "Metric": [
            "Purchase Frequency (orders/yr)", "Total Orders (36 Mo)", "Garments Returned",
            "Gross Product Margin (₹)", "Fulfillment Freight (₹)", "TradeBack Credit Cost (₹)",
            "Net Salvage Cash (₹)", "Repeat Marketing Paid (₹)", "Customer Acquisition Cost (CAC ₹)",
            "36-Month Net Contribution (₹)", "LTV / CAC Ratio"
        ],
        "Baseline D2C (A)": [
            f"{custom_params['baseline_annual_orders']:.2f}", f"{res.n_orders_base:.2f}", "0.00",
            f"₹{res.n_orders_base * custom_params['aov'] * custom_params['gross_margin_pct']:,.0f}",
            f"-₹{res.n_orders_base * custom_params['forward_fulfillment_cost']:,.0f}", "₹0", "₹0",
            f"-₹{max(0.0, res.n_orders_base - 1.0) * custom_params['repeat_ad_cac']:,.0f}",
            f"-₹{custom_params['cac']:,.0f}", f"₹{res.ltc_baseline:,.0f}", f"{res.ltv_cac_baseline:.2f}x"
        ],
        "TradeBack Model (B)": [
            f"{custom_params['baseline_annual_orders'] + custom_params['causal_frequency_uplift']:.2f}",
            f"{res.n_orders_cohort:.2f}", f"{res.n_returns_cohort:.2f}",
            f"₹{res.n_orders_cohort * custom_params['aov'] * custom_params['gross_margin_pct']:,.0f}",
            f"-₹{res.n_orders_cohort * custom_params['forward_fulfillment_cost']:,.0f}",
            f"-₹{res.n_returns_cohort * custom_params['aov'] * custom_params['tradeback_credit_pct']:,.0f}",
            f"+₹{res.n_returns_cohort * res.unit_net_salvage_recovery:,.0f}",
            f"-₹{custom_params['tradeback_adoption_rate'] * res.adopter_repeat_ad_cac_paid + (1.0 - custom_params['tradeback_adoption_rate']) * max(0.0, res.n_orders_base - 1.0) * custom_params['repeat_ad_cac']:,.0f}",
            f"-₹{custom_params['cac']:,.0f}", f"₹{res.ltc_cohort_tradeback:,.0f}", f"{res.ltv_cac_tradeback:.2f}x"
        ],
        "System C: Promo Coupon": [
            f"{custom_params['baseline_annual_orders'] + custom_params['causal_frequency_uplift']:.2f}",
            f"{res.n_orders_cohort:.2f}", "0.00",
            f"₹{res.n_orders_cohort * custom_params['aov'] * custom_params['gross_margin_pct']:,.0f}",
            f"-₹{res.n_orders_cohort * custom_params['forward_fulfillment_cost']:,.0f}", "₹0", "₹0",
            f"-₹{custom_params['tradeback_adoption_rate'] * max(0.0, res.n_orders_adopter - 1.0) * custom_params['repeat_ad_cac'] * 0.2 + (1.0 - custom_params['tradeback_adoption_rate']) * max(0.0, res.n_orders_base - 1.0) * custom_params['repeat_ad_cac']:,.0f}",
            f"-₹{custom_params['cac']:,.0f}", f"₹{res.ltc_benchmark_promo:,.0f}", f"{res.ltv_cac_promo:.2f}x"
        ],
        "Net Accretion (B - A)": [
            f"+{custom_params['causal_frequency_uplift']:.2f}", f"+{res.n_orders_cohort - res.n_orders_base:.2f}",
            f"+{res.n_returns_cohort:.2f}", "-", "-", "-", "-", "-", "-",
            f"{'+' if res.delta_contribution_tradeback >= 0 else ''}₹{res.delta_contribution_tradeback:.1f}",
            f"{'+' if res.ltv_cac_tradeback >= res.ltv_cac_baseline else ''}{res.ltv_cac_tradeback - res.ltv_cac_baseline:.2f}x"
        ]
    })
    st.dataframe(df_statement, use_container_width=True, hide_index=True)

# --- TAB 2: BREAK-EVEN ISOCLINE ---
with tab2:
    st.subheader("The 2D Break-Even Surface: Net Recovery vs. Causal Uplift")
    st.markdown("The line marks the exact boundary where **TradeBack Net Accretion (ΔContribution) = ₹0**.")
    
    isocline = generate_breakeven_isocline(custom_params)
    df_iso = pd.DataFrame(isocline)
    
    current_df = custom_params["causal_frequency_uplift"]
    current_rec = res.unit_net_salvage_recovery
    
    fig_iso = go.Figure()
    
    # Break-even line
    fig_iso.add_trace(go.Scatter(
        x=df_iso["causal_frequency_uplift"],
        y=df_iso["required_net_recovery"],
        mode="lines+markers",
        name="Break-Even Boundary (ΔCM = 0)",
        line={"color": "#1f77b4", "width": 3},
        marker={"size": 6}
    ))
    
    # Current Operating Point
    fig_iso.add_trace(go.Scatter(
        x=[current_df],
        y=[current_rec],
        mode="markers",
        name="Current Position",
        marker={"size": 14, "color": "#2ca02c" if res.delta_contribution_tradeback >= 0 else "#d62728", "symbol": "diamond"}
    ))
    
    fig_iso.update_layout(
        title="Break-Even Isocline: Required Net Garment Recovery (₹) vs. Incremental Purchase Frequency",
        xaxis_title="Causal Annual Order Uplift (Δf orders/year)",
        yaxis_title="Required Net Garment Recovery E[R_net] (₹)",
        template="plotly_white",
        height=480,
        hovermode="x unified"
    )
    
    col_iso1, col_iso2 = st.columns([3, 1])
    with col_iso1:
        st.plotly_chart(fig_iso, use_container_width=True)
    with col_iso2:
        st.markdown("### Diligence Boundary Cards")
        min_rec_zero = solve_breakeven_recovery(0.0, custom_params)
        min_f_zero = solve_breakeven_delta_f(0.0, custom_params)
        st.info(f"**If Uplift = 0 (Δf = 0.0):**\nMust recover at least **₹{min_rec_zero:.1f}** net per garment.")
        st.info(f"**If Recovery = ₹0 (Scrap):**\nMust cause at least **+{min_f_zero:.2f}** orders/year.")
        st.info(f"**Max Affordable Credit:**\n**{q_ans['Q5_max_affordable_credit_pct']}%** of AOV (₹{custom_params['aov']*q_ans['Q5_max_affordable_credit_pct']/100:.0f}).")

# --- TAB 3: TORNADO SENSITIVITY ---
with tab3:
    st.subheader("Global Tornado Sensitivity Analysis")
    st.markdown("Measures the swing impact on 36-month net contribution when each variable moves from its minimum to maximum tested bound.")
    
    tornado_data = run_tornado_sensitivity(custom_params)
    df_tor = pd.DataFrame(tornado_data)
    
    fig_tor = go.Figure()
    fig_tor.add_trace(go.Bar(
        y=df_tor["display_name"][::-1],
        x=df_tor["swing_range"][::-1],
        orientation="h",
        marker_color="#1f77b4",
        text=[f"₹{x:,.0f}" for x in df_tor["swing_range"][::-1]],
        textposition="outside"
    ))
    fig_tor.update_layout(
        title="Top 12 Drivers of 3-Year TradeBack Profitability (Ranked by ₹ Impact)",
        xaxis_title="Total Swing Range in 3-Year Contribution (₹)",
        template="plotly_white",
        height=520
    )
    st.plotly_chart(fig_tor, use_container_width=True)
    
    st.dataframe(df_tor[["display_name", "min_val", "max_val", "unit", "delta_cm_at_min", "delta_cm_at_max", "swing_range"]], use_container_width=True)

# --- TAB 4: SECTION 17 BUSINESS Q&A ---
with tab4:
    st.subheader("Investor Diligence Answers (Section 17 from Project Brief)")
    st.markdown("Dynamic answers calibrated to your current slider assumptions:")
    
    col_q1, col_q2 = st.columns(2)
    with col_q1:
        st.markdown(f"""
        * **Q1. At {custom_params['tradeback_credit_pct']*100:.0f}% credit, what min net recovery is required?**  
          👉 **₹{q_ans['Q1_min_net_recovery_at_20pct_credit']:.2f} / return** (Current realized: ₹{res.unit_net_salvage_recovery:.2f}).
        
        * **Q2. If net recovery is only ₹250, what incremental frequency is required?**  
          👉 **{q_ans['Q2_req_freq_uplift_if_recovery_250']:.2f} orders/year** (Accretive even at zero or minor negative uplift!).
        
        * **Q3. If annual purchase frequency increases by only 10% (+0.25 orders/yr), does it work?**  
          👉 **{'YES (+₹' + str(q_ans['Q3_delta_cm']) + ')' if q_ans['Q3_works_with_10pct_freq_uplift'] else 'NO (Loss: ₹' + str(q_ans['Q3_delta_cm']) + ')'}**.
        
        * **Q4. If only 40% of returned garments can be resold, does it work?**  
          👉 **{'YES (+₹' + str(q_ans['Q4_delta_cm']) + ')' if q_ans['Q4_works_with_40pct_resale'] else 'NO (Loss: ₹' + str(q_ans['Q4_delta_cm']) + ')'}**.
        
        * **Q5. What is the maximum TradeBack credit % we can offer?**  
          👉 **{q_ans['Q5_max_affordable_credit_pct']}% of original price** (₹{custom_params['aov']*q_ans['Q5_max_affordable_credit_pct']/100:.0f}).
        """)
    with col_q2:
        st.markdown(f"""
        * **Q6. What is the minimum resale probability required?**  
          👉 **{q_ans['Q6_min_resale_prob_pct']}%** resale success rate.
        
        * **Q7. What is the maximum processing + QC cost we can tolerate?**  
          👉 **₹{q_ans['Q7_max_tolerable_qc_cost']:.2f} / garment** (Current: ₹{custom_params['qc_inspection_cost']:.2f}).
        
        * **Q8. How does a 5%, 10%, 20% increase in customer retention change economics?**  
          👉 {q_ans['Q8_retention_sensitivity']}.
        
        * **Q9. What combination produces break-even?**  
          👉 At {custom_params['tradeback_adoption_rate']*100:.0f}% adoption and +{custom_params['causal_frequency_uplift']:.2f} uplift, requires **₹{q_ans['Q1_min_net_recovery_at_20pct_credit']:.2f}** net recovery.
        
        * **Q10. At what point is TradeBack worse than spending on marketing / coupons?**  
          👉 Current TradeBack advantage over ₹200 promo coupon is **+₹{q_ans['Q10_tradeback_vs_coupon_superiority']:.2f} / customer**. If net recovery drops below ₹45, promo couponing becomes strictly superior.
        """)

# --- TAB 5: MODEL ARCHITECTURE & FORMULAS (1-2 PAGER) ---
with tab5:
    st.subheader("📐 Master Architecture & Accounting Identities (1-2 Pager)")
    st.markdown("Mathematical specifications, order truncation mechanics, and operational identities calibrated to your live inputs.")

    # Download button for co-founder memo
    memo_path = os.path.join(os.path.dirname(__file__), "..", "docs", "MODEL_COMPARISON_1PAGER.md")
    if os.path.exists(memo_path):
        with open(memo_path, "r") as f:
            memo_text = f.read()
        st.download_button(
            label="📥 Download 1-Pager Model Memo (.md)",
            data=memo_text,
            file_name="tradeback_model_comparison_1pager.md",
            mime="text/markdown",
            key="dl_1pager_memo"
        )

    # 1. Strategy Comparison Matrix
    st.markdown("### 1. Executive Strategy Comparison Matrix")
    matrix_df = pd.DataFrame([
        {
            "Dimension": "Core Customer Incentive",
            "System A (Baseline D2C)": "None (Full payment)",
            "System B (TradeBack)": f"{custom_params['tradeback_credit_pct']*100:.0f}% Store Credit (₹{custom_params['aov']*custom_params['tradeback_credit_pct']:.0f})",
            "System C (Promo Coupon)": f"₹{custom_params['benchmark_coupon_discount']:.0f} Instant Voucher"
        },
        {
            "Dimension": "Prerequisite Action",
            "System A (Baseline D2C)": "Out-of-pocket repeat order",
            "System B (TradeBack)": "Physical return of 3-6 mo old item",
            "System C (Promo Coupon)": "Promo code entry at checkout"
        },
        {
            "Dimension": "Operational Reverse Chain",
            "System A (Baseline D2C)": "None (Forward shipping only)",
            "System B (TradeBack)": "Doorstep swap, QC & secondary salvage",
            "System C (Promo Coupon)": "None (Pure digital discount)"
        },
        {
            "Dimension": "Lifetime Contribution (LTC)",
            "System A (Baseline D2C)": f"₹{res.ltc_baseline:,.2f}",
            "System B (TradeBack)": f"₹{res.ltc_cohort_tradeback:,.2f} (Adopter: ₹{res.ltc_adopter:,.2f})",
            "System C (Promo Coupon)": f"₹{res.ltc_benchmark_promo:,.2f}"
        },
        {
            "Dimension": "LTV / CAC Ratio",
            "System A (Baseline D2C)": f"{res.ltv_cac_baseline:.2f}x",
            "System B (TradeBack)": f"{res.ltv_cac_tradeback:.2f}x",
            "System C (Promo Coupon)": f"{res.ltv_cac_promo:.2f}x"
        },
        {
            "Dimension": "Net Accretion vs Baseline A",
            "System A (Baseline D2C)": "Baseline (₹0.00)",
            "System B (TradeBack)": f"+₹{res.delta_contribution_tradeback:,.2f} / customer",
            "System C (Promo Coupon)": f"+₹{res.delta_contribution_promo:,.2f} / customer"
        },
        {
            "Dimension": "Strategic Superiority",
            "System A (Baseline D2C)": "Vulnerable to rising Meta CAC",
            "System B (TradeBack)": f"+₹{res.tradeback_vs_promo_delta:,.2f} vs Promo Coupon",
            "System C (Promo Coupon)": "Margin drag without inventory salvage"
        }
    ])
    st.dataframe(matrix_df, use_container_width=True, hide_index=True)

    # 2. Governing Equations by System
    st.markdown("---")
    st.markdown("### 2. Governing Equations & Accounting Identities")

    with st.expander("System A: Conventional D2C Baseline Equations", expanded=True):
        st.markdown("Every repeat order requires paid performance marketing retargeting. No reverse logistics or credits.")
        st.latex(r"N_{\text{base}} = f_{\text{base}} \times \left(\frac{T_{\text{active}}}{12}\right)")
        st.latex(r"\text{LTC}_{\text{baseline}} = -\text{CAC}_{\text{init}} + N_{\text{base}} \times (\text{AOV} \times \text{GM} - C_{\text{fulfill}}) - (N_{\text{base}} - 1) \times \text{CAC}_{\text{repeat}}")
        st.info(f"**Current System A Live Output:** Orders = {res.n_orders_base:.2f} | LTC = **₹{res.ltc_baseline:,.2f}** | LTV/CAC = **{res.ltv_cac_baseline:.2f}x**")

    with st.expander("System B: TradeBack Closed-Loop Buy-Back Equations", expanded=True):
        st.markdown("#### A. Order Accounting & Return Frequency Decomposition")
        st.markdown("""
        In a 4.50-order lifecycle ($N_{\\text{adopter}} = 4.50$), there are $N_{\\text{adopter}} - 1 = 3.50$ repeat order opportunities:
        * **Terminal Stranded Garment ($N_{\\text{stranded}} = 1.0$):** The final garment bought before the customer churns remains stranded in their wardrobe (no subsequent order to redeem against).
        * **Return Expiration / Window Dropout (~1.0 order):** Repeat purchases occurring outside the eligible 3–6 month return window or where the customer keeps the item yield no return.
        * **Eligible TradeBack Returns:** $N_{\\text{returns}} = \\max\\left(0, \\; N_{\\text{adopter}} - 1 - N_{\\text{stranded}}\\right) = 4.50 - 1 - 1 = \\mathbf{2.50} \\text{ returns}$.
        * **Full-Margin Orders:** $N_{\\text{full-margin}} = N_{\\text{adopter}} - N_{\\text{returns}} = 4.50 - 2.50 = \\mathbf{2.00} \\text{ orders}$ (earn full gross margin without store credit discount).
        """)
        st.latex(r"N_{\text{adopter}} = (f_{\text{base}} + \Delta f_{\text{causal}}) \times \left(\frac{T_{\text{active}}}{12}\right)")
        st.latex(r"N_{\text{returns}} = \max\left(0, \; N_{\text{adopter}} - 1 - N_{\text{stranded}}\right)")
        st.latex(r"N_{\text{full-margin}} = N_{\text{adopter}} - N_{\text{returns}}")

        st.markdown("#### B. Blended Reverse Logistics Cascade ($C_{\\text{collection}}$)")
        st.markdown("Doorstep swap fails at rate $P_{\\text{fail}}$, cascading into standalone courier or forward RTO freight penalty:")
        st.latex(r"C_{\text{collection}} = C_{\text{swap}} + P_{\text{fail}} \times \left[ C_{\text{standalone-rev}} + P_{\text{RTO}} \times (C_{\text{forward}} + C_{\text{RTO-freight}}) \right]")
        st.write(f"👉 **Current Blended Collection Cost:** **₹{res.blended_collection_cost:.2f} / return** (Base swap: ₹{custom_params['doorstep_swap_cost']:.0f}, Failure rate: {custom_params['swap_failure_rate']*100:.0f}%, RTO penalty: {custom_params['swap_fail_rto_rate']*100:.0f}%)")

        st.markdown("#### C. Expected Net Garment Salvage Recovery ($E[R_{\\text{net}}]$)")
        st.latex(r"E[R_{\text{net}}] = \sum_{k} P_k \times \left( V_k \times (1 - d_{\text{trend}})^{\frac{t_{\text{hold}}}{30}} - C_{\text{route-}k} \right) - C_{\text{collection}} - C_{\text{QC}} - \text{Tax}_{\text{GST}}")
        st.write(f"👉 **Current Realized Net Salvage Recovery:** **₹{res.unit_net_salvage_recovery:.2f} / returned garment** (B2B jobber gross: ₹{custom_params['b2b_gross_price']:.0f}, QC: ₹{custom_params['qc_inspection_cost']:.0f})")

        st.markdown("#### D. Adopter Lifetime Contribution ($\\text{LTC}_{\\text{adopter}}$)")
        st.markdown("*Avoided Marketing Formula Reconciled:* Repeat ad spend is charged across all $(N_{\\text{adopter}} - 1)$ repeat orders, with savings $S_{\\text{ad}} = 80\\%$ applied strictly to the $N_{\\text{returns}}$ orders triggered via TradeBack:")
        st.latex(r"\text{LTC}_{\text{adopter}} = -\text{CAC}_{\text{init}} + N_{\text{adopter}} (\text{AOV} \cdot \text{GM} - C_{\text{fulfill}}) + N_{\text{returns}} E[R_{\text{net}}] - N_{\text{returns}} (\text{AOV} \cdot \text{Credit}_{\text{pct}}) - N_{\text{returns}} P_{\text{D2C}} \theta_{\text{cannibal}} (\text{AOV} \cdot \text{GM}) - (N_{\text{adopter}} - 1) \text{CAC}_{\text{repeat}} + N_{\text{returns}} (\text{CAC}_{\text{repeat}} \cdot S_{\text{ad}})")
        st.write(f"👉 **Current Adopter LTC:** **₹{res.ltc_adopter:,.2f}** (vs Baseline: ₹{res.ltc_baseline:,.2f})")

        st.markdown("#### E. Partitioned Cohort Blended Economics (Zero Breakage $\\beta = 0\%$)")
        st.latex(r"\text{Cohort LTC} = \alpha \times \text{LTC}_{\text{adopter}} + (1 - \alpha) \times \text{LTC}_{\text{baseline}}")
        st.latex(r"\Delta \text{Contribution}_{\text{TradeBack}} = \alpha \times (\text{LTC}_{\text{adopter}} - \text{LTC}_{\text{baseline}})")
        st.info(f"**Current Cohort Live Calculation (Adoption $\\alpha = {custom_params['tradeback_adoption_rate']*100:.0f}\%$):** Cohort LTC = **₹{res.ltc_cohort_tradeback:,.2f}** | Net Accretion = **+₹{res.delta_contribution_tradeback:,.2f} / acquired customer**")

    with st.expander("System C: Benchmark Promotional Coupon Equations", expanded=True):
        st.markdown("Simulates an aggressive loyalty discount benchmark evaluated on the same 40% cohort adoption basis ($\\alpha = 0.40$):")
        st.latex(r"\text{LTC}_{\text{promo-adopter}} = -\text{CAC}_{\text{init}} + N_{\text{adopter}} (\text{AOV} \cdot \text{GM} - C_{\text{fulfill}}) - (N_{\text{adopter}} - 1) \text{Discount}_{\text{coupon}} - (N_{\text{adopter}} - 1) \text{CAC}_{\text{repeat}} (1 - S_{\text{ad}})")
        st.latex(r"\text{Cohort LTC}_{\text{promo}} = \alpha \times \text{LTC}_{\text{promo-adopter}} + (1 - \alpha) \times \text{LTC}_{\text{baseline}}")
        st.latex(r"\Delta \text{Contribution}_{\text{Promo}} = \text{Cohort LTC}_{\text{promo}} - \text{LTC}_{\text{baseline}}")
        st.latex(r"\text{TradeBack Superiority} = \text{Cohort LTC}_{\text{TradeBack}} - \text{Cohort LTC}_{\text{promo}}")
        st.info(f"**Current System C Live Output:** Promo Adopter LTC = **₹1,405.00** | Cohort Blended LTC = **₹{res.ltc_benchmark_promo:,.2f}** | TradeBack Superiority vs Promo = **{'+' if res.tradeback_vs_promo_delta>=0 else ''}₹{res.tradeback_vs_promo_delta:,.2f} / customer**")

    # 3. 5 Deal-Breaker Investor Thresholds
    st.markdown("---")
    st.markdown("### 3. The 5 Deal-Breaker Investor Threshold Formulas")
    col_t1, col_t2 = st.columns(2)
    with col_t1:
        st.markdown(f"""
        * **1. Minimum Net Recovery Required ($E[R_{{\\text{{net}}}}]$ at $\\Delta f = 0$):**  
          $$\\text{{Break-Even Recovery}} = \\text{{Credit}} - \\text{{Ad Savings}} = ₹{custom_params['aov']*custom_params['tradeback_credit_pct']:.0f} - ₹{custom_params['repeat_ad_cac']*custom_params['ad_spend_reduction_tradeback']:.0f}$$  
          👉 **₹{q_ans['Q1_min_net_recovery_at_20pct_credit']:.2f} / return** (Current realized: ₹{res.unit_net_salvage_recovery:.2f}).

        * **2. Minimum Causal Frequency Uplift ($\Delta f_{{\\text{{causal}}}}$ at $E[R] = ₹0$):**  
          $$\\Delta f_{{\\text{{min}}}} = \\frac{{N_{{\\text{{returns}}}} \\times (\\text{{Credit}} - \\text{{Ad Savings}})}}{{(T_{{\\text{{active}}}}/12) \\times (\\text{{AOV}} \\cdot \\text{{GM}} - C_{{\\text{{fulfill}}}} - \\text{{CAC}}_{{\\text{{repeat}}}})}}$$  
          👉 **+{q_ans['Q2_req_freq_uplift_if_recovery_250']:.2f} orders/year** required if net salvage recovery is zero.

        * **3. Maximum Affordable Credit % Ceiling:**  
          $$\\text{{Credit}}_{{\\text{{max}}}} = \\frac{{\\text{{Contribution Margin}} + E[R_{{\\text{{net}}}}] + \\text{{Ad Savings}}}}{{\\text{{AOV}}}}$$  
          👉 **{q_ans['Q5_max_affordable_credit_pct']:.1f}% of AOV** (₹{custom_params['aov']*q_ans['Q5_max_affordable_credit_pct']/100:.0f}). Exceeding this destroys replacement gross margins!
        """)
    with col_t2:
        st.markdown(f"""
        * **4. Maximum Tolerable QC & Sanitization Cost ($C_{{\\text{{QC, max}}}}$):**  
          $$C_{{\\text{{QC, max}}}} = C_{{\\text{{QC, current}}}} + (\\text{{LTC}}_{{\\text{{adopter}}}} - \\text{{LTC}}_{{\\text{{baseline}}}})/N_{{\\text{{returns}}}}$$  
          👉 **₹{q_ans['Q7_max_tolerable_qc_cost']:.2f} / garment** (Current: ₹{custom_params['qc_inspection_cost']:.2f}).

        * **5. TradeBack vs Promo Coupon Superiority Threshold:**  
          $$\\text{{TradeBack is Accretive vs Promo}} \\iff E[R_{{\\text{{net}}}}] \\ge \\text{{Credit}} - \\text{{Discount}}_{{\\text{{promo}}}} - (S_{{\\text{{ad, TradeBack}}}} - S_{{\\text{{ad, Promo}}}}) \\text{{CAC}}_{{\\text{{repeat}}}}$$  
          👉 Current Advantage: **+₹{q_ans['Q10_tradeback_vs_coupon_superiority']:.2f} / customer**. TradeBack remains superior as long as net salvage $\\ge$ **₹45.00 / garment**.
        """)

# --- TAB 6: ASSUMPTIONS & TAXONOMY ---
with tab6:
    st.subheader("Assumptions Registry Classified by 5-Tier Data Taxonomy")
    
    rows = []
    for k, meta in PARAMETER_REGISTRY.items():
        rows.append({
            "Display Name": meta.display_name,
            "Key": meta.name,
            "Default": meta.default_value,
            "Unit": meta.unit,
            "Taxonomy Tier": meta.taxonomy_tier,
            "ADR Ref": meta.adr_reference,
            "Source Description": meta.source_description
        })
    df_tax = pd.DataFrame(rows)
    st.dataframe(df_tax, use_container_width=True, hide_index=True)
