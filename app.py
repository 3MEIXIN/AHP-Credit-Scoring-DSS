import io
import datetime
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
)
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT


# ─────────────────────────────────────────────────────────────────────────────
# 1. CONSTANTS  (AHP weights unchanged)
# ─────────────────────────────────────────────────────────────────────────────

SYSTEM_NAME = "SME Loan Assessment System"

CRITERIA_WEIGHTS = {
    "Financial Stability":  0.4030,
    "Creditworthiness":     0.3570,
    "Repayment Capacity":   0.1581,
    "Borrower Reliability": 0.0818,
}

GLOBAL_WEIGHTS = {
    "Financial Records":           0.1804,
    "Credit History":              0.1514,
    "Income Stability":            0.1358,
    "Repayment Period":            0.1328,
    "Savings and Current Account": 0.0868,
    "Monthly Income":              0.0824,
    "Existing Loan":               0.0729,
    "Debt Ratio":                  0.0380,
    "Cash Liquidity":              0.0377,
    "Integrity":                   0.0321,
    "Business Background":         0.0288,
    "Business Experience":         0.0209,
}

ASSESSMENT_GROUPS = {
    "Financial Stability":  ["Financial Records", "Income Stability", "Savings and Current Account"],
    "Creditworthiness":     ["Credit History", "Repayment Period", "Existing Loan"],
    "Repayment Capacity":   ["Monthly Income", "Cash Liquidity", "Debt Ratio"],
    "Borrower Reliability": ["Integrity", "Business Background", "Business Experience"],
}

PAGES = ["Home", "Evaluation Factors", "Loan Application Assessment", "Assessment Result"]

BUSINESS_TYPES = [
    "Retail", "Manufacturing", "Services", "Construction",
    "Food & Beverage", "Technology", "Others",
]

LOAN_PURPOSES = [
    "Working Capital", "Business Expansion", "Equipment Purchase",
    "Inventory Purchase", "Cash Flow Management", "Others",
]

RISK_THEMES = {
    "Low Risk": {
        "accent":        "#1a7f4b",
        "bg":            "#edfaf3",
        "border":        "#a3d9bb",
        "badge_bg":      "#d0f5e3",
        "badge_text":    "#0f5132",
        "decision_note": "Generally Recommended for Approval",
        "risk_note":     "Sound credit profile",
    },
    "Moderate Risk": {
        "accent":        "#c07a00",
        "bg":            "#fffbea",
        "border":        "#f0c060",
        "badge_bg":      "#fef3cd",
        "badge_text":    "#7d4e00",
        "decision_note": "Subject to Additional Review",
        "risk_note":     "Requires further evaluation",
    },
    "High Risk": {
        "accent":        "#b91c1c",
        "bg":            "#fff5f5",
        "border":        "#fca5a5",
        "badge_bg":      "#fee2e2",
        "badge_text":    "#7f1d1d",
        "decision_note": "Not Recommended — Further Review Needed",
        "risk_note":     "Insufficient credit strength",
    },
}

# ─────────────────────────────────────────────────────────────────────────────
# 2. PAGE CONFIG
# ─────────────────────────────────────────────────────────────────────────────

st.set_page_config(
    page_title=SYSTEM_NAME,
    page_icon="🏦",
    layout="wide",
)

# ─────────────────────────────────────────────────────────────────────────────
# 3. CSS
# ─────────────────────────────────────────────────────────────────────────────

