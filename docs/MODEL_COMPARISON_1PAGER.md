# 3-System Economic Comparison & Model Architecture (1-2 Pager)

**Project:** TradeBack Economics & Customer Lifecycle Engine  
**Target Market:** AI-Native Fast Fashion D2C (India)  
**Evaluation Horizon:** 36-Month Acquired Cohort Lifecycle (Active Lifespan = 18 Months)

---

## 1. Executive Summary & Strategy Matrix

| Dimension | System A: Conventional D2C | System B: TradeBack Canonical Model | System C: ₹200 Promo Coupon |
| :--- | :--- | :--- | :--- |
| **Core Incentive** | None (Organic / Performance Retargeting) | **20% Store Credit** (₹260 applied at checkout) | **₹200 Instant Voucher** (Checkout code) |
| **Prerequisite** | Full out-of-pocket payment | Physical return of eligible garment | Re-engagement code entry |
| **Operational Reverse Chain** | None (Forward delivery only) | **Doorstep swap, QC & 5-route salvage** | None (Pure digital discount) |
| **Cohort Lifetime Contribution (LTC)** | **₹1,568.75** | **₹1,631.74** *(Adopter: ₹1,726.21 @ 40% adoption)* | **₹1,525.75** *(Adopter: ₹1,461.25 @ 40% adoption)* |
| **LTV / CAC Ratio** | **4.92x** | **5.08x** *(Adopters: 5.32x)* | **4.81x** *(Adopters: 4.65x)* |
| **Net Accretion vs Baseline A** | Baseline (₹0.00) | **+₹62.98 / acquired customer** | **-₹43.00 / acquired customer** |
| **Strategic Advantage** | Vulnerable to rising Meta CAC | **+₹105.98 vs Promo Coupon C** | Severe margin drag without garment salvage |

---

## 2. The Four Critical Structural Corrections

1. **The Paid Reacquisition Trap ($p_{\text{paid-rep}} = 50\%$):** In consumer D2C, assuming every repeat order burns ₹150 in Meta ads is flawed; 50% of repeats occur organically or via CRM WhatsApp/email flows (<₹2). Crediting TradeBack with avoiding ad spend only applies to the paid share:
   $$E[\text{CAC}_{\text{avoided}}] = \text{CAC}_{\text{rep}} \times S_{\text{ad}} \times p_{\text{paid-rep}} = 150 \times 0.60 \times 0.50 = \mathbf{₹45.00 / return}$$

2. **Disentangling Adoption ($\alpha = 40\%$) from Order Utilization ($u = 75\%$):** Enrolled customers do not return a garment on 100% of orders. Eligible repeat orders ($N_{\text{adopter}} - 1 - N_{\text{stranded}} = 4.50 - 1 - 1 = 2.50$) multiplied by $u = 75\%$ yields **$N_{\text{TB}} = 1.875$ actual returns per adopter**.

3. **Unpacking the 5-Route Secondary Recovery Tree:** Gross clearance cash ($E[V_{\text{salv}}] = ₹158.68$) less blended doorstep collection (-₹46.70) and warehouse QC (-₹45.00) gives **True $E[R_{\text{net-ops}}] = \mathbf{₹66.98 / return}$**.

4. **Honest Data Taxonomy:** Eliminates misleading "Ground Truth" tags; categorizes variables under `[Observed]`, `[External Benchmark]`, `[Management Assumption]`, `[Model Assumption]`, and `[Unknown]`.

---

## 3. The Canonical 2-Lever Master Architecture

Rather than complex nested polynomials, the economics collapse into two transparent, audit-proof levers:

$$\Delta \text{LTC} = \underbrace{\Delta N_{\text{orders}} \times \text{CM}_{\text{order}}}_{\text{1. Incremental Volume Margin}} + \underbrace{N_{\text{TB}} \times \Big( E[R_{\text{net-ops}}] + E[\text{CAC}_{\text{avoided}}] - C_{\text{TB}} \Big)}_{\text{2. Net Unit Circular Balance}}$$

### Live Base-Case Parameter Decomposition:

* **Order Margin ($\text{CM}_{\text{order}}$):** $(\text{AOV} \times \text{GM}_{\text{prod}}) - C_{\text{fulfill}} = (1,300 \times 0.50) - 70 = \mathbf{₹580.00 / order}$
* **Incremental Orders ($\Delta N_{\text{orders}}$):** $\Delta f \times (T_{\text{active}} / 12) = 0.50 \times 1.5 = \mathbf{+0.75 \text{ orders / adopter}}$
* **Actual Returns ($N_{\text{TB}}$):** $(4.50 - 1 - 1) \times 0.75 = \mathbf{1.875 \text{ returns / adopter}}$
* **Circular Unit Spread:** $E[R_{\text{net-ops}}] + E[\text{CAC}_{\text{avoided}}] - C_{\text{TB}} = 66.98 + 45.00 - 260.00 = \mathbf{-₹148.02 / return}$

### Step-by-Step Financial Accretion:

1. **Lever 1 (Incremental Volume Expansion):**
   $$\Delta N_{\text{orders}} \times \text{CM}_{\text{order}} = 0.75 \times ₹580.00 = \mathbf{+₹435.00}$$
2. **Lever 2 (Net Unit Circular Balance):**
   $$N_{\text{TB}} \times \text{Circular Unit Spread} = 1.875 \times (-₹148.02) = \mathbf{-₹277.54}$$
3. **Incremental Adopter Contribution ($\Delta \text{LTC}_{\text{adopter}}$):**
   $$\Delta \text{LTC}_{\text{adopter}} = +435.00 - 277.54 = \mathbf{+₹157.46}$$
