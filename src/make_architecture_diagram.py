from graphviz import Digraph

TEAL = "#0B7A66"
ORANGE = "#E8732C"
DARKTEAL = "#0E4C46"
LIGHT = "#F2F7F6"

g = Digraph("architecture", format="png")
g.attr(rankdir="LR", bgcolor="white", fontname="Helvetica", splines="ortho", nodesep="0.4", ranksep="0.7")
g.attr("node", fontname="Helvetica", fontsize="11", style="filled", shape="box",
       margin="0.18,0.12", color=DARKTEAL, penwidth="1.3")

def cluster(name, label, color, nodes):
    with g.subgraph(name=f"cluster_{name}") as c:
        c.attr(label=label, style="rounded,filled", color=color, fillcolor=LIGHT,
               fontname="Helvetica-Bold", fontsize="12", fontcolor=DARKTEAL, margin="16")
        for n_id, n_label, fill in nodes:
            c.node(n_id, n_label, fillcolor=fill, fontcolor="white" if fill != LIGHT else DARKTEAL)

# 1. Data Sources
cluster("src", "Data Sources", TEAL, [
    ("cbs", "Core Banking\n(EMI, DPD, Balances)", TEAL),
    ("bureau", "Bureau Data\n(CIBIL/Score)", TEAL),
    ("gst", "GST / ITR Filings", TEAL),
    ("txn", "Transaction\nNarrations", TEAL),
    ("news", "News & Sector\nSentiment Feeds", TEAL),
])

# 2. Feature Engineering
cluster("feat", "Unified Feature Store", ORANGE, [
    ("struct", "Structured Feature\nEngineering", ORANGE),
    ("nlp", "NLP Engine\n(Sentiment + Keyword\nStress Signals)", ORANGE),
    ("store", "Feature Store\n(Segment-tagged)", ORANGE),
])

# 3. Modeling
cluster("model", "Segment-Aware Scoring Engine", TEAL, [
    ("model1", "Gradient Boosted\nDefault Model\n(loan-type aware)", TEAL),
    ("calib", "Probability\nCalibration", TEAL),
])

# 4. Interpretation Layer
cluster("interp", "Common Interpretation Framework", ORANGE, [
    ("score", "Sentinel Risk Score\n(0-1000)", ORANGE),
    ("grade", "Risk Grade\n(AAA - D)", ORANGE),
    ("shap", "Explainability\n(Top Risk Drivers)", ORANGE),
])

# 5. Consumption
cluster("app", "Early-Warning & Delivery", DARKTEAL, [
    ("dash", "Portfolio Dashboard\n& Watchlist", DARKTEAL),
    ("api", "Scoring API\n(Loan Origination /\nMonitoring Systems)", DARKTEAL),
    ("alert", "RM / Credit Team\nAlerts", DARKTEAL),
])

edges = [
    ("cbs", "struct"), ("bureau", "struct"),
    ("gst", "nlp"), ("txn", "nlp"), ("news", "nlp"),
    ("struct", "store"), ("nlp", "store"),
    ("store", "model1"), ("model1", "calib"),
    ("calib", "score"), ("score", "grade"), ("calib", "shap"),
    ("grade", "dash"), ("shap", "dash"), ("score", "api"), ("api", "alert"), ("dash", "alert"),
]
for a, b in edges:
    g.edge(a, b, color=DARKTEAL, penwidth="1.2", arrowsize="0.7")

g.attr(label="CreditSentinel 360 - Solution Architecture", labelloc="t", fontsize="18",
       fontname="Helvetica-Bold", fontcolor=DARKTEAL)

g.render("/home/claude/idbi-default-predictor/diagrams/architecture", cleanup=True)
print("done")
