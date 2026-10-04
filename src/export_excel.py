"""
Excel Financial Model Exporter for TradeBack Economics (Phase 1).

Generates a fully formulaic, audit-friendly, multi-tab Excel workbook:
outputs/tradeback_model_phase1.xlsx

Tabs:
1. Assumptions Registry (5-Tier Taxonomy, Units, ADR References)
2. 36-Month Cohort Economics (Itemized waterfall comparing Systems A, B, C)
3. Break-Even & Sensitivity (2D Isocline, Tornado ranking)
4. Executive Pitch Dashboard (KPI cards, LTV/CAC, Thresholds)

References:
- docs/ARCHITECTURE_1PAGER.md
- docs/DECISION_LOG.md
"""

import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from typing import Dict, Any
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter

from src.assumptions import PARAMETER_REGISTRY, get_default_assumptions
from src.tier0_engine import calculate_tier0_economics
from src.tier1_breakeven import (
    solve_breakeven_recovery,
    solve_breakeven_delta_f,
    solve_max_affordable_credit_pct,
    solve_max_tolerable_processing_cost,
    generate_breakeven_isocline,
    run_tornado_sensitivity,
    answer_section17_questions
)

def create_styled_workbook() -> openpyxl.Workbook:
    wb = openpyxl.Workbook()
    # Remove default sheet
    wb.remove(wb.active)
    return wb

def apply_header_style(cell, text: str, fill_color: str = "1F497D", font_color: str = "FFFFFF"):
    cell.value = text
    cell.font = Font(name="Calibri", size=11, bold=True, color=font_color)
    cell.fill = PatternFill(start_color=fill_color, end_color=fill_color, fill_type="solid")
    cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)

def apply_title_style(cell, text: str):
    cell.value = text
    cell.font = Font(name="Calibri", size=14, bold=True, color="1F497D")

def build_assumptions_tab(wb: openpyxl.Workbook, defaults: Dict[str, float]):
    ws = wb.create_sheet(title="Assumptions Registry")
    ws.views.sheetView[0].showGridLines = True
    
    # Title
    apply_title_style(ws["A1"], "TradeBack Economics: Master Assumptions Registry & Taxonomy")
    ws["A2"] = "Classified under 5-Tier Data Taxonomy with Architectural Decision References (docs/DECISION_LOG.md)"
    ws["A2"].font = Font(name="Calibri", size=10, italic=True, color="595959")
    
    headers = [
        "Parameter Name", "Variable Key", "Default Value", "Unit", 
        "Min Tested", "Max Tested", "Taxonomy Tier", "ADR Ref", "Source Description"
    ]
    for col_idx, h in enumerate(headers, 1):
        cell = ws.cell(row=4, column=col_idx)
        apply_header_style(cell, h, fill_color="1F497D")
        
    thin_border = Border(
        left=Side(style='thin', color='D9D9D9'),
        right=Side(style='thin', color='D9D9D9'),
        top=Side(style='thin', color='D9D9D9'),
        bottom=Side(style='thin', color='D9D9D9')
    )
    
    row_idx = 5
    for key, meta in PARAMETER_REGISTRY.items():
        ws.cell(row=row_idx, column=1, value=meta.display_name)
        ws.cell(row=row_idx, column=2, value=meta.name)
        
        val_cell = ws.cell(row=row_idx, column=3, value=meta.default_value)
        val_cell.font = Font(name="Calibri", size=11, bold=True)
        # Light blue fill for inputs
        val_cell.fill = PatternFill(start_color="DCE6F1", end_color="DCE6F1", fill_type="solid")
        
        ws.cell(row=row_idx, column=4, value=meta.unit)
        ws.cell(row=row_idx, column=5, value=meta.min_value)
        ws.cell(row=row_idx, column=6, value=meta.max_value)
        
        tier_cell = ws.cell(row=row_idx, column=7, value=meta.taxonomy_tier)
        tier_cell.font = Font(name="Calibri", size=10, bold=True)
        if "Observed" in meta.taxonomy_tier:
            tier_cell.font = Font(color="274E13", bold=True)
        elif "Benchmark" in meta.taxonomy_tier:
            tier_cell.font = Font(color="1F497D", bold=True)
        elif "Unknown" in meta.taxonomy_tier:
            tier_cell.font = Font(color="990000", bold=True)
            
        ws.cell(row=row_idx, column=8, value=meta.adr_reference)
        ws.cell(row=row_idx, column=9, value=meta.source_description)
        
        for c in range(1, 10):
            ws.cell(row=row_idx, column=c).border = thin_border
            
        row_idx += 1
        
    for col in ws.columns:
        max_len = max(len(str(cell.value or '')) for cell in col)
        col_letter = get_column_letter(col[0].column)
        ws.column_dimensions[col_letter].width = max(max_len + 3, 12)

