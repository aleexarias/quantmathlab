"""Tests for quantmathlab.features: indicators and model inputs."""

import numpy as np
import pandas as pd
import pytest
from hypothesis import given
from hypothesis import strategies as st

from quantmathlab.features import (
    bollinger_bands,
    cyclical_encoding,
    macd,
    relative_strength_index,
    sliding_windows,
    stochastic_oscillator,
    williams_r,
)


def _prices(seed: int, periods: int) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    close = 1.1 + np.cumsum(rng.normal(0.0, 1e-3, periods))
    open_ = np.concatenate([[1.1], close[:-1]])
    wick = np.abs(rng.normal(0.0, 5e-4, periods))
    return pd.DataFrame(
        {
            "high": np.maximum(open_, close) + wick,
            "low": np.minimum(open_, close) - wick,
            "close": close,
        }
    )


def test_averaging_indicators_match_hand_computed_values() -> None:
    """RSI, MACD and Bollinger bands match values worked out by hand."""
    close = pd.Series([1.0, 2.0, 3.0, 2.0, 3.0, 4.0])
    rsi = relative_strength_index(close, window=2)
    lines = macd(close.iloc[:3], fast=1, slow=2, signal=2)
    bands = bollinger_bands(close, window=2, width=1.0)
    np.testing.assert_allclose(rsi, [np.nan, np.nan, 100, 50, 75, 87.5])
    np.testing.assert_allclose(lines["macd"], [0, 1 / 3, 4 / 9])
    np.testing.assert_allclose(lines["signal"], [0, 2 / 9, 10 / 27])
    np.testing.assert_allclose(lines["histogram"], [0, 1 / 9, 2 / 27])
    np.testing.assert_allclose(
        bands["middle"].iloc[1:], [1.5, 2.5, 2.5, 2.5, 3.5]
    )
    np.testing.assert_allclose(
        bands["upper"] - bands["middle"], [np.nan] + [0.5] * 5
    )


def test_range_indicators_match_hand_computed_values() -> None:
    """The stochastic oscillator and Williams %R match hand-worked values."""
    high = pd.Series([2.0, 3.0, 4.0, 3.0])
    low = pd.Series([1.0, 1.5, 2.0, 2.5])
    close = pd.Series([1.5, 2.5, 2.5, 3.0])
    stochastic = stochastic_oscillator(high, low, close, window=2, smoothing=2)
    np.testing.assert_allclose(stochastic["k"], [np.nan, 75, 40, 50])
    np.testing.assert_allclose(stochastic["d"], [np.nan, np.nan, 57.5, 45])
    np.testing.assert_allclose(
        williams_r(high, low, close, window=2), [np.nan, -25, -60, -50]
    )


@given(
    seed=st.integers(0, 2**32 - 1),
    periods=st.integers(30, 300),
    window=st.integers(2, 20),
)
def test_indicators_stay_in_their_ranges(
    seed: int, periods: int, window: int
) -> None:
    """Oscillators stay within their bounds, %R is %K - 100, bands ordered."""
    prices = _prices(seed, periods)
    high, low, close = prices["high"], prices["low"], prices["close"]
    rsi = relative_strength_index(close, window).dropna()
    stochastic = stochastic_oscillator(high, low, close, window, 3).dropna()
    percent_r = williams_r(high, low, close, window)
    bands = bollinger_bands(close, window, 2.0).dropna()
    assert rsi.between(0, 100).all()
    assert stochastic["k"].between(0, 100).all()
    assert stochastic["d"].between(0, 100).all()
    np.testing.assert_allclose(
        percent_r.loc[stochastic.index], stochastic["k"] - 100, atol=1e-9
    )
    assert (bands["lower"] <= bands["middle"]).all()
    assert (bands["middle"] <= bands["upper"]).all()


def test_cyclical_encoding_wraps_around() -> None:
    """Values lie on the unit circle and repeat after one period."""
    hours = np.arange(48)
    points = cyclical_encoding(hours, period=24)
    assert points.shape == (48, 2)
    np.testing.assert_allclose(np.hypot(points[:, 0], points[:, 1]), 1.0)
    np.testing.assert_allclose(points[:24], points[24:], atol=1e-12)
    np.testing.assert_allclose(points[6], [1.0, 0.0], atol=1e-12)
    with pytest.raises(ValueError, match="period"):
        cyclical_encoding(hours, period=0)


@given(rows=st.integers(1, 50), columns=st.integers(1, 4), data=st.data())
def test_windows_hold_consecutive_rows(
    rows: int, columns: int, data: st.DataObject
) -> None:
    """Window i holds rows i to i + length - 1, in the table's dtype."""
    length = data.draw(st.integers(1, rows))
    table = np.arange(rows * columns, dtype=np.float32).reshape(rows, columns)
    windows = sliding_windows(table, length)
    assert windows.shape == (rows - length + 1, length, columns)
    assert windows.dtype == np.float32
    for i, window in enumerate(windows):
        np.testing.assert_array_equal(window, table[i : i + length])


@pytest.mark.parametrize("length", [0, 4])
def test_windows_reject_invalid_length(length: int) -> None:
    """A window length of zero, or longer than the table, is rejected."""
    with pytest.raises(ValueError, match="length"):
        sliding_windows(np.zeros((3, 2)), length)
