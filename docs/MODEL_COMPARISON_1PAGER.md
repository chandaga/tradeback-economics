# 3-System Economic Comparison & Model Architecture (1-2 Pager)

**Project:** TradeBack Economics & Customer Lifecycle Engine  
**Target Market:** AI-Native Fast Fashion D2C (India)  
**Evaluation Horizon:** 36-Month Acquired Cohort Lifecycle (Active Lifespan = 18 Months)

---

## 1. Executive Summary & Strategy Matrix

| Dimension | System A: Conventional D2C | System B: TradeBack Closed-Loop | System C: ₹200 Promo Coupon |
| :--- | :--- | :--- | :--- |
| **Core Incentive** | None (Organic / Performance Retargeting) | **20% Store Credit** (₹260 at checkout) | **₹200 Instant Discount Voucher** |
| **Prerequisite** | Full out-of-pocket payment | Physical return of 3–6 mo old garment | Re-engagement code entry |
| **Operational Reverse Supply Chain** | None (Standard forward delivery only) | **Doorstep swap, QC, sanitization & B2B salvage** | None (Pure digital discount) |
| **Lifetime Contribution (LTC / Customer)** | **₹1,362.50** | **₹1,398.00** *(Cohort blended @ 40% adoption)* | **₹1,379.50** |
| **LTV / CAC Ratio** | **4.41x** | **4.50x** *(Adopters: 4.63x)* | **4.45x** |
| **Net Accretion vs Baseline A** | Baseline (₹0.00) | **+₹35.50 / acquired customer** | **+₹17.00 / acquired customer** |
| **Strategic Superiority** | Vulnerable to rising Meta CAC | **+₹18.50 vs System C** | Margin dilution without inventory recovery |

---

## 2. Core Accounting Identities & Governing Equations

### System A: Conventional D2C Baseline
Every repeat order requires paid performance marketing retargeting. No reverse logistics or credits.

$$\text{Total Orders } (N_{\text{base}}) = f_{\text{base}} \times \left(\frac{T_{\text{active}}}{12}\right)$$
$$\text{LTC}_{\text{baseline}} = -\text{CAC}_{\text{init}} + N_{\text{base}} \times (\text{AOV} \times \text{GM} - C_{\text{fulfill}}) - (N_{\text{base}} - 1) \times \text{CAC}_{\text{repeat}}$$

---

### System B: TradeBack Closed-Loop Buy-Back
Customers opt-in at rate $\alpha$. Adopters generate causal purchase uplift $\Delta f$, receive instant store credit at replacement checkout, and the brand recovers net salvage value from the returned garment.

#### 1. Garment Ceiling & Truncation (Order Accounting)
* **First Purchase:** Initial wardrobe acquisition $\rightarrow$ No return possible.
* **Terminal Purchase:** Final garment bought before customer churns remains stranded in wardrobe $\rightarrow$ No credit issued.

$$N_{\text{adopter}} = (f_{\text{base}} + \Delta f_{\text{causal}}) \times \left(\frac{T_{\text{active}}}{12}\right)$$
$$N_{\text{returns}} = \max\left(0, \; N_{\text{adopter}} - 1 - N_{\text{stranded}}\right)$$
$$N_{\text{full\_margin\_orders}} = N_{\text{adopter}} - N_{\text{returns}}$$

#### 2. Reverse Logistics & Cascading Collection Cost ($C_{\text{collection}}$)
Doorstep swap fails at rate $P_{\text{fail}}$, cascading into standalone courier or forward RTO freight penalty:

$$C_{\text{collection}} = C_{\text{swap}} + P_{\text{fail}} \times \left[ C_{\text{standalone\_rev}} + P_{\text{RTO}} \times (C_{\text{forward}} + C_{\text{RTO\_freight}}) \right]$$

#### 3. Expected Unit Net Salvage Recovery ($E[R_{\text{net}}]$)
$$E[R_{\text{net}}] = \sum_{k} P_k \times \left( V_k \times (1 - d_{\text{trend}})^{\frac{t_{\text{hold}}}{30}} - C_{\text{route\_}k} \right) - C_{\text{collection}} - C_{\text{QC}} - \text{Tax}_{\text{GST}}$$

#### 4. Adopter Lifetime Contribution ($\text{LTC}_{\text{adopter}}$)
$$\text{LTC}_{\text{adopter}} = -\text{CAC}_{\text{init}} + N_{\text{adopter}} \times (\text{AOV} \times \text{GM} - C_{\text{fulfill}}) + N_{\text{returns}} \times E[R_{\text{net}}] + N_{\text{returns}} \times (\text{CAC}_{\text{repeat}} \times S_{\text{ad}}) - N_{\text{returns}} \times (\text{AOV} \times \text{Credit}_{\%}) - (N_{\text{adopter}} - 1 - N_{\text{returns}}) \times \text{CAC}_{\text{repeat}}$$

#### 5. Cohort Blended Contribution & Accretion
$$\text{Cohort LTC} = \alpha \times \text{LTC}_{\text{adopter}} + (1 - \alpha) \times \text{LTC}_{\text{baseline}}$$
$$\Delta \text{Contribution}_{\text{TradeBack}} = \alpha \times (\text{LTC}_{\text{adopter}} - \text{LTC}_{\text{baseline}})$$

---

### System C: Benchmark Promotional Coupon (₹200 Discount)
Simulates an aggressive loyalty discount without reverse logistics or garment recovery.