4. **Cohort Blended Net Accretion ($\alpha = 40\%$):**
   $$\Delta \text{LTC}_{\text{cohort}} = 0.40 \times +₹157.46 = \mathbf{+₹62.98 \text{ / acquired customer}}$$

---

## 4. Itemized 5-Route Secondary Recovery Tree

| Route ($k$) | Allocation ($P_k$) | Gross Value | Trend Decay | Route Cost | Net Realized | Weighted Net |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **1. B2B Jobbers** | 60.0% | ₹150.00 | -7.4% (45d) | ₹10.00 | ₹128.90 | **₹77.34** |
| **2. D2C Resale Portal** | 20.0% | ₹450.00 | -7.4% (45d) | ₹80.00 (clean/shoot) | ₹336.70 | **₹67.34** |
| **3. Upcycling / Rework** | 10.0% | ₹160.00 | 0.0% | ₹30.00 | ₹130.00 | **₹13.00** |
| **4. Industrial Scrap** | 5.0% | ₹35.00 | 0.0% | ₹5.00 | ₹30.00 | **₹1.50** |
| **5. Loss / Write-off** | 5.0% | ₹0.00 | 0.0% | ₹10.00 (disposal) | -₹10.00 | **-₹0.50** |
| **Gross Realized Salvage $E[V_{\text{salv}}]$** | **100%** | — | — | — | — | **₹158.68** |
| *Less: Blended Collection Friction* | — | — | — | — | — | **-₹46.70** |
| *Less: Intake QC & Steaming* | — | — | — | — | — | **-₹45.00** |
| **True $E[R_{\text{net-ops}}]$ (Pre-tax)** | — | — | — | — | — | **₹66.98** |

*Note: Blended collection friction accounts for doorstep swap failure ($P_{\text{fail}} = 15\%$) and swap-induced RTO freight penalties ($P_{\text{RTO}} = 10\%$, ₹130 freight burn):*  
$$C_{\text{collection}} = 35 + 0.15 \times [65 + 0.10 \times 130] = 35 + 11.70 = \mathbf{₹46.70 / return}$$

---

## 5. System C (Promo Coupon Benchmark) Comparison

In System C, the brand matches the causal order uplift ($\Delta N_{\text{orders}} = +0.75$) by issuing a flat ₹200 instant discount voucher on repeat purchases without reverse logistics:

* Incremental Volume Margin: $0.75 \times 580.00 = +₹435.00$
* Repeat Coupon Cost: $3.50 \text{ repeats} \times ₹200 = -₹700.00$
* Avoided Repeat Paid Ads: $3.50 \times (150 \times 0.60 \times 0.50) = +₹157.50$
* **Promo Adopter $\Delta \text{LTC}$:** $435.00 - 700.00 + 157.50 = \mathbf{-₹107.50}$
* **Promo Cohort Net Dilution ($\alpha = 40\%$):** $0.40 \times (-107.50) = \mathbf{-₹43.00 \text{ / acquired customer}}$
* **TradeBack Advantage over Promo Coupon:** $+62.98 - (-43.00) = \mathbf{+₹105.98 \text{ / acquired customer}}$

---

## 6. The 5 Deal-Breaker Investor Threshold Numbers

1. **Zero-Uplift Required Recovery ($E[R_{\text{net-ops}}]$ at $\Delta f = 0$):**
   $$E[R_{\text{net-ops}}] \ge C_{\text{TB}} - E[\text{CAC}_{\text{avoided}}] = ₹260.00 - ₹45.00 = \mathbf{₹215.00 / return}$$
   *Takeaway:* If TradeBack produces zero behavioral frequency lift, each returned garment must yield at least ₹215.00 net to prevent margin destruction.

2. **Zero-Recovery Required Uplift ($\Delta f$ at $E[R] = ₹0$):**
   $$\Delta N_{\text{orders}} \ge \frac{N_{\text{TB}} \times (C_{\text{TB}} - E[\text{CAC}_{\text{avoided}}])}{\text{CM}_{\text{order}}} = \frac{1.875 \times ₹215}{₹580} \approx 0.695 \text{ orders} \implies \mathbf{+0.46 \text{ orders/year}}$$
   *Takeaway:* If all garments are sent to zero-recovery scrap, customer order frequency must increase from 2.50 to at least **2.96 orders/year** to fund the credit and courier costs.

3. **Maximum Economically Affordable Credit % Ceiling:**
   $$\text{Credit}_{\text{max}} = \frac{E[R_{\text{net-ops}}] + E[\text{CAC}_{\text{avoided}}] + \frac{\Delta N \times \text{CM}}{N_{\text{TB}}}}{\text{AOV}} = \frac{66.98 + 45.00 + 232.00}{1,300} = \mathbf{26.5\% \text{ of AOV (₹344.00)}}$$
   *Takeaway:* Offering a flat 30% credit guarantees margin dilution under a 50% gross margin structure.

4. **Maximum Tolerable QC & Sanitization Cost ($C_{\text{QC, max}}$):**
   $$C_{\text{QC, max}} = C_{\text{QC, base}} + \frac{\Delta \text{LTC}_{\text{adopter}}}{N_{\text{TB}}} = 45.00 + \frac{157.46}{1.875} = \mathbf{₹128.98 / garment}$$
   *Takeaway:* The brand maintains an ₹83.98 cost buffer above its current ₹45.00 warehouse intake cost.

5. **TradeBack vs Promo Coupon Superiority Threshold:**
   TradeBack remains strictly accretive over couponing whenever secondary salvage $E[R_{\text{net-ops}}] \ge \mathbf{₹45.00 / return}$.
