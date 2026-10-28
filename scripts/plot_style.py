"""Consistent, accessible chart style used by every figure in the project.

Rules followed (colour-blind-safe fixed-order palette, one axis per chart, thin
marks, recessive grid, no chart titles inside the image because APA places the
figure number and title above the figure in the document).
"""
import matplotlib as mpl
import matplotlib.pyplot as plt
from config import PALETTE, INK, INK_2, GRID, FIG


def set_style():
    mpl.rcParams.update({
        "figure.figsize": (6.5, 3.6),
        "figure.dpi": 110,
        "savefig.dpi": 220,
        "savefig.bbox": "tight",
        "font.family": "DejaVu Sans",
        "font.size": 9,
        "axes.edgecolor": INK_2,
        "axes.labelcolor": INK,
        "axes.titlecolor": INK,
        "axes.spines.top": False,
        "axes.spines.right": False,
        "axes.grid": True,
        "grid.color": GRID,
        "grid.linewidth": 0.6,
        "axes.axisbelow": True,
        "xtick.color": INK_2,
        "ytick.color": INK_2,
        "text.color": INK,
        "lines.linewidth": 1.8,
        "lines.markersize": 4.5,
        "axes.prop_cycle": mpl.cycler(color=PALETTE),
        "legend.frameon": False,
    })


def save_fig(fig, name):
    """Save into outputs/figures/<name>.png and close the figure."""
    path = FIG / f"{name}.png"
    fig.savefig(path, facecolor="white")
    plt.close(fig)
    return str(path.relative_to(FIG.parents[1]))
