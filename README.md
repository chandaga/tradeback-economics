# TradeBack Economics & Customer Lifecycle Model

A quantitative unit economics, customer lifecycle, and break-even framework for an AI-native fast fashion D2C brand in India exploring a **TradeBack** circular retention mechanism.

---

## Project Purpose

Rather than using synthetic simulations to "prove" the business, this model evaluates **under what exact economic conditions TradeBack is accretive vs. a conventional D2C model and alternative marketing incentives (e.g. ₹200 discount coupon)**.

### The Phased Architecture

* **Phase 1 (Deterministic Core):**
  * **Tier 0:** Closed-form, 36-month customer lifecycle accounting engine (Zero Breakage, Stranded Garment Truncation, Partitioned Cohort, Blended RTO Logistics Cascade).
  * **Tier 1:** Analytical 2D Break-Even Surface Solver (`ΔContribution(Δf_causal, E[R_net]) = 0`) and 12-variable Tornado Sensitivity ranking.
  * **Deliverables:** Modular Python package, formulaic Excel financial model (`.xlsx`), interactive local Streamlit dashboard, and Executive De-Risking Memo.
* **Phase 2 (Stochastic Engine):**
  * **Tier 2:** Discrete-hazard Monte Carlo simulation modeling customer-level heterogeneity, purchase timing distributions, and working capital cash lag.

---

## Directory Structure

```
tradeback-economics/
├── docs/
│   ├── ARCHITECTURE_1PAGER.md     # Master 1-Pager Architecture & Formulations
│   ├── DECISION_LOG.md            # Architectural Decision Records (ADRs)
│   └── PROMPT_AUDIT_TRAIL.md      # Chronological history of prompts & reviews
├── src/
│   ├── assumptions.py             # Parameter registry with 5-tier taxonomy
│   ├── tier0_engine.py            # Deterministic accounting engine (Systems A, B, C)
│   ├── tier1_breakeven.py         # Analytical break-even & sensitivity solver
│   ├── export_excel.py            # Investor-ready formulaic Excel generator
│   └── app.py                     # Interactive Streamlit Web UI
├── outputs/                       # Generated Excel models and executive memos
├── tests/                         # Verification unit tests
└── requirements.txt
```

---

## Setup & Running

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Run the interactive Streamlit dashboard
streamlit run src/app.py
```
