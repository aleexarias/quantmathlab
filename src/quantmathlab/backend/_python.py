"""Pure-Python reference implementations of core kernels.

Each kernel mirrors one in the compiled ``_cpp`` module, written for
readability rather than speed; the tests check that both agree. These kernels
are not expected to be used directly.
"""

import math

import numpy as np

from quantmathlab._typing import FloatArray

__all__ = ["black_scholes_call", "black_scholes_put", "normal_cdf"]

_erfc = np.vectorize(math.erfc, otypes=[np.float64])


def normal_cdf(x: FloatArray) -> FloatArray:
    """Standard normal distribution function, elementwise."""
    cdf: FloatArray = 0.5 * _erfc(-x / math.sqrt(2.0))
    return cdf


def _d1_d2(
    spot: FloatArray,
    strike: FloatArray,
    maturity: FloatArray,
    rate: FloatArray,
    volatility: FloatArray,
) -> tuple[FloatArray, FloatArray]:
    spread = volatility * np.sqrt(maturity)
    d1 = (np.log(spot / strike) + (rate + 0.5 * volatility**2) * maturity) / (
        spread
    )
    return d1, d1 - spread


def black_scholes_call(
    spot: FloatArray,
    strike: FloatArray,
    maturity: FloatArray,
    rate: FloatArray,
    volatility: FloatArray,
) -> FloatArray:
    """Black-Scholes call prices; reference for ``_cpp.black_scholes_call``."""
    d1, d2 = _d1_d2(spot, strike, maturity, rate, volatility)
    discount = np.exp(-rate * maturity)
    price: FloatArray = spot * normal_cdf(d1) - strike * discount * (
        normal_cdf(d2)
    )
    return price


def black_scholes_put(
    spot: FloatArray,
    strike: FloatArray,
    maturity: FloatArray,
    rate: FloatArray,
    volatility: FloatArray,
) -> FloatArray:
    """Black-Scholes put prices; reference for ``_cpp.black_scholes_put``."""
    d1, d2 = _d1_d2(spot, strike, maturity, rate, volatility)
    discount = np.exp(-rate * maturity)
    price: FloatArray = strike * discount * normal_cdf(-d2) - spot * (
        normal_cdf(-d1)
    )
    return price