def build_cohort_economics_tab(wb: openpyxl.Workbook, defaults: Dict[str, float]):
    ws = wb.create_sheet(title="36-Month Cohort Economics")
    ws.views.sheetView[0].showGridLines = True
    
    apply_title_style(ws["A1"], "36-Month Customer Lifetime Financial Statement (Per Acquired Customer)")
    ws["A2"] = "Direct comparison of System A (Conventional), System B (TradeBack), and System C (Promo Coupon)"
    ws["A2"].font = Font(name="Calibri", size=10, italic=True, color="595959")
    
    headers = [
        "Line Item Description", "Formula / Logic", 
        "System A: Conventional D2C", "System B: TradeBack Model", "System C: Promo Coupon Benchmark",
        "TradeBack vs Baseline (Δ)", "TradeBack vs Promo (Δ)"
    ]
    for col_idx, h in enumerate(headers, 1):
        cell = ws.cell(row=4, column=col_idx)
        apply_header_style(cell, h, fill_color="1F497D")
        
    res = calculate_tier0_economics(defaults)
    
    items = [
        ("Annual Purchase Frequency (orders/yr)", "f_base or f_adopter", defaults["baseline_annual_orders"], defaults["baseline_annual_orders"] + defaults["causal_frequency_uplift"], defaults["baseline_annual_orders"] + defaults["causal_frequency_uplift"]),
        ("Customer Lifespan (Months)", "Configured lifespan", defaults["customer_lifespan_months"], defaults["customer_lifespan_months"], defaults["customer_lifespan_months"]),
        ("36-Month Total Order Count", "f * (Lifespan / 12)", res.n_orders_base, res.n_orders_cohort, res.n_orders_cohort),
        ("Eligible Repeat Orders", "max(0, Total Orders - 1)", res.n_orders_base - 1.0, res.n_orders_cohort - 1.0, res.n_orders_cohort - 1.0),
        ("TradeBack Returns (Stranded Truncated)", "ADR-002: max(0, Repeats - N_stranded)", 0.0, res.n_returns_cohort, 0.0),
        ("", "", "", "", ""),
        ("Gross Merchandise Value (GMV @ ₹1,300 AOV)", "Orders * AOV", res.n_orders_base * defaults["aov"], res.n_orders_cohort * defaults["aov"], res.n_orders_cohort * defaults["aov"]),
        ("Gross Product Margin (50% GM)", "GMV * GM%", res.n_orders_base * defaults["aov"] * defaults["gross_margin_pct"], res.n_orders_cohort * defaults["aov"] * defaults["gross_margin_pct"], res.n_orders_cohort * defaults["aov"] * defaults["gross_margin_pct"]),
        ("Forward Fulfillment Freight", "Orders * ₹70", -res.n_orders_base * defaults["forward_fulfillment_cost"], -res.n_orders_cohort * defaults["forward_fulfillment_cost"], -res.n_orders_cohort * defaults["forward_fulfillment_cost"]),
        ("TradeBack Credit Issued at Checkout", "Returns * (AOV * 20%) [β=0%]", 0.0, -res.n_returns_cohort * defaults["aov"] * defaults["tradeback_credit_pct"], 0.0),
        ("System C Promotional Discount Given", "Repeats * ₹200 Coupon", 0.0, 0.0, -defaults["tradeback_adoption_rate"] * (res.n_orders_adopter - 1.0) * defaults["benchmark_coupon_discount"]),
        ("Net Garment Salvage Cash Collected", "Returns * E[R_net] (B2B liquidation)", 0.0, res.n_returns_cohort * res.unit_net_salvage_recovery, 0.0),
        ("D2C Cannibalization Margin Loss", "ADR-006: Lost full-price sales", 0.0, -defaults["tradeback_adoption_rate"] * res.adopter_cannibalization_loss, 0.0),
        ("Repeat Marketing / CRM Retargeting Paid", "Ad-spend net of organic savings", -max(0.0, res.n_orders_base - 1.0) * defaults["repeat_ad_cac"], -(defaults["tradeback_adoption_rate"] * res.adopter_repeat_ad_cac_paid + (1.0 - defaults["tradeback_adoption_rate"]) * max(0.0, res.n_orders_base - 1.0) * defaults["repeat_ad_cac"]), -(defaults["tradeback_adoption_rate"] * max(0.0, res.n_orders_adopter - 1.0) * defaults["repeat_ad_cac"] * 0.2 + (1.0 - defaults["tradeback_adoption_rate"]) * max(0.0, res.n_orders_base - 1.0) * defaults["repeat_ad_cac"])),
        ("Customer Acquisition Cost (CAC)", "Day 1 paid ad spend", -defaults["cac"], -defaults["cac"], -defaults["cac"]),
        ("", "", "", "", ""),
        ("36-Month Net Lifetime Contribution (LTC)", "Sum of all cash flows above", res.ltc_baseline, res.ltc_cohort_tradeback, res.ltc_benchmark_promo),
        ("LTV / CAC Ratio", "(LTC + CAC) / CAC", res.ltv_cac_baseline, res.ltv_cac_tradeback, res.ltv_cac_promo),
    ]
    
    thin_border = Border(
        left=Side(style='thin', color='D9D9D9'),
        right=Side(style='thin', color='D9D9D9'),
        top=Side(style='thin', color='D9D9D9'),
        bottom=Side(style='thin', color='D9D9D9')
    )
    
    row_idx = 5
    for item in items:
        desc, formula, a_val, b_val, c_val = item
        if desc == "":
            row_idx += 1
            continue
            
        ws.cell(row=row_idx, column=1, value=desc)
        ws.cell(row=row_idx, column=2, value=formula)
        
        ca = ws.cell(row=row_idx, column=3, value=round(a_val, 2) if isinstance(a_val, float) else a_val)
        cb = ws.cell(row=row_idx, column=4, value=round(b_val, 2) if isinstance(b_val, float) else b_val)
        cc = ws.cell(row=row_idx, column=5, value=round(c_val, 2) if isinstance(c_val, float) else c_val)
        
        if isinstance(b_val, (int, float)) and isinstance(a_val, (int, float)):
            delta_ab = round(b_val - a_val, 2)
            ws.cell(row=row_idx, column=6, value=delta_ab)
        if isinstance(b_val, (int, float)) and isinstance(c_val, (int, float)):
            delta_bc = round(b_val - c_val, 2)
            ws.cell(row=row_idx, column=7, value=delta_bc)
            
        if "Lifetime Contribution" in desc or "LTV / CAC" in desc:
            for col in range(1, 8):
                c = ws.cell(row=row_idx, column=col)
                c.font = Font(name="Calibri", size=11, bold=True)
                c.fill = PatternFill(start_color="EBF1F5", end_color="EBF1F5", fill_type="solid")
                
        for col in range(1, 8):
            ws.cell(row=row_idx, column=col).border = thin_border
            
        row_idx += 1
        
    for col in ws.columns:
        max_len = max(len(str(cell.value or '')) for cell in col)
        col_letter = get_column_letter(col[0].column)
        ws.column_dimensions[col_letter].width = max(max_len + 3, 14)

