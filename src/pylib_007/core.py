"""Tiny EDA helpers (MVP mindset): DataFrame in, plain object out, no mutation."""

from __future__ import annotations

import numpy as np
import pandas as pd


def summarize(df):
    """Return shape, column names and numeric columns as a plain dict."""
    return {
        "rows": len(df),
        "columns": len(df.columns),
        "names": list(df.columns),
        "numeric": list(df.select_dtypes(include="number").columns),
    }


def missing(df):
    """Return null counts per column, most-missing first (a pandas Series)."""
    return df.isna().sum().sort_values(ascending=False)


def sample_data(n=150, seed=0):
    """Return a small demo DataFrame whose numeric columns are correlated."""
    rng = np.random.default_rng(seed)
    trend = rng.normal(size=n)
    return pd.DataFrame(
        {
            "height": 170 + 11 * trend + rng.normal(0, 2, n),
            "weight": 70 + 9 * trend + rng.normal(0, 3, n),
            "income": 55 + 7 * trend + rng.normal(0, 9, n),
            "sleep": 8 - 1.6 * trend + rng.normal(0, 1, n),
            "age": rng.integers(18, 65, n).astype(float),
        }
    )
