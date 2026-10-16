"""Technical-analysis indicators computed from price series."""

import pandas as pd

__all__ = [
    "bollinger_bands",
    "macd",
    "relative_strength_index",
    "stochastic_oscillator",
    "williams_r",
]


def relative_strength_index(close: pd.Series, window: int) -> pd.Series:
    r"""Relative strength index of a price series.

    Compares the average size of rises with that of falls over the last
    ``window`` periods, as described by :footcite:t:`murphy_1999_technical`:

    .. math::

       \mathrm{RSI}_t = 100 - \frac{100}{1 + G_t / L_t},

    where :math:`G_t` and :math:`L_t` are the average gain and average loss
    of the close. Both are exponential averages with weight :math:`1 / n`
    on the newest change, started from the first change rather than from a
    simple average of the first :math:`n`, which only affects early values.

    Parameters
    ----------
    close : pandas.Series
        Closing prices, in time order.
    window : int
        Number of periods :math:`n` averaged over.

    Returns
    -------
    pandas.Series
        Values between 0 and 100, undefined for the first ``window``
        periods and while prices do not move.

    References
    ----------
    .. footbibliography::
    """
    change = close.diff()
    gain = change.clip(lower=0.0)
    loss = -change.clip(upper=0.0)
    average_gain = gain.ewm(
        alpha=1 / window, adjust=False, min_periods=window
    ).mean()
    average_loss = loss.ewm(
        alpha=1 / window, adjust=False, min_periods=window
    ).mean()
    return 100.0 - 100.0 / (1.0 + average_gain / average_loss)


def macd(close: pd.Series, fast: int, slow: int, signal: int) -> pd.DataFrame:
    r"""Moving average convergence/divergence of a price series.

    The MACD line is the difference between a fast and a slow exponential
    moving average of the close, the signal line an exponential moving
    average of the MACD line, and the histogram their difference, as
    described by :footcite:t:`murphy_1999_technical`:

    .. math::

       \mathrm{MACD}_t = \mathrm{EMA}_{\text{fast}}(C)_t
                       - \mathrm{EMA}_{\text{slow}}(C)_t.

    Each exponential moving average over :math:`n` periods gives weight
    :math:`2 / (n + 1)` to the newest value and starts from the first.

    Parameters
    ----------
    close : pandas.Series
        Closing prices, in time order.
    fast, slow, signal : int
        Periods of the fast and slow averages and of the signal line.

    Returns
    -------
    pandas.DataFrame
        Columns ``macd``, ``signal`` and ``histogram``.

    References
    ----------
    .. footbibliography::
    """
    line = (
        close.ewm(span=fast, adjust=False).mean()
        - close.ewm(span=slow, adjust=False).mean()
    )
    signal_line = line.ewm(span=signal, adjust=False).mean()
    return pd.DataFrame(
        {
            "macd": line,
            "signal": signal_line,
            "histogram": line - signal_line,
        }
    )


def stochastic_oscillator(
    high: pd.Series,
    low: pd.Series,
    close: pd.Series,
    window: int,
    smoothing: int,
) -> pd.DataFrame:
    r"""Stochastic oscillator of a price series.

    Locates the close within the range of the last ``window`` periods, as
    described by :footcite:t:`murphy_1999_technical`:

    .. math::

       \%K_t = 100 \, \frac{C_t - L_t}{H_t - L_t},

    where :math:`H_t` and :math:`L_t` are the highest high and lowest low of
    those periods; :math:`\%D` is the simple moving average of :math:`\%K`
    over ``smoothing`` periods.

    Parameters
    ----------
    high, low, close : pandas.Series
        High, low and closing prices, in time order.
    window : int
        Number of periods the range is taken over.
    smoothing : int
        Number of periods :math:`\%D` averages over.

    Returns
    -------
    pandas.DataFrame
        Columns ``k`` and ``d``, between 0 and 100.

    References
    ----------
    .. footbibliography::
    """
    highest = high.rolling(window).max()
    lowest = low.rolling(window).min()
    k = 100.0 * (close - lowest) / (highest - lowest)
    return pd.DataFrame({"k": k, "d": k.rolling(smoothing).mean()})


def williams_r(
    high: pd.Series, low: pd.Series, close: pd.Series, window: int
) -> pd.Series:
    r"""Williams %R of a price series.

    Measures how far the close lies below the highest high of the last
    ``window`` periods, relative to their range, as described by
    :footcite:t:`murphy_1999_technical`:

    .. math::

       \%R_t = -100 \, \frac{H_t - C_t}{H_t - L_t},

    with :math:`H_t` and :math:`L_t` as in the stochastic oscillator, so
    that :math:`\%R_t = \%K_t - 100`.

    Parameters
    ----------
    high, low, close : pandas.Series
        High, low and closing prices, in time order.
    window : int
        Number of periods the range is taken over.

    Returns
    -------
    pandas.Series
        Values between -100 and 0.

    References
    ----------
    .. footbibliography::
    """
    highest = high.rolling(window).max()
    lowest = low.rolling(window).min()
    return -100.0 * (highest - close) / (highest - lowest)


def bollinger_bands(
    close: pd.Series, window: int, width: float
) -> pd.DataFrame:
    r"""Bollinger bands of a price series.

    A simple moving average of the close over ``window`` periods, with
    bands ``width`` standard deviations above and below it, as described by
    :footcite:t:`murphy_1999_technical`:

    .. math::

       \mathrm{SMA}_t \pm k \, \sigma_t,

    where :math:`\sigma_t` is the population standard deviation of the same
    closes.

    Parameters
    ----------
    close : pandas.Series
        Closing prices, in time order.
    window : int
        Number of periods averaged over.
    width : float
        Number of standard deviations :math:`k` between the middle and each
        band.

    Returns
    -------
    pandas.DataFrame
        Columns ``lower``, ``middle`` and ``upper``.

    References
    ----------
    .. footbibliography::
    """
    middle = close.rolling(window).mean()
    deviation = close.rolling(window).std(ddof=0)
    return pd.DataFrame(
        {
            "lower": middle - width * deviation,
            "middle": middle,
            "upper": middle + width * deviation,
        }
    )
