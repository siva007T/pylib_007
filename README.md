# pylib_007

Beautiful **bar-chart** and **Circos correlation** plots for pandas DataFrames —
a tiny, installable library built by following *Build Your First Library: the path to PyPI*.

The `visualize()` function draws two panels side by side:

- **Bar chart** — the mean of each numeric column, one colorblind-safe hue per column.
- **Circos plot** — a circular chord diagram of the correlations between numeric
  columns. Each column is an arc on the ring; chords link column pairs, colored
  **blue** for positive and **red** for negative correlation, with width and
  opacity showing the strength.

Each column keeps the same hue across both panels, so the two views read as one.

## Install

```bash
pip install pylib_007
```

From source (editable, for development):

```bash
python -m pip install -e .
```

## Use

```python
import pylib_007 as pl

df = pl.sample_data()          # demo DataFrame with correlated columns
print(pl.summarize(df))        # {'rows': 150, 'columns': 5, ...}
print(pl.missing(df))          # null counts per column (pandas Series)

pl.visualize(df, "eda.png")    # bar chart + Circos plot -> saved to eda.png
```

Bring your own data — any DataFrame with **two or more numeric columns** works.
A ready-made example dataset ships in [`examples/data.csv`](examples/data.csv):

```python
import pandas as pd
df = pd.read_csv("examples/data.csv")   # or your own CSV
pl.visualize(df)               # returns a matplotlib Figure

# or draw the panels individually onto your own axes:
pl.bar_chart(df)
pl.circos_plot(df, threshold=0.3)   # only show |correlation| > 0.3
```

## Public API

| Function | Returns | Description |
|----------|---------|-------------|
| `summarize(df)` | `dict` | rows, column count, names, numeric columns |
| `missing(df)` | `Series` | null counts per column, most-missing first |
| `sample_data(n=150, seed=0)` | `DataFrame` | demo data with correlated columns |
| `bar_chart(df, ax=None)` | `Axes` | bar chart of column means |
| `circos_plot(df, threshold=0.0, ax=None)` | `Axes` | Circos correlation chord diagram |
| `visualize(df, path=None)` | `Figure` | both panels side by side; saves if `path` given |

## Requirements

Python 3.9+, `pandas`, `matplotlib`, `numpy` (installed automatically).

## License

MIT — see [LICENSE](LICENSE).
