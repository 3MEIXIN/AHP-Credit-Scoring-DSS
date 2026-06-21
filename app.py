import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

st.set_page_config(
    page_title="AHP Credit Scoring DSS",
    page_icon="📊",
    layout="wide"
)

criteria_weights = {
    "Financial Stability": 0.4030,
    "Creditworthiness": 0.3570,
    "Repayment Capacity": 0.1581,
    "Borrower Reliability": 0.0818
}

global_weights = {
    "Financial Records": 0.1804,
    "Credit History": 0.1514,
    "Income Stability": 0.1358,
    "Repayment Period": 0.1328,
    "Savings and Current Account": 0.0868,
    "Monthly Income": 0.0824,
    "Existing Loan": 0.0729,
    "Debt Ratio": 0.0380,
    "Cash Liquidity": 0.0377,
    "Integrity": 0.0321,
    "Business Background": 0.0288,
    "Business Experience": 0.0209
}

pages = ["Home", "AHP Weights", "Applicant Evaluation", "Result Dashboard"]

if "page" not in st.session_state:
    st.session_state.page = "Home"

st.sidebar.title("Navigation")

page = st.sidebar.radio(
    "Go to",
    pages,
    index=pages.index(st.session_state.page)
)

st.session_state.page = page

if page == "Home":
    st.title("AHP-Based Credit Scoring Decision Support System")
    st.subheader("For SME Loan Evaluation")

    st.write("""
    This system supports SME loan evaluation by applying criteria and subcriteria
    weights derived from the Analytic Hierarchy Process (AHP).
    """)

    st.info("""
    System Flow:
    Literature Review → Expert Evaluation → AHP Weight Calculation → Applicant Scoring → Loan Recommendation
    """)

    st.header("System Objectives")
    st.write("""
    1. To apply AHP-derived weights in SME loan evaluation.  
    2. To calculate weighted credit scores based on applicant assessment.  
    3. To support loan officers in making structured and transparent decisions.
    """)

elif page == "AHP Weights":
    st.title("AHP Criteria and Global Weights")

    st.header("Main Criteria Weights")

    criteria_df = pd.DataFrame({
        "Criteria": list(criteria_weights.keys()),
        "Weight": list(criteria_weights.values())
    })

    st.dataframe(criteria_df, use_container_width=True)

    st.header("Subcriteria Global Weights")

    weight_df = pd.DataFrame({
        "Subcriteria": list(global_weights.keys()),
        "Global Weight": list(global_weights.values())
    })

    weight_df = weight_df.sort_values(by="Global Weight", ascending=False)
    weight_df.insert(0, "Rank", range(1, len(weight_df) + 1))

    st.dataframe(weight_df, use_container_width=True)

    st.info("""
    Based on the AHP global weights, Financial Records is the most influential subcriterion,
    while Business Experience has the lowest influence in the proposed credit scoring model.
    """)

    st.subheader("AHP Global Weight Ranking")

    chart_df = weight_df.sort_values(by="Global Weight", ascending=True)

    fig, ax = plt.subplots(figsize=(7, 3.5))
    ax.barh(chart_df["Subcriteria"], chart_df["Global Weight"])
    ax.set_xlabel("Global Weight")
    ax.set_ylabel("Subcriteria")
    ax.set_title("AHP Global Weight Ranking")
    st.pyplot(fig)