def apply_css():
    st.markdown("""
    <style>
    /* ── Palette ── */
    :root {
        --navy:   #0f2747;
        --navy2:  #173a63;
        --slate:  #5b6675;
        --bg:     #f0f4f9;
        --white:  #ffffff;
        --border: #d4dde8;
        --muted:  #6b7280;
        --text:   #1f2937;
    }

    /* ── Global ── */
    .stApp { background-color: var(--bg); color: var(--text); }
    h1, h2, h3, h4 { color: var(--navy); }

    /* ── Constrain form page width ── */
    .form-page-wrap {
        max-width: 860px;
        margin: 0 auto;
    }

    /* ── Sidebar ── */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #091929 0%, #0f2747 100%);
    }
    [data-testid="stSidebar"] * { color: #e8f0f8 !important; }
    [data-testid="stSidebar"] .stCaption { color: #a0b4c8 !important; }
    [data-testid="stSidebar"] hr { border-color: rgba(255,255,255,0.12); }

    /* ── Buttons ── */
    .stButton > button, .stDownloadButton > button {
        background: var(--navy);
        color: #fff;
        border: none;
        border-radius: 10px;
        font-weight: 600;
        padding: 0.65rem 1rem;
        transition: background 0.2s;
    }
    .stButton > button:hover, .stDownloadButton > button:hover {
        background: var(--navy2);
        color: #fff;
    }

    /* ── Generic card ── */
    .card {
        background: var(--white);
        border: 1px solid var(--border);
        border-radius: 14px;
        padding: 20px;
        box-shadow: 0 2px 10px rgba(15,39,71,0.06);
        margin-bottom: 14px;
    }

    /* ── Hero banner ── */
    .hero {
        background: linear-gradient(135deg, #0a1e38 0%, #163759 100%);
        color: #fff;
        border-radius: 16px;
        padding: 28px 32px;
        box-shadow: 0 8px 28px rgba(15,39,71,0.18);
        margin-bottom: 18px;
    }
    .hero h1 { color: #fff; font-size: 1.85rem; margin: 0 0 10px 0; }
    .hero p  { color: #cfe0f0; font-size: 0.97rem; line-height: 1.8; margin: 0; }

    /* ── Metric tiles ── */
    .metric-tile {
        background: var(--white);
        border: 1px solid var(--border);
        border-radius: 14px;
        padding: 18px;
        box-shadow: 0 2px 10px rgba(15,39,71,0.05);
        min-height: 120px;
    }
    .metric-tile .label { font-size: 0.82rem; color: var(--muted); font-weight: 600;
                          letter-spacing: .4px; text-transform: uppercase; margin-bottom: 8px; }
    .metric-tile .value { font-size: 1.85rem; font-weight: 800; color: var(--navy); line-height: 1.1; }
    .metric-tile .note  { font-size: 0.84rem; color: var(--slate); margin-top: 8px; line-height: 1.5; }

    /* ── Workflow step ── */
    .workflow-step {
        background: #f6f9fd;
        border: 1px solid #dce8f5;
        border-radius: 12px;
        padding: 18px;
        min-height: 118px;
    }
    .workflow-step h4 { margin: 0 0 8px 0; font-size: 0.95rem; color: var(--navy); }
    .workflow-step p  { margin: 0; color: var(--slate); font-size: 0.88rem; line-height: 1.65; }

    /* ── Info tile (result page) ── */
    .info-tile {
        background: var(--white);
        border: 1px solid var(--border);
        border-radius: 14px;
        padding: 18px 20px;
        box-shadow: 0 2px 10px rgba(15,39,71,0.05);
        
        height: 200px;          
        display: flex;
        flex-direction: column;
    }
    .info-tile h4 {
        margin: 0 0 12px 0; font-size: 0.85rem; font-weight: 700;
        color: var(--muted); letter-spacing: .5px; text-transform: uppercase;
        border-bottom: 1px solid var(--border); padding-bottom: 8px;
    }
    .info-tile .row {
        display: flex; justify-content: space-between;
        padding: 5px 0; font-size: 0.9rem; border-bottom: 1px dashed #e8edf3;
    }
    .info-tile .row:last-child { border-bottom: none; }
    .info-tile .row .lbl { color: var(--muted); }
    .info-tile .row .val { color: var(--text); font-weight: 600; }

    /* ── Result summary card ── */
    .result-card {
        border-radius: 14px;
        padding: 20px;
        box-shadow: 0 2px 10px rgba(15,39,71,0.06);
        margin-bottom: 4px;
    }
    .result-card .rc-label { font-size: 0.78rem; font-weight: 700;
                              letter-spacing: .5px; text-transform: uppercase; margin-bottom: 8px; }
    .result-card .rc-value { font-size: 1.8rem; font-weight: 800; line-height: 1.1; margin-bottom: 10px; }
    .result-card .rc-badge { display: inline-block; padding: 4px 12px;
                              border-radius: 999px; font-size: 0.78rem; font-weight: 700; }

    /* ── Criteria mini card ── */
    .crit-card {
        background: var(--white);
        border: 1px solid var(--border);
        border-radius: 14px;
        padding: 16px;
        box-shadow: 0 2px 10px rgba(15,39,71,0.05);
        min-height: 130px;
    }
    .crit-card h4     { margin: 0 0 8px 0; font-size: 0.85rem; font-weight: 700; color: var(--navy); }
    .crit-card .score { font-size: 1.55rem; font-weight: 800; color: var(--navy); }
    .crit-card .meta  { color: var(--muted); font-size: 0.82rem; margin-top: 6px; line-height: 1.6; }

    /* ── Pill note ── */
    .pill {
        display: inline-block; padding: 6px 14px; background: #e8f0fb;
        border-radius: 999px; color: var(--navy); font-weight: 700;
        font-size: 0.83rem; margin-bottom: 10px;
    }

    /* ── Sidebar brand ── */
    .sidebar-brand {
        background: rgba(255,255,255,0.07);
        border: 1px solid rgba(255,255,255,0.12);
        border-radius: 12px;
        padding: 16px;
        margin-bottom: 14px;
    }
    .sidebar-brand h2 { margin: 0; font-size: 1.2rem; color: #fff !important; }
    .sidebar-brand p  { margin: 6px 0 0; font-size: 0.85rem; color: #b0c8e0 !important; }

    /* ── Assessment group section header ── */
    .group-header {
        font-size: 0.78rem; font-weight: 700; color: var(--navy);
        text-transform: uppercase; letter-spacing: 0.5px;
        padding: 10px 0 4px 0; border-bottom: 1px solid var(--border);
        margin-bottom: 12px;
    }

    /* ── Dataframe tweaks ── */
    .stDataFrame { border-radius: 12px; overflow: hidden; }

    /* ── Remarks card ── */
    .remarks-card {
        background: #f6f9fd;
        border-left: 5px solid var(--navy);
        border-radius: 0 12px 12px 0;
        padding: 18px 22px;
        line-height: 1.85;
        color: #374558;
        font-size: 0.95rem;
    }

    /* ── Section marker ── */
    .sec-marker {
        display: flex; align-items: center; gap: 10px;
        margin: 24px 0 14px;
    }
    .sec-marker-bar {
        width: 4px; height: 22px; background: #0f2747;
        border-radius: 2px; flex-shrink: 0;
    }
    .sec-marker-text {
        font-size: 1.05rem; font-weight: 700; color: #0f2747;
    }
    </style>
    """, unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# 4. HELPERS
# ─────────────────────────────────────────────────────────────────────────────

def initialize_session_state():
    if "page" not in st.session_state:
        st.session_state.page = "Home"


def fmt_currency(value: float) -> str:
    return f"RM {value:,.2f}"


def safe_name(name: str) -> str:
    s = str(name).strip()
    return s if s else "Not Provided"


def ratio_status(ratio: float) -> str:
    if ratio <= 2:  return "Low"
    if ratio <= 5:  return "Moderate"
    return "High"


def reset_assessment_state():
    keys = [
        "result_df", "final_percentage", "decision", "risk_level",
        "business_name", "business_type", "loan_amount", "loan_purpose",
        "monthly_revenue", "loan_income_ratio", "years_in_business",
        "calculated", "criteria_summary_df", "assessment_remarks",
    ]
    for k in keys:
        st.session_state.pop(k, None)


def result_card_html(label, value, badge_text, theme):
    return f"""
    <div class="result-card" style="background:{theme['bg']};border:1.5px solid {theme['border']};">
        <div class="rc-label" style="color:{theme['accent']};">{label}</div>
        <div class="rc-value" style="color:{theme['accent']};">{value}</div>
        <div class="rc-badge" style="background:{theme['badge_bg']};color:{theme['badge_text']};">{badge_text}</div>
    </div>"""


def info_row(label, value):
    return f'<div class="row"><span class="lbl">{label}</span><span class="val">{value}</span></div>'


def section_marker(text: str):
    st.markdown(f"""
    <div class="sec-marker">
        <div class="sec-marker-bar"></div>
        <span class="sec-marker-text">{text}</span>
    </div>""", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# 5. CALCULATION
# ─────────────────────────────────────────────────────────────────────────────

def calculate_assessment(scores: dict, monthly_revenue: float, loan_amount: float):
    rows, total = [], 0.0
    for factor, weight in GLOBAL_WEIGHTS.items():
        score   = scores[factor]
        contrib = score * weight
        total  += contrib
        rows.append({
            "Assessment Factor":  factor,
            "Applicant Rating":   score,
            "Factor Weight":      weight,
            "Score Contribution": round(contrib, 4),
        })

    result_df         = pd.DataFrame(rows)
    final_percentage  = (total / 5) * 100
    loan_income_ratio = (loan_amount / monthly_revenue) if monthly_revenue > 0 else 0.0

    if   final_percentage >= 70: decision, risk_level = "Approved",                 "Low Risk"
    elif final_percentage >= 50: decision, risk_level = "Approved with Conditions", "Moderate Risk"
    else:                        decision, risk_level = "Rejected",                 "High Risk"

    return result_df, final_percentage, loan_income_ratio, decision, risk_level


def build_criteria_summary(result_df: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for criterion, factors in ASSESSMENT_GROUPS.items():
        w_score   = result_df.loc[result_df["Assessment Factor"].isin(factors), "Score Contribution"].sum()
        raw_score = result_df.loc[result_df["Assessment Factor"].isin(factors), "Applicant Rating"].sum() / len(factors)
        rows.append({
            "Main Criterion":      criterion,
            "Criterion Weight":    CRITERIA_WEIGHTS[criterion],
            "Avg Rating (/ 5)":    round(raw_score, 2),
            "Criterion Score (%)": round((w_score / CRITERIA_WEIGHTS[criterion]) * 100, 2) if CRITERIA_WEIGHTS[criterion] else 0,
            "Weighted Score":      round(w_score, 4),
        })
    return pd.DataFrame(rows)


def generate_remarks(decision: str, risk_level: str, pct: float, r_status: str, years: int) -> str:
    if decision == "Approved":
        return (
            f"The applicant demonstrates a sound overall credit profile, recording a composite score of {pct:.2f}%. "
            f"All major evaluation criteria reflect adequate business strength and financial capacity. "
            f"Based on the current assessment, the application is recommended for approval subject to standard "
            f"documentation verification and applicable credit facility terms."
        )
    if decision == "Approved with Conditions":
        return (
            f"The applicant records a composite score of {pct:.2f}%, reflecting a moderate credit standing that "
            f"warrants additional scrutiny before a final lending decision is made. "
            f"The loan-to-income exposure is assessed as {r_status.lower()}, and the business has been in operation "
            f"for {years} year(s). Approval may be considered subject to enhanced monitoring, additional supporting "
            f"documentation, guarantor requirements, or revised facility terms as deemed appropriate by the lending officer."
        )
    return (
        f"The applicant records a composite score of {pct:.2f}%, which falls within the high-risk classification "
        f"under the current credit scoring model. "
        f"The overall assessment indicates that the business does not presently demonstrate sufficient financial "
        f"strength, creditworthiness, or repayment capacity to support the requested financing. "
        f"Based on the findings, the application is not recommended for approval at this time. "
        f"The applicant is advised to address identified weaknesses and reapply with improved business fundamentals "
        f"and supporting financial documentation."
    )


# ─────────────────────────────────────────────────────────────────────────────
# 6. PDF EXPORT
# ─────────────────────────────────────────────────────────────────────────────

def generate_pdf_report(result_df: pd.DataFrame, criteria_df: pd.DataFrame) -> bytes:
    """Generate a compact professional PDF report for loan officer documentation."""
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        leftMargin=12 * mm,
        rightMargin=12 * mm,
        topMargin=10 * mm,
        bottomMargin=13 * mm,
    )

    NAVY = colors.HexColor("#0f2747")
    NAVY2 = colors.HexColor("#173a63")
    SLATE = colors.HexColor("#5b6675")
    BG = colors.HexColor("#edf3f8")
    WHITE = colors.white
    BORDER = colors.HexColor("#d4dde8")
    MUTED = colors.HexColor("#6b7280")
    TEXT = colors.HexColor("#1f2937")

    risk_level = st.session_state["risk_level"]
    risk_colors = {
        "Low Risk": colors.HexColor("#1a7f4b"),
        "Moderate Risk": colors.HexColor("#c07a00"),
        "High Risk": colors.HexColor("#b91c1c"),
    }
    risk_color = risk_colors.get(risk_level, NAVY)

    generated_dt = datetime.datetime.now()
    generated = generated_dt.strftime("%d %B %Y, %I:%M %p")
    biz_name = safe_name(st.session_state["business_name"])

    base = getSampleStyleSheet()
    h_title = ParagraphStyle(
        "h_title", parent=base["Normal"], fontSize=14, leading=17,
        textColor=WHITE, fontName="Helvetica-Bold", alignment=TA_LEFT,
    )
    h_sub = ParagraphStyle(
        "h_sub", parent=base["Normal"], fontSize=7.3, leading=9.5,
        textColor=colors.HexColor("#cfe0f0"), fontName="Helvetica", alignment=TA_RIGHT,
    )
    h2 = ParagraphStyle(
        "h2", parent=base["Normal"], fontSize=9.2, leading=11,
        textColor=NAVY, fontName="Helvetica-Bold", spaceBefore=4, spaceAfter=3,
    )
    label_s = ParagraphStyle(
        "label_s", parent=base["Normal"], fontSize=6.2, leading=7.3,
        textColor=MUTED, fontName="Helvetica-Bold", alignment=TA_LEFT,
    )
    value_s = ParagraphStyle(
        "value_s", parent=base["Normal"], fontSize=7.3, leading=8.6,
        textColor=TEXT, fontName="Helvetica-Bold",
    )
    footer_s = ParagraphStyle(
        "footer_s", parent=base["Normal"], fontSize=6.3, leading=8,
        textColor=MUTED, fontName="Helvetica", alignment=TA_CENTER,
    )

    story = []
    W = A4[0] - 24 * mm

    def compact_spacer(height=5):
        story.append(Spacer(1, height))

    def section_title(title: str):
        story.append(Paragraph(title, h2))

    def info_pair(lbl, val):
        return [Paragraph(lbl.upper(), label_s), Paragraph(str(val), value_s)]

    # Header
    header_data = [[
        Paragraph(SYSTEM_NAME, h_title),
        Paragraph(
            f"Loan Assessment Report<br/>Generated: {generated}",
            h_sub,
        ),
    ]]
    header_tbl = Table(header_data, colWidths=[W * 0.56, W * 0.44])
    header_tbl.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), NAVY),
        ("LEFTPADDING", (0, 0), (-1, -1), 10),
        ("RIGHTPADDING", (0, 0), (-1, -1), 10),
        ("TOPPADDING", (0, 0), (-1, -1), 9),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 9),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("ALIGN", (1, 0), (1, 0), "RIGHT"),
    ]))
    story.append(header_tbl)
    compact_spacer(6)

    # Summary
    final_pct = st.session_state["final_percentage"]
    decision = st.session_state["decision"]

    sum_label = ParagraphStyle(
        "sum_label", parent=base["Normal"], fontSize=6.4, leading=7.4,
        textColor=MUTED, fontName="Helvetica-Bold", alignment=TA_CENTER,
    )
    sum_value = ParagraphStyle(
        "sum_value", parent=base["Normal"], fontSize=13, leading=15,
        textColor=NAVY, fontName="Helvetica-Bold", alignment=TA_CENTER,
    )
    sum_risk = ParagraphStyle(
        "sum_risk", parent=base["Normal"], fontSize=12, leading=14,
        textColor=risk_color, fontName="Helvetica-Bold", alignment=TA_CENTER,
    )

    cw = W / 3
    summary_data = [[
        [Paragraph("OVERALL CREDIT SCORE", sum_label), Paragraph(f"{final_pct:.2f}%", sum_value)],
        [Paragraph("RISK CLASSIFICATION", sum_label), Paragraph(risk_level, sum_risk)],
        [Paragraph("RECOMMENDED DECISION", sum_label), Paragraph(decision, sum_value)],
    ]]
    summary_tbl = Table(summary_data, colWidths=[cw, cw, cw])
    summary_tbl.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), BG),
        ("BOX", (0, 0), (-1, -1), 0.6, BORDER),
        ("INNERGRID", (0, 0), (-1, -1), 0.35, BORDER),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
    ]))
    story.append(summary_tbl)
    compact_spacer(7)

    # Business Information
    section_title("Business Information")

    li_ratio = st.session_state["loan_income_ratio"]
    r_status = ratio_status(li_ratio)
    biz_data = [
        info_pair("Business Name", biz_name) +
        info_pair("Loan Amount Requested", fmt_currency(st.session_state["loan_amount"])),
        info_pair("Business Type", st.session_state["business_type"]) +
        info_pair("Loan Purpose", st.session_state["loan_purpose"]),
        info_pair("Years in Business", f"{st.session_state['years_in_business']} year(s)") +
        info_pair("Monthly Revenue", fmt_currency(st.session_state["monthly_revenue"])),
        info_pair("Loan-to-Income Ratio", f"{li_ratio:.2f}×") +
        ["", ""],
    ]
    biz_tbl = Table(biz_data, colWidths=[W * 0.16, W * 0.34, W * 0.18, W * 0.32])
    biz_tbl.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), WHITE),
        ("BOX", (0, 0), (-1, -1), 0.45, BORDER),
        ("INNERGRID", (0, 0), (-1, -1), 0.28, BORDER),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ("LEFTPADDING", (0, 0), (-1, -1), 7),
        ("RIGHTPADDING", (0, 0), (-1, -1), 7),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
    ]))
    story.append(biz_tbl)
    compact_spacer(6)


    # Main Criteria Summary
    section_title("Main Criteria Summary")

    cr_head_s = ParagraphStyle(
        "cr_head_s", parent=base["Normal"], fontSize=6.8, leading=8,
        textColor=WHITE, fontName="Helvetica-Bold", alignment=TA_CENTER,
    )
    cr_val_s = ParagraphStyle(
        "cr_val_s", parent=base["Normal"], fontSize=9, leading=10.2,
        textColor=NAVY, fontName="Helvetica-Bold", alignment=TA_CENTER,
    )
    cr_sub_s = ParagraphStyle(
        "cr_sub_s", parent=base["Normal"], fontSize=6.4, leading=7.5,
        textColor=SLATE, fontName="Helvetica", alignment=TA_CENTER,
    )

    cw4 = W / 4
    crit_rows = criteria_df.to_dict("records")
    cr_header = [[Paragraph(r["Main Criterion"], cr_head_s) for r in crit_rows]]
    cr_values = [[
        [
            Paragraph(f"{r['Avg Rating (/ 5)']:.2f} / 5", cr_val_s),
            Paragraph(f"Performance: {r['Criterion Score (%)']:.1f}%", cr_sub_s),
            Paragraph(f"Weight: {r['Criterion Weight']:.4f} · Score: {r['Weighted Score']:.4f}", cr_sub_s),
        ]
        for r in crit_rows
    ]]

    crit_tbl = Table(cr_header + cr_values, colWidths=[cw4] * 4)
    crit_tbl.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), NAVY2),
        ("BACKGROUND", (0, 1), (-1, 1), WHITE),
        ("BOX", (0, 0), (-1, -1), 0.45, BORDER),
        ("INNERGRID", (0, 0), (-1, -1), 0.3, BORDER),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ("LEFTPADDING", (0, 0), (-1, -1), 4),
        ("RIGHTPADDING", (0, 0), (-1, -1), 4),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
    ]))
    story.append(crit_tbl)
    compact_spacer(6)

    # Detailed Assessment Factors
    section_title("Detailed Assessment Factors")

    th_s = ParagraphStyle(
        "th_s", parent=base["Normal"], fontSize=6.8, leading=8,
        textColor=WHITE, fontName="Helvetica-Bold", alignment=TA_CENTER,
    )
    td_s = ParagraphStyle(
        "td_s", parent=base["Normal"], fontSize=7.3, leading=8.5,
        textColor=TEXT, fontName="Helvetica",
    )
    td_r = ParagraphStyle(
        "td_r", parent=base["Normal"], fontSize=7.3, leading=8.5,
        textColor=TEXT, fontName="Helvetica", alignment=TA_CENTER,
    )

    pdf_df = result_df.sort_values("Score Contribution", ascending=False).reset_index(drop=True)

    factor_header = [[
        Paragraph("Rank", th_s),
        Paragraph("Assessment Factor", th_s),
        Paragraph("Rating", th_s),
        Paragraph("Factor Weight", th_s),
        Paragraph("Score Contribution", th_s),
    ]]

    factor_rows = []
    for idx, row in pdf_df.iterrows():
        factor_rows.append([
            Paragraph(str(idx + 1), td_r),
            Paragraph(row["Assessment Factor"], td_s),
            Paragraph(str(int(row["Applicant Rating"])), td_r),
            Paragraph(f"{row['Factor Weight']:.4f}", td_r),
            Paragraph(f"{row['Score Contribution']:.4f}", td_r),
        ])

    factor_tbl = Table(
        factor_header + factor_rows,
        colWidths=[W * 0.08, W * 0.40, W * 0.12, W * 0.18, W * 0.22],
        repeatRows=1,
    )

    style_cmds = [
        ("BACKGROUND", (0, 0), (-1, 0), NAVY),
        ("BOX", (0, 0), (-1, -1), 0.45, BORDER),
        ("INNERGRID", (0, 0), (-1, -1), 0.25, BORDER),
        ("TOPPADDING", (0, 0), (-1, -1), 3),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
        ("LEFTPADDING", (0, 0), (-1, -1), 5),
        ("RIGHTPADDING", (0, 0), (-1, -1), 5),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("ALIGN", (0, 0), (0, -1), "CENTER"),
        ("ALIGN", (2, 0), (-1, -1), "CENTER"),
    ]

    for i in range(1, len(factor_rows) + 1):
        style_cmds.append(("BACKGROUND", (0, i), (-1, i), BG if i % 2 == 0 else WHITE))

    factor_tbl.setStyle(TableStyle(style_cmds))
    story.append(factor_tbl)


    doc.build(story)


