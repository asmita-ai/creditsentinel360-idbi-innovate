"""
CreditSentinel 360 - Explainability layer.
Trains a plain (uncalibrated) pipeline purely to extract global feature
importances so every risk score shown on the dashboard can be backed by a
plain-language 'why' -- the common interpretation framework the problem
statement asks for.
"""
import json
from pathlib import Path

import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder
from sklearn.pipeline import Pipeline
from xgboost import XGBClassifier

from train_model import NUMERIC_COLS, CATEGORICAL_COLS, engineer_features, DATA, ROOT

FRIENDLY_NAMES = {
    "bureau_score": "Credit Bureau Score",
    "dpd_last_12m_max": "Max Days-Past-Due (12m)",
    "emi_to_income_ratio": "EMI-to-Income Ratio",
    "num_restructures": "Prior Loan Restructures",
    "existing_npa_flag": "Existing NPA Flag",
    "sector_stress_index": "Sector Stress Index",
    "turnover_decline_pct_yoy": "YoY Turnover Decline",
    "gst_filing_delay_days": "GST Filing Delay (days)",
    "news_sentiment_score": "News Sentiment Score",
    "news_stress_kw_score": "Negative News Keyword Score",
    "gst_stress_kw_score": "GST Remark Stress Score",
    "txn_stress_flag": "Stressed Transaction Narration",
    "unstructured_risk_index": "Unstructured Risk Index (NLP)",
    "collateral_coverage_ratio": "Collateral Coverage Ratio",
    "utilization_ratio": "Credit Utilization Ratio",
    "dpd_last_3m": "Days-Past-Due (last 3m)",
    "vintage_months": "Account Vintage (months)",
    "loan_amount": "Loan Amount",
    "tenure_months": "Loan Tenure (months)",
    "interest_rate": "Interest Rate",
}


def main():
    raw = pd.read_csv(DATA)
    df = engineer_features(raw)
    X = df[NUMERIC_COLS + CATEGORICAL_COLS]
    y = df["default_12m"]

    pre = ColumnTransformer([
        ("num", "passthrough", NUMERIC_COLS),
        ("cat", OneHotEncoder(handle_unknown="ignore"), CATEGORICAL_COLS),
    ])
    model = XGBClassifier(
        n_estimators=350, max_depth=5, learning_rate=0.05, subsample=0.85,
        colsample_bytree=0.8, reg_lambda=1.5, eval_metric="logloss", random_state=42, n_jobs=4,
    )
    pipe = Pipeline([("pre", pre), ("clf", model)])
    pipe.fit(X, y)

    feat_names = pipe.named_steps["pre"].get_feature_names_out()
    importances = pipe.named_steps["clf"].feature_importances_
    imp_df = pd.DataFrame({"feature": feat_names, "importance": importances})
    imp_df = imp_df[imp_df["feature"].str.startswith("num__")]
    imp_df["feature"] = imp_df["feature"].str.replace("num__", "", regex=False)
    imp_df["friendly"] = imp_df["feature"].map(lambda f: FRIENDLY_NAMES.get(f, f))
    imp_df = imp_df.sort_values("importance", ascending=False).head(12)

    imp_df[["friendly", "importance"]].to_json(
        ROOT / "models" / "feature_importance.json", orient="records", indent=2
    )

    # Chart for the deck
    fig, ax = plt.subplots(figsize=(9, 6))
    colors = ["#0B7A66"] * len(imp_df)
    ax.barh(imp_df["friendly"][::-1], imp_df["importance"][::-1], color=colors)
    ax.set_xlabel("Relative Importance (drives Sentinel Risk Score)")
    ax.set_title("Top Risk Drivers - Structured + Unstructured (NLP) Signals", fontsize=13, fontweight="bold")
    for spine in ["top", "right"]:
        ax.spines[spine].set_visible(False)
    plt.tight_layout()
    out = ROOT / "diagrams" / "feature_importance.png"
    plt.savefig(out, dpi=160)
    print(f"Saved {out}")
    print(imp_df[["friendly", "importance"]])


if __name__ == "__main__":
    main()
