"""
AI Economics & Market Diligence Knowledge Base & Live Gemini Integration.

Contains:
1. Built-in instant local economic theories & benchmarks.
2. Live Google Gemini 2.5 Flash API connector for dynamic diligence reasoning.
"""

import os
import json
import urllib.request
from typing import Dict, Any, Optional

def load_gemini_api_key() -> Optional[str]:
    """Reads GEMINI_API_KEY from st.secrets, .env, or environment variable."""
    try:
        import streamlit as st
        if hasattr(st, "secrets") and "GEMINI_API_KEY" in st.secrets:
            return str(st.secrets["GEMINI_API_KEY"]).strip()
    except Exception:
        pass
    if os.getenv("GEMINI_API_KEY"):
        return os.getenv("GEMINI_API_KEY")
    env_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".env"))
    if os.path.exists(env_path):
        try:
            with open(env_path) as f:
                for line in f:
                    if line.startswith("GEMINI_API_KEY="):
                        return line.split("=", 1)[1].strip().strip('"').strip("'")
        except Exception:
            pass
    return None

def call_gemini_diligence_advisor(
    param_key: str,
    current_value: float,
    all_params: Dict[str, float],
    economics_summary: Dict[str, Any],
    custom_question: str = ""
) -> str:
    """
    Calls Google Gemini 2.5 Flash live to perform real-time venture capital diligence
    and economic stress-testing on the founder's exact scenario.
    """
FOUNDATIONAL_LITERATURE_REGISTRY: Dict[str, Dict[str, Any]] = {
    "behavioral_economics": {
        "title": "Behavioral & Mental Accounting Frameworks",
        "citations": [
            "Thaler, R. (1985, 1999). 'Mental Accounting and Consumer Choice'. Marketing Science / Journal of Behavioral Decision Making. (Fungibility violation: store credit perceived as 'unearned windfall' or 'house money', lowering transaction pain on replacement orders).",
            "Akerlof, G. A. (1970). 'The Market for Lemons: Quality Uncertainty and the Market Mechanism'. Quarterly Journal of Economics. (Adverse selection: uniform buy-back price causes customers to hoard mint items and return heavily worn/stained lemons).",
            "Kahneman, D., Knetsch, J. L., & Thaler, R. H. (1990). 'Experimental Tests of the Endowment Effect and the Coase Theorem'. Journal of Political Economy. (Divestiture disutility: customers systematically overvalue owned clothes, requiring higher credit thresholds to overcome endowment bias).",
            "Prelec, D., & Loewenstein, G. (1998). 'The Red and the Black: Mental Accounting of Savings and Debt'. Marketing Science. (Payment coupling/decoupling: immediate checkout credit deduction vs delayed store wallet balances).",
            "Rubin, D. B. (1974) / Imbens & Rubin (2015). 'Causal Inference in Statistics, Social, and Biomedical Sciences'. (Rubin Causal Model: isolating true causal repeat purchase lift Δf_causal from observational loyalty self-selection)."
        ]
    },
    "closed_loop_supply_chains": {
        "title": "Closed-Loop Supply Chains & Re-commerce Operations",
        "citations": [
            "Guide, V. D. R., & Van Wassenhove, L. N. (2009). 'The Evolution of Closed-Loop Supply Chains'. Operations Research. (Quality uncertainty of returns, inspection/grading triage bottlenecks, and rapid depreciation of seasonal fashion inventory).",
            "Ray, S., Boyaci, T., & Aras, N. (2005). 'Optimal Cannibalization and Trade-In Rebates in Closed-Loop Supply Chains'. M&SOM. (Trade-off between trade-in incentives, new product cannibalization, and remanufacturing yield).",
            "Coase, R. H. (1937, 1960). 'The Nature of the Firm' & 'The Problem of Social Cost'. (Transaction cost economics: bilateral friction of B2C re-commerce vs low-friction bulk B2B jobber liquidation)."
        ]
    },
    "indian_market_benchmarks": {
        "title": "Empirical Indian E-Commerce & Secondary Textile Benchmarks",
        "citations": [
            "Bain & Company / Flipkart (2023–2025). 'How India Shops Online'. (Indian fashion D2C annual frequency 2.2–2.8 orders/yr; AOV ₹1,000–₹1,400; gross margin 48%–52%; COD prevalence).",
            "RedSeer Strategy Consultants (2024). 'India E-Commerce Logistics & Reverse Supply Chains'. (Forward shipping ₹65–₹80; reverse pickup ₹90–₹120; doorstep exchange/swap failure rate 18%–25%; COD RTO rates 25%–35%).",
            "Delhivery & Shadowfax Operational Filings (2024). (Courier stop-time limits <3 mins per delivery; doorstep subjective QC false acceptance rate exceeds 85% without automated optical verification).",
            "Panipat Recycled Textile Association & Surat Textile Trade (2024). (Post-consumer synthetic blended garments trade by weight at ₹15–₹30/kg for shoddy yarn/insulation; bulk brand deadstock liquidates at ₹80–₹160/unit)."
        ]
    }
}

