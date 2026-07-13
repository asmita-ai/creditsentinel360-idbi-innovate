# 🛡️ CreditSentinel 360
### 12-Month Forward Default Prediction & Early-Warning Platform
**IDBI Innovate 2026 — Problem Statement 4: Default Prediction Model**

---

## Problem

IDBI Bank's current default-prediction capability sits at **16–22% accuracy**,
relies on **structured data only**, and uses **fragmented methodologies**
across loan types and borrower segments — making it reactive rather than
predictive, and impossible to compare across a Retail loan vs. an MSME loan
vs. a Corporate facility.

## Solution

**CreditSentinel 360** is a unified, segment-aware AI engine that:

1. **Fuses structured + unstructured data** — bureau scores, EMI/DPD history,
   financial ratios *plus* NLP-derived signals from GST filing remarks,
   transaction narrations, and news/sector sentiment.
2. **Predicts 12 months forward** — estimates Probability of Default (PD)
   a full year ahead, not just current delinquency.
3. **Works across all loan types** — one segment-aware model (Retail, MSME,
   Corporate, Agri) instead of fragmented, siloed scorecards.
4. **Speaks one common language** — every account gets a **Sentinel Risk
   Score (0–1000)** and **Risk Grade (AAA–D)**, directly comparable across
   the whole portfolio.
5. **Explains itself** — a plain-language "top risk drivers" layer for every
   score, so credit teams see *why*, not just *what*.

**Result on held-out synthetic test data:** ~90% default-capture recall
(vs. the legacy 16–22%), ROC-AUC 0.79.

---

## Repository Structure

```
idbi-default-predictor/
├── data/
│   ├── generate_data.py         # (see src/) synthetic portfolio generator
│   ├── loan_portfolio_synthetic.csv
│   └── scored_portfolio.csv     # portfolio scored by the trained model
├── src/
│   ├── generate_data.py         # structured + unstructured synthetic data
│   ├── train_model.py           # feature engineering, training, calibration
│   ├── explainability.py        # global feature-importance / explainability
│   ├── make_architecture_diagram.py
│   ├── make_process_flow.py
│   └── make_dashboard_mockup.py
├── models/
│   ├── sentinel_model.joblib    # trained calibrated model
│   ├── metrics.json             # evaluation metrics
│   └── feature_importance.json
├── app/
│   └── streamlit_app.py         # interactive prototype dashboard
├── diagrams/                    # architecture, process-flow, charts
├── deck/
│   └── IDBI_Innovate_CreditSentinel360.pdf   # submission deck
└── requirements.txt
```

---

## Running the Prototype

```bash
pip install -r requirements.txt

# 1. Generate the synthetic structured + unstructured dataset
python src/generate_data.py

# 2. Train the segment-aware calibrated model
python src/train_model.py

# 3. Build the explainability chart
python src/explainability.py

# 4. Launch the dashboard
streamlit run app/streamlit_app.py
```

The dashboard has four views: **Portfolio Overview** (risk distribution,
early-warning watchlist), **Borrower Drill-down** (score + explanation +
raw unstructured signals for a single loan), **Model Performance**
(recall/precision/AUC vs. the legacy baseline), and **Score New Loan**
(a live scoring form simulating the API).

---

## Architecture

See `diagrams/architecture.png` — Data Sources → Unified Feature Store
(structured features + NLP engine) → Segment-Aware Scoring Engine →
Calibration → Common Interpretation Framework (Score + Grade +
Explainability) → Dashboard / Scoring API → RM/Credit Team Alerts.

## Tech Stack

- **ML:** Python, scikit-learn, XGBoost, probability calibration
- **NLP:** lexicon/sentiment-based stress-signal extraction (upgradeable to
  transformer embeddings with more data/compute)
- **App:** Streamlit (prototype), FastAPI (proposed production scoring API)
- **Cloud (proposed):** AWS SageMaker, Lambda + API Gateway, S3, QuickSight

## Data

This prototype uses a **synthetic dataset** (`src/generate_data.py`) that
mimics realistic structured banking fields and unstructured text
(GST remarks, transaction narrations, news headlines), with a latent
risk function driving a 12-month-forward default label — so the model has
genuine, learnable signal for demo purposes. In the IDBI sandbox, this
would be replaced by real core-banking, bureau, GST/ITR and transaction
data feeds.

## Note on the Deck / Screenshots

The dashboard mockup image in the deck (`diagrams/dashboard_mockup.png`)
is composed directly from the model's real outputs (not a placeholder).
For the final submission, run `streamlit run app/streamlit_app.py`
locally and swap in live screenshots / your deployment link and demo
video before submitting.

## Team

- Team Name: *Asmita*
- Team Leader: *Asmita Karmakar*
- Problem Statement: PS 4 — Default Prediction Model
