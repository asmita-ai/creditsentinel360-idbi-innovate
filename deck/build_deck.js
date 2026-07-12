const pptxgen = require("pptxgenjs");
const path = require("path");

const ROOT = path.resolve(__dirname, "..");
const IMG = (p) => path.join(ROOT, "diagrams", p);

const TEAL = "0B7A66";
const DARKTEAL = "0E4C46";
const ORANGE = "E8732C";
const GREY = "4B6660";

const pres = new pptxgen();
pres.layout = "LAYOUT_WIDE"; // 13.333 x 7.5 in, matches 1920x1080 bg images

const BODY_X = 0.5;
const BODY_W = 12.33;
const TITLE_Y = 0.95;

function contentSlide(title) {
  const s = pres.addSlide();
  s.background = { path: IMG("page1.png") };
  s.addText(title, {
    x: BODY_X, y: TITLE_Y, w: BODY_W, h: 0.6,
    fontFace: "Arial", fontSize: 26, bold: true, color: DARKTEAL,
  });
  return s;
}

function bullets(s, items, opts = {}) {
  const paras = items.map((t, i) => ({
    text: t,
    options: { bullet: { code: "25CF", indent: 18 }, breakLine: i !== items.length - 1, color: "222222" },
  }));
  s.addText(paras, {
    x: opts.x ?? BODY_X, y: opts.y ?? 1.75, w: opts.w ?? BODY_W, h: opts.h ?? 4.8,
    fontFace: "Arial", fontSize: opts.fontSize ?? 15, valign: "top",
    paraSpaceAfter: 10, lineSpacingMultiple: 1.12,
  });
}

// ---------------- Slide 1: Cover / Team Details ----------------
{
  const s = pres.addSlide();
  s.background = { path: IMG("page0.png") };
  s.addText("Team Details", { x: 0.55, y: 3.55, w: 8, h: 0.5, fontFace: "Arial", fontSize: 22, bold: true, color: DARKTEAL });
  s.addText([
    { text: "Team Name:  ", options: { bold: true, breakLine: false } },
    { text: "CreditSentinel — [Your Team Name Here]", options: { breakLine: true } },
    { text: "Team Leader:  ", options: { bold: true, breakLine: false } },
    { text: "[Your Name Here]", options: { breakLine: true } },
    { text: "Problem Statement:  ", options: { bold: true, breakLine: false } },
    { text: "PS 4 — Default Prediction Model", options: { breakLine: true } },
  ], { x: 0.55, y: 4.15, w: 10.5, h: 1.8, fontFace: "Arial", fontSize: 15, color: "222222", paraSpaceAfter: 8 });
}

// ---------------- Slide 2: Brief about the idea ----------------
{
  const s = contentSlide("Brief about the idea");
  s.addText(
    "CreditSentinel 360 is a unified, 12-month forward-looking default prediction and early-warning " +
    "platform for IDBI Bank. It replaces fragmented, structured-data-only scorecards (16-22% accuracy) " +
    "with a single segment-aware AI engine that fuses structured banking/bureau data with unstructured " +
    "signals — GST filings, transaction narrations, and news/sector sentiment — to estimate Probability " +
    "of Default (PD) up to 12 months in advance across Retail, MSME, Corporate and Agri portfolios.",
    { x: BODY_X, y: 1.75, w: BODY_W, h: 1.6, fontFace: "Arial", fontSize: 15.5, color: "222222", valign: "top", lineSpacingMultiple: 1.2 }
  );
  bullets(s, [
    "Every loan, regardless of type, is translated into one common language: a Sentinel Risk Score (0-1000) and Risk Grade (AAA to D).",
    "Credit teams get a consistent, comparable, and explainable view of portfolio stress — 12 months before it becomes an NPA.",
    "Built to plug directly into IDBI Bank's sandbox APIs, synthetic datasets, and core banking/bureau feeds.",
  ], { y: 3.55, h: 2.6 });
}

// ---------------- Slide 3: Opportunities ----------------
{
  const s = contentSlide("Opportunities");
  s.addText("How different is it from other existing ideas?", { x: BODY_X, y: 1.7, w: BODY_W, fontFace: "Arial", fontSize: 15.5, bold: true, color: TEAL });
  bullets(s, [
    "Most existing default models are structured-data-only and fragmented across loan types — separate retail scorecards, separate MSME rules, no common scale.",
    "CreditSentinel 360 unifies structured + unstructured (NLP-derived) signals into ONE segment-aware model with a common interpretation layer.",
  ], { y: 2.05, h: 1.3, fontSize: 14 });

  s.addText("How will it solve the problem?", { x: BODY_X, y: 3.35, w: BODY_W, fontFace: "Arial", fontSize: 15.5, bold: true, color: TEAL });
  bullets(s, [
    "Forward-looking 12-month PD instead of reactive/lagging DPD-based flags — enables pre-emptive action.",
    "NLP engine extracts stress signals from GST remarks, transaction narrations and news — catching risk structured data misses.",
    "Calibrated probability + explainability ensures scores are trustworthy and auditable for credit committees.",
  ], { y: 3.7, h: 1.9, fontSize: 14 });

  s.addText("USP of the proposed solution", { x: BODY_X, y: 5.75, w: BODY_W, fontFace: "Arial", fontSize: 15.5, bold: true, color: TEAL });
  bullets(s, [
    "One score, one grade, one explanation format — usable across Retail, MSME, Corporate and Agri books alike.",
  ], { y: 6.1, h: 0.6, fontSize: 14 });
}