elif page == "Applicant Evaluation":
    st.title("Applicant Evaluation")

    st.header("Applicant Information")

    business_name = st.text_input("Business Name")

    business_type = st.selectbox(
        "Business Type",
        [
            "Retail",
            "Manufacturing",
            "Services",
            "Construction",
            "Food & Beverage",
            "Technology",
            "Others"
        ]
    )

    years_in_business = st.number_input(
        "Years in Business",
        min_value=0,
        step=1
    )

    loan_amount = st.number_input(
        "Loan Amount Requested (RM)",
        min_value=0.0,
        step=1000.0
    )

    loan_purpose = st.selectbox(
        "Loan Purpose",
        [
            "Working Capital",
            "Business Expansion",
            "Equipment Purchase",
            "Inventory Purchase",
            "Cash Flow Management",
            "Others"
        ]
    )

    monthly_revenue = st.number_input(
        "Monthly Business Revenue (RM)",
        min_value=0.0,
        step=1000.0
    )

    st.header("Subcriteria Assessment")
    st.caption("Rate each subcriterion from 1 to 5.")
    st.caption("1 = Very Poor, 2 = Poor, 3 = Fair, 4 = Good, 5 = Excellent")

    scores = {}

    for subcriterion in global_weights.keys():
        scores[subcriterion] = st.slider(
            subcriterion,
            min_value=1,
            max_value=5,
            value=3
        )

    if st.button("Calculate Credit Score"):
        result_data = []
        total_score = 0

        for subcriterion, weight in global_weights.items():
            score = scores[subcriterion]
            weighted_score = score * weight
            total_score += weighted_score

            result_data.append({
                "Subcriteria": subcriterion,
                "Applicant Score": score,
                "AHP Global Weight": weight,
                "Weighted Score": round(weighted_score, 4)
            })

        final_percentage = (total_score / 5) * 100

        if monthly_revenue > 0:
            loan_income_ratio = loan_amount / monthly_revenue
        else:
            loan_income_ratio = 0

        if final_percentage >= 80:
            decision = "Approved"
            risk_level = "Low Risk"
        elif final_percentage >= 60:
            decision = "Conditional Approval"
            risk_level = "Moderate Risk"
        elif final_percentage >= 40:
            decision = "Further Review Required"
            risk_level = "High Risk"
        else:
            decision = "Rejected"
            risk_level = "Very High Risk"

        st.session_state["result_df"] = pd.DataFrame(result_data)
        st.session_state["final_percentage"] = final_percentage
        st.session_state["decision"] = decision
        st.session_state["risk_level"] = risk_level
        st.session_state["business_name"] = business_name
        st.session_state["business_type"] = business_type
        st.session_state["loan_amount"] = loan_amount
        st.session_state["loan_purpose"] = loan_purpose
        st.session_state["monthly_revenue"] = monthly_revenue
        st.session_state["loan_income_ratio"] = loan_income_ratio
        st.session_state["years_in_business"] = years_in_business
        st.session_state["calculated"] = True

        st.success("Credit score calculated successfully.")

    if st.session_state.get("calculated", False):
        if st.button("View Result"):
            st.session_state.page = "Result Dashboard"
            st.session_state["calculated"] = False
            st.rerun()