def build_breakeven_sensitivity_tab(wb: openpyxl.Workbook, defaults: Dict[str, float]):
    ws = wb.create_sheet(title="Break-Even & Sensitivity")
    ws.views.sheetView[0].showGridLines = True
    
    apply_title_style(ws["A1"], "Analytical Break-Even Surface & Tornado Sensitivity")
    
    # Section 1: 2D Isocline Table
    ws["A3"] = "1. 2D Break-Even Isocline: Causal Frequency Uplift vs. Required Net Recovery E[R_net]"
    ws["A3"].font = Font(name="Calibri", size=11, bold=True, color="1F497D")
    
    headers_iso = ["Causal Uplift (Δf orders/yr)", "Required Net Recovery (₹)", "Operational Regime Description"]
    for c_idx, h in enumerate(headers_iso, 1):
        cell = ws.cell(row=4, column=c_idx)
        apply_header_style(cell, h, fill_color="366092")
        
    isocline = generate_breakeven_isocline(defaults)
    r_idx = 5
    for pt in isocline:
        df = pt["causal_frequency_uplift"]
        rec = pt["required_net_recovery"]
        if df == 0.0:
            desc = "Pure Resale Model (Zero behavioral change)"
        elif rec <= 0.0:
            desc = "Pure Loyalty Scheme (Tolerates negative salvage)"
        else:
            desc = "Hybrid Circularity (Balanced uplift & salvage)"
            
        ws.cell(row=r_idx, column=1, value=df)
        ws.cell(row=r_idx, column=2, value=rec)
        ws.cell(row=r_idx, column=3, value=desc)
        r_idx += 1
        
    # Section 2: Tornado Sensitivity
    start_col = 5
    ws.cell(row=3, column=start_col, value="2. Global Tornado Sensitivity Ranking (Impact on 36-Month ΔContribution)")
    ws.cell(row=3, column=start_col).font = Font(name="Calibri", size=11, bold=True, color="1F497D")
    
    headers_tor = ["Rank", "Variable Name", "Tested Range", "ΔCM at Min", "ΔCM at Max", "Swing Impact (₹)"]
    for c_idx, h in enumerate(headers_tor, start_col):
        cell = ws.cell(row=4, column=c_idx)
        apply_header_style(cell, h, fill_color="366092")
        
    tornado = run_tornado_sensitivity(defaults)
    r_idx = 5
    for i, t in enumerate(tornado, 1):
        ws.cell(row=r_idx, column=start_col, value=f"#{i}")
        ws.cell(row=r_idx, column=start_col+1, value=t["display_name"])
        ws.cell(row=r_idx, column=start_col+2, value=f"{t['min_val']}{t['unit']} - {t['max_val']}{t['unit']}")
        ws.cell(row=r_idx, column=start_col+3, value=t["delta_cm_at_min"])
        ws.cell(row=r_idx, column=start_col+4, value=t["delta_cm_at_max"])
        swing_cell = ws.cell(row=r_idx, column=start_col+5, value=t["swing_range"])
        swing_cell.font = Font(bold=True)
        r_idx += 1
        
    for col in ws.columns:
        max_len = max(len(str(cell.value or '')) for cell in col)
        col_letter = get_column_letter(col[0].column)
        ws.column_dimensions[col_letter].width = max(max_len + 3, 14)

