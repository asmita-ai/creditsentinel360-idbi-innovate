"""
CreditSentinel 360 - Streamlit prototype for IDBI Innovate 2026
Problem Statement 4: Default Prediction Model

Run: streamlit run app/streamlit_app.py
"""
import json
from pathlib import Path

import pandas as pd
import numpy as np
import streamlit as st
import plotly.express as px

ROOT = Path(__file__).resolve().parents[1]

st.set_page_config(page_title="CreditSentinel 360 | IDBI Innovate", page_icon=":shield:", layout="wide")

TEAL = "#0B7A66"
ORANGE = "#E8732C"
DARKTEAL = "#0E4C46"

st.markdown(f"""
<style>
.big-title {{font-size:2.1rem; font-weight:800; color:{DARKTEAL}; margin-bottom:0;}}
.subtitle {{color:#4B6660; font-size:1.05rem; margin-top:0;}}
div[data-testid="stMetricValue"] {{color:{DARKTEAL}; font-weight:700;}}
</style>
""", unsafe_allow_html=True)


@st.cache_data
def load_data():
    df = pd.read_csv(ROOT / "data" / "scored_portfolio.csv")
    return df


@st.cache_data
def load_metrics():
    with open(ROOT / "models" / "metrics.json") as f:
        return json.load(f)


@st.cache_data
def load_importance():
    with open(ROOT / "models" / "feature_importance.json") as f:
        return pd.DataFrame(json.load(f))


df = load_data()
metrics = load_metrics()
imp_df = load_importance()

st.markdown('<p class="big-title">CreditSentinel 360</p>', unsafe_allow_html=True)
st.markdown('<p class="subtitle">12-Month Forward Default Prediction & Early Warning System &nbsp;|&nbsp; '
            'IDBI Innovate 2026 - Problem Statement 4</p>', unsafe_allow_html=True)

tab1, tab2, tab3, tab4 = st.tabs(
    ["Portfolio Overview", "Borrower Drill-down", "Model Performance", "Score New Loan"]
)

# ------------------ TAB 1: Portfolio Overview ------------------
with tab1:
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total Accounts", f"{len(df):,}")
    c2.metric("Early-Warning Flags (12m)", f"{int(df['early_warning_flag'].sum()):,}",
               f"{df['early_warning_flag'].mean()*100:.1f}% of portfolio")
    c3.metric("Avg Sentinel Risk Score", f"{df['sentinel_risk_score'].mean():.0f} / 1000")
    c4.metric("Default-Capture Recall", f"{metrics['default_capture_recall']*100:.0f}%",
               "vs 16-22% legacy models")

    st.markdown("#### Portfolio Risk Distribution by Loan Type")
    colA, colB = st.columns([1.3, 1])
    with colA:
        fig = px.box(df, x="loan_type", y="sentinel_risk_score", color="loan_type",
                      color_discrete_sequence=px.colors.sequential.Teal_r)
        fig.update_layout(showlegend=False, height=380)
        st.plotly_chart(fig, use_container_width=True)
    with colB:
        grade_counts = df["risk_grade"].value_counts().reindex(
            ["AAA", "AA", "A", "BBB", "BB", "C", "D"]).fillna(0)
        fig2 = px.bar(x=grade_counts.index, y=grade_counts.values,
                       labels={"x": "Risk Grade", "y": "# Accounts"},
                       color=grade_counts.index,
                       color_discrete_sequence=px.colors.sequential.Oranges_r)
        fig2.update_layout(showlegend=False, height=380, title="Common Risk Grade Distribution")
        st.plotly_chart(fig2, use_container_width=True)

    st.markdown("#### Early-Warning Watchlist (Top 15 highest-risk accounts)")
    watch = df.sort_values("pd_12m", ascending=False).head(15)[
        ["loan_id", "loan_type", "borrower_segment", "sector", "sentinel_risk_score",
         "risk_grade", "pd_12m", "news_headline_text"]
    ]
    watch["pd_12m"] = (watch["pd_12m"] * 100).round(1).astype(str) + "%"
    st.dataframe(watch, use_container_width=True, hide_index=True)

# ------------------ TAB 2: Borrower Drill-down ------------------
with tab2:
    loan_id = st.selectbox("Select a Loan Account", df["loan_id"].tolist())
    row = df[df["loan_id"] == loan_id].iloc[0]

    c1, c2, c3 = st.columns([1, 1, 2])
    with c1:
        st.metric("Sentinel Risk Score", f"{int(row['sentinel_risk_score'])}/1000")
        st.metric("Risk Grade", row["risk_grade"])
    with c2:
        st.metric("12-Month PD", f"{row['pd_12m']*100:.1f}%")
        st.metric("Early Warning", "FLAGGED" if row["early_warning_flag"] else "Normal")
    with c3:
        st.write(f"**Loan Type:** {row['loan_type']}  |  **Segment:** {row['borrower_segment']}  |  **Sector:** {row['sector']}")
        st.write(f"**Bureau Score:** {int(row['bureau_score'])}  |  **EMI/Income:** {row['emi_to_income_ratio']:.2f}  "
                  f"|  **DPD (12m max):** {int(row['dpd_last_12m_max'])} days")

    st.markdown("##### Unstructured Data Signals")
    u1, u2, u3 = st.columns(3)
    u1.info(f"**News:** {row['news_headline_text']}")
    u2.warning(f"**Transaction Narration:** {row['txn_narration_sample']}")
    u3.error(f"**GST Remark:** {row['gst_remark_text']}") if "DELAYED" in str(row['gst_remark_text']) \
        else u3.success(f"**GST Remark:** {row['gst_remark_text']}")

    st.markdown("##### Why this score? (Explainability - Common Interpretation Framework)")
    st.dataframe(imp_df, use_container_width=True, hide_index=True)
    st.caption("Every score is traceable to the same set of plain-language drivers, "
               "regardless of loan type - enabling consistent, comparable, actionable decisions "
               "across Retail, MSME, Corporate and Agri portfolios.")

