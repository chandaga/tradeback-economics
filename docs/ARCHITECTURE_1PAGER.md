# TradeBack Economics & Customer Lifecycle Model: 1-Pager Architecture (Phase 1)

**Project:** TradeBack Economics & Customer Lifecycle Model  
**Version:** Phase 1 (Deterministic Core & Analytical Break-Even Solver)  
**Target Market:** AI-Native Fast Fashion D2C in India  

---

## 1. Executive Concept & Problem Statement

TradeBack is a closed-loop customer-retention mechanism:
* Customer purchases a garment (AOV ₹1,300, 50% gross margin).
* Within an eligible holding window (e.g. 3–6 months), the customer places a new replacement order and returns the old garment.
* Customer receives instant store credit applied directly at checkout (e.g., 20% = ₹260).
* The old garment is recovered via doorstep swap / reverse pickup and liquidated across a 5-route secondary market tree.
* **Core Objective:** Build an audit-proof quantitative model to evaluate under what exact conditions TradeBack is accretive vs. a conventional D2C baseline (System A) and alternative promotional benchmarks such as instant discount coupons (System C).

---

## 2. System Flow Diagram

```
┌──────────────────────────────────────────────────────────────────┐
│                 INPUT REGISTRY (5-TIER TAXONOMY)                 │
│ [Observed] [External Benchmark] [Management] [Model] [Unknown]  │
└────────────────────────────────┬─────────────────────────────────┘
                                 │
                                 ▼
┌──────────────────────────────────────────────────────────────────┐
│             TIER 0: CANONICAL 2-LEVER LIFECYCLE ENGINE           │
│                                                                  │
│  Lever 1: Incremental Volume Margin (ΔN_orders * CM_order)       │
│  Lever 2: Net Unit Circular Balance                              │
│           (N_TB * [E[R_net_ops] + E[CAC_avoided] - C_TB])        │
│                                                                  │
│  ΔLTC_adopter = Lever 1 + Lever 2                                │
│  ΔLTC_cohort  = α * ΔLTC_adopter                                 │
│  (Benchmarked vs System C: ₹200 Promo Coupon Discount)           │
└────────────────────────────────┬─────────────────────────────────┘
                                 │
                                 ▼
┌──────────────────────────────────────────────────────────────────┐
│           TIER 1: ANALYTICAL BREAK-EVEN & SENSITIVITY            │
│ 1. 2D Isocline Solver: ΔContribution(Δf, E[R_net_ops]) = 0       │
│ 2. 5 Deal-Breaker Boundary Thresholds (Investor Pitch Metrics)   │
│ 3. 12-Variable Global Tornado Sensitivity Analysis               │
└────────────────────────────────┬─────────────────────────────────┘
                                 │
                                 ▼
┌──────────────────────────────────────────────────────────────────┐
│                  DELIVERABLES & USER INTERFACES                  │
│ 1. Python Package (`src/`)       3. Streamlit App (`src/app.py`) │
│ 2. Test Suite (`tests/`)         4. Executive Memo (`outputs/`)  │
└──────────────────────────────────────────────────────────────────┘
```

---

## 3. Core Accounting Identities & Formulations

### A. Blended Reverse Logistics & RTO Penalty Cascade
Indian 3PL doorstep exchanges fail 15% of the time, triggering standalone couriers or forward parcel RTO freight penalties:

$$C_{\text{collection}} = C_{\text{swap}} + P_{\text{fail}} \times \left[ C_{\text{rev}} + P_{\text{RTO}} \times (C_{\text{forward}} + C_{\text{RTO-freight}}) \right]$$

* **Base Doorstep Swap Cost (`C_swap`):** ₹35
* **Swap Failure Rate (`P_fail`):** 15%
* **Standalone Reverse Courier (`C_rev`):** ₹65
* **RTO Rate (`P_RTO`):** 10%
* **Wasted Freight (`C_forward + C_RTO-freight`):** ₹70 + ₹60 = ₹130
* **Resulting Blended Collection Cost:** **₹46.70 / return**

---

### B. Audit-Proof 5-Route Secondary Recovery Tree ($E[R_{\text{net-ops}}]$)

$$E[R_{\text{net-ops}}] = \sum_{k} P_k \times \left( V_k \times (1 - d_{\text{trend}})^{\frac{t_{\text{hold}}}{30}} - C_{\text{route-}k} \right) - C_{\text{collection}} - C_{\text{QC}}$$