elif page == "Result Dashboard":
    st.title("Result Dashboard")

    if "result_df" not in st.session_state:
        st.warning("No evaluation result found. Please complete the Applicant Evaluation first.")
    else:
        result_df = st.session_state["result_df"]
        decision = st.session_state["decision"]

        st.info("""
        This result is calculated using AHP-derived global weights obtained from expert evaluation.
        The applicant score is multiplied by each subcriterion weight to produce the final credit score.
        """)

        st.header("Executive Summary")

        col1, col2, col3 = st.columns(3)

        col1.metric("Final Credit Score", f"{st.session_state['final_percentage']:.2f}%")
        col2.metric("Risk Level", st.session_state["risk_level"])

        with col3:
            st.metric("Loan Recommendation", decision)

            if decision == "Approved":
                st.success("Recommended for approval")

            elif decision == "Conditional Approval":
                st.warning("Approval with additional review")

            elif decision == "Further Review Required":
                st.warning("Further assessment required")

            else:
                st.error("Not recommended for approval")

        st.header("Applicant Summary")

        col1, col2 = st.columns(2)

        col1.write(f"**Business Name:** {st.session_state['business_name']}")
        col1.write(f"**Business Type:** {st.session_state['business_type']}")
        col1.write(f"**Years in Business:** {st.session_state['years_in_business']}")

        col2.write(f"**Loan Amount Requested:** RM {st.session_state['loan_amount']:,.2f}")
        col2.write(f"**Monthly Revenue:** RM {st.session_state['monthly_revenue']:,.2f}")
        col2.write(f"**Loan Purpose:** {st.session_state['loan_purpose']}")

        st.header("Loan Evaluation Metrics")

        ratio = st.session_state["loan_income_ratio"]

        if ratio <= 2:
            ratio_status = "Low"
        elif ratio <= 5:
            ratio_status = "Moderate"
        else:
            ratio_status = "High"

        col1, col2 = st.columns(2)
        col1.metric("Loan-to-Income Ratio", f"{ratio:.2f}")
        col2.metric("Financing Risk", ratio_status)

        st.subheader("Recommendation Report")

        if decision == "Approved":
            st.success("""
            The applicant demonstrates satisfactory performance across the major evaluation criteria.
            Loan approval is recommended based on the AHP-weighted credit score.
            """)
        elif decision == "Conditional Approval":
            st.warning("""
            The applicant demonstrates moderate creditworthiness.
            Additional review or supporting documents are recommended before final approval.
            """)
        elif decision == "Further Review Required":
            st.warning("""
            The applicant presents several risk factors.
            Further investigation is recommended before making the final loan decision.
            """)
        else:
            st.error("""
            The applicant demonstrates a high level of credit risk.
            Loan approval is not recommended based on the current evaluation.
            """)

        st.subheader("Applicant Risk Profile")

        strength_df = result_df.sort_values(
            by="Weighted Score",
            ascending=False
        ).head(3)

        weak_df = result_df.sort_values(
            by=["Applicant Score", "AHP Global Weight"],
            ascending=[True, False]
        ).head(3)

        col1, col2 = st.columns(2)

        with col1:
            st.success("Strength Areas")
            for item in strength_df["Subcriteria"]:
                st.write(f"✓ {item}")

        with col2:
            st.error("Improvement Areas")
            for item in weak_df["Subcriteria"]:
                st.write(f"✗ {item}")

        st.subheader("Top Strength Factors")

        st.dataframe(
            strength_df[["Subcriteria", "Applicant Score", "AHP Global Weight", "Weighted Score"]],
            use_container_width=True
        )

        st.subheader("Key Weak Areas")

        st.dataframe(
            weak_df[["Subcriteria", "Applicant Score", "AHP Global Weight", "Weighted Score"]],
            use_container_width=True
        )

        st.subheader("AHP Criteria Contribution Chart")

        chart_df = result_df.sort_values(by="Weighted Score", ascending=True)

        fig, ax = plt.subplots(figsize=(7, 3.5))

        ax.barh(
            chart_df["Subcriteria"],
            chart_df["Weighted Score"]
        )

        ax.set_xlabel("Weighted Score")
        ax.set_title("Weighted Score Contribution by Subcriteria")

        plt.tight_layout()

        st.pyplot(fig, use_container_width=False)

        st.subheader("Detailed AHP Weighted Score Calculation")

        st.dataframe(result_df, use_container_width=True,height=300)

        st.subheader("Export Result")

        csv = result_df.to_csv(index=False).encode("utf-8")

        st.download_button(
            label="Download Evaluation Result as CSV",
            data=csv,
            file_name="ahp_credit_scoring_result.csv",
            mime="text/csv"
        )

        st.subheader("New Evaluation")

        if st.button("Evaluate New Applicant"):
            keys_to_clear = [
                "result_df",
                "final_percentage",
                "decision",
                "risk_level",
                "business_name",
                "business_type",
                "loan_amount",
                "loan_purpose",
                "monthly_revenue",
                "loan_income_ratio",
                "years_in_business",
                "calculated"
            ]

            for key in keys_to_clear:
                if key in st.session_state:
                    del st.session_state[key]

            st.session_state.page = "Applicant Evaluation"
            st.rerun()