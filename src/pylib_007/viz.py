"""Beautiful matplotlib charts for a DataFrame: a bar chart + a Circos plot.

Colors come from a validated, colorblind-safe palette (blue = positive,
red = negative correlation).
"""

from __future__ import annotations

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.path import Path
from matplotlib.patches import PathPatch, Wedge

# Validated data-viz palette (light surface): 8 categorical hues + diverging poles.
_CAT = ["#2a78d6", "#eb6834", "#1baf7a", "#eda100",
        "#e87ba4", "#008300", "#4a3aa7", "#e34948"]
_POS, _NEG = "#2a78d6", "#e34948"           # positive / negative correlation
_INK, _MUTED, _SURFACE = "#0b0b0b", "#898781", "#fcfcfb"


def _numeric(df):
    num = df.select_dtypes(include="number")
    if num.shape[1] < 2:
        raise ValueError("need at least two numeric columns to visualize")
    return num


def bar_chart(df, ax=None):
    """Bar chart of each numeric column's mean, one categorical hue per bar."""
    num = _numeric(df)
    order = list(num.columns)  # stable hue per column, matching circos_plot
    means = num.mean().sort_values(ascending=False)
    if ax is None:
        _, ax = plt.subplots(figsize=(6, 6))
    ax.set_facecolor(_SURFACE)
    colors = [_CAT[order.index(c) % len(_CAT)] for c in means.index]
    bars = ax.bar(range(len(means)), means.values, width=0.62, color=colors, zorder=3)
    for rect, value in zip(bars, means.values):
        ax.text(rect.get_x() + rect.get_width() / 2, value, f"{value:.1f}",
                ha="center", va="bottom", color=_INK, fontsize=9)
    ax.set_xticks(range(len(means)))
    ax.set_xticklabels(means.index, rotation=25, ha="right", color=_INK)
    ax.set_yticks([])
    ax.margins(y=0.16)
    for spine in ax.spines.values():
        spine.set_visible(False)
    ax.tick_params(length=0)
    ax.set_title("Column means", color=_INK, fontsize=13, weight="bold", loc="left", pad=12)
    return ax


def circos_plot(df, threshold=0.0, ax=None):
    """Circos chord diagram of correlations: each numeric column is an arc,
    chords link pairs above ``threshold``; color = sign, width = strength."""
    corr = _numeric(df).corr().fillna(0.0)
    labels = list(corr.columns)
    n = len(labels)
    if ax is None:
        _, ax = plt.subplots(figsize=(6, 6))
    ax.set_facecolor(_SURFACE)
    ax.set_aspect("equal")
    ax.axis("off")

    gap, ring, width = np.radians(6), 1.0, 0.12
    span = (2 * np.pi - n * gap) / n
    center = {}
    for i, label in enumerate(labels):
        a0 = i * (span + gap)
        a1, mid = a0 + span, a0 + span / 2
        center[label] = mid
        ax.add_patch(Wedge((0, 0), ring, np.degrees(a0), np.degrees(a1), width=width,
                           facecolor=_CAT[i % len(_CAT)], edgecolor=_SURFACE, lw=2, zorder=3))
        r = ring + 0.16
        ax.text(r * np.cos(mid), r * np.sin(mid), label, color=_INK, fontsize=10,
                ha="center", va="center", rotation=_text_angle(mid), rotation_mode="anchor")

    inner = ring - width
    for a in range(n):
        for b in range(a + 1, n):
            c = corr.iloc[a, b]
            if abs(c) <= threshold:
                continue
            ta, tb = center[labels[a]], center[labels[b]]
            p0 = (inner * np.cos(ta), inner * np.sin(ta))
            p1 = (inner * np.cos(tb), inner * np.sin(tb))
            path = Path([p0, (0, 0), p1], [Path.MOVETO, Path.CURVE3, Path.CURVE3])
            ax.add_patch(PathPatch(path, facecolor="none", edgecolor=_POS if c > 0 else _NEG,
                                   lw=1 + 5 * abs(c), alpha=0.25 + 0.55 * abs(c), zorder=2))

    ax.set_xlim(-1.45, 1.45)
    ax.set_ylim(-1.45, 1.45)
    ax.plot([], [], color=_POS, lw=3, label="positive")
    ax.plot([], [], color=_NEG, lw=3, label="negative")
    ax.legend(loc="lower center", ncol=2, frameon=False, labelcolor=_INK,
              bbox_to_anchor=(0.5, -0.04), fontsize=9)
    ax.set_title("Correlation Circos", color=_INK, fontsize=13, weight="bold")
    return ax


def _text_angle(theta):
    deg = np.degrees(theta) % 360
    return deg - 180 if 90 < deg < 270 else deg


def visualize(df, path=None):
    """Draw the bar chart and Circos plot side by side; return the Figure.
    If ``path`` is given (e.g. ``"eda.png"``), also save it there."""
    fig, (left, right) = plt.subplots(1, 2, figsize=(13, 6.5))
    fig.patch.set_facecolor(_SURFACE)
    bar_chart(df, ax=left)
    circos_plot(df, ax=right)
    fig.suptitle("pylib_007 — data at a glance", color=_INK, fontsize=16, weight="bold")
    fig.tight_layout(rect=(0, 0, 1, 0.96))
    if path:
        fig.savefig(path, dpi=150, facecolor=_SURFACE, bbox_inches="tight")
    return fig
