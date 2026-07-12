"""
CreditSentinel 360 - Synthetic Data Generator
Generates a realistic structured + unstructured banking dataset spanning
multiple loan types and borrower segments, with a 12-month-forward
default label driven by a latent risk function (so the model has real
signal to learn, not random noise).

Loan types: Retail (Personal/Home/Auto), MSME, Corporate, Agri
Each record = one loan account as of an "observation date", with a
label = did this account default (90+ DPD) within the NEXT 12 months.
"""

import numpy as np
import pandas as pd
from pathlib import Path

RNG = np.random.default_rng(42)
N = 12000

LOAN_TYPES = ["Retail-Personal", "Retail-Home", "Retail-Auto", "MSME", "Corporate", "Agri"]
LOAN_WEIGHTS = [0.22, 0.14, 0.14, 0.28, 0.10, 0.12]

SEGMENTS = {
    "Retail-Personal": "Salaried",
    "Retail-Home": "Salaried",
    "Retail-Auto": "Self-Employed",
    "MSME": "Business-Owner",
    "Corporate": "Corporate-Entity",
    "Agri": "Agri-Borrower",
}

SECTORS = ["Manufacturing", "Trading", "Services", "Construction", "Agriculture",
           "Textiles", "IT/ITES", "Healthcare", "Real Estate", "Hospitality"]

NEWS_TEMPLATES_NEG = [
    "faces liquidity crunch amid delayed receivables",
    "reports order book decline for third straight quarter",
    "under scrutiny after key client contract termination",
    "flags working capital stress in latest filing",
    "sees promoter stake pledge increase sharply",
    "hit by raw material cost spike and margin pressure",
]
NEWS_TEMPLATES_POS = [
    "wins large government infrastructure contract",
    "reports record quarterly revenue growth",
    "expands operations with new manufacturing unit",
    "secures fresh equity investment round",
    "upgraded by rating agency on strong fundamentals",
]
NEWS_TEMPLATES_NEUTRAL = [
    "continues routine operations this quarter",
    "files regular GST returns on schedule",
    "renews existing supplier agreements",
]

TXN_NARRATIONS_STRESS = [
    "CHEQUE RETURN INSUFFICIENT FUNDS", "PENALTY CHARGE LATE EMI", "OD LIMIT BREACH",
    "ECS BOUNCE CHARGES", "MINIMUM BALANCE PENALTY", "LOAN RESTRUCTURE REQUEST",
]
TXN_NARRATIONS_NORMAL = [
    "SALARY CREDIT", "EMI AUTO DEBIT SUCCESS", "GST PAYMENT", "VENDOR PAYMENT NEFT",
    "FD RENEWAL", "UTILITY BILL PAYMENT",
]


def sample_loan_profile(n):
    loan_type = RNG.choice(LOAN_TYPES, size=n, p=LOAN_WEIGHTS)
    segment = np.array([SEGMENTS[lt] for lt in loan_type])
    sector = RNG.choice(SECTORS, size=n)
    return loan_type, segment, sector


