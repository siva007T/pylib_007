import matplotlib
matplotlib.use("Agg")  # headless backend for CI
import pandas as pd
import pytest
import pylib_007 as pl

def test_summarize():
    out = pl.summarize(pl.sample_data(n=10))
    assert out["rows"] == 10 and "height" in out["numeric"]

def test_missing_counts():
    assert int(pl.missing(pl.sample_data(n=10)).sum()) == 0

def test_visualize_returns_figure():
    assert len(pl.visualize(pl.sample_data(n=30)).axes) >= 2

def test_needs_two_numeric_columns():
    with pytest.raises(ValueError):
        pl.bar_chart(pd.DataFrame({"only": [1, 2, 3]}))