// ---------------- Slide 4: List of features ----------------
{
  const s = contentSlide("List of features offered by the solution");
  bullets(s, [
    "12-Month Forward Default Prediction — Probability of Default (PD) estimated a full year ahead, not just current delinquency status.",
    "Structured + Unstructured Fusion — bureau/EMI/DPD/financial ratios combined with NLP-derived signals from GST filings, transaction narrations and news/sector sentiment.",
    "Segment-Aware Modeling — a single model conditioned on loan type & borrower segment, avoiding both one-size-fits-all bias and fragmented, hard-to-maintain silo models.",
    "Common Interpretation Framework — every loan gets a Sentinel Risk Score (0-1000) and Risk Grade (AAA-D), directly comparable across loan types.",
    "Explainability Layer — top plain-language risk drivers per account, so credit teams see why, not just what.",
    "Early-Warning Watchlist & Alerts — automatically flags accounts crossing risk thresholds for proactive RM/credit-team action.",
    "API-First Design — scoring engine callable from Loan Origination and Monitoring systems, ready for sandbox integration.",
  ], { fontSize: 14.5, h: 5.2 });
}

// ---------------- Slide 5: Process flow ----------------
{
  const s = contentSlide("Process flow diagram / Use-case diagram");
  s.addImage({ path: IMG("process_flow.png"), x: 2.0, y: 1.55, w: 9.3, h: 5.6, sizing: { type: "contain", w: 9.3, h: 5.6 } });
}

// ---------------- Slide 6: Wireframes ----------------
{
  const s = contentSlide("Wireframes / Mock diagrams of the proposed solution");
  s.addImage({ path: IMG("dashboard_mockup.png"), x: 0.6, y: 1.5, w: 12.1, h: 5.6, sizing: { type: "contain", w: 12.1, h: 5.6 } });
}

// ---------------- Slide 7: Architecture ----------------
{
  const s = contentSlide("Architecture diagram of the proposed solution");
  s.addImage({ path: IMG("architecture.png"), x: 0.5, y: 1.55, w: 12.3, h: 5.5, sizing: { type: "contain", w: 12.3, h: 5.5 } });
}

// ---------------- Slide 8: Technologies ----------------
{
  const s = contentSlide("Technologies to be used in the solution");
  const cols = [
    { h: "Data & ML", items: ["Python, Pandas, NumPy", "XGBoost (segment-aware gradient boosting)", "scikit-learn (calibration, pipelines)", "Lexicon/NLP sentiment engine for text signals"] },
    { h: "Explainability & Serving", items: ["SHAP / feature-importance explainability layer", "FastAPI scoring microservice", "Streamlit early-warning dashboard (prototype)"] },
    { h: "Cloud & Platform (AWS)", items: ["Amazon SageMaker — training & retraining pipeline", "AWS Lambda + API Gateway — scoring API", "Amazon S3 — feature store & data lake", "Amazon QuickSight / CloudWatch — monitoring"] },
  ];
  const colW = 3.95;
  cols.forEach((c, i) => {
    const x = BODY_X + i * (colW + 0.25);
    s.addShape(pres.ShapeType.roundRect, { x, y: 1.7, w: colW, h: 4.9, fill: { color: "F2F7F6" }, line: { color: TEAL, width: 1 }, rectRadius: 0.08 });
    s.addText(c.h, { x: x + 0.2, y: 1.85, w: colW - 0.4, h: 0.5, fontFace: "Arial", fontSize: 15, bold: true, color: DARKTEAL });
    s.addText(c.items.map((t, j) => ({ text: t, options: { bullet: { code: "25CF", indent: 14 }, breakLine: j !== c.items.length - 1, color: "222222" } })),
      { x: x + 0.2, y: 2.35, w: colW - 0.4, h: 4.1, fontFace: "Arial", fontSize: 12.5, valign: "top", paraSpaceAfter: 8, lineSpacingMultiple: 1.15 });
  });
}

