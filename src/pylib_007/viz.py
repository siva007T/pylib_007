"""Glossy "liquid" charts: gradient bar chart + Circos plot (colorblind-safe)."""
from __future__ import annotations

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.colors import LinearSegmentedColormap, to_rgb
from matplotlib.patches import PathPatch, Rectangle, Wedge
from matplotlib.path import Path

_CAT = ["#2a78d6", "#eb6834", "#1baf7a", "#eda100",
        "#e87ba4", "#008300", "#4a3aa7", "#e34948"]
_POS, _NEG, _INK, _MUTED, _GRID = "#2a78d6", "#e34948", "#0b0b0b", "#52514e", "#dbe4f1"

def _numeric(df):
    num = df.select_dtypes(include="number")
    if num.shape[1] < 2:
        raise ValueError("need at least two numeric columns to visualize")
    return num

def _tint(c, t):  # blend a color toward white (glossy highlight)
    r, g, b = to_rgb(c)
    return (r + (1 - r) * t, g + (1 - g) * t, b + (1 - b) * t)

def _shade(c, t):  # blend a color toward black (deep base)
    r, g, b = to_rgb(c)
    return (r * (1 - t), g * (1 - t), b * (1 - t))

def _bg(ax, extent):  # soft watery vertical gradient wash
    cmap = LinearSegmentedColormap.from_list("bg", ["#fdfeff", "#e9f1fc"])
    ax.imshow(np.linspace(0, 1, 256).reshape(-1, 1), extent=extent,
              origin="lower", aspect="auto", zorder=0, cmap=cmap)

def _text_angle(theta):
    deg = np.degrees(theta) % 360
    return deg - 180 if 90 < deg < 270 else deg

def bar_chart(df, ax=None):
    """Glossy gradient bar chart of each numeric column's mean, with a y-axis."""
    num = _numeric(df)
    order = list(num.columns)  # stable hue per column, matching circos_plot
    means = num.mean().sort_values(ascending=False)
    if ax is None:
        _, ax = plt.subplots(figsize=(6, 6))
    top = float(means.max()) * 1.22
    ax.set(xlim=(-0.7, len(means) - 0.3), ylim=(0, top))
    ax.set_autoscale_on(False)
    _bg(ax, (-0.7, len(means) - 0.3, 0, top))
    ax.set_axisbelow(True)
    ax.grid(axis="y", color=_GRID, lw=1.1, zorder=1)
    grad = np.linspace(0, 1, 256).reshape(-1, 1)
    for i, (name, value) in enumerate(means.items()):
        color = _CAT[order.index(name) % len(_CAT)]
        rect = ax.bar(i, value, width=0.6, color="none", zorder=3)[0]
        cmap = LinearSegmentedColormap.from_list("b", [_shade(color, .3), color, _tint(color, .6)])
        im = ax.imshow(grad, extent=(i - 0.3, i + 0.3, 0, value), origin="lower",
                       aspect="auto", cmap=cmap, zorder=3)
        im.set_clip_path(rect)
        sheen = Rectangle((i - 0.19, 0), 0.11, value, facecolor="white", alpha=.3, lw=0, zorder=4)
        ax.add_patch(sheen)
        sheen.set_clip_path(rect)
        ax.text(i, value + top * 0.02, f"{value:.1f}", ha="center", va="bottom",
                color=_INK, fontsize=9, weight="bold")
    ax.set_xticks(range(len(means)))
    ax.set_xticklabels(means.index, rotation=25, ha="right", color=_INK)
    ax.set_ylabel("mean value", color=_MUTED, fontsize=10)
    ax.tick_params(colors=_MUTED)
    for side in ("top", "right"):
        ax.spines[side].set_visible(False)
    for side in ("left", "bottom"):
        ax.spines[side].set_color(_GRID)
    ax.set_title("Column means", color=_INK, fontsize=13, weight="bold", loc="left", pad=12)
    return ax

