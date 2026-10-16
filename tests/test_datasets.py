"""Tests for quantmathlab.datasets: loading quotes and preprocessing bars.

The histdata.com loader is tested without network access, on small zip files
written like the ones histdata.com serves.
"""

import datetime as dt
import zipfile
from pathlib import Path

import numpy as np
import pandas as pd
import pytest
from hypothesis import given
from hypothesis import strategies as st

from quantmathlab.datasets import _histdata, load_histdata, resample_bars


def _write_archive(directory: Path, year: int, rows: list[str]) -> None:
    name = f"DAT_ASCII_EURUSD_M1_{year}"
    with zipfile.ZipFile(directory / f"{name}.zip", "w") as zipped:
        zipped.writestr(f"{name}.csv", "\n".join(rows) + "\n")
        zipped.writestr(f"{name}.txt", "HistData.com status report\n")


def _bars(start: str, periods: int) -> pd.DataFrame:
    rng = np.random.default_rng(0)
    close = 1.1 + np.cumsum(rng.normal(0.0, 1e-4, periods))
    open_ = np.concatenate([[1.1], close[:-1]])
    wick = np.abs(rng.normal(0.0, 5e-5, periods))
    return pd.DataFrame(
        {
            "open": open_,
            "high": np.maximum(open_, close) + wick,
            "low": np.minimum(open_, close) - wick,
            "close": close,
        },
        index=pd.date_range(start, periods=periods, freq="min"),
    )


@pytest.fixture
def downloads(
    monkeypatch: pytest.MonkeyPatch,
) -> list[dict[str, object]]:
    calls: list[dict[str, object]] = []

    def fake_download(**kwargs: object) -> str:
        calls.append(kwargs)
        year = int(str(kwargs["year"]))
        directory = Path(str(kwargs["output_directory"]))
        _write_archive(
            directory, year, [f"{year}0104 000000;1.1;1.2;1.0;1.15;0"]
        )
        return str(directory)

    monkeypatch.setattr(_histdata, "download_hist_data", fake_download)
    return calls


def test_reads_bars_in_histdata_time(tmp_path: Path) -> None:
    """A file reads into float prices with histdata's plain times."""
    _write_archive(
        tmp_path,
        2010,
        [
            "20100103 170000;1.430100;1.430400;1.430100;1.430400;0",
            "20100103 170100;1.430300;1.430300;1.430200;1.430300;0",
        ],
    )
    quotes = load_histdata("eurusd", [2010], tmp_path)
    assert list(quotes.columns) == ["open", "high", "low", "close"]
    assert all(dtype == "float64" for dtype in quotes.dtypes)
    assert quotes.index.name == "time"
    assert pd.DatetimeIndex(quotes.index).tz is None
    assert quotes.index[0] == pd.Timestamp("2010-01-03 17:00")
    assert quotes.iloc[1].tolist() == [1.4303, 1.4303, 1.4302, 1.4303]


def test_downloads_only_missing_years(
    tmp_path: Path, downloads: list[dict[str, object]]
) -> None:
    """Only years without a local file are downloaded, correctly."""
    _write_archive(tmp_path, 2010, ["20100104 000000;1.4;1.5;1.3;1.45;0"])
    quotes = load_histdata("EURUSD", [2011, 2010], tmp_path)
    assert downloads == [
        {
            "year": "2011",
            "pair": "eurusd",
            "time_frame": "M1",
            "platform": "ASCII",
            "output_directory": str(tmp_path),
            "verbose": False,
        }
    ]
    assert pd.DatetimeIndex(quotes.index).year.tolist() == [2010, 2011]


def test_merges_years_and_drops_repeated_bars(tmp_path: Path) -> None:
    """Years merge in time order and repeated bars are kept once."""
    repeated = "20201025 190000;1.18;1.19;1.17;1.185;0"
    _write_archive(tmp_path, 2020, [repeated, repeated])
    _write_archive(tmp_path, 2019, ["20191231 120000;1.12;1.13;1.11;1.125;0"])
    quotes = load_histdata("eurusd", range(2019, 2021), tmp_path)
    assert len(quotes) == 2
    assert quotes.index.is_monotonic_increasing
    assert not quotes.index.has_duplicates


@pytest.mark.parametrize("years", [[], [2010, 9999]])
def test_rejects_invalid_years(tmp_path: Path, years: list[int]) -> None:
    """No years, or a year not yet over, raises a ValueError."""
    with pytest.raises(ValueError, match="years"):
        load_histdata("eurusd", years, tmp_path)


def test_aggregates_bars_and_skips_gaps() -> None:
    """Bars take first open, max high, min low and last close; gaps vanish."""
    friday = _bars("2010-01-08 15:00", 120)
    sunday = _bars("2010-01-10 17:00", 60)
    resampled = resample_bars(pd.concat([friday, sunday]), "60min")
    first_hour = friday.iloc[:60]
    assert pd.DatetimeIndex(resampled.index).strftime("%a %H:%M").tolist() == [
        "Fri 15:00",
        "Fri 16:00",
        "Sun 17:00",
    ]
    assert resampled.iloc[0].tolist() == [
        first_hour["open"].iloc[0],
        first_hour["high"].max(),
        first_hour["low"].min(),
        first_hour["close"].iloc[-1],
        60,
    ]


def test_bars_start_from_anchor() -> None:
    """Bars start at the anchor, midnight by default, every length after."""
    bars = _bars("2010-01-05 00:00", 3 * 1440)
    default = resample_bars(bars, "8h")
    evening = resample_bars(bars, "12h", anchor=dt.time(17))
    assert sorted(set(pd.DatetimeIndex(default.index).strftime("%H:%M"))) == [
        "00:00",
        "08:00",
        "16:00",
    ]
    assert sorted(set(pd.DatetimeIndex(evening.index).strftime("%H:%M"))) == [
        "05:00",
        "17:00",
    ]


def test_rejects_non_positive_length() -> None:
    """A bar length of zero raises a ValueError."""
    with pytest.raises(ValueError, match="length"):
        resample_bars(_bars("2010-01-04 17:00", 10), "0min")


@given(
    periods=st.integers(61, 2000),
    length=st.sampled_from(["5min", "60min", "4h", "12h"]),
    gap=st.integers(0, 1999),
)
def test_bars_contain_their_bars(periods: int, length: str, gap: int) -> None:
    """Every input bar lands in one new bar, within its high and low."""
    bars = _bars("2010-01-04 17:00", periods)
    bars = bars.drop(bars.index[gap % periods :][:60])
    resampled = resample_bars(bars, length)
    assert resampled["count"].sum() == len(bars)
    assert (
        resampled["high"] >= resampled[["open", "close"]].max(axis=1)
    ).all()
    assert (resampled["low"] <= resampled[["open", "close"]].min(axis=1)).all()
    assert resampled["high"].max() == bars["high"].max()
    assert resampled["low"].min() == bars["low"].min()