$$\text{LTC}_{\text{promo}} = -\text{CAC}_{\text{init}} + N_{\text{promo}} \times (\text{AOV} \times \text{GM} - C_{\text{fulfill}}) - (N_{\text{promo}} - 1) \times \text{Discount}_{\text{coupon}} - (N_{\text{promo}} - 1) \times \text{CAC}_{\text{repeat}} \times (1 - S_{\text{ad\_promo}})$$
$$\Delta \text{Contribution}_{\text{Promo}} = \text{LTC}_{\text{promo}} - \text{LTC}_{\text{baseline}}$$

---

## 3. Base Case Parameters & Empirical Ground Truth

| Parameter Category | Symbol | Default Value | Unit | Ground Truth / Benchmark Source |
| :--- | :--- | :---: | :---: | :--- |
| **Average Order Value** | $\text{AOV}$ | **₹1,300** | ₹/order | Mid-market Indian fast fashion (Urbanic, Snitch, Westside) |
| **Gross Margin %** | $\text{GM}$ | **50.0%** | % | Direct apparel COGS = ₹650 (Surat/Tirupur manufacturing) |
| **Initial Acquisition CAC** | $\text{CAC}_{\text{init}}$ | **₹400** | ₹/cust | Blended paid Meta/Google acquisition cost |
| **Baseline Frequency** | $f_{\text{base}}$ | **2.50** | orders/yr | Standard Indian apparel repurchase rate (Bain/Flipkart) |
| **Active Lifespan** | $T_{\text{active}}$ | **18.0** | months | 3.75 baseline orders before customer dormancy |
| **Repeat Ad Retargeting CAC** | $\text{CAC}_{\text{repeat}}$ | **₹150** | ₹/order | Cost per repeat order via Meta DPA / SMS / WhatsApp |
| **TradeBack Adoption Rate** | $\alpha$ | **40.0%** | % | Target cohort participation in buy-back |
| **Causal Order Uplift** | $\Delta f_{\text{causal}}$ | **+0.50** | orders/yr | +0.75 incremental orders over 18 months ($N_{\text{adopter}} = 4.50$) |
| **TradeBack Credit %** | $\text{Credit}_{\%}$ | **20.0%** | % of AOV | ₹260 store credit applied directly at checkout |
| **Credit Breakage Rate** | $\beta$ | **0.0%** | % | Instant checkout deduction (ADR-001: no phantom breakage) |
| **Terminal Stranded Garments** | $N_{\text{stranded}}$ | **1.0** | units | Garments retained at customer lifecycle exit (ADR-002) |
| **Fulfillment / Forward Ship** | $C_{\text{fulfill}}$ | **₹70** | ₹/order | Standard 3PL forward shipping + packaging (Delhivery) |
| **Doorstep Swap Cost** | $C_{\text{swap}}$ | **₹35** | ₹/swap | Delivery partner incremental fee for doorstep exchange |
| **Swap Failure Rate** | $P_{\text{fail}}$ | **15.0%** | % | Customer unprepared / courier SLA pressure (Shadowfax) |
| **Standalone Reverse Pickup** | $C_{\text{rev}}$ | **₹65** | ₹/pickup | Fallback reverse courier cost upon swap failure |
| **QC & Sanitization Cost** | $C_{\text{QC}}$ | **₹45** | ₹/garment | Warehouse unboxing, grading, steam press, polybag |
| **B2B Jobber Liquidation Price** | $V_{\text{B2B}}$ | **₹150** | ₹/garment | Bulk wholesale lot clearance price (Surat/Delhi hubs) |
| **B2B Liquidation Allocation** | $P_{\text{B2B}}$ | **60.0%** | % | Primary disposition channel (ADR-004) |
| **Holding Delay & Decay** | $t_{\text{hold}}, d_{\text{trend}}$ | **45d, 5%** | days, %/mo | Time-value depreciation before secondary liquidation |
| **System C Coupon Value** | $\text{Discount}$ | **₹200** | ₹/order | Promotional benchmark instant coupon voucher |

---

## 4. The 5 Deal-Breaker Threshold Numbers for Investors

1. **Minimum Net Garment Recovery Required ($E[R_{\text{net}}] \text{ at } \Delta f = 0$):**
   * **₹182.26 / garment**  
   * *Takeaway:* If TradeBack produces zero behavioral frequency uplift, each returned garment must yield at least ₹182.26 net to avoid destroying capital. At base case uplift ($\Delta f = +0.50$), required recovery drops to **₹30.82**.

2. **Minimum Causal Uplift Required ($\Delta f_{\text{causal}} \text{ at } E[R_{\text{net}}] = ₹0$):**
   * **+0.66 orders/year** (+0.99 orders over 18 months)  
   * *Takeaway:* If returned garments are discarded for ₹0 net salvage, customer order frequency must increase from 2.50 to at least **3.16 orders/year** to fund the credit and logistics.

3. **Maximum Affordable Credit % Ceiling:**
   * **22.7% of AOV (₹295.50)**  
   * *Takeaway:* Offering a 25% or 30% flat credit is mathematically non-viable under 50% gross margins, turning the program into a guaranteed margin drag.

4. **Maximum Tolerable QC & Sanitization Cost:**
   * **₹80.49 / garment**  
   * *Takeaway:* If warehouse unboxing, grading, and cleaning costs exceed ₹80.49, the reverse supply chain turns negative even with ₹150 jobber liquidation.

5. **TradeBack vs Promo Coupon Superiority Threshold:**
   * **$E[R_{\text{net}}] \ge ₹45.00 / \text{garment}$**  
   * *Takeaway:* TradeBack generates **+₹18.50 more contribution per customer** than a ₹200 discount coupon as long as net garment recovery covers the basic QC cost (₹45).
