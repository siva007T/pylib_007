"""Clean, business-style charts for a DataFrame: bar chart + Circos plot.

Palette is colorblind-safe; blue = positive, red = negative correlation.
"""
from __future__ import annotations

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import PathPatch, Wedge
from matplotlib.path import Path

# Muted, corporate palette — desaturated slate/teal/taupe tones (no rainbow, no red+green clash).
_CAT = ["#33475b", "#4e6e8e", "#5b8a8f", "#8a7f6d",
        "#a86b7f", "#6b7a99", "#9c8452", "#6d6a7c"]
_POS, _NEG = "#3d6d9e", "#b0655a"            # muted blue (+) / muted terracotta (-)
_INK, _MUTED, _GRID = "#2b2f36", "#6b7078", "#e6e6e6"
_FONT = "DejaVu Sans"

def _numeric(df):
    num = df.select_dtypes(include="number")
    if num.shape[1] < 2:
        raise ValueError("need at least two numeric columns to visualize")
    return num

def _align(theta):  # anchor a horizontal label just outside its point on the ring
    c, s = np.cos(theta), np.sin(theta)
    return ("left" if c > 0.05 else "right" if c < -0.05 else "center",
            "bottom" if s > 0.05 else "top" if s < -0.05 else "center")

def bar_chart(df, ax=None):
    """Clean bar chart of each numeric column's mean, with labeled x and y axes."""
    num = _numeric(df)
    order = list(num.columns)  # stable hue per column, matching circos_plot
    means = num.mean().sort_values(ascending=False)
    if ax is None:
        _, ax = plt.subplots(figsize=(6.5, 6))
    colors = [_CAT[order.index(c) % len(_CAT)] for c in means.index]
    bars = ax.bar(range(len(means)), means.values, width=0.66, color=colors,
                  edgecolor="white", linewidth=0.8, zorder=3)
    for rect, value in zip(bars, means.values):
        ax.annotate(f"{value:,.1f}", (rect.get_x() + rect.get_width() / 2, value),
                    xytext=(0, 4), textcoords="offset points", ha="center", va="bottom",
                    color=_INK, fontsize=10, fontfamily=_FONT)
    ax.set_axisbelow(True)
    ax.grid(axis="y", color=_GRID, lw=1, zorder=0)
    ax.set_ylim(0, float(means.max()) * 1.15)
    ax.set_xticks(range(len(means)))
    ax.set_xticklabels(means.index, color=_INK, fontsize=10, fontfamily=_FONT)
    ax.set_xlabel("Column", color=_MUTED, fontsize=11, fontfamily=_FONT, labelpad=8)
    ax.set_ylabel("Mean value", color=_MUTED, fontsize=11, fontfamily=_FONT, labelpad=8)
    ax.tick_params(colors=_MUTED, length=0)
    for side in ("top", "right"):
        ax.spines[side].set_visible(False)
    for side in ("left", "bottom"):
        ax.spines[side].set_color(_GRID)
    ax.set_title("Column means", color=_INK, fontsize=14, weight="bold",
                 loc="left", pad=12, fontfamily=_FONT)
    return ax

def circos_plot(df, threshold=0.0, ax=None):
    """Clean Circos chord diagram: each numeric column is an arc; ribbons link
    pairs above ``threshold``; color = sign, width/opacity = strength."""
    corr = _numeric(df).corr().fillna(0.0)
    labels = list(corr.columns)
    n = len(labels)
    if ax is None:
        _, ax = plt.subplots(figsize=(6.5, 6.5))
    ax.set_aspect("equal")
    ax.set_xlim(-1.6, 1.6)
    ax.set_ylim(-1.6, 1.6)
    ax.axis("off")
    gap, ring, width = np.radians(5), 1.0, 0.10
    span = (2 * np.pi - n * gap) / n
    center = {}
    for i, label in enumerate(labels):
        a0, a1 = i * (span + gap), i * (span + gap) + span
        mid = center[label] = (a0 + a1) / 2
        ax.add_patch(Wedge((0, 0), ring, np.degrees(a0), np.degrees(a1), width=width,
                           facecolor=_CAT[i % len(_CAT)], edgecolor="white", lw=1.5, zorder=4))
        ha, va = _align(mid)
        r = ring + 0.09
        ax.text(r * np.cos(mid), r * np.sin(mid), label, ha=ha, va=va, color=_INK,
                fontsize=10.5, fontfamily=_FONT, clip_on=False)
    inner = ring - width
    for a in range(n):
        for b in range(a + 1, n):
            c = corr.iloc[a, b]
            if abs(c) <= threshold:
                continue
            ta, tb = center[labels[a]], center[labels[b]]
            path = Path([(inner * np.cos(ta), inner * np.sin(ta)), (0, 0),
                         (inner * np.cos(tb), inner * np.sin(tb))],
                        [Path.MOVETO, Path.CURVE3, Path.CURVE3])
            p = PathPatch(path, facecolor="none", edgecolor=_POS if c > 0 else _NEG,
                          lw=0.8 + 4 * abs(c), alpha=0.2 + 0.5 * abs(c), zorder=2)
            p.set_capstyle("round")
            ax.add_patch(p)
    ax.plot([], [], color=_POS, lw=3, label="Positive")
    ax.plot([], [], color=_NEG, lw=3, label="Negative")
    ax.legend(loc="lower center", ncol=2, frameon=False, fontsize=10, labelcolor=_INK,
              bbox_to_anchor=(0.5, -0.03))
    ax.set_title("Correlation Circos", color=_INK, fontsize=14, weight="bold", fontfamily=_FONT)
    return ax

def visualize(df, path=None, title=None):
    """Draw the bar chart and Circos plot side by side; return the Figure.
    ``title`` defaults to a summary of the data (rows x numeric columns).
    If ``path`` is given (e.g. ``"eda.png"``), also save it there."""
    num = _numeric(df)
    if title is None:
        title = f"{len(df):,} rows  x  {num.shape[1]} numeric columns"
    fig, (left, right) = plt.subplots(1, 2, figsize=(14, 6.5))
    fig.patch.set_facecolor("white")
    bar_chart(df, ax=left)
    circos_plot(df, ax=right)
    fig.suptitle(title, color=_INK, fontsize=17, weight="bold", fontfamily=_FONT)
    fig.tight_layout(rect=(0, 0, 1, 0.95))
    if path:
        fig.savefig(path, dpi=200, facecolor="white", bbox_inches="tight")
    return fig
