# Architectural Decision Records (ADR) & Design Log

This log chronicles every major structural and accounting design choice in the TradeBack model, tracking the rationale, review origin, and implementation details.

---

### ADR-001: Strict Zero Credit Breakage (β = 0%)
* **Status:** Adopted
* **Context / Challenge:** Traditional retail gift card or loyalty point models assume 10%–20% of issued credits expire unredeemed ("breakage"), dropping straight to gross margin.
* **Original Consideration:** The initial proposal included an assumed breakage rate of 10%.
* **Critique & Decision:** In TradeBack, credit is selected and applied **instantly at the checkout screen of the replacement order** during the exchange declaration. Customers do not hold unredeemed vouchers; the credit is granted simultaneously with the purchase intent.
* **Implementation:** `credit_breakage_pct` is set strictly to `0.0%`. Prevents artificial margin inflation.

---

### ADR-002: Stranded Garment Ceiling (N_returns Truncation)
* **Status:** Adopted
* **Context / Challenge:** Naive models assume `N_returns ≈ N_orders - 1` or that every repeat order returns an old garment.
* **Critique & Decision:** 
  1. Order 1 is an initial purchase (zero garments in wardrobe to return).
  2. Repeat orders occurring under the minimum holding window (e.g. < 3 months) are ineligible.
  3. The final order(s) placed before a customer churns permanently strand garments in the customer's closet, because no future order is ever placed to return them.
* **Implementation:** `N_returns = max(0, N_total - 1 - N_stranded)`, where `N_stranded >= 1`. Terminal orders earn full, un-discounted gross margin, while expected salvage cash is reduced realistically.

---

### ADR-003: Reverse Logistics Failure & RTO Penalty Cascade
* **Status:** Adopted
* **Context / Challenge:** Assuming doorstep exchanges cost only ₹30–₹35 flat severely underestimates real-world reverse logistics friction in India.
* **Critique & Decision:** Indian 3PLs experience 15%–20% doorstep swap failure rates (customer not home, wrong item, package unsealed). When a swap fails, either:
  1. A standalone reverse courier pickup must be booked (+₹65).
  2. The delivery agent refuses handover and returns the *new* forward parcel to origin (RTO), burning both forward (₹70) and reverse (₹60) freight while locking up fresh inventory.
* **Implementation:**
  ```
  C_collection_blended = C_swap + P_fail * [ C_standalone_reverse + P_RTO * (C_forward + C_RTO_freight) ]
  ```
  Increases effective collection cost from ₹35 to ~₹46.70–₹65.00 per return.

---

### ADR-004: Partitioned Cohort Lifetime Contribution
* **Status:** Adopted
* **Context / Challenge:** Multiplying adoption rate across terms already aggregated at the cohort level creates risks of double-counting or misallocating adoption.
* **Critique & Decision:** Split the cohort into two mutually exclusive tracks:
  ```
  Cohort_LTC = α * LTC_adopter + (1 - α) * LTC_baseline
  ```
* **Implementation:** Adopter unit economics are computed cleanly first, then blended with non-adopters. This makes the analytical break-even solver strictly linear with respect to `α`.

---

### ADR-005: Inclusion of Benchmark System C (Promo / Ad Spend Alternative)
* **Status:** Adopted
* **Context / Challenge:** Evaluating TradeBack only against "doing nothing" (System A) ignores the fact that management can spend the same incentive budget on standard D2C marketing tactics.
* **Critique & Decision:** TradeBack must justify its operational complexity (reverse logistics, inspection, inventory aging) against a simpler marketing alternative: offering an instant ₹200 discount coupon or spending ₹150 on Meta retargeting ads.
* **Implementation:** Tier 0 evaluates System A (Baseline), System B (TradeBack), and System C (Promo/Coupon) side-by-side.

---

### ADR-006: Secondary Channel Liquidity & B2B Jobbers Default
* **Status:** Adopted
* **Context / Challenge:** Fast fashion at ₹1,300 AOV lacks a liquid online peer-to-peer (P2P) resale market in India. High platform fees and reverse logistics wipe out resale margins.
* **Critique & Decision:** The baseline secondary route must be B2B liquidation lots to offline jobbers/discount stores in Tier 2/3 cities (recovering ₹100–₹180 flat), with online D2C resale treated as an optional secondary route with associated cannibalization penalties.
* **Implementation:** Default secondary allocation: 60% B2B Jobbers, 20% D2C Clearance, 10% Upcycle, 5% Recycling, 5% Write-off.

---

### ADR-007: Phased Architecture (Tier 0 & Tier 1 First)
* **Status:** Adopted
* **Context / Challenge:** Building a complex 100,000-agent Monte Carlo simulator first risks hiding accounting errors and bad unit economics inside stochastic noise.
* **Critique & Decision:** Build a transparent, deterministic closed-form engine (Tier 0) and analytical break-even surface solver (Tier 1) first. Prove the mathematical logic in plain daylight before layering on discrete-hazard Monte Carlo simulation in Phase 2.
* **Implementation:** Phase 1 delivers pure mathematical Python modules and a formulaic linked Excel model.
