import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

st.set_page_config(
    page_title="SME Loan Assessment System",
    page_icon="🏦",
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

assessment_groups = {
    "Financial Stability": [
        "Financial Records",
        "Income Stability",
        "Savings and Current Account"
    ],
    "Creditworthiness": [
        "Credit History",
        "Repayment Period",
        "Existing Loan"
    ],
    "Repayment Capacity": [
        "Monthly Income",
        "Cash Liquidity",
        "Debt Ratio"
    ],
    "Business Reliability": [
        "Integrity",
        "Business Background",
        "Business Experience"
    ]
}

pages = [
    "Home",
    "Evaluation Factors",
    "Loan Application Assessment",
    "Assessment Result"
]

if "page" not in st.session_state:
    st.session_state.page = "Home"

st.sidebar.markdown("## 🏦 SME Loan DSS")
st.sidebar.caption("Decision Support System")

page = st.sidebar.radio(
    "Navigation",
    pages,
    index=pages.index(st.session_state.page)
)

st.session_state.page = page


if page == "Home":
    st.title("🏦 SME Loan Assessment System")
    st.markdown("### Helping loan officers evaluate business loan applications")

    st.info("""
    This system supports SME loan evaluation by combining expert-defined importance levels
    with business performance ratings to generate an assessment score and recommended decision.
    """)

    st.markdown("---")

    col1, col2, col3, col4 = st.columns(4)

    col1.metric("Main Categories", "4")
    col2.metric("Assessment Factors", "12")
    col3.metric("Expert Input", "AHP")
    col4.metric("Output", "Loan Decision")

    st.header("How the System Works")

    st.write("""
    1. Important loan evaluation factors are identified from literature and expert input.  
    2. Each factor is assigned an importance level using the Analytic Hierarchy Process (AHP).  
    3. The loan officer rates the applicant's business performance from 1 to 5.  
    4. The system calculates the overall assessment score and suggests a loan decision.
    """)

    st.header("System Purpose")

    st.write("""
    This system is designed to support a more structured, consistent, and transparent
    loan assessment process for SME loan applications.
    """)


elif page == "Evaluation Factors":
    st.title("Loan Evaluation Factors")

    st.write("""
    This section shows the main categories and detailed factors used in the loan assessment.
    The importance levels are based on expert evaluation using the AHP method.
    """)

    st.header("Main Evaluation Categories")

    criteria_df = pd.DataFrame({
        "Evaluation Category": list(criteria_weights.keys()),
        "Importance Level": list(criteria_weights.values())
    })

    criteria_df["Importance Level"] = criteria_df["Importance Level"].round(4)

    st.dataframe(
        criteria_df,
        use_container_width=True,
        hide_index=True
    )

    st.header("Detailed Assessment Factors")

    weight_df = pd.DataFrame({
        "Assessment Factor": list(global_weights.keys()),
        "Importance Level": list(global_weights.values())
    })

    weight_df = weight_df.sort_values(by="Importance Level", ascending=False)
    weight_df.insert(0, "Rank", range(1, len(weight_df) + 1))

    st.dataframe(
        weight_df,
        use_container_width=True,
        hide_index=True,
        height=400
    )

    st.success("""
    Financial Records has the highest importance level in this model.
    This means that proper financial documentation plays an important role
    in SME loan assessment.
    """)

    st.subheader("Importance Ranking of Assessment Factors")

    chart_df = weight_df.sort_values(by="Importance Level", ascending=True)

    fig, ax = plt.subplots(figsize=(6, 3))
    ax.barh(chart_df["Assessment Factor"], chart_df["Importance Level"])
    ax.set_xlabel("Importance Level")
    ax.set_title("Importance Ranking of Assessment Factors")
    plt.tight_layout()

    st.pyplot(fig, use_container_width=False)


elif page == "Loan Application Assessment":
    st.title("Loan Application Assessment")

    st.header("Business Information")

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

    st.header("Business Performance Rating")

    st.caption("Rate each factor based on the applicant's business condition.")
    st.caption("1 = Very Weak, 2 = Weak, 3 = Average, 4 = Good, 5 = Excellent")

    scores = {}

    for group, factors in assessment_groups.items():
        with st.expander(group, expanded=True):
            for factor in factors:
                scores[factor] = st.slider(
                    factor,
                    min_value=1,
                    max_value=5,
                    value=3
                )

    if st.button("Calculate Assessment Score"):
        result_data = []
        total_score = 0

        for factor, weight in global_weights.items():
            score = scores[factor]
            weighted_score = score * weight
            total_score += weighted_score

            result_data.append({
                "Assessment Factor": factor,
                "Applicant Rating": score,
                "Importance Level": weight,
                "Score Contribution": round(weighted_score, 4)
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
            decision = "Approved with Conditions"
            risk_level = "Moderate Risk"
        elif final_percentage >= 40:
            decision = "Manual Review Required"
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

        st.success("Assessment completed successfully.")

    if st.session_state.get("calculated", False):
        if st.button("View Assessment Result"):
            st.session_state.page = "Assessment Result"
            st.session_state["calculated"] = False
            st.rerun()


elif page == "Assessment Result":
    st.title("Assessment Result")

    if "result_df" not in st.session_state:
        st.warning("No assessment result found. Please complete the loan application assessment first.")
    else:
        result_df = st.session_state["result_df"]
        decision = st.session_state["decision"]

        st.info("""
        This assessment is based on expert-defined importance levels and the applicant's
        performance across different business factors.
        """)

        st.header("Assessment Summary")

        col1, col2, col3 = st.columns(3)

        col1.metric(
            "Overall Assessment Score",
            f"{st.session_state['final_percentage']:.2f}%"
        )

        col2.metric(
            "Business Risk Level",
            st.session_state["risk_level"]
        )

        col3.metric(
            "Recommended Decision",
            decision
        )

        st.header("Business Profile")

        col1, col2 = st.columns(2)

        business_name_display = st.session_state["business_name"]
        if business_name_display == "":
            business_name_display = "Not provided"

        col1.write(f"**Business Name:** {business_name_display}")
        col1.write(f"**Business Type:** {st.session_state['business_type']}")
        col1.write(f"**Years in Business:** {st.session_state['years_in_business']}")

        col2.write(f"**Loan Amount Requested:** RM {st.session_state['loan_amount']:,.2f}")
        col2.write(f"**Monthly Revenue:** RM {st.session_state['monthly_revenue']:,.2f}")
        col2.write(f"**Loan Purpose:** {st.session_state['loan_purpose']}")

        st.header("Financial Indicators")

        ratio = st.session_state["loan_income_ratio"]

        if ratio <= 2:
            ratio_status = "Low"
        elif ratio <= 5:
            ratio_status = "Moderate"
        else:
            ratio_status = "High"

        col1, col2 = st.columns(2)

        col1.metric(
            "Loan Affordability Ratio",
            f"{ratio:.2f}"
        )

        col2.metric(
            "Financing Risk Assessment",
            ratio_status
        )

        st.subheader("Decision Explanation")

        if decision == "Approved":
            st.success("""
            The business shows strong overall performance based on the selected assessment factors.
            Loan approval is recommended.
            """)
        elif decision == "Approved with Conditions":
            st.warning("""
            The business shows acceptable performance, but some areas may require additional review.
            Loan approval may be considered with supporting documents or specific conditions.
            """)
        elif decision == "Manual Review Required":
            st.warning("""
            The business shows several risk areas. A manual review is recommended before making
            the final loan decision.
            """)
        else:
            st.error("""
            The business shows a high risk level based on the current assessment.
            Loan approval is not recommended.
            """)

        st.subheader("Business Risk Profile")

        strength_df = result_df.sort_values(
            by="Score Contribution",
            ascending=False
        ).head(3)

        weak_df = result_df.sort_values(
            by=["Applicant Rating", "Importance Level"],
            ascending=[True, False]
        ).head(3)

        col1, col2 = st.columns(2)


        with col1:
            st.success("Key Strengths")

            for item in strength_df["Assessment Factor"]:
                 st.write(f"✓ {item}")

        with col2:
            st.error("Areas for Improvement")

            for item in weak_df["Assessment Factor"]:
                st.write(f"• {item}")

        st.subheader("Key Strengths")

        st.dataframe(
            strength_df[[
                "Assessment Factor",
                "Applicant Rating",
                "Importance Level",
                "Score Contribution"
            ]],
            use_container_width=True,
            hide_index=True
        )

        st.subheader("Key Areas for Improvement")

        st.dataframe(
            weak_df[[
                "Assessment Factor",
                "Applicant Rating",
                "Importance Level",
                "Score Contribution"
            ]],
            use_container_width=True,
            hide_index=True
        )

        st.subheader("Factors Contributing to the Final Score")

        chart_df = result_df.sort_values(by="Score Contribution", ascending=True)

        fig, ax = plt.subplots(figsize=(7, 3.5))

        ax.barh(
            chart_df["Assessment Factor"],
            chart_df["Score Contribution"]
        )

        ax.set_xlabel("Score Contribution")
        ax.set_title("Contribution of Each Assessment Factor")

        plt.tight_layout()

        st.pyplot(fig, use_container_width=False)

        st.subheader("Detailed Score Breakdown")

        st.dataframe(
            result_df,
            use_container_width=True,
            hide_index=True,
            height=300
        )

        st.subheader("Export Result")

        csv = result_df.to_csv(index=False).encode("utf-8")

        st.download_button(
            label="Download Assessment Result as CSV",
            data=csv,
            file_name="sme_loan_assessment_result.csv",
            mime="text/csv"
        )

        st.subheader("New Assessment")

        if st.button("Assess New Applicant"):
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

            st.session_state.page = "Loan Application Assessment"
            st.rerun()

        st.markdown("---")
        st.caption("SME Loan Assessment Decision Support System | Final Year Project")