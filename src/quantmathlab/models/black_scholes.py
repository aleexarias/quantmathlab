"""Black-Scholes prices of European options, computed by the C++ backend."""

import numpy as np
import numpy.typing as npt

from quantmathlab._typing import FloatArray
from quantmathlab.backend import _cpp

__all__ = ["bs_call_price", "bs_put_price"]

_POSITIVE = ("spot", "strike", "maturity", "volatility")


def _validate(
    spot: npt.ArrayLike,
    strike: npt.ArrayLike,
    maturity: npt.ArrayLike,
    rate: npt.ArrayLike,
    volatility: npt.ArrayLike,
) -> tuple[FloatArray, FloatArray, FloatArray, FloatArray, FloatArray]:
    inputs = {
        "spot": spot,
        "strike": strike,
        "maturity": maturity,
        "rate": rate,
        "volatility": volatility,
    }
    arrays = np.broadcast_arrays(
        *(np.asarray(value, dtype=np.float64) for value in inputs.values())
    )
    for name, values in zip(inputs, arrays, strict=True):
        if not np.all(np.isfinite(values)):
            raise ValueError(f"{name} must be finite")
        if name in _POSITIVE and not np.all(values > 0.0):
            raise ValueError(f"{name} must be positive")
    s, k, t, r, v = arrays
    return s, k, t, r, v


def bs_call_price(
    spot: npt.ArrayLike,
    strike: npt.ArrayLike,
    maturity: npt.ArrayLike,
    rate: npt.ArrayLike,
    volatility: npt.ArrayLike,
) -> FloatArray:
    r"""Price European call options with the Black-Scholes formula.

    Computes the price of a European call under the model of
    :footcite:t:`black+scholes_1973_pricing`, in which the underlying
    follows a geometric Brownian motion with constant volatility
    :math:`\sigma` and the risk-free rate :math:`r` is constant:

    .. math::

       C = S\,\Phi(d_1) - K e^{-rT}\,\Phi(d_2),
       \qquad
       d_{1,2} = \frac{\ln(S/K) + \left(r \pm \tfrac{1}{2}\sigma^2\right) T}
                      {\sigma\sqrt{T}},

    where :math:`\Phi` is the standard normal distribution function. The
    arguments broadcast against each other like NumPy arrays, and the
    formula is evaluated by the compiled C++ kernel.

    Parameters
    ----------
    spot : array_like
        Current price of the underlying, :math:`S > 0`.
    strike : array_like
        Strike prices, :math:`K > 0`.
    maturity : array_like
        Time to expiry in years, :math:`T > 0`.
    rate : array_like
        Continuously compounded risk-free rate :math:`r`.
    volatility : array_like
        Annualized volatility of the underlying, :math:`\sigma > 0`.

    Returns
    -------
    FloatArray
        Call prices, with the broadcast shape of the arguments.

    Raises
    ------
    ValueError
        If any argument is not finite, if ``spot``, ``strike``, ``maturity``
        or ``volatility`` is not positive, or if the shapes of the arguments
        do not broadcast.

    See Also
    --------
    bs_put_price : Put prices under the same model.

    References
    ----------
    .. footbibliography::
    """
    prices = _cpp.black_scholes_call(
        *_validate(spot, strike, maturity, rate, volatility)
    )
    return np.asarray(prices, dtype=np.float64)


def bs_put_price(
    spot: npt.ArrayLike,
    strike: npt.ArrayLike,
    maturity: npt.ArrayLike,
    rate: npt.ArrayLike,
    volatility: npt.ArrayLike,
) -> FloatArray:
    r"""Price European put options with the Black-Scholes formula.

    Computes the price of a European put under the model of
    :footcite:t:`black+scholes_1973_pricing`, with the same assumptions as
    :func:`bs_call_price`:

    .. math::

       P = K e^{-rT}\,\Phi(-d_2) - S\,\Phi(-d_1),

    with :math:`d_1`, :math:`d_2` and :math:`\Phi` as for the call. The
    arguments broadcast against each other like NumPy arrays, and the
    formula is evaluated by the compiled C++ kernel.

    Parameters
    ----------
    spot : array_like
        Current price of the underlying, :math:`S > 0`.
    strike : array_like
        Strike prices, :math:`K > 0`.
    maturity : array_like
        Time to expiry in years, :math:`T > 0`.
    rate : array_like
        Continuously compounded risk-free rate :math:`r`.
    volatility : array_like
        Annualized volatility of the underlying, :math:`\sigma > 0`.

    Returns
    -------
    FloatArray
        Put prices, with the broadcast shape of the arguments.

    Raises
    ------
    ValueError
        If any argument is not finite, if ``spot``, ``strike``, ``maturity``
        or ``volatility`` is not positive, or if the shapes of the arguments
        do not broadcast.

    See Also
    --------
    bs_call_price : Call prices under the same model.

    References
    ----------
    .. footbibliography::
    """
    prices = _cpp.black_scholes_put(
        *_validate(spot, strike, maturity, rate, volatility)
    )
    return np.asarray(prices, dtype=np.float64)