# ------------------ TAB 3: Model Performance ------------------
with tab3:
    st.markdown("#### Model Performance vs Legacy Baseline")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("ROC-AUC", metrics["roc_auc"])
    c2.metric("Default-Capture Recall", f"{metrics['default_capture_recall']*100:.0f}%")
    c3.metric("Precision @ Threshold", f"{metrics['precision_at_threshold']*100:.0f}%")
    c4.metric("F1 Score", metrics["f1_at_threshold"])

    st.info(f"**Legacy structured-only, fragmented models:** {metrics['baseline_legacy_accuracy_range']} "
            f"default-identification accuracy.  \n"
            f"**CreditSentinel 360:** {metrics['default_capture_recall']*100:.0f}% of true 12-month defaults "
            f"correctly identified in advance (test set n={metrics['n_test']}), using a unified "
            f"structured + unstructured, segment-aware model.")

    cm = metrics["confusion_matrix"]
    cm_df = pd.DataFrame(
        [[cm["TN"], cm["FP"]], [cm["FN"], cm["TP"]]],
        index=["Actual: No Default", "Actual: Default"],
        columns=["Predicted: No Default", "Predicted: Default"]
    )
    st.markdown("##### Confusion Matrix (held-out test set)")
    st.dataframe(cm_df, use_container_width=True)

    st.markdown("##### Global Risk Drivers")
    fig3 = px.bar(imp_df.sort_values("importance"), x="importance", y="friendly", orientation="h",
                   color_discrete_sequence=[TEAL])
    fig3.update_layout(height=420, yaxis_title="", xaxis_title="Relative Importance")
    st.plotly_chart(fig3, use_container_width=True)

# ------------------ TAB 4: Score New Loan ------------------
with tab4:
    st.markdown("#### Score a New / Hypothetical Loan Account")
    st.caption("Simulates the scoring API a Loan Origination or Early-Warning System would call.")
    colf1, colf2, colf3 = st.columns(3)
    with colf1:
        loan_type_in = st.selectbox("Loan Type", sorted(df["loan_type"].unique()))
        bureau_in = st.slider("Bureau Score", 300, 900, 700)
        emi_in = st.slider("EMI-to-Income Ratio", 0.0, 1.3, 0.35)
    with colf2:
        dpd_in = st.slider("Max DPD (last 12m)", 0, 180, 5)
        restructures_in = st.slider("Prior Restructures", 0, 5, 0)
        sector_stress_in = st.slider("Sector Stress Index", 0.0, 1.0, 0.4)
    with colf3:
        news_sent_in = st.slider("News Sentiment (-1 negative, +1 positive)", -1.0, 1.0, 0.0)
        gst_delay_in = st.slider("GST Filing Delay (days)", 0, 120, 5)
        collateral_in = st.slider("Collateral Coverage Ratio", 0.0, 2.5, 0.9)

    if st.button("Score This Account", type="primary"):
        # simplified transparent scoring heuristic mirroring the trained model's logit,
        # for an instant, explainable demo without a live API round-trip
        logit = (
            -4.2 + 4.0 * (1 - (bureau_in - 300) / 600) + 2.0 * max(emi_in - 0.4, 0)
            + 0.035 * dpd_in + 1.4 * sector_stress_in + 0.9 * restructures_in
            + 0.015 * gst_delay_in - 1.6 * news_sent_in - 0.8 * collateral_in
        )
        pd_est = 1 / (1 + np.exp(-logit))
        score = int((1 - pd_est) * 1000)
        bins = [0, 300, 450, 600, 700, 800, 870, 1000]
        labels = ["D", "C", "BB", "BBB", "A", "AA", "AAA"]
        grade = labels[max(0, min(np.digitize(score, bins) - 1, len(labels) - 1))]

        r1, r2, r3 = st.columns(3)
        r1.metric("12-Month PD", f"{pd_est*100:.1f}%")
        r2.metric("Sentinel Risk Score", f"{score}/1000")
        r3.metric("Risk Grade", grade)
        if pd_est >= metrics["operating_threshold"]:
            st.error("Early-Warning: recommend proactive review within this cycle.")
        else:
            st.success("Within normal risk appetite for continued standard monitoring.")

st.divider()
st.caption("CreditSentinel 360 - Prototype built for IDBI Innovate 2026, Problem Statement 4 "
           "(Default Prediction Model). Synthetic data used for demonstration; production "
           "deployment would connect to IDBI Bank's sandbox APIs and datasets.")
