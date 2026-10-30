"""Draw the workflow, database and deployment diagrams used in the final report.

    python scripts/make_diagrams.py
"""
import sys
from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch, Patch

sys.path.insert(0, str(Path(__file__).resolve().parent))
from config import PALETTE, INK, INK_2, FIG                 # noqa: E402
from plot_style import set_style, save_fig                   # noqa: E402

set_style()
LAYER = {"data": "#DCE9F8", "analysis": "#E6F2DC", "model": "#F8E8D2", "delivery": "#EBDDF2"}
EDGE = {"data": PALETTE[0], "analysis": PALETTE[2], "model": PALETTE[1], "delivery": PALETTE[3]}


def box(ax, x, y, w, h, title, lines, layer, fs=6.5, tl=1):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.02,rounding_size=0.08", fc=LAYER[layer], ec=EDGE[layer], lw=1.5))
    ax.text(x + w / 2, y + h - 0.14, title, ha="center", va="top", fontsize=fs + 1.3, fontweight="bold", color=INK, linespacing=1.15)
    ax.text(x + w / 2, y + h - 0.2 - 0.42 * tl - 0.22, "\n".join(lines), ha="center", va="top", fontsize=fs, color=INK, linespacing=1.4)


def arrow(ax, p, q, style="-|>", ls="-", rad=0.0, color=None):
    ax.add_patch(FancyArrowPatch(p, q, arrowstyle=style, mutation_scale=11, lw=1.3, ls=ls, color=color or INK_2,
                                 connectionstyle=f"arc3,rad={rad}", shrinkA=0, shrinkB=0))


def elbow(ax, pts, color=None, ls="-"):
    """Polyline with an arrow head on the last segment."""
    xs, ys = zip(*pts[:-1])
    ax.plot(list(xs) + [pts[-2][0]], list(ys) + [pts[-2][1]], color=color or INK_2, lw=1.3, ls=ls, solid_capstyle="butt")
    arrow(ax, pts[-2], pts[-1], ls=ls, color=color)