def call_gemini_diligence_advisor(
    param_key: str,
    current_value: float,
    all_params: Dict[str, float],
    economics_summary: Dict[str, Any],
    custom_question: str = ""
) -> str:
    """
    Calls Google Gemini live to perform real-time venture capital diligence
    and economic stress-testing grounded on curated literature and empirical benchmarks.
    """
    api_key = load_gemini_api_key()
    if not api_key:
        return "⚠️ Gemini API key not found. Please set GEMINI_API_KEY in .env file."
        
    kb_entry = ADVISOR_KNOWLEDGE_BASE.get(param_key, {})
    param_title = kb_entry.get("title", param_key)
    param_theory = kb_entry.get("theory", "Unit Economics & Microeconomic Principles")
    param_theory_detail = kb_entry.get("theory_detail", "")
    param_benchmark = kb_entry.get("india_benchmark", "")
    param_verdict = kb_entry.get("investor_verdict", "")

    # Format academic literature citations
    lit_text = ""
    for group_key, group_data in FOUNDATIONAL_LITERATURE_REGISTRY.items():
        lit_text += f"\n### {group_data['title']}:\n"
        for cit in group_data["citations"]:
            lit_text += f"- {cit}\n"

    prompt = f"""
You are a top-tier Venture Capital Diligence Partner and Retail Economist specializing in Indian fast-fashion D2C e-commerce (benchmarking against Urbanic, Snitch, Myntra, Meesho, and Delhivery).

The founder is building 'TradeBack'—a closed-loop garment buy-back model where customers return 3-6 month old clothes for store credit on their next purchase.

======================================================================
1. FOUNDATIONAL ACADEMIC & MARKET LITERATURE (SHARED CONTEXT FOR VERDICT):
You MUST strictly anchor and ground your evaluation on this literature dataset:
{lit_text}

PARAMETER-SPECIFIC THEORETICAL PREMISE:
- Parameter Inspected: {param_title} ({param_key} = {current_value})
- Core Theoretical Lens: {param_theory}
- Theoretical Rationale: {param_theory_detail}
- Indian Empirical Ground Truth Benchmark: {param_benchmark}
- Founding Team Governance Heuristic: {param_verdict}
======================================================================

2. CURRENT OPERATING STATE & FINANCIAL ENGINE OUTPUT (EXACT NUMBERS):
- Average Order Value (AOV): ₹{all_params.get('aov', 1300):,.0f}
- Gross Margin %: {all_params.get('gross_margin_pct', 0.50)*100:.1f}%
- Customer Acquisition Cost (CAC): ₹{all_params.get('cac', 400):,.0f}
- Baseline Annual Purchases: {all_params.get('baseline_annual_orders', 2.5):.2f} orders/year
- Active Customer Lifespan: {all_params.get('customer_lifespan_months', 18):.0f} months
- TradeBack Credit %: {all_params.get('tradeback_credit_pct', 0.20)*100:.1f}% of original price
- TradeBack Adoption Rate (α): {all_params.get('tradeback_adoption_rate', 0.40)*100:.1f}%
- Causal Order Uplift (Δf): +{all_params.get('causal_frequency_uplift', 0.50):.2f} orders/year
- Credit Breakage % (β): {all_params.get('credit_breakage_pct', 0.0)*100:.1f}%
- Terminal Stranded Garments: {all_params.get('stranded_garments_terminal', 1.0):.1f}
- B2B Jobber Liquidation Price: ₹{all_params.get('b2b_gross_price', 150):,.0f}
- Doorstep Swap Failure Rate: {all_params.get('swap_failure_rate', 0.15)*100:.1f}%
- QC & Sanitization Cost: ₹{all_params.get('qc_inspection_cost', 45):,.0f}
- Net 36-Month Accretion vs Baseline: ₹{economics_summary.get('delta_contribution_tradeback', 0.0):,.2f} / acquired customer
- Break-Even Net Recovery Required: ₹{economics_summary.get('min_recovery_required', 0.0):,.2f}
{f"- Specific Question from Founder: {custom_question}" if custom_question else ""}

======================================================================
3. YOUR EVALUATION MANDATE:
Deliver a razor-sharp, 3-part investment memo critique.
IMPORTANT: You MUST explicitly cite the authors, papers, and market studies provided in Section 1 to support your verdict.

Format your response strictly as follows:

### 1. Literature & Theoretical Verdict
(Explicitly cite specific papers from the shared context—e.g. Akerlof 1970 Lemons problem, Thaler 1985 Mental Accounting, Kahneman/Tversky 1990 Endowment Effect, Rubin 1974 Causal Model, or Guide & Van Wassenhove 2009. Explain precisely how the theory supports or invalidates the parameter value {current_value}).

### 2. Indian Market Ground Reality & Operational Friction
(Cross-examine the number against the provided Indian market empirical benchmarks—e.g. Bain/Flipkart order frequency, RedSeer reverse logistics costs ₹90-₹120, Delhivery doorstep QC limits, or Panipat weight-based textile salvage ₹15-₹30/kg).

### 3. Investment Verdict, Hidden Failure Mode & Pilot Test
- **Verdict:** [DEFENSIBLE or NOT DEFENSIBLE] with concise financial justification.
- **Hidden Failure Mode:** What specific operational disaster happens if this assumption is off by 20%?
- **Pilot Experimentation Protocol:** What exact A/B test or measurement protocol should the founders run in their 500-customer pilot to validate this number empirically?
"""

    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {
            "temperature": 0.4,
            "maxOutputTokens": 4096
        }
    }
    
    models_to_try = ["gemini-3.5-flash", "gemini-2.5-flash", "gemini-flash-latest"]
    last_err = ""
    for model_name in models_to_try:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent?key={api_key}"
        req = urllib.request.Request(
            url,
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"}
        )
        try:
            with urllib.request.urlopen(req, timeout=20) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                output_text = data["candidates"][0]["content"]["parts"][0]["text"]
                return f"**Model: `{model_name}`**\n\n" + output_text
        except Exception as e:
            last_err = f"{model_name}: {e}"
            continue
            
    return f"⚠️ Live Gemini call failed ({last_err}). Please check internet connection or API quota."