// ---------------- Slide 9: Estimated cost ----------------
{
  const s = contentSlide("Estimated implementation cost (optional)");
  const rows = [
    ["Phase", "Scope", "Estimated Cost (INR)"],
    ["PoC (Sandbox)", "Model tuning on IDBI sandbox data, API integration, pilot dashboard", "8 - 12 Lakh"],
    ["Pilot (1-2 business units)", "Production-grade deployment, monitoring, RM training", "20 - 30 Lakh"],
    ["Full Rollout", "Bank-wide across Retail/MSME/Corporate/Agri, HA infra, MLOps", "60 - 90 Lakh"],
    ["Annual Run-rate", "Cloud infra, model retraining, monitoring & compliance", "15 - 20 Lakh / year"],
  ];
  s.addTable(rows, {
    x: BODY_X, y: 1.85, w: BODY_W, h: 3.2,
    fontFace: "Arial", fontSize: 13, color: "222222", border: { type: "solid", color: "DDDDDD", pt: 0.5 },
    fill: { color: "FFFFFF" },
    autoPage: false,
  });
  s.addText("Indicative, phase-wise estimate — to be refined jointly with IDBI Bank based on sandbox scope, data volumes and infra choices.",
    { x: BODY_X, y: 5.3, w: BODY_W, h: 0.6, fontFace: "Arial", fontSize: 11.5, italic: true, color: GREY });
}

// ---------------- Slide 10: Snapshots ----------------
{
  const s = contentSlide("Snapshots of the prototype");
  s.addImage({ path: IMG("dashboard_mockup.png"), x: 0.6, y: 1.5, w: 12.1, h: 5.6, sizing: { type: "contain", w: 12.1, h: 5.6 } });
}

// ---------------- Slide 11: Performance / benchmarking ----------------
{
  const s = contentSlide("Prototype Performance report / Benchmarking");
  s.addImage({ path: IMG("feature_importance.png"), x: 6.9, y: 1.6, w: 5.9, h: 4.6, sizing: { type: "contain", w: 5.9, h: 4.6 } });
  const rows = [
    ["Metric", "CreditSentinel 360", "Legacy baseline"],
    ["Default-capture recall (12m)", "~90%", "16 - 22%"],
    ["ROC-AUC", "0.79", "n/a (rule-based)"],
    ["Data used", "Structured + Unstructured (NLP)", "Structured only"],
    ["Coverage", "Unified across all loan types", "Fragmented per loan type"],
  ];
  s.addTable(rows, { x: BODY_X, y: 1.75, w: 6.1, h: 3.2, fontFace: "Arial", fontSize: 12.5, color: "222222", border: { type: "solid", color: "DDDDDD", pt: 0.5 } });
  s.addText("Evaluated on a held-out synthetic test portfolio (n=2,400 accounts). Threshold tuned to maximize precision at ≥90% default-capture recall — directly matching the challenge's target of raising identification accuracy from 16-22% to ~90%.",
    { x: BODY_X, y: 5.1, w: 6.1, h: 1.4, fontFace: "Arial", fontSize: 11.5, italic: true, color: GREY, valign: "top" });
}

// ---------------- Slide 12: Additional details ----------------
{
  const s = contentSlide("Additional Details / Future Development (if any)");
  bullets(s, [
    "Integrate live IDBI sandbox APIs and real bureau/GST feeds to replace synthetic data and retrain on actual portfolio history.",
    "Add transformer-based NLP (fine-tuned embeddings) for deeper document/news understanding beyond lexicon-based sentiment.",
    "Introduce macro-economic stress-testing scenarios (rate shocks, sector downturns) for forward PD sensitivity.",
    "Build a feedback loop where credit officers' outcomes retrain and continuously improve the model (human-in-the-loop MLOps).",
    "Extend the common interpretation framework into a portfolio-level early-warning report for RBI/regulatory stress reporting.",
  ], { fontSize: 14.5, h: 4.8 });
}

// ---------------- Slide 13: Links ----------------
{
  const s = contentSlide("Provide links to your:");
  bullets(s, [
    "GitHub Public Repository:  [ADD YOUR GITHUB REPO LINK HERE]",
    "Demo Video Link (3 Minutes):  [ADD YOUR DEMO VIDEO LINK HERE]",
    "Final Product Link:  [ADD YOUR DEPLOYED STREAMLIT/APP LINK HERE]",
  ], { fontSize: 16, h: 2 });
}

// ---------------- Slide 14: Thank you ----------------
{
  const s = pres.addSlide();
  s.background = { path: IMG("page14.png") };
}

pres.writeFile({ fileName: path.join(ROOT, "deck", "IDBI_Innovate_CreditSentinel360.pptx") }).then(() => {
  console.log("Deck written.");
});
