# Executive Investment Memo: TradeBack Economics & Unit Feasibility

**To:** Investment Committee & Founding Team  
**Subject:** Phase 1 Quantitative Model Findings: What Has to Be True for TradeBack to Succeed  
**Date:** October 2026  
**Status:** Phase 1 Complete (Deterministic Closed-Form Engine)  

---

## 1. Executive Summary

We developed a 36-month customer lifecycle unit economics model for an AI-native fast-fashion D2C brand in India exploring **TradeBack**—a closed-loop program allowing customers to return 3–6 month-old garments for store credit (10%–30%) when placing a new order.

Rather than assuming TradeBack increases LTV, the model stress-tests the concept against two baselines:
1. **System A (Conventional D2C):** Standard marketing reacquisition and organic repeat buying.
2. **System C (Promotional Benchmark):** A standard ₹200 discount coupon or retargeting ad campaign with zero reverse supply chain complexity.

### The Bottom-Line Finding
Under realistic Indian market assumptions (AOV ₹1,300, 50% gross margin, ₹400 CAC, 2.5 baseline orders/year, B2B offline jobber liquidation):
* **TradeBack is moderately accretive:** **+₹35.50 / acquired customer** over conventional D2C.
* **TradeBack outperforms promo discounting:** **+₹18.50 / customer** over a flat ₹200 repeat discount coupon.

However, profitability is governed by a **tight economic corridor**. The business cannot afford loose policy rules or operational inefficiencies.

---

## 2. The 5 Deal-Breaker Thresholds (Investor Pitch Boundaries)

Our Tier 1 analytical solver identified the 5 exact boundary conditions required for TradeBack to remain profitable:

| Threshold Metric | Boundary Value | Current Base Position | Strategic Meaning |
| :--- | :---: | :---: | :--- |
| **1. Minimum Net Recovery (if Δf = 0)** | **₹182.26 / return** | ₹72.50 / return | If TradeBack fails to change customer buying behavior, garment salvage alone *cannot* cover the credit and reverse freight. It requires behavioral uplift. |
| **2. Minimum Causal Frequency Uplift (if E[R] = ₹0)** | **+0.66 orders/year** | +0.50 orders/year | If returned garments are completely unsalvageable (0% resale value), TradeBack must increase annual purchases from 2.5 to 3.16 to break even. |
| **3. Maximum Affordable Credit %** | **22.7% of AOV** | 20.0% (₹260) | **A hard ceiling.** Offering a 25% or 30% credit destroys unit economics and makes TradeBack value-destructive. |
| **4. Maximum Tolerable QC & Processing Cost** | **₹80.49 / garment** | ₹45.00 / garment | Sorting, unboxing, sanitizing, and grading must stay strictly below ₹80. |
| **5. TradeBack Superiority Threshold vs. Coupon** | **Net Recovery ≥ ₹45** | ₹72.50 / return | If net garment recovery falls below ₹45, offering a simple ₹200 discount coupon is strictly more profitable than running reverse logistics. |

---

## 3. Global Sensitivity Ranking: What Actually Matters

Our 12-variable Tornado Analysis ranks the factors by their impact on 3-year bottom line:

1. **TradeBack Credit % (₹325 swing):** The single most sensitive operational lever. A 5% increase in credit reduces cohort profit by more than any logistics failure.
2. **Causal Frequency Uplift Δf (₹303 swing):** The engine of accretion. High garment salvage cannot rescue a program that fails to generate incremental repeat orders.
3. **Baseline Order Frequency (₹140 swing):** Higher baseline purchase frequency provides more natural opportunities for customers to be inside the 3–6 month eligibility window.
4. **Repeat Marketing Ad Savings (₹100 swing):** TradeBack must act as the primary re-engagement trigger, replacing expensive Meta/Google retargeting ads.
5. **Operational Logistics Friction (₹20 swing):** Doorstep swap courier failures (15% failure rate and RTO penalties) create drag (~₹12/return), but do not break the business thesis.

---

## 4. Key Accounting Guardrails Implemented

The model enforces 4 critical real-world accounting corrections:

* **Zero Credit Breakage (β = 0%):** Because TradeBack credit is applied instantly at replacement checkout, no phantom breakage is counted.
* **Stranded Garment Ceiling Truncation:** Order 1 has no return, and terminal orders before churn remain stranded in customer wardrobes. Returns are capped at `N_returns = max(0, N_total - 1 - N_stranded)` (2.5 returns over 18 months rather than 3.5), while terminal orders earn 100% full margin.
* **Realistic B2B Liquidation:** Defaults to bulk offline jobber lots in Tier 2/3 Indian markets (₹150 gross salvage) rather than assuming optimistic consumer P2P resale.
* **Cannibalization Penalty:** Online refurbished clearance sales are penalized for displacing full-price new garment demand.

---

## 5. The Pilot Experimentation Protocol (What to Validate Before Scaling)

Before investing in automated reverse logistics software or warehouse refurbishment lines, the founders should execute a **concierge pilot with 500 customers** to validate 4 specific assumptions:

1. **Test 1: True Adoption Rate (α)**
   * *Target:* ≥ 35%.
   * *Method:* Offer TradeBack via WhatsApp to 500 customers who bought 4 months ago. Measure how many initiate a replacement order.
2. **Test 2: Actual Return Condition & Jobber Liquidation (V_gross)**
   * *Target:* Average B2B liquidation realization ≥ ₹140 / garment.
   * *Method:* Manually inspect 200 returned garments and sell them to local liquidation jobbers in Delhi/Surat/Tirupur.
3. **Test 3: Doorstep Swap Success Rate (1 - P_fail)**
   * *Target:* ≥ 80% first-attempt handover success.
   * *Method:* Measure courier partner handover friction on 200 replacement deliveries.
4. **Test 4: Causal Incrementality vs. Control**
   * *Target:* +0.35 to +0.50 incremental orders/year.
   * *Method:* A/B test 500 eligible customers offered TradeBack vs. 500 control customers offered standard new collection marketing.

---

## 6. Conclusion & Recommendation

TradeBack is **economically viable in India**, provided:
1. Credit is strictly capped at **15%–20%**.
2. Garments are routed primarily to **B2B liquidation jobbers** to minimize holding time, avoid new-garment cannibalization, and eliminate listing costs.
3. The program is treated as a **direct replacement for paid Meta retargeting ads**, rather than an additional marketing cost.

*The model artifacts (`tradeback_model_phase1.xlsx` and `src/app.py`) are fully generated and available for investor review.*