# --- CURATED LOCAL KNOWLEDGE BASE ---
ADVISOR_KNOWLEDGE_BASE: Dict[str, Dict[str, Any]] = {
    "tradeback_credit_pct": {
        "title": "TradeBack Credit %",
        "theory": "Mental Accounting (Richard Thaler) & Price Elasticity",
        "theory_detail": (
            "Customers perceive store credits as 'house money' rather than a price discount, "
            "reducing transaction friction. However, exceeding unit contribution boundaries converts "
            "the incentive into a severe margin drag on replacement orders."
        ),
        "india_benchmark": (
            "Indian D2C fast fashion operates at 48%–52% gross margin. At ₹1,300 AOV, a 25% credit (₹325) "
            "leaves only ₹325 to cover product COGS (₹650), forward shipping (₹70), and reverse swap (₹47), "
            "destroying unit economics."
        ),
        "check": lambda val, p: (
            ("🔴 Margin Destruction Alert: At {:.1f}%, credit exceeds the break-even ceiling (~22.7%). You are losing money on every TradeBack transaction!".format(val * 100))
            if val > 0.227
            else ("🟡 Borderline Corridor: {:.1f}% requires high B2B salvage (≥₹120) and +0.6 orders/yr uplift to avoid dilution.".format(val * 100))
            if val > 0.18
            else ("🟢 Healthy Economic Corridor: {:.1f}% leaves sufficient contribution margin on the replacement order.".format(val * 100))
        ),
        "investor_verdict": (
            "Cap credit at 15%–20% flat, or use a condition-tiered schedule (30% for Grade A down to 5% for Grade C) "
            "to protect gross margins."
        )
    },

    "credit_breakage_pct": {
        "title": "Credit Breakage Rate % (β)",
        "theory": "Breakage Subsidy vs. Deferred Revenue Accounting",
        "theory_detail": (
            "In traditional gift card programs, breakage (unredeemed balances) drops straight to 100% gross margin. "
            "However, applying breakage when credits are redeemed instantly at checkout creates phantom profits on paper."
        ),
        "india_benchmark": (
            "Because TradeBack credit is applied instantly during the new replacement purchase declaration, "
            "customers do not hold floating unspent wallet balances. Observed breakage in instant exchange flows is ~0%."
        ),
        "check": lambda val, p: (
            ("⚠️ Optimism Trap: Assuming {:.1f}% breakage when credits apply instantly at checkout inflates projected profits by counting discounts customers never actually forego!".format(val * 100))
            if val > 0.05
            else ("🟢 Realistic Accounting: {:.1f}% breakage enforces conservative, defensible financial discipline.".format(val * 100))
        ),
        "investor_verdict": (
            "Keep β at 0.0% when presenting to investors. Only model >0% if you issue a separate standalone voucher code with a strict 60-day expiry."
        )
    },

    "causal_frequency_uplift": {
        "title": "Causal Frequency Uplift (Δf orders/year)",
        "theory": "Causal Inference vs. Selection Bias (Rubin Causal Model)",
        "theory_detail": (
            "Highly engaged fashion shoppers naturally buy more frequently and are also the most likely to opt into TradeBack. "
            "The model must isolate true incremental orders caused strictly by the credit from natural repeat orders."
        ),
        "india_benchmark": (
            "Indian fashion e-commerce benchmarks (Urbanic, Myntra Insider, Nykaa Privé) show top-tier loyalty nudges "
            "typically expand annual repeat frequency by +0.3 to +0.6 orders/year over an 18-month horizon."
        ),
        "check": lambda val, p: (
            ("🔴 Unrealistic Behavioral Assumption: Expecting +{:.2f} extra orders/year from a buy-back program is unsupported by Indian D2C benchmarks (industry top-tier is +0.4 to +0.6).".format(val))
            if val > 0.80
            else ("🟢 Defensible Uplift: +{:.2f} orders/year is within reach for an active fashion brand with monthly collection drops.".format(val))
            if val >= 0.25
            else ("🟡 Minimal Nudge: +{:.2f} orders/year means TradeBack relies almost entirely on garment salvage cash to break even.".format(val))
        ),
        "investor_verdict": (
            "A/B test eligible customers vs. a control group in your 500-customer pilot to prove true causal uplift (Δf_causal) vs. selection bias."
        )
    },

    "b2b_gross_price": {
        "title": "B2B Jobber Price (₹)",
        "theory": "Secondary Market Liquidity & Coase Theorem",
        "theory_detail": (
            "Fast fashion depreciates rapidly. Offline B2B jobbers offer immediate, friction-free liquidity and bulk cash flow "
            "with zero platform take rates, zero return risk, and zero brand cannibalization."
        ),
        "india_benchmark": (
            "Textile hubs like Surat, Ludhiana, Tirupur, and Delhi Gandhi Nagar liquidate customer returns and surplus "
            "to Tier 2/3 discount retailers at ₹80–₹160 per garment in bulk 100-piece lots."
        ),
        "check": lambda val, p: (
            ("🔴 Aggressive Salvage Assumption: ₹{:.0f} exceeds standard bulk jobber liquidation rates for worn fast fashion (typical realization is ₹100–₹160).".format(val))
            if val > 180.0
            else ("🟢 Realistic Liquidation Rate: ₹{:.0f} matches wholesale lot clearance rates in Indian textile hubs.".format(val))
            if val >= 90.0
            else ("⚠️ Scrap Pricing: At ₹{:.0f}, salvage barely covers warehouse unboxing and sanitization costs.".format(val))
        ),
        "investor_verdict": (
            "B2B jobber sales are the safest baseline route because they eliminate brand cannibalization and avoid warehousing delay."
        )
    },

    "swap_failure_rate": {
        "title": "Doorstep Swap Failure Rate %",
        "theory": "Friction Cascade in Last-Mile Reverse Logistics",
        "theory_detail": (
            "Doorstep exchanges couple forward delivery with reverse pickup. When the exchange fails, it creates "
            "operational friction that cascades into standalone reverse pickups or complete Return to Origin (RTO)."
        ),
        "india_benchmark": (
            "Indian 3PL logistics carriers (Delhivery, Shadowfax, Xpressbees, Shiprocket) report 15%–25% failure on doorstep swaps "
            "due to customers not having the old garment ready, packaging issues, or courier delivery time pressures."
        ),
        "check": lambda val, p: (
            ("⚠️ Unrealistic Logistics Assumption: {:.1f}% failure rate is far below Indian 3PL reality (observed is 15%–22%). You will underestimate reverse shipping friction.".format(val * 100))
            if val < 0.10
            else ("🔴 Severe Operations Drag: {:.1f}% failure will cause heavy RTO freight burns and customer dissatisfaction.".format(val * 100))
            if val > 0.28
            else ("🟢 Grounded Logistics Metric: {:.1f}% reflects standard Indian courier doorstep handover friction.".format(val * 100))
        ),
        "investor_verdict": (
            "Prepare your warehouse team to handle failed doorstep handovers via scheduled standalone pickups rather than canceling the forward order."
        )
    },

    "d2c_cannibalization_rate": {
        "title": "D2C Cannibalization Rate (θ_cannibal)",
        "theory": "Product Line Cannibalization & Market Segmentation",
        "theory_detail": (
            "Selling refurbished garments on your own website or clearance portal can displace full-margin sales of new garments. "
            "Every cannibalized new garment destroys ~₹650 of gross margin in exchange for ~₹450 of resale revenue."
        ),
        "india_benchmark": (
            "Fashion brands with secondary clearance portals (e.g. FabIndia outlet, Myntra refurbished) observe 15%–30% "
            "demand overlap between clearance shoppers and primary full-price shoppers."
        ),
        "check": lambda val, p: (
            ("⚠️ Underestimating Cannibalization: Assuming {:.1f}% overlap ignores the fact that brand loyalists love discounted refurbished stock.".format(val * 100))
            if val < 0.10 and p.get("d2c_route_prob", 0) > 0.15
            else ("🔴 Margin Destruction Zone: {:.1f}% cannibalization erodes new garment sales faster than refurbished recovery can compensate.".format(val * 100))
            if val > 0.35
            else ("🟢 Prudent Cannibalization Factor: {:.1f}% appropriately penalizes online resale for demand substitution.".format(val * 100))
        ),
        "investor_verdict": (
            "If cannibalization exceeds 20%, offload garments to offline B2B jobbers rather than reselling online under your primary brand name."
        )
    },

    "aov": {
        "title": "Average Order Value (AOV)",
        "theory": "Unit Contribution Absorption & Shipping Cost Amortization",
        "theory_detail": (
            "Fixed operational costs (₹70 forward shipping, ₹47 reverse swap, ₹45 QC) are largely invariant to order price. "
            "Higher AOVs absorb logistics friction much more effectively."
        ),
        "india_benchmark": (
            "Indian fast-fashion mid-market brands (Urbanic, Snitch, Westside, Zara online) maintain basket sizes between ₹1,200 and ₹1,800. "
            "Budget D2C (e.g. Meesho, Bewakoof) operates at ₹400–₹800, where TradeBack logistics would completely fail."
        ),
        "check": lambda val, p: (
            ("🔴 Logistics Deficit Risk: At ₹{:.0f} AOV, reverse shipping and QC eat up almost the entire gross margin. TradeBack is untenable at low price points!".format(val))
            if val < 950.0
            else ("🟢 Strong Logistics Absorption: ₹{:.0f} AOV provides sufficient gross margin buffer (₹{:.0f} @ GM%) to absorb reverse freight.".format(val, val * p.get("gross_margin_pct", 0.5)))
        ),
        "investor_verdict": (
            "TradeBack requires an AOV of at least ₹1,100–₹1,300. Do not launch buy-back on sub-₹800 entry-level fashion SKUs."
        )
    },

    "gross_margin_pct": {
        "title": "Gross Margin %",
        "theory": "Contribution Velocity & Operating Leverage",
        "theory_detail": (
            "Gross margin determines how much gross profit is generated per extra order created by TradeBack. "
            "Higher margins drastically lower the required break-even purchase frequency."
        ),
        "india_benchmark": (
            "Apparel manufacturing in India (Tirupur, Surat, Noida) allows fast-fashion brands to achieve 50%–60% gross margin "
            "when sourcing directly from contract manufacturers, vs 35%–42% for multi-brand aggregators."
        ),
        "check": lambda val, p: (
            ("🔴 Tight Margin Squeeze: At {:.1f}%, you have zero tolerance for reverse logistics glitches or TradeBack credit costs.".format(val * 100))
            if val < 0.42
            else ("🟢 Venture-Grade D2C Margin: {:.1f}% provides the unit economics needed to fund customer retention programs.".format(val * 100))
        ),
        "investor_verdict": (
            "Aim for ≥50% gross margin through direct contract manufacturing before rolling out TradeBack credits."
        )
    },

    "cac": {
        "title": "Customer Acquisition Cost (CAC)",
        "theory": "Customer Lifetime Value (LTV) to CAC Ratio",
        "theory_detail": (
            "CAC is the sunk upfront expense on Day 1. TradeBack's goal is to increase 36-month LTV so the initial acquisition "
            "investment yields a venture-grade 4x+ return."
        ),
        "india_benchmark": (
            "Meta ad costs (CPM/CPC) in India have escalated 25% YoY. Blended fashion CAC for first-time buyers ranges from ₹300 to ₹600. "
            "Re-acquisition via paid retargeting costs ₹120–₹180 per order."
        ),
        "check": lambda val, p: (
            ("⚠️ Elevated Acquisition Cost: ₹{:.0f} CAC puts pressure on payback period. TradeBack must accelerate order #2 and #3 into months 4–8 to recover cash.".format(val))
            if val > 550.0
            else ("🟢 Healthy Acquisition Cost: ₹{:.0f} CAC enables quick cohort payback within 2–3 purchases.".format(val))
        ),
        "investor_verdict": (
            "TradeBack's biggest value proposition is turning expensive first-time acquisitions into long-term repeat buyers without relying on paid Meta retargeting."
        )
    },

    "tradeback_adoption_rate": {
        "title": "TradeBack Adoption Rate % (α)",
        "theory": "Diffusion of Innovation & Customer Friction",
        "theory_detail": (
            "The share of eligible customers who actually pack and hand over an old garment during a new purchase. "
            "If adoption is too low, the reverse supply chain suffers from diseconomies of scale."
        ),
        "india_benchmark": (
            "In e-commerce exchange programs (e.g. mobile/laptop exchange on Amazon/Flipkart), adoption ranges from 25% to 45%. "
            "Fashion buy-back pilots in Europe (Zalando Pre-owned) saw 30%–45% adoption among repeat buyers."
        ),
        "check": lambda val, p: (
            ("⚠️ High Friction Risk: Expecting {:.1f}% of fashion shoppers to consistently store and return garments is aggressive for an unproven pilot.".format(val * 100))
            if val > 0.60
            else ("🟢 Realistic Adoption Target: {:.1f}% matches consumer electronics and fashion exchange benchmark ranges.".format(val * 100))
            if val >= 0.25
            else ("🟡 Low Participation: At {:.1f}%, TradeBack is a niche feature with negligible impact on overall cohort LTV.".format(val * 100))
        ),
        "investor_verdict": (
            "Validate true customer willingness to store clothes for 4 months in your initial 500-customer concierge pilot."
        )
    },

    "stranded_garments_terminal": {
        "title": "Terminal Stranded Garments (N_stranded)",
        "theory": "Lifecycle Truncation & Closet Lock-in",
        "theory_detail": (
            "When a customer leaves the brand (churns), the last garment(s) bought remain in their closet forever. "
            "They will never be returned or salvaged."
        ),
        "india_benchmark": (
            "In non-contractual retail, customers do not announce when they churn. The terminal purchase remains in their wardrobe. "
            "Modeling N_stranded=1.0 reflects the reality that the final garment bought is never exchanged."
        ),
        "check": lambda val, p: (
            ("⚠️ Underestimating Stranded Inventory: Setting this to 0 assumes customers never churn with a garment in their closet, artificially inflating salvage cash.".format())
            if val == 0.0
            else ("🟢 Realistic Churn Truncation: {:.1f} stranded garments correctly accounts for customer churn dynamics while recognizing 100% full margin on terminal orders.".format(val))
        ),
        "investor_verdict": (
            "Stranded garments are actually profitable for the company because the customer paid full price and never redeemed credit against it!"
        )
    },

    "qc_inspection_cost": {
        "title": "QC, Sanitization & Sorting Cost (₹)",
        "theory": "Operational Bottleneck & Reverse Processing Burden",
        "theory_detail": (
            "Returned garments must be opened, inspected for tears/stains, steam-sanitized, barcode-graded, and re-bagged. "
            "Warehouse labor and sorting overhead add up quickly."
        ),
        "india_benchmark": (
            "Third-party reverse logistics hubs in Bhiwandi, Manesar, and Bangalore charge ₹35–₹60 per apparel unit for unboxing, "
            "grading, sanitization, and polybagging."
        ),
        "check": lambda val, p: (
            ("🔴 Excessive Warehouse Cost: ₹{:.0f} QC cost severely erodes net salvage recovery (our break-even tolerance is ₹80.50).".format(val))
            if val > 75.0
            else ("🟢 Efficient Processing Cost: ₹{:.0f} matches standard Indian 3PL apparel reverse inspection contracts.".format(val))
        ),
        "investor_verdict": (
            "Keep QC automated and simple: binary grading (Grade A = Clean/Like-New vs Grade B = Jobber Liquidation) to minimize warehouse labor."
        )
    },

    "inventory_holding_days": {
        "title": "Inventory Holding Delay (t_hold)",
        "theory": "Working Capital Drag & Trend Obsolescence",
        "theory_detail": (
            "Fast-fashion styles lose value as fashion trends change. Holding inventory in warehouse racks ties up working capital "
            "and forces steeper secondary discounts."
        ),
        "india_benchmark": (
            "B2B jobber bulk lots can be sold every 30–45 days. Online clearance portals take 60–90 days to liquidate long-tail SKU sizes."
        ),
        "check": lambda val, p: (
            ("⚠️ High Inventory Drag: Holding garments for {:.0f} days causes significant trend obsolescence and working capital lockup.".format(val))
            if val > 60.0
            else ("🟢 Fast Liquidation Velocity: {:.0f} days keeps warehouse footprint small and minimizes trend depreciation.".format(val))
        ),
        "investor_verdict": (
            "Liquidate returned garments in bi-weekly B2B jobber auctions to keep holding delay under 30 days."
        )
    },
}

def get_parameter_advice(param_key: str, current_value: float, all_params: Dict[str, float]) -> Dict[str, str]:
    """
    Returns the economic theory, market benchmark, sanity check status, and advice for any parameter.
    """
    if param_key in ADVISOR_KNOWLEDGE_BASE:
        info = ADVISOR_KNOWLEDGE_BASE[param_key]
        status = info["check"](current_value, all_params)
        return {
            "title": info["title"],
            "theory": info["theory"],
            "theory_detail": info["theory_detail"],
            "india_benchmark": info["india_benchmark"],
            "status_message": status,
            "investor_verdict": info["investor_verdict"]
        }
    else:
        return {
            "title": param_key.replace("_", " ").title(),
            "theory": "Unit Economics & Cash Flow Mechanics",
            "theory_detail": "Direct input into 36-month customer contribution and operational friction.",
            "india_benchmark": "Calibrated against Indian D2C fast-fashion supply chain benchmarks.",
            "status_message": "🟢 Parameter active in deterministic calculations.",
            "investor_verdict": "Test sensitivity in Tier 1 tornado analysis to measure bottom-line impact."
        }
