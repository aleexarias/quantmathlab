"""
quantmathlab: A research library for quantitative finance.

Methods are developed paper by paper: the mathematics is worked out in the
LaTeX notes under ``research/``, and whatever a paper needs is implemented
here as typed, tested code. Everything fitted to data follows the same
``fit(data, **params) -> self`` / ``predict(data) -> result`` contract, so
methods from different papers can be composed and compared on the same data.
"""

# Single source of truth for the project version. pyproject.toml and
# docs/conf.py derive from this line; CITATION.cff must be bumped by hand.
__version__ = "0.1.0"

__all__: list[str] = []
