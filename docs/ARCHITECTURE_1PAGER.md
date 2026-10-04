# TradeBack Economics & Customer Lifecycle Model: 1-Pager Architecture (Phase 1)

**Project:** TradeBack Economics & Customer Lifecycle Model  
**Version:** Phase 1 (Deterministic Core & Analytical Break-Even Solver)  
**Target Market:** AI-Native Fast Fashion D2C in India  

---

## 1. Executive Concept & Problem Statement

TradeBack is a proposed closed-loop customer-retention mechanism:
* Customer purchases a garment (AOV ₹1,300).
* Within an eligible holding window (e.g. 3–6 months), the customer places a new replacement order and returns the old garment.
* Customer receives instant store credit at checkout (e.g., 20% = ₹260).
* The old garment is recovered via doorstep swap/reverse pickup and liquidated (primarily via B2B offline jobbers in India).
* **Core Objective:** Build a quantitative model to identify under what exact economic conditions TradeBack is accretive vs. a conventional D2C model and alternative promotional benchmarks (e.g., standard discount coupons or ad re-targeting).

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
│           TIER 0: PARTITIONED COHORT LIFECYCLE ENGINE            │
│                                                                  │
│ ┌───────────────────────────┐   ┌──────────────────────────────┐ │
│ │ Cohort A: Baseline        │   │ Cohort B: TradeBack Model    │ │
│ │ - Standard Repeat Orders  │   │ - Partitioned Lifecycle      │ │
│ │ - Full Repeat Ad CAC      │   │ - Instant Credit (β = 0%)    │ │
│ │ - Normal Fulfillment      │   │ - Stranded Ceiling Truncation│ │
│ │ - 100% Margin             │   │ - Blended Reverse Logistics  │ │
│ └─────────────┬─────────────┘   └──────────────┬───────────────┘ │
│               │                                │                 │
│               └────────────────┬───────────────┘                 │
│                                ▼                                 │
│              ΔContribution = Cohort_B - Cohort_A                 │
│              (Benchmarked vs System C: ₹200 Promo)               │
└────────────────────────────────┬─────────────────────────────────┘
                                 │
                                 ▼
┌──────────────────────────────────────────────────────────────────┐
│           TIER 1: ANALYTICAL BREAK-EVEN & SENSITIVITY            │
│ 1. 2D Isocline Solver: ΔContribution(Δf_causal, E[R_net]) = 0    │
│ 2. 5 Deal-Breaker Thresholds (Min Recovery, Uplift, Credit, etc) │
│ 3. 12-Variable Global Tornado Sensitivity Analysis               │
└────────────────────────────────┬─────────────────────────────────┘
                                 │
                                 ▼
┌──────────────────────────────────────────────────────────────────┐
│                  DELIVERABLES & USER INTERFACES                  │
│ 1. Python Package (`src/`)       3. Streamlit App (`src/app.py`) │
│ 2. Excel Model (`.xlsx`)         4. Executive Memo (`outputs/`)  │
└──────────────────────────────────────────────────────────────────┘
```

---

## 3. Core Accounting Identities & Formulations

### A. Blended Reverse Logistics & RTO Penalty Cascade
Indian 3PL doorstep exchanges fail 15%–20% of the time, triggering either a separate reverse courier or an RTO of the forward parcel:

```
C_collection_blended = C_swap + P_fail * [ C_standalone_reverse + P_RTO * (C_forward + C_RTO_freight) ]
```

* **Base Doorstep Swap Cost (`C_swap`):** ₹35
* **Swap Failure Rate (`P_fail`):** 15%
* **Standalone Reverse Courier (`C_standalone_reverse`):** ₹65
* **RTO Rate (`P_RTO`):** 10%
* **Wasted Freight (`C_forward + C_RTO_freight`):** ₹70 + ₹60 = ₹130
* **Resulting Blended Collection Cost:** **~₹46.70 / return**

---

### B. Expected Net Garment Salvage Recovery (`E[R_net]`)

```
E[R_net] = SUM_k [ P_k * ( V_gross_k * (1 - d_trend)^(t_hold / 30) - C_route_k ) ] 
           - C_collection_blended - C_QC - Tax_GST
```

* **Default Secondary Routes (`k`):**
  * B2B Offline Jobbers: 60% probability @ ₹150 gross price
  * D2C Clearance Portal: 20% probability @ ₹450 gross price
  * Upcycle / Redesign: 10% probability @ ₹120 gross price
  * Industrial Rag Recycling: 5% probability @ ₹15 gross price
  * Unsalvageable Write-off: 5% probability @ ₹0
* **Holding Delay (`t_hold`):** 45 days
* **Trend Depreciation (`d_trend`):** 5% per 30 days
* **QC & Sanitization (`C_QC`):** ₹45
* **Resulting Net Salvage Recovery:** **~₹72.50 / returned garment**

---

### C. Stranded Garment Ceiling (`N_returns` Truncation)
For an adopter placing `N_total` orders over 36 months:

```
N_eligible_repeats = max(0, N_total - 1)
N_returns          = max(0, N_total - 1 - N_stranded)
```

* **Order 1:** Initial purchase (no prior garment in wardrobe).
* **Terminal Orders:** The final garment(s) bought before a customer churns (`N_stranded >= 1`) remain stranded in their closet forever.
* **Economic Reality:** Terminal orders earn **100% full gross margin with ₹0 credit discount**.

---

### D. Partitioned Cohort Economics (Zero Breakage `β = 0%`)

#### 1. Adopter Lifetime Contribution (`LTC_adopter`)
```
LTC_adopter = - CAC
              + N_total_adopter * (AOV * GM - C_fulfill)
              + N_returns * E[R_net]
              + N_returns * (M_base * S_ad)
              - N_returns * (AOV * Credit_pct)
              - N_returns * P_D2C * Cannibal_rate * (AOV * GM)
              - (N_eligible_repeats - N_returns) * M_base
```

#### 2. Non-Adopter Baseline Lifetime Contribution (`LTC_baseline`)
```
LTC_baseline = - CAC
               + N_total_base * (AOV * GM - C_fulfill)
               - (N_total_base - 1) * M_base
```

#### 3. Cohort Blended Contribution
```
Cohort_LTC = α * LTC_adopter + (1 - α) * LTC_baseline
```

#### 4. Net TradeBack Accretion per Acquired Customer
```
ΔContribution = Cohort_LTC - LTC_baseline = α * (LTC_adopter - LTC_baseline)
```

---

## 4. Benchmark System C: Promotional Coupon Alternative

To ensure TradeBack is evaluated against standard D2C marketing alternatives, we model **System C**:
* The customer receives a flat ₹200 instant discount voucher (or equivalent Meta retargeting incentive) on repeat orders.
* Reverse logistics, QC, and garment recovery are zero.
* Enables answering: *"Does spending ₹260 on TradeBack generate more contribution than offering a ₹200 discount coupon?"*
