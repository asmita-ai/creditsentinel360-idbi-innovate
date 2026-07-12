import json
from pathlib import Path

import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch

ROOT = Path(__file__).resolve().parents[1]
TEAL = "#0B7A66"
ORANGE = "#E8732C"
DARKTEAL = "#0E4C46"
LIGHT = "#EAF4F2"

df = pd.read_csv(ROOT / "data" / "scored_portfolio.csv")
with open(ROOT / "models" / "metrics.json") as f:
    metrics = json.load(f)

fig = plt.figure(figsize=(14, 8.5), facecolor="white")
gs = fig.add_gridspec(4, 4, hspace=0.9, wspace=0.5, top=0.90, bottom=0.05, left=0.05, right=0.97)

# Header bar
fig.text(0.05, 0.965, "🛡  CreditSentinel 360", fontsize=20, fontweight="bold", color=DARKTEAL)
fig.text(0.05, 0.935, "12-Month Forward Default Prediction & Early Warning System  |  IDBI Innovate 2026 - Problem Statement 4",
         fontsize=10.5, color="#4B6660")

# KPI cards
kpis = [
    ("Total Accounts", f"{len(df):,}"),
    ("Early-Warning Flags", f"{int(df['early_warning_flag'].sum()):,} ({df['early_warning_flag'].mean()*100:.1f}%)"),
    ("Avg Risk Score", f"{df['sentinel_risk_score'].mean():.0f}/1000"),
    ("Default-Capture Recall", f"{metrics['default_capture_recall']*100:.0f}% (vs 16-22% legacy)"),
]
for i, (label, value) in enumerate(kpis):
    ax = fig.add_subplot(gs[0, i])
    ax.axis("off")
    box = FancyBboxPatch((0.03, 0.05), 0.94, 0.85, boxstyle="round,pad=0.02,rounding_size=0.06",
                          transform=ax.transAxes, facecolor=LIGHT, edgecolor=TEAL, linewidth=1.3)
    ax.add_patch(box)
    ax.text(0.5, 0.62, value, ha="center", va="center", fontsize=14, fontweight="bold",
            color=DARKTEAL, transform=ax.transAxes)
    ax.text(0.5, 0.22, label, ha="center", va="center", fontsize=9.5, color="#4B6660",
            transform=ax.transAxes)

# Risk score distribution by loan type (boxplot)
ax1 = fig.add_subplot(gs[1:3, 0:2])
loan_types = sorted(df["loan_type"].unique())
data = [df[df["loan_type"] == lt]["sentinel_risk_score"] for lt in loan_types]
bp = ax1.boxplot(data, labels=loan_types, patch_artist=True, showfliers=False)
for patch in bp['boxes']:
    patch.set_facecolor(TEAL)
    patch.set_alpha(0.75)
for median in bp['medians']:
    median.set_color(ORANGE)
    median.set_linewidth(2)
ax1.set_title("Portfolio Risk Distribution by Loan Type", fontsize=12, fontweight="bold", color=DARKTEAL, loc="left")
ax1.tick_params(axis="x", rotation=20)
ax1.spines[["top", "right"]].set_visible(False)
ax1.set_ylabel("Sentinel Risk Score")

# Risk grade distribution (bar)
ax2 = fig.add_subplot(gs[1:3, 2:4])
order = ["AAA", "AA", "A", "BBB", "BB", "C", "D"]
grade_counts = df["risk_grade"].value_counts().reindex(order).fillna(0)
colors = plt.cm.RdYlGn([0.9, 0.75, 0.6, 0.5, 0.35, 0.2, 0.05])
ax2.bar(grade_counts.index, grade_counts.values, color=colors, edgecolor=DARKTEAL, linewidth=0.6)
ax2.set_title("Common Risk Grade Distribution (AAA - D)", fontsize=12, fontweight="bold", color=DARKTEAL, loc="left")
ax2.spines[["top", "right"]].set_visible(False)
ax2.set_ylabel("# Accounts")

# Watchlist table
ax3 = fig.add_subplot(gs[3, :])
ax3.axis("off")
watch = df.sort_values("pd_12m", ascending=False).head(5)[
    ["loan_id", "loan_type", "sentinel_risk_score", "risk_grade", "pd_12m"]
].copy()
watch["pd_12m"] = (watch["pd_12m"] * 100).round(1).astype(str) + "%"
watch.columns = ["Loan ID", "Loan Type", "Risk Score", "Grade", "12m PD"]
tbl = ax3.table(cellText=watch.values, colLabels=watch.columns, loc="center", cellLoc="center")
tbl.auto_set_font_size(False)
tbl.set_fontsize(9.5)
tbl.scale(1, 1.7)
for (row_i, col_i), cell in tbl.get_celld().items():
    if row_i == 0:
        cell.set_facecolor(DARKTEAL)
        cell.set_text_props(color="white", fontweight="bold")
    else:
        cell.set_facecolor("#FBEEE6" if row_i % 2 else "white")
    cell.set_edgecolor("#DDDDDD")
ax3.set_title("Early-Warning Watchlist (Top 5 Highest-Risk Accounts)", fontsize=12, fontweight="bold",
              color=DARKTEAL, loc="left", pad=14)

out = ROOT / "diagrams" / "dashboard_mockup.png"
plt.savefig(out, dpi=170, facecolor="white")
print(f"Saved {out}")