def workflow():
    fig, ax = plt.subplots(figsize=(7.0, 5.3)); ax.set_xlim(0, 12.6); ax.set_ylim(0, 9.2); ax.axis("off"); ax.grid(False)
    W, H = 2.75, 2.75
    row1, row2 = 5.9, 2.45
    xs = [0.2, 3.3, 6.4, 9.5]
    stages1 = [
        ("1  Data", ["Bureau of Transportation", "Statistics flight records", "(2024 and 2025) and", "monthly capacity data", "(2022 to 2026)"], "data", 1),
        ("2  Preprocessing", ["Types set, duplicates", "checked, outliers flagged,", "missing values handled,", "tables joined by", "identification numbers"], "data", 1),
        ("3  Exploratory\nData Analysis", ["Distributions, trends,", "seasonality, delay causes", "and correlations"], "analysis", 2),
        ("4  Feature\nEngineering", ["Encoding, rescaling,", "airport grouping,", "previous-month", "load factor"], "analysis", 2),
    ]
    for (t, l, k, tl), x in zip(stages1, xs):
        box(ax, x, row1, W, H, t, l, k, tl=tl)
    for i in range(3):
        arrow(ax, (xs[i] + W + 0.03, row1 + H / 2), (xs[i + 1] - 0.03, row1 + H / 2))
    # row 2 runs right to left
    stages2 = [
        ("5  Model", ["Logistic regression, random", "forest, gradient boosting;", "correlation, regression;", "k-means; seasonal models;", "long short-term memory"], "model", 9.5),
        ("6  Evaluation", ["Training and test scores,", "cross-validation, tests at", "the 5% level, confusion", "matrix, receiver operating", "characteristic curve"], "model", 6.4),
        ("7  Deployment", ["Scoring module, dashboard,", "programming interface,", "database queries for", "historical context"], "delivery", 3.3),
    ]
    for t, l, k, x in stages2:
        box(ax, x, row2, W, H - 0.3, t, l, k, tl=1)
    arrow(ax, (xs[3] + W - 0.35, row1 - 0.03), (xs[3] + W - 0.35, row2 + H - 0.3 + 0.03))          # 4 -> 5
    arrow(ax, (9.47, row2 + 1.2), (6.4 + W + 0.03, row2 + 1.2))                                      # 5 -> 6
    arrow(ax, (6.37, row2 + 1.2), (3.3 + W + 0.03, row2 + 1.2))                                      # 6 -> 7
    elbow(ax, [(7.4, row2 + H - 0.3 + 0.03), (7.4, 5.25), (10.1, 5.25), (10.1, row1 - 0.03)], color=EDGE["model"], ls="--")   # feedback
    ax.text(8.75, 5.33, "iterate: tune and refit", fontsize=6.6, color=INK_2, ha="center", va="bottom", style="italic")
    # storage strip
    ax.add_patch(FancyBboxPatch((0.2, 0.35), 12.05, 1.15, boxstyle="round,pad=0.02,rounding_size=0.08", fc="#F2F2F2", ec=INK_2, lw=1.1))
    ax.text(6.22, 0.92, "Storage and access layer\nParquet files hold the 14.1 million flight records; a DuckDB database holds the route-month,\n"
            "carrier-airport and passenger tables; an outputs folder holds tables, figures and saved models",
            ha="center", va="center", fontsize=6.2, color=INK, linespacing=1.5)
    for x in (4.65, 7.75, 10.85):
        arrow(ax, (x, 1.52), (x, row2 - 0.03), style="<|-|>", color=INK_2)
    # legend inside the empty slot
    handles = [Patch(fc=LAYER[k], ec=EDGE[k], label=v) for k, v in
               (("data", "Data layer"), ("analysis", "Analysis layer"), ("model", "Modelling layer"), ("delivery", "Delivery layer"))]
    handles += [plt.Line2D([0], [0], color=INK_2, lw=1.3, label="Forward data flow"),
                plt.Line2D([0], [0], color=EDGE["model"], lw=1.3, ls="--", label="Feedback loop"),
                plt.Line2D([0], [0], color=INK_2, lw=1.3, marker=(3, 0, 0), markevery=[0, 1], label="Read and write storage")]
    ax.legend(handles=handles, loc="center left", bbox_to_anchor=(0.0, 0.325), fontsize=6.2, frameon=True, edgecolor=INK_2, title="Legend", title_fontsize=6.8, borderpad=0.5, labelspacing=0.35)
    fig.tight_layout(); save_fig(fig, "fig23_workflow")


def schema():
    fig, ax = plt.subplots(figsize=(7.0, 4.6)); ax.set_xlim(0, 12.6); ax.set_ylim(0, 8.2); ax.axis("off"); ax.grid(False)

    def table(x, y, w, name, cols, kind):
        h = 0.55 + 0.36 * len(cols)
        ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.01,rounding_size=0.05", fc="white", ec=EDGE[kind], lw=1.4))
        ax.add_patch(FancyBboxPatch((x, y + h - 0.55), w, 0.55, boxstyle="round,pad=0.01,rounding_size=0.05", fc=LAYER[kind], ec=EDGE[kind], lw=1.4))
        ax.text(x + w / 2, y + h - 0.28, name, ha="center", va="center", fontsize=7.4, fontweight="bold", color=INK)
        for i, c in enumerate(cols):
            ax.text(x + 0.12, y + h - 0.78 - 0.36 * i, c, fontsize=6.0, va="center", color=INK)
        return h
    table(0.2, 5.0, 3.0, "dim_carrier", ["carrier_id (key)", "carrier_code", "carrier_name"], "data")
    table(0.2, 1.9, 3.0, "dim_airport", ["airport_id (key)", "airport_code", "state", "airport_name"], "data")
    table(4.5, 3.4, 4.0, "fact_route_month", ["year, month", "carrier_id, origin_id, dest_id (key)", "flights_scheduled, flights_operated",
                                              "late_rate, cancel_rate", "passengers, seats, load_factor"], "model")
    table(9.2, 5.35, 3.2, "fact_carrier_airport", ["carrier_id, origin_id (key)", "flights_scheduled, cancelled", "avg_load_factor, avg_distance", "seasonal_cv, cancel_rate"], "model")
    table(9.2, 2.2, 3.2, "fact_route_passengers", ["route, period (key)", "passengers"], "model")
    table(4.5, 0.2, 4.0, "flight (view on a Parquet file)", ["14,080,680 flight records", "carrier_id, origin_id, dest_id, flight_date", "is_late, cancelled, dep_time_blk"], "analysis")
    # relationships (labelled with the joining column)
    def rel(p, q, label, lp, rad=0.0):
        arrow(ax, p, q, style="-", rad=rad)
        ax.text(lp[0], lp[1], label, fontsize=5.8, color=INK_2, ha="center", va="center", style="italic", bbox=dict(fc="white", ec="none", pad=0.8))
    rel((3.2, 5.7), (4.5, 5.0), "carrier_id", (3.85, 5.5))
    rel((3.2, 3.2), (4.5, 4.4), "origin_id, dest_id", (3.55, 3.55))
    rel((3.2, 6.2), (9.2, 6.4), "carrier_id", (6.2, 6.85), rad=-0.12)
    rel((3.2, 2.3), (9.2, 2.9), "route = origin and destination codes", (5.3, 2.3), rad=0.1)
    arrow(ax, (6.5, 1.75), (6.5, 3.38), style="-|>", ls="--", color=EDGE["analysis"])
    handles = [Patch(fc=LAYER["data"], ec=EDGE["data"], label="Dimension table"), Patch(fc=LAYER["model"], ec=EDGE["model"], label="Fact table"),
               Patch(fc=LAYER["analysis"], ec=EDGE["analysis"], label="Flight-level view"), plt.Line2D([0], [0], color=INK_2, lw=1.3, label="Relationship (joining column)"),
               plt.Line2D([0], [0], color=EDGE["analysis"], lw=1.3, ls="--", label="Derived by aggregation")]
    ax.legend(handles=handles, loc="upper center", ncol=5, fontsize=6.2, bbox_to_anchor=(0.5, 1.04), frameon=False)
    fig.tight_layout(); save_fig(fig, "fig24_database_schema")


