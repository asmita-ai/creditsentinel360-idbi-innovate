from graphviz import Digraph

TEAL = "#0B7A66"
ORANGE = "#E8732C"
DARKTEAL = "#0E4C46"

g = Digraph("flow", format="png")
g.attr(rankdir="TB", bgcolor="white", fontname="Helvetica", nodesep="0.5", ranksep="0.55")
g.attr("node", fontname="Helvetica", fontsize="12", shape="box", style="rounded,filled",
       color=DARKTEAL, fontcolor="white", margin="0.25,0.15", penwidth="1.2")
g.attr("edge", color=DARKTEAL, penwidth="1.3", arrowsize="0.8", fontname="Helvetica", fontsize="10")

steps = [
    ("s1", "New/Existing Loan\nAccount Observation\n(monthly refresh)", TEAL),
    ("s2", "Pull Structured Data\n(EMI, DPD, Bureau, Financials)", TEAL),
    ("s3", "Pull Unstructured Data\n(GST remarks, txn narrations,\nnews/sector sentiment)", ORANGE),
    ("s4", "NLP Engine extracts\nstress signals & sentiment score", ORANGE),
    ("s5", "Feature Store merges\nstructured + unstructured signals", TEAL),
    ("s6", "Segment-Aware Model scores\nProbability of Default (12m)", TEAL),
    ("s7", "Calibration + Common\nInterpretation Framework\n(Risk Score 0-1000, Grade AAA-D)", ORANGE),
    ("s8", "Explainability Layer\ngenerates top risk drivers", ORANGE),
]
for nid, label, color in steps:
    g.node(nid, label, fillcolor=color)

g.node("d1", "PD >= Early-Warning\nThreshold?", shape="diamond", fillcolor="#FFFFFF",
       fontcolor=DARKTEAL, style="filled", color=DARKTEAL)

g.node("s9", "Flag Account on\nEarly-Warning Watchlist\n+ Alert RM/Credit Team", fillcolor=DARKTEAL)
g.node("s10", "Continue Standard\nMonitoring Cycle", fillcolor="#6B9E97")
g.node("s11", "Credit Team Reviews\n(score + plain-language drivers)\n-> Preventive Action", fillcolor=DARKTEAL)

order = ["s1", "s2", "s5"]
g.edge("s1", "s2")
g.edge("s1", "s3")
g.edge("s3", "s4")
g.edge("s2", "s5")
g.edge("s4", "s5")
g.edge("s5", "s6")
g.edge("s6", "s7")
g.edge("s7", "s8")
g.edge("s8", "d1")
g.edge("d1", "s9", label="Yes")
g.edge("d1", "s10", label="No")
g.edge("s9", "s11")

g.attr(label="CreditSentinel 360 - 12-Month Early Warning Process Flow", labelloc="t",
       fontsize="17", fontname="Helvetica-Bold", fontcolor=DARKTEAL)

g.render("/home/claude/idbi-default-predictor/diagrams/process_flow", cleanup=True)
print("done")
