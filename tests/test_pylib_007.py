import matplotlib

matplotlib.use("Agg")  # headless backend for CI

import pylib_007 as pl


def test_summarize():
    df = pl.sample_data(n=10)
    out = pl.summarize(df)
    assert out["rows"] == 10
    assert "height" in out["numeric"]


def test_missing_counts():
    df = pl.sample_data(n=10)
    assert int(pl.missing(df).sum()) == 0


def test_visualize_returns_figure():
    df = pl.sample_data(n=30)
    fig = pl.visualize(df)
    assert len(fig.axes) >= 2


def test_needs_two_numeric_columns():
    import pandas as pd
    import pytest

    with pytest.raises(ValueError):
        pl.bar_chart(pd.DataFrame({"only": [1, 2, 3]}))
