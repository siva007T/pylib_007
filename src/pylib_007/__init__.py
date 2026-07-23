"""pylib_007 — a tiny, publishable EDA + visualization library.

    import pylib_007 as pl
    df = pl.sample_data()
    pl.summarize(df)                 # -> dict
    pl.visualize(df, "eda.png")      # -> bar chart + Circos plot in one figure
"""

from .core import missing, sample_data, summarize
from .viz import bar_chart, circos_plot, visualize

__version__ = "0.1.0"
__all__ = ["summarize", "missing", "sample_data",
           "bar_chart", "circos_plot", "visualize", "__version__"]