def build_dataset():
    loan_type, segment, sector = sample_loan_profile(N)

    # ---------------- Structured features ----------------
    bureau_score = np.clip(RNG.normal(680, 90, N), 300, 900)
    loan_amount = np.clip(RNG.lognormal(mean=13.0, sigma=1.1, size=N), 5e4, 5e8)
    tenure_months = RNG.integers(12, 240, N)
    interest_rate = np.clip(RNG.normal(11.5, 3.0, N), 6, 24)
    emi_to_income = np.clip(RNG.normal(0.35, 0.15, N), 0.05, 1.3)
    collateral_coverage = np.clip(RNG.normal(0.9, 0.4, N), 0.0, 2.5)  # collateral/loan value
    utilization_ratio = np.clip(RNG.normal(0.55, 0.25, N), 0.0, 1.5)  # for CC/OD/working capital
    dpd_last_3m = np.clip(RNG.poisson(1.2, N) + (bureau_score < 620) * RNG.poisson(4, N), 0, 90)
    dpd_last_12m_max = np.clip(dpd_last_3m + RNG.poisson(3, N), 0, 180)
    num_restructures = RNG.poisson(0.15, N) + (bureau_score < 600).astype(int) * RNG.poisson(0.6, N)
    existing_npa_flag = (RNG.random(N) < 0.03).astype(int)
    sector_stress_index = np.clip(RNG.normal(0.4, 0.2, N), 0, 1)  # macro/sector risk proxy
    gst_filing_delay_days = np.clip(RNG.exponential(5, N), 0, 120)
    turnover_decline_pct = np.clip(RNG.normal(2, 12, N), -40, 60)  # YoY % (negative = growth)
    vintage_months = RNG.integers(3, 180, N)

    # ---------------- Unstructured signals ----------------
    # Latent "true stress" drives whether we sample negative news/txn narrations
    latent_stress = (
        0.35 * (1 - (bureau_score - 300) / 600)
        + 0.20 * np.clip(emi_to_income, 0, 1)
        + 0.15 * (dpd_last_12m_max / 180)
        + 0.15 * sector_stress_index
        + 0.10 * np.clip(turnover_decline_pct / 60, 0, 1)
        + 0.05 * (num_restructures > 0)
    )
    latent_stress = np.clip(latent_stress + RNG.normal(0, 0.05, N), 0, 1)

    news_sentiment_score = []
    news_headline = []
    txn_narration_sample = []
    gst_remark = []
    for ls in latent_stress:
        if RNG.random() < ls * 0.8:
            news_headline.append(RNG.choice(NEWS_TEMPLATES_NEG))
            news_sentiment_score.append(np.clip(RNG.normal(-0.6, 0.2), -1, 0))
        elif RNG.random() < 0.3:
            news_headline.append(RNG.choice(NEWS_TEMPLATES_POS))
            news_sentiment_score.append(np.clip(RNG.normal(0.6, 0.2), 0, 1))
        else:
            news_headline.append(RNG.choice(NEWS_TEMPLATES_NEUTRAL))
            news_sentiment_score.append(np.clip(RNG.normal(0.0, 0.15), -0.3, 0.3))

        if RNG.random() < ls * 0.7:
            txn_narration_sample.append(RNG.choice(TXN_NARRATIONS_STRESS))
        else:
            txn_narration_sample.append(RNG.choice(TXN_NARRATIONS_NORMAL))

        if RNG.random() < ls * 0.6:
            gst_remark.append("DELAYED FILING - MISMATCH IN ITC CLAIM")
        else:
            gst_remark.append("FILED ON TIME - NO DISCREPANCY")

    news_sentiment_score = np.array(news_sentiment_score)

    # ---------------- 12-month forward default label ----------------
    # Combine structured + unstructured-derived signal into a logit
    logit = (
        -4.2
        + 4.0 * (1 - (bureau_score - 300) / 600)
        + 2.0 * np.clip(emi_to_income - 0.4, 0, None)
        + 0.035 * dpd_last_12m_max
        + 1.4 * sector_stress_index
        + 0.9 * num_restructures
        + 2.5 * existing_npa_flag
        + 0.02 * np.clip(turnover_decline_pct, 0, None)
        + 0.015 * gst_filing_delay_days
        - 1.6 * news_sentiment_score          # negative sentiment -> higher risk
        - 0.8 * collateral_coverage
        + 0.6 * (txn_narration_sample and 0)  # placeholder, replaced below
    )
    stress_txn_flag = np.array([1 if t in TXN_NARRATIONS_STRESS else 0 for t in txn_narration_sample])
    logit = logit + 0.9 * stress_txn_flag
    logit = logit + RNG.normal(0, 0.6, N)  # idiosyncratic noise

    pd_prob = 1 / (1 + np.exp(-logit))
    default_12m = (RNG.random(N) < pd_prob).astype(int)

    df = pd.DataFrame({
        "loan_id": [f"L{100000+i}" for i in range(N)],
        "loan_type": loan_type,
        "borrower_segment": segment,
        "sector": sector,
        "bureau_score": bureau_score.round(0),
        "loan_amount": loan_amount.round(0),
        "tenure_months": tenure_months,
        "interest_rate": interest_rate.round(2),
        "emi_to_income_ratio": emi_to_income.round(3),
        "collateral_coverage_ratio": collateral_coverage.round(3),
        "utilization_ratio": utilization_ratio.round(3),
        "dpd_last_3m": dpd_last_3m,
        "dpd_last_12m_max": dpd_last_12m_max,
        "num_restructures": num_restructures,
        "existing_npa_flag": existing_npa_flag,
        "sector_stress_index": sector_stress_index.round(3),
        "gst_filing_delay_days": gst_filing_delay_days.round(1),
        "turnover_decline_pct_yoy": turnover_decline_pct.round(2),
        "vintage_months": vintage_months,
        "news_headline_text": news_headline,
        "news_sentiment_score": news_sentiment_score.round(3),
        "txn_narration_sample": txn_narration_sample,
        "gst_remark_text": gst_remark,
        "true_pd_12m": pd_prob.round(4),
        "default_12m": default_12m,
    })
    return df


if __name__ == "__main__":
    df = build_dataset()
    out = Path(__file__).resolve().parents[1] / "data" / "loan_portfolio_synthetic.csv"
    out.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(out, index=False)
    print(f"Saved {len(df)} rows to {out}")
    print(df["default_12m"].value_counts(normalize=True))
    print(df.groupby("loan_type")["default_12m"].mean())