* **Route 1 (B2B Jobbers):** 60% @ ₹150, -7.4% 45d trend decay, ₹10 handling cost $\rightarrow$ Net ₹128.90 $\rightarrow$ **₹77.34 weighted**
* **Route 2 (D2C Resale Portal):** 20% @ ₹450, -7.4% 45d trend decay, ₹80 clean/shoot $\rightarrow$ Net ₹336.70 $\rightarrow$ **₹67.34 weighted**
* **Route 3 (Upcycling / Rework):** 10% @ ₹160, 0% decay, ₹30 rework cost $\rightarrow$ Net ₹130.00 $\rightarrow$ **₹13.00 weighted**
* **Route 4 (Industrial Scrap):** 5% @ ₹35, 0% decay, ₹5 route cost $\rightarrow$ Net ₹30.00 $\rightarrow$ **₹1.50 weighted**
* **Route 5 (Loss / Write-off):** 5% @ ₹0, ₹10 disposal cost $\rightarrow$ Net -₹10.00 $\rightarrow$ **-₹0.50 weighted**
* **Gross Realized Weighted Salvage $E[V_{\text{salv}}]$:** **₹158.68**
* **Less: Blended Collection Friction:** **-₹46.70**
* **Less: Intake QC & Steaming ($C_{\text{QC}}$):** **-₹45.00**
* **True Realized Net Salvage $E[R_{\text{net-ops}}]$ (Pre-tax):** **₹66.98 / return**

---

### C. Order Truncation & Return Utilization ($u = 75\%$)
Disentangles customer-level enrollment ($\alpha = 40\%$) from order-level swap compliance ($u = 75\%$):

$$N_{\text{eligible repeat}} = \max\left(0, \; N_{\text{adopter}} - 1 - N_{\text{stranded}}\right) = 4.50 - 1 - 1 = \mathbf{2.50 \text{ orders}}$$
$$N_{\text{TB}} = N_{\text{eligible repeat}} \times u = 2.50 \times 0.75 = \mathbf{1.875 \text{ actual returns per adopter}}$$

* **Order 1:** Initial customer acquisition purchase (cannot swap).
* **Terminal Garment ($N_{\text{stranded}} = 1.0$):** Retained in wardrobe upon churn (earns full margin with ₹0 credit discount).

---

### D. The Canonical 2-Lever Master Equation

$$\Delta \text{LTC}_{\text{adopter}} = \underbrace{\Delta N_{\text{orders}} \times \text{CM}_{\text{order}}}_{\text{1. Incremental Volume Margin}} + \underbrace{N_{\text{TB}} \times \Big( E[R_{\text{net-ops}}] + E[\text{CAC}_{\text{avoided}}] - C_{\text{TB}} \Big)}_{\text{2. Net Unit Circular Balance}}$$

* **Lever 1 (Volume Expansion):** $+0.75 \text{ orders} \times ₹580.00 \text{ CM} = \mathbf{+₹435.00}$
* **Lever 2 (Net Unit Circular Balance):** $1.875 \text{ returns} \times (₹66.98 + ₹45.00 - ₹260.00) = 1.875 \times (-₹148.02) = \mathbf{-₹277.54}$
* **Incremental Adopter LTC ($\Delta \text{LTC}_{\text{adopter}}$):** $+435.00 - 277.54 = \mathbf{+₹157.46}$
* **Blended Cohort Net Accretion ($\alpha = 40\%$):** $0.40 \times +157.46 = \mathbf{+₹62.98 \text{ / acquired customer}}$

---

## 4. Benchmark System C: Promotional Coupon Alternative

Evaluates an instant ₹200 discount voucher on repeat purchases without reverse supply chain operations:

$$\Delta \text{LTC}_{\text{promo-adopter}} = (\Delta N_{\text{orders}} \times \text{CM}_{\text{order}}) - (N_{\text{repeats}} \times \text{Discount}_{\text{coupon}}) + (N_{\text{repeats}} \times E[\text{CAC}_{\text{avoided}}])$$
$$\Delta \text{LTC}_{\text{promo-adopter}} = 435.00 - (3.50 \times 200) + (3.50 \times 45) = 435.00 - 700.00 + 157.50 = \mathbf{-₹107.50}$$
$$\text{Cohort Dilution}_{\text{promo}} = 0.40 \times (-107.50) = \mathbf{-₹43.00 \text{ / acquired customer}}$$

**TradeBack Strategic Superiority over Promo Coupon:**
$$\Delta \text{LTC}_{\text{cohort, TradeBack}} - \Delta \text{LTC}_{\text{cohort, Promo}} = +62.98 - (-43.00) = \mathbf{+₹105.98 \text{ / acquired customer}}$$
