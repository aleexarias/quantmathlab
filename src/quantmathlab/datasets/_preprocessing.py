"""Preprocessing of market data, such as aggregating bars into longer ones."""

import datetime as dt

import pandas as pd

__all__ = ["resample_bars"]


def resample_bars(
    bars: pd.DataFrame,
    length: str | dt.timedelta,
    anchor: dt.time = dt.time(0),
) -> pd.DataFrame:
    """Aggregate price bars into longer bars of a fixed length.

    Each new bar takes the first ``open``, the highest ``high``, the lowest
    ``low`` and the last ``close`` of the bars falling inside it. The new
    bars are laid out from ``anchor`` on the first day of the data, so one
    starts at that time of day whenever ``length`` divides a day. Periods
    without any bar give no new bar.

    Parameters
    ----------
    bars : pandas.DataFrame
        Bars with ``open``, ``high``, ``low`` and ``close`` columns, indexed
        by their start time, with or without a time zone. Other columns are
        ignored.
    length : str or datetime.timedelta
        Length of the new bars, such as ``"60min"``, ``"4h"`` or ``"1D"``.
    anchor : datetime.time, default midnight
        Time of day the new bars are laid out from.

    Returns
    -------
    pandas.DataFrame
        The new bars, indexed by their start time, with ``open``, ``high``,
        ``low`` and ``close`` prices and a ``count`` column giving the
        number of bars each was built from.

    Raises
    ------
    ValueError
        If ``length`` is not positive.
    """
    step = pd.Timedelta(length)
    if step <= pd.Timedelta(0):
        raise ValueError("length must be positive")
    offset = pd.Timedelta(hours=anchor.hour, minutes=anchor.minute)
    groups = bars.resample(
        step, origin="start_day", offset=offset, closed="left", label="left"
    )
    resampled = groups.agg(
        {"open": "first", "high": "max", "low": "min", "close": "last"}
    )
    resampled["count"] = groups.size()
    return resampled[resampled["count"] > 0]
