"""Compiled C++ kernels, built from ``cpp/`` with pybind11."""

# This module is only useful for type checking and to orient the user to use
# the available kernels; the actual implementations are in the compiled
# ``_cpp`` module.

import numpy as np
import numpy.typing as npt

def black_scholes_call(
    spot: npt.ArrayLike,
    strike: npt.ArrayLike,
    maturity: npt.ArrayLike,
    rate: npt.ArrayLike,
    volatility: npt.ArrayLike,
) -> npt.NDArray[np.float64] | float: ...
def black_scholes_put(
    spot: npt.ArrayLike,
    strike: npt.ArrayLike,
    maturity: npt.ArrayLike,
    rate: npt.ArrayLike,
    volatility: npt.ArrayLike,
) -> npt.NDArray[np.float64] | float: ...
