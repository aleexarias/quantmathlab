"""One-minute foreign exchange quotes from histdata.com."""

import datetime as dt
import os
import zipfile
from collections.abc import Iterable
from pathlib import Path

import pandas as pd
from histdata.api import Platform, TimeFrame, download_hist_data

__all__ = ["load_histdata"]

_PRICES = ["open", "high", "low", "close"]


def _archive(directory: Path, pair: str, year: int) -> Path:
    return directory / f"DAT_ASCII_{pair.upper()}_M1_{year}.zip"


def _download(directory: Path, pair: str, year: int) -> Path:
    archive = _archive(directory, pair, year)
    if not archive.is_file():
        download_hist_data(
            year=str(year),
            pair=pair.lower(),
            time_frame=TimeFrame.ONE_MINUTE,
            platform=Platform.GENERIC_ASCII,
            output_directory=str(directory),
            verbose=False,
        )
    return archive


def _read(archive: Path) -> pd.DataFrame:
    with zipfile.ZipFile(archive) as zipped:
        name = next(n for n in zipped.namelist() if n.endswith(".csv"))
        with zipped.open(name) as csv:
            bars = pd.read_csv(
                csv,
                sep=";",
                header=None,
                names=["time", *_PRICES, "volume"],
                usecols=["time", *_PRICES],
                dtype=dict.fromkeys(_PRICES, "float64"),
            )
    times = pd.to_datetime(bars.pop("time"), format="%Y%m%d %H%M%S")
    bars.index = pd.DatetimeIndex(times).rename("time")
    return bars


def load_histdata(
    pair: str, years: Iterable[int], directory: str | os.PathLike[str]
) -> pd.DataFrame:
    """Load one-minute foreign exchange quotes from histdata.com.

    histdata.com publishes free one-minute bars for major currency pairs as
    one zip file per pair and year. Files missing from ``directory`` are
    downloaded there with the ``histdata`` package; files already present
    are read without downloading them again.

    Parameters
    ----------
    pair : str
        Currency pair or other instrument as listed on histdata.com, such
        as ``"eurusd"``, in any letter case.
    years : iterable of int
        Calendar years to load. Only complete years are available, so every
        year must be before the current one.
    directory : str or path-like
        Folder holding the downloaded zip files, created if needed.

    Returns
    -------
    pandas.DataFrame
        The ``open``, ``high``, ``low`` and ``close`` prices of every
        one-minute bar, indexed by the bar's start time as histdata.com
        publishes it, without a time zone, and sorted in time.

    Raises
    ------
    ValueError
        If ``years`` is empty or contains the current or a future year.
    AssertionError
        If histdata.com cannot be reached or has no data for the pair and
        year, as raised by the ``histdata`` package.

    Notes
    -----
    histdata.com records times in US Eastern Standard Time without daylight
    saving, a fixed offset of five hours behind UTC, so the trading week
    opens at 17:00. The times are returned as published, without a time
    zone; ``quotes.tz_localize("Etc/GMT+5").tz_convert("UTC")`` gives the
    same bars in UTC (``Etc/GMT+5`` is the standard name for a fixed
    UTC-5 offset, with the sign inverted by convention).

    Some of its yearly files list one hour of bars twice, as identical
    copies; EUR/USD does so in 2019, 2020 and 2021. Only the first copy of
    each bar is kept.
    """
    wanted = sorted(set(years))
    if not wanted:
        raise ValueError("years must not be empty")
    current_year = dt.datetime.now(dt.UTC).year
    if wanted[-1] >= current_year:
        raise ValueError(
            f"histdata.com only has complete years before {current_year}"
        )
    folder = Path(directory)
    folder.mkdir(parents=True, exist_ok=True)
    yearly = [_read(_download(folder, pair, year)) for year in wanted]
    quotes = pd.concat(yearly).sort_index(kind="stable")
    return quotes[~quotes.index.duplicated()]
