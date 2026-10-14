"""Tests for the Black-Scholes pricers and their C++ kernel."""

import numpy as np
import numpy.typing as npt
import pytest
from hypothesis import given
from hypothesis import strategies as st

from quantmathlab.backend import _cpp, _python
from quantmathlab.models import bs_call_price, bs_put_price

# On Linux the C++ kernel and the NumPy reference agree bit for bit, and
# put-call parity holds to 5e-16 of max(S, K) over 200,000 random inputs;
# 1e-12 leaves room for the different libm of macOS and Windows.
RELATIVE_TOLERANCE = 1e-12

spots = st.floats(1.0, 1000.0)
moneyness = st.floats(0.25, 4.0)
maturities = st.floats(0.01, 10.0)
rates = st.floats(-0.05, 0.2)
volatilities = st.floats(0.01, 2.0)


def test_textbook_values() -> None:
    call = bs_call_price(100.0, 100.0, 1.0, 0.05, 0.2)
    put = bs_put_price(100.0, 100.0, 1.0, 0.05, 0.2)
    assert float(call) == pytest.approx(10.4506, abs=5e-5)
    assert float(put) == pytest.approx(5.5735, abs=5e-5)


@given(spots, moneyness, maturities, rates, volatilities)
def test_cpp_kernels_match_python_reference(
    spot: float, ratio: float, maturity: float, rate: float, vol: float
) -> None:
    args = [np.array([value]) for value in (spot, spot * ratio, maturity)]
    args += [np.array([rate]), np.array([vol])]
    scale = RELATIVE_TOLERANCE * max(spot, spot * ratio)
    for name in ("black_scholes_call", "black_scholes_put"):
        compiled = getattr(_cpp, name)(*args)
        reference = getattr(_python, name)(*args)
        np.testing.assert_allclose(compiled, reference, rtol=0, atol=scale)


@given(spots, moneyness, maturities, rates, volatilities)
def test_put_call_parity_and_bounds(
    spot: float, ratio: float, maturity: float, rate: float, vol: float
) -> None:
    strike = spot * ratio
    discounted_strike = strike * np.exp(-rate * maturity)
    tolerance = RELATIVE_TOLERANCE * max(spot, strike)
    call = float(bs_call_price(spot, strike, maturity, rate, vol))
    put = float(bs_put_price(spot, strike, maturity, rate, vol))
    assert call - put == pytest.approx(spot - discounted_strike, abs=tolerance)
    assert max(spot - discounted_strike, 0.0) - tolerance <= call
    assert call <= spot + tolerance
    assert max(discounted_strike - spot, 0.0) - tolerance <= put
    assert put <= discounted_strike + tolerance


@given(spots, maturities, rates, volatilities)
def test_monotone_and_convex_in_strike(
    spot: float, maturity: float, rate: float, vol: float
) -> None:
    strikes = np.linspace(0.5 * spot, 2.0 * spot, 31)
    tolerance = RELATIVE_TOLERANCE * 2.0 * spot
    calls = bs_call_price(spot, strikes, maturity, rate, vol)
    puts = bs_put_price(spot, strikes, maturity, rate, vol)
    assert np.all(np.diff(calls) <= tolerance)
    assert np.all(np.diff(puts) >= -tolerance)
    assert np.all(np.diff(calls, 2) >= -tolerance)
    assert np.all(np.diff(puts, 2) >= -tolerance)


def test_output_shapes() -> None:
    grid = bs_call_price(100.0, [[90.0], [110.0]], [0.5, 1.0], 0.05, 0.2)
    assert grid.shape == (2, 2)
    assert grid[1, 0] == bs_call_price(100.0, 110.0, 0.5, 0.05, 0.2)
    single = bs_put_price(100.0, 100.0, 1.0, 0.05, 0.2)
    assert isinstance(single, np.ndarray)
    assert single.shape == ()


def test_invalid_arguments_raise() -> None:
    valid: dict[str, npt.ArrayLike] = {
        "spot": 100.0,
        "strike": 100.0,
        "maturity": 1.0,
        "rate": 0.05,
        "volatility": 0.2,
    }
    cases: list[tuple[dict[str, npt.ArrayLike], str]] = [
        ({"spot": 0.0}, "spot must be positive"),
        ({"strike": -1.0}, "strike must be positive"),
        ({"maturity": 0.0}, "maturity must be positive"),
        ({"volatility": 0.0}, "volatility must be positive"),
        ({"rate": np.nan}, "rate must be finite"),
        ({"spot": np.inf}, "spot must be finite"),
        ({"strike": [90.0, 110.0], "maturity": [0.5, 1.0, 2.0]}, "broadcast"),
    ]
    for pricer in (bs_call_price, bs_put_price):
        for overrides, message in cases:
            with pytest.raises(ValueError, match=message):
                pricer(**(valid | overrides))