# ─────────────────────────────────────────────────────────────────────────────
# 7. SIDEBAR
# ─────────────────────────────────────────────────────────────────────────────

def render_sidebar() -> str:
    with st.sidebar:
        st.markdown(f"""
        <div class="sidebar-brand">
            <h2>🏦 {SYSTEM_NAME}</h2>
            <p>Credit Scoring Decision Support<br>for SME Loan Evaluation</p>
        </div>
        """, unsafe_allow_html=True)

        page = st.radio("Navigation", PAGES, index=PAGES.index(st.session_state.page))
        st.markdown("---")
        st.caption("Structured credit evaluation framework for SME loan officers.")

    st.session_state.page = page
    return page


# ─────────────────────────────────────────────────────────────────────────────
# 8. HOME PAGE
# ─────────────────────────────────────────────────────────────────────────────

def render_home():
    st.markdown(f"""
    <div class="hero">
        <h1>{SYSTEM_NAME}</h1>
        <p>
            This system assists loan officers in evaluating SME financing applications through a structured,
            weighted credit scoring model. It promotes consistency, transparency, and professionalism
            in every lending assessment.
        </p>
    </div>""", unsafe_allow_html=True)

    tiles = [
        ("Main Criteria",      "4",            "Financial Stability, Creditworthiness, Repayment Capacity, Borrower Reliability"),
        ("Assessment Factors", "12",           "Twelve weighted factors evaluated per applicant"),
        ("Scoring Method",     "Weighted",     "Expert-derived factor weights applied to each rating"),
        ("Decision Output",    "Loan Decision","Final score, risk classification, and recommendation"),
    ]
    cols = st.columns(4)
    for col, (label, val, note) in zip(cols, tiles):
        with col:
            st.markdown(f"""
            <div class="metric-tile">
                <div class="label">{label}</div>
                <div class="value">{val}</div>
                <div class="note">{note}</div>
            </div>""", unsafe_allow_html=True)

    st.markdown("## System Overview")
    st.markdown("""
    <div class="card">
        <p style="margin:0;line-height:1.85;color:#445166;">
            The system translates expert-assigned factor importance into a practical loan assessment workflow.
            Applicant performance is rated across predefined evaluation factors, combined with validated
            assessment weights, and converted into a final percentage score and a structured lending
            recommendation. The model is intended to support — not replace — professional judgment.
        </p>
    </div>""", unsafe_allow_html=True)

    st.markdown("## Assessment Workflow")
    steps = [
        ("1 · Applicant Information", "Capture business details, financing amount, business type, and purpose of the loan request."),
        ("2 · Performance Rating",    "Rate the applicant across 12 predefined factors on a scale of 1 (Very Weak) to 5 (Excellent)."),
        ("3 · Weighted Scoring",      "Apply validated factor weights to compute a composite credit score."),
        ("4 · Decision Output",       "Review the overall score, risk classification, factor contributions, and lending recommendation."),
    ]
    cols = st.columns(4)
    for col, (title, desc) in zip(cols, steps):
        with col:
            st.markdown(f"""
            <div class="workflow-step">
                <h4>{title}</h4>
                <p>{desc}</p>
            </div>""", unsafe_allow_html=True)

    st.markdown("## Purpose")
    st.markdown("""
    <div class="card">
        <p style="margin:0;line-height:1.85;color:#445166;">
            This system provides a more structured, consistent, and transparent approach to SME loan evaluation.
            By organising key business, financial, and borrower-related considerations into a single weighted
            model, it supports decision quality while preserving the original assessment framework.
        </p>
    </div>""", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# 9. EVALUATION FACTORS PAGE
# ─────────────────────────────────────────────────────────────────────────────

def render_evaluation_factors():
    st.markdown("## Evaluation Factors and Assessment Weights")
    st.markdown("""
    <div class="card">
        <p style="margin:0;line-height:1.8;color:#445166;">
            This section presents the main evaluation criteria and detailed assessment factors used in the
            credit scoring model. The importance weights shown below are derived from expert analysis
            and are applied directly in the scoring calculation.
        </p>
    </div>""", unsafe_allow_html=True)

    st.markdown("### Main Evaluation Criteria")
    criteria_df = pd.DataFrame({
        "Evaluation Category": list(CRITERIA_WEIGHTS.keys()),
        "Assessment Weight":   [round(v, 4) for v in CRITERIA_WEIGHTS.values()],
    })
    st.dataframe(criteria_df, use_container_width=True, hide_index=True)

    st.markdown("### Detailed Assessment Factors")
    weight_df = (
        pd.DataFrame({
            "Assessment Factor": list(GLOBAL_WEIGHTS.keys()),
            "Factor Weight":     list(GLOBAL_WEIGHTS.values()),
        })
        .sort_values("Factor Weight", ascending=False)
        .reset_index(drop=True)
    )
    weight_df.insert(0, "Rank", range(1, len(weight_df) + 1))
    st.dataframe(weight_df, use_container_width=True, hide_index=True, height=460)

    st.markdown("### Top 5 Most Important Factors")
    st.table(weight_df.head(5)[["Rank", "Assessment Factor", "Factor Weight"]])

    st.markdown("""
    <div class="card">
        <span class="pill">Factor Weight Interpretation</span>
        <p style="margin:10px 0 0;line-height:1.8;color:#445166;">
            A higher factor weight means the factor has a stronger influence on the final credit score.
            Factors with larger weights contribute more substantially to the composite score when the
            applicant receives a high or low rating on that dimension.
        </p>
    </div>""", unsafe_allow_html=True)

    st.markdown("### Importance Ranking of Assessment Factors")
    chart_df = weight_df.sort_values("Factor Weight", ascending=True)
    fig, ax  = plt.subplots(figsize=(9, 5.2))
    bars     = ax.barh(chart_df["Assessment Factor"], chart_df["Factor Weight"],
                       color="#173a63", height=0.6)
    ax.set_xlabel("Factor Weight", fontsize=10)
    ax.set_title("Assessment Factor Importance Ranking", fontsize=11, pad=10)
    ax.grid(axis="x", linestyle="--", alpha=0.22)
    ax.spines[["top", "right"]].set_visible(False)
    ax.tick_params(axis="y", labelsize=9)
    ax.tick_params(axis="x", labelsize=9)
    for bar in bars:
        w = bar.get_width()
        ax.text(w + 0.003, bar.get_y() + bar.get_height() / 2,
                f"{w:.4f}", va="center", fontsize=8.5)
    ax.set_xlim(0, chart_df["Factor Weight"].max() + 0.045)
    plt.tight_layout()
    st.pyplot(fig, use_container_width=True)


# ─────────────────────────────────────────────────────────────────────────────
# 10. LOAN APPLICATION ASSESSMENT PAGE
# ─────────────────────────────────────────────────────────────────────────────

def render_assessment_form():
    # Constrain width on wide screens
    _, center, _ = st.columns([1, 5, 1])
    with center:
        st.markdown("## Loan Application Assessment")
        st.markdown("""
        <div class="card">
            <p style="margin:0;line-height:1.8;color:#445166;">
                Complete the applicant's business profile and assign ratings for each assessment factor.
                All ratings are processed using the credit scoring model to generate a lending recommendation.
            </p>
        </div>""", unsafe_allow_html=True)

        # ── Section 1: Business Information
        section_marker("Section 1 — Business Information")
        with st.container(border=True):
            c1, c2 = st.columns(2, gap="large")
            with c1:
                st.markdown("**Business Details**")
                business_name     = st.text_input("Business Name", placeholder="e.g. Syarikat Maju Jaya Sdn Bhd")
                business_type     = st.selectbox("Business Type", BUSINESS_TYPES)
                years_in_business = st.number_input("Years in Business", min_value=0, step=1)
            with c2:
                st.markdown("**Financing Request**")
                loan_amount     = st.number_input("Loan Amount Requested (RM)", min_value=0.0, step=1000.0)
                loan_purpose    = st.selectbox("Loan Purpose", LOAN_PURPOSES)
                monthly_revenue = st.number_input("Monthly Business Revenue (RM)", min_value=0.0, step=1000.0)

        # ── Section 2: Performance Rating
        section_marker("Section 2 — Applicant Performance Rating")
        st.markdown("""
        <div class="card" style="margin-bottom:16px;">
            <p style="margin:0 0 6px;color:#445166;line-height:1.7;">
                Assign a rating to each factor based on the applicant's current business condition.
                All sliders default to <strong>3 (Average)</strong>.
            </p>
            <p style="margin:0;font-weight:700;color:#0f2747;">
                Rating Scale: &nbsp; 1 = Very Weak &nbsp;·&nbsp; 2 = Weak &nbsp;·&nbsp; 3 = Average
                &nbsp;·&nbsp; 4 = Good &nbsp;·&nbsp; 5 = Excellent
            </p>
        </div>""", unsafe_allow_html=True)

        scores = {}
        for group, factors in ASSESSMENT_GROUPS.items():
            st.markdown(f"<div class='group-header'>{group}</div>", unsafe_allow_html=True)
            with st.container(border=True):
                for factor in factors:
                    scores[factor] = st.slider(factor, min_value=1, max_value=5, value=3)

        # ── Section 3: Submit
        section_marker("Section 3 — Calculate &amp; Submit")
        st.markdown("""
        <div class="card" style="margin-bottom:14px;">
            <p style="margin:0;color:#445166;line-height:1.7;">
                Once all ratings have been assigned, click <strong>Calculate Assessment Score</strong> to
                generate the composite credit score and recommended lending decision.
            </p>
        </div>""", unsafe_allow_html=True)

        if st.button("Calculate Assessment Score", use_container_width=True):
            result_df, final_pct, li_ratio, decision, risk_level = calculate_assessment(
                scores, monthly_revenue, loan_amount
            )
            criteria_df = build_criteria_summary(result_df)
            r_status    = ratio_status(li_ratio)
            remarks     = generate_remarks(decision, risk_level, final_pct, r_status, years_in_business)

            st.session_state.update({
                "result_df":           result_df,
                "final_percentage":    final_pct,
                "decision":            decision,
                "risk_level":          risk_level,
                "business_name":       business_name,
                "business_type":       business_type,
                "loan_amount":         loan_amount,
                "loan_purpose":        loan_purpose,
                "monthly_revenue":     monthly_revenue,
                "loan_income_ratio":   li_ratio,
                "years_in_business":   years_in_business,
                "calculated":          True,
                "criteria_summary_df": criteria_df,
                "assessment_remarks":  remarks,
            })
            st.success("Assessment completed. Review the result below or navigate to Assessment Result.")

        if st.session_state.get("calculated", False):
            if st.button("View Assessment Result →", use_container_width=True):
                st.session_state.page       = "Assessment Result"
                st.session_state["calculated"] = False
                st.rerun()


# ─────────────────────────────────────────────────────────────────────────────
# 11. ASSESSMENT RESULT DASHBOARD
# ─────────────────────────────────────────────────────────────────────────────

def render_result_dashboard():
    st.markdown("## Assessment Result Dashboard")

    if "result_df" not in st.session_state:
        st.warning("No assessment result found. Please complete the Loan Application Assessment first.")
        return

    result_df   = st.session_state["result_df"]
    final_pct   = st.session_state["final_percentage"]
    decision    = st.session_state["decision"]
    risk_level  = st.session_state["risk_level"]
    biz_name    = safe_name(st.session_state["business_name"])
    li_ratio    = st.session_state["loan_income_ratio"]
    years       = st.session_state["years_in_business"]
    criteria_df = st.session_state["criteria_summary_df"]
    remarks     = st.session_state["assessment_remarks"]
    r_status    = ratio_status(li_ratio)
    theme       = RISK_THEMES[risk_level]

    st.markdown("""
    <div class="card">
        <p style="margin:0;line-height:1.8;color:#445166;">
            Results are generated using validated assessment weights and applicant performance ratings
            entered in the assessment form. This dashboard is intended for loan officer review and documentation.
        </p>
    </div>""", unsafe_allow_html=True)

    # ── Result summary cards
    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown(result_card_html("Overall Credit Score", f"{final_pct:.2f}%",
                                     "Score out of 100%", theme), unsafe_allow_html=True)
    with c2:
        st.markdown(result_card_html("Risk Classification", risk_level,
                                     theme["risk_note"], theme), unsafe_allow_html=True)
    with c3:
        st.markdown(result_card_html("Recommended Decision", decision,
                                     theme["decision_note"], theme), unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Business profile
    st.markdown("### Business Profile & Financial Indicators")
    i1, i2 = st.columns(2,gap="medium")
    with i1:
        st.markdown(f"""
        <div class="info-tile">
            <h4>Business Profile</h4>
            {info_row("Business Name",     biz_name)}
            {info_row("Business Type",     st.session_state['business_type'])}
            {info_row("Years in Business", f"{years} year(s)")}
        </div>""", unsafe_allow_html=True)
    with i2:
        st.markdown(f"""
        <div class="info-tile">
            <h4>Financing Request</h4>
            {info_row("Loan Amount",     fmt_currency(st.session_state['loan_amount']))}
            {info_row("Loan Purpose",    st.session_state['loan_purpose'])}
            {info_row("Monthly Revenue", fmt_currency(st.session_state['monthly_revenue']))}
            {info_row("Loan-to-Income Ratio", f"{li_ratio:.2f}×")}
        </div>""", unsafe_allow_html=True)

    # ── Criteria summary
    st.markdown("### Main Criteria Summary")
    cols = st.columns(4)
    for col, row in zip(cols, criteria_df.to_dict("records")):
        with col:
            st.markdown(f"""
            <div class="crit-card">
                <h4>{row['Main Criterion']}</h4>
                <div class="score">{row['Avg Rating (/ 5)']:.2f} / 5</div>
                <div class="meta">
                    Performance: {row['Criterion Score (%)']:.1f}%<br>
                    Weight: {row['Criterion Weight']:.4f}<br>
                    Weighted Score: {row['Weighted Score']:.4f}
                </div>
            </div>""", unsafe_allow_html=True)

    # ── Chart + table (no card box — plain headings)
    display_df = result_df.copy()
    display_df["Factor Weight"]      = display_df["Factor Weight"].round(4)
    display_df["Score Contribution"] = display_df["Score Contribution"].round(4)
    compact_df = display_df.rename(columns={
        "Assessment Factor": "Factor",
        "Applicant Rating":  "Rating",
        "Factor Weight":     "Weight",
        "Score Contribution":"Score",
    })

    chart_col, table_col = st.columns([1.05, 1.15], gap="large")
    with chart_col:
        st.markdown("#### Score Contribution Chart")
        cdf = result_df.sort_values("Score Contribution", ascending=True)
        fig, ax = plt.subplots(figsize=(6.8, 4.4))
        ax.barh(cdf["Assessment Factor"], cdf["Score Contribution"],
                color=theme["accent"], height=0.58)
        ax.set_xlabel("Score Contribution", fontsize=9)
        ax.set_title("Contribution by Assessment Factor", fontsize=10, pad=8)
        ax.grid(axis="x", linestyle="--", alpha=0.22)
        ax.spines[["top", "right"]].set_visible(False)
        ax.tick_params(axis="y", labelsize=8.5)
        ax.tick_params(axis="x", labelsize=8.5)
        for bar in ax.patches:
            w = bar.get_width()
            ax.text(w + 0.006, bar.get_y() + bar.get_height() / 2,
                    f"{w:.4f}", va="center", fontsize=8)
        ax.set_xlim(0, cdf["Score Contribution"].max() + 0.12)
        plt.tight_layout()
        st.pyplot(fig, use_container_width=False)

    with table_col:
        st.markdown("#### Detailed Assessment Table")
        st.dataframe(
            compact_df,
            hide_index=True,
            use_container_width=True,
            height=388,
            column_config={
                "Factor": st.column_config.TextColumn("Factor",  width="medium"),
                "Rating": st.column_config.NumberColumn("Rating", width="small"),
                "Weight": st.column_config.NumberColumn("Weight", format="%.4f", width="small"),
                "Score":  st.column_config.NumberColumn("Score",  format="%.4f", width="small"),
            },
        )

    # ── Remarks
    st.markdown("### Assessment Remarks")
    st.markdown(f'<div class="remarks-card">{remarks}</div>', unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)

    # ── Export & actions
    st.markdown("### Export & Next Action")
    slug    = safe_name(st.session_state["business_name"]).replace(" ", "_")
    pdf_bytes = generate_pdf_report(result_df, criteria_df)

    b1, b2 = st.columns(2)
    with b1:
        st.download_button(
            "⬇ Download Assessment Report (PDF)",
            data=pdf_bytes,
            file_name=f"{slug}_assessment_report.pdf",
            mime="application/pdf",
            use_container_width=True,
        )
    with b2:
        if st.button("Assess New Applicant", use_container_width=True):
            reset_assessment_state()
            st.session_state.page = "Loan Application Assessment"
            st.rerun()


# ─────────────────────────────────────────────────────────────────────────────
# 12. MAIN
# ─────────────────────────────────────────────────────────────────────────────

def main():
    initialize_session_state()
    apply_css()
    page = render_sidebar()

    if   page == "Home":                        render_home()
    elif page == "Evaluation Factors":          render_evaluation_factors()
    elif page == "Loan Application Assessment": render_assessment_form()
    elif page == "Assessment Result":           render_result_dashboard()


if __name__ == "__main__":
    main()