def _chord(ax, p0, p1, color, s):  # glossy ribbon: soft glow + body + bright core
    path = Path([p0, (0, 0), p1], [Path.MOVETO, Path.CURVE3, Path.CURVE3])
    base = 2.5 + 9 * s
    for lw, a, col, z in [(base * 2.1, .10 + .12 * s, color, 2),
                          (base, .34 + .42 * s, color, 3),
                          (base * .32, .55 + .35 * s, _tint(color, .7), 4)]:
        p = PathPatch(path, facecolor="none", edgecolor=col, lw=lw, alpha=min(a, 1), zorder=z)
        p.set_capstyle("round")
        ax.add_patch(p)

def circos_plot(df, threshold=0.0, ax=None):
    """Glossy Circos chord diagram: each column is an arc, ribbons link pairs
    above ``threshold``; color = sign, width/opacity = strength."""
    corr = _numeric(df).corr().fillna(0.0)
    labels = list(corr.columns)
    n = len(labels)
    if ax is None:
        _, ax = plt.subplots(figsize=(6, 6))
    ax.set(xlim=(-1.5, 1.5), ylim=(-1.5, 1.5))
    ax.set_autoscale_on(False)
    _bg(ax, (-1.5, 1.5, -1.5, 1.5))
    ax.set_aspect("equal")  # after _bg: imshow(aspect="auto") would override it
    ax.axis("off")
    gap, ring, width = np.radians(6), 1.0, 0.13
    span = (2 * np.pi - n * gap) / n
    center = {}
    for i, label in enumerate(labels):
        a0, a1 = i * (span + gap), i * (span + gap) + span
        mid = center[label] = (a0 + a1) / 2
        col, d0, d1 = _CAT[i % len(_CAT)], np.degrees(a0), np.degrees(a1)
        ax.add_patch(Wedge((0, 0), ring, d0, d1, width=width, facecolor=col,
                           edgecolor="#fbfcff", lw=2, zorder=5))
        ax.add_patch(Wedge((0, 0), ring, d0, d1, width=width * .4,
                           facecolor=_tint(col, .6), lw=0, alpha=.7, zorder=6))
        r = ring + 0.17
        ax.text(r * np.cos(mid), r * np.sin(mid), label, color=_INK, fontsize=10,
                ha="center", va="center", rotation=_text_angle(mid), rotation_mode="anchor")
    inner = ring - width
    for a in range(n):
        for b in range(a + 1, n):
            c = corr.iloc[a, b]
            if abs(c) > threshold:
                ta, tb = center[labels[a]], center[labels[b]]
                _chord(ax, (inner * np.cos(ta), inner * np.sin(ta)),
                       (inner * np.cos(tb), inner * np.sin(tb)), _POS if c > 0 else _NEG, abs(c))
    ax.plot([], [], color=_POS, lw=4, label="positive")
    ax.plot([], [], color=_NEG, lw=4, label="negative")
    ax.legend(loc="lower center", ncol=2, frameon=False, labelcolor=_INK,
              bbox_to_anchor=(0.5, -0.02), fontsize=9)
    ax.set_title("Correlation Circos", color=_INK, fontsize=13, weight="bold")
    return ax

def visualize(df, path=None):
    """Draw the bar chart and Circos plot side by side; return the Figure.
    If ``path`` is given (e.g. ``"eda.png"``), also save it there."""
    fig, (left, right) = plt.subplots(1, 2, figsize=(13, 6.5))
    fig.patch.set_facecolor("#ffffff")
    bar_chart(df, ax=left)
    circos_plot(df, ax=right)
    fig.suptitle("pylib_007 — data at a glance", color=_INK, fontsize=16, weight="bold")
    fig.tight_layout(rect=(0, 0, 1, 0.96))
    if path:
        fig.savefig(path, dpi=150, facecolor="#ffffff", bbox_inches="tight")
    return fig