def deployment():
    fig, ax = plt.subplots(figsize=(7.0, 3.5)); ax.set_xlim(0, 12.6); ax.set_ylim(0, 6.0); ax.axis("off"); ax.grid(False)
    box(ax, 0.2, 1.5, 2.6, 3.3, "Users", ["Dispatcher or", "schedule planner", "(web page)", "", "Airline operations", "system (program call)"], "delivery")
    box(ax, 3.7, 3.35, 2.7, 1.9, "Dashboard", ["Streamlit page: inputs,", "probability, risk band,", "factor chart"], "delivery")
    box(ax, 3.7, 0.75, 2.7, 1.9, "Programming interface", ["FastAPI service with", "predict and health", "endpoints (structured text)"], "delivery")
    box(ax, 7.3, 1.5, 2.5, 3.3, "Scoring module", ["Builds the same", "features as in training,", "returns the probability", "and the factor", "contributions"], "model")
    box(ax, 10.4, 3.35, 2.1, 1.9, "Saved model", ["Model file and", "feature specification"], "model", fs=6.0)
    box(ax, 10.4, 0.75, 2.1, 1.9, "Database", ["Historical late rate", "for similar flights", "(structured query)"], "data", fs=6.0)
    arrow(ax, (2.83, 4.3), (3.67, 4.3)); arrow(ax, (2.83, 2.0), (3.67, 1.7))
    arrow(ax, (6.43, 4.3), (7.27, 4.1)); arrow(ax, (6.43, 1.7), (7.27, 2.2))
    arrow(ax, (9.83, 4.3), (10.37, 4.3), style="<|-|>"); arrow(ax, (9.83, 2.0), (10.37, 1.7), style="<|-|>")
    handles = [Patch(fc=LAYER["delivery"], ec=EDGE["delivery"], label="Delivery layer"), Patch(fc=LAYER["model"], ec=EDGE["model"], label="Modelling layer"),
               Patch(fc=LAYER["data"], ec=EDGE["data"], label="Data layer"), plt.Line2D([0], [0], color=INK_2, lw=1.3, label="Request and response")]
    ax.legend(handles=handles, loc="lower center", ncol=4, fontsize=6.4, bbox_to_anchor=(0.5, -0.04), frameon=False)
    fig.tight_layout(); save_fig(fig, "fig25_deployment")


if __name__ == "__main__":
    workflow(); schema(); deployment()