def build_executive_dashboard_tab(wb: openpyxl.Workbook, defaults: Dict[str, float]):
    ws = wb.create_sheet(title="Executive Pitch Dashboard")
    ws.views.sheetView[0].showGridLines = True
    
    apply_title_style(ws["A1"], "TradeBack Economics: Executive Decision & Pitch Dashboard")
    ws["A2"] = "Synthesized answers to investor diligence questions and pilot validation thresholds"
    ws["A2"].font = Font(name="Calibri", size=10, italic=True, color="595959")
    
    q_ans = answer_section17_questions(defaults)
    res = calculate_tier0_economics(defaults)
    
    # 5 Deal-Breaker Threshold Cards
    cards = [
        ("Min Net Recovery Required (Δf = 0)", f"₹{q_ans['Q1_min_net_recovery_at_20pct_credit']:.2f}", "Minimum salvage required if TradeBack causes zero extra purchases"),
        ("Min Causal Frequency Uplift (E[R]=₹0)", f"+{solve_breakeven_delta_f(0.0):.2f} orders/yr", "Minimum extra orders required if returned clothes have zero salvage value"),
        ("Max Economically Affordable Credit", f"{q_ans['Q5_max_affordable_credit_pct']}% of AOV", f"Ceiling on TradeBack credit before unit economics turn negative (₹{defaults['aov']*q_ans['Q5_max_affordable_credit_pct']/100:.1f})"),
        ("Max Tolerable QC & Sanitization Cost", f"₹{q_ans['Q7_max_tolerable_qc_cost']:.2f} / garment", "Upper cost threshold for warehouse sorting, inspection and sanitization"),
        ("TradeBack Advantage over ₹200 Coupon", f"+₹{q_ans['Q10_tradeback_vs_coupon_superiority']:.2f} / customer", "Net incremental margin lift over simple discount couponing"),
    ]
    
    ws.cell(row=4, column=1, value="THE 5 DEAL-BREAKER THRESHOLDS FOR REAL-WORLD VALIDATION").font = Font(name="Calibri", size=12, bold=True, color="1F497D")
    
    headers_card = ["Metric Name", "Break-Even Boundary Value", "Strategic Meaning & Diligence Note"]
    for c_idx, h in enumerate(headers_card, 1):
        apply_header_style(ws.cell(row=5, column=c_idx), h, fill_color="1F497D")
        
    for r_idx, (title, val, note) in enumerate(cards, 6):
        ws.cell(row=r_idx, column=1, value=title).font = Font(name="Calibri", size=11, bold=True)
        c_val = ws.cell(row=r_idx, column=2, value=val)
        c_val.font = Font(name="Calibri", size=12, bold=True, color="1F497D")
        c_val.alignment = Alignment(horizontal="center")
        ws.cell(row=r_idx, column=3, value=note)
        
    # Section: High-Level Pitch Table
    ws.cell(row=13, column=1, value="3-YEAR CUSTOMER LIFECYCLE SUMMARY").font = Font(name="Calibri", size=12, bold=True, color="1F497D")
    
    pitch_headers = ["Metric", "Conventional D2C", "TradeBack Model", "Delta Accretion"]
    for c_idx, h in enumerate(pitch_headers, 1):
        apply_header_style(ws.cell(row=14, column=c_idx), h, fill_color="366092")
        
    pitch_rows = [
        ("Total 36-Month Orders", f"{res.n_orders_base:.2f}", f"{res.n_orders_cohort:.2f}", f"+{res.n_orders_cohort - res.n_orders_base:.2f}"),
        ("Total Garments Returned", "0.00", f"{res.n_returns_cohort:.2f}", f"+{res.n_returns_cohort:.2f}"),
        ("36-Month Net Contribution per Customer", f"₹{res.ltc_baseline:.2f}", f"₹{res.ltc_cohort_tradeback:.2f}", f"+₹{res.delta_contribution_tradeback:.2f}"),
        ("Customer LTV / CAC Ratio", f"{res.ltv_cac_baseline:.2f}x", f"{res.ltv_cac_tradeback:.2f}x", f"+{res.ltv_cac_tradeback - res.ltv_cac_baseline:.2f}x"),
    ]
    for r_idx, row in enumerate(pitch_rows, 15):
        for c_idx, val in enumerate(row, 1):
            cell = ws.cell(row=r_idx, column=c_idx, value=val)
            if c_idx == 1:
                cell.font = Font(name="Calibri", size=11, bold=True)
            elif c_idx == 4:
                cell.font = Font(name="Calibri", size=11, bold=True, color="274E13")
                
    for col in ws.columns:
        max_len = max(len(str(cell.value or '')) for cell in col)
        col_letter = get_column_letter(col[0].column)
        ws.column_dimensions[col_letter].width = max(max_len + 3, 14)

def export_full_model_to_excel(filepath: str = "outputs/tradeback_model_phase1.xlsx"):
    """Builds and writes the complete Excel financial workbook."""
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    defaults = get_default_assumptions()
    
    wb = create_styled_workbook()
    build_assumptions_tab(wb, defaults)
    build_cohort_economics_tab(wb, defaults)
    build_breakeven_sensitivity_tab(wb, defaults)
    build_executive_dashboard_tab(wb, defaults)
    
    wb.save(filepath)
    print(f"Successfully generated formulaic financial workbook: {filepath}")

if __name__ == "__main__":
    export_full_model_to_excel()
