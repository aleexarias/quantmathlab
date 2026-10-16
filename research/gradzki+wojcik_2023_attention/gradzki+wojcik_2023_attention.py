"""
Notebook
========

Numerical experiments reproducing
:cite:t:`gradzki+wojcik_2023_attention`.
"""

# %%

import datetime as dt
import io
from pathlib import Path

import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from quantmathlab.datasets import load_histdata, resample_bars
from quantmathlab.features import (
    bollinger_bands,
    cyclical_encoding,
    macd,
    relative_strength_index,
    sliding_windows,
    stochastic_oscillator,
    williams_r,
)
from quantmathlab.validation import accuracy, roc_auc

# %%
# Data
# ----
# The paper uses one-minute quotes from histdata.com for 2010 to 2021, six
# currency pairs and five bar lengths. This notebook reproduces it for the
# series that lead to the paper's main conclusion: EUR/CHF at 60, 120 and 720
# minutes, and USD/JPY at 60 minutes as the counterexample. The yearly files
# are downloaded into ``data/`` the first time it runs, and read from there
# afterwards.
#
# histdata.com stamps its quotes with its own clock. The paper's times run six
# hours ahead of it. The quotes are moved to the paper's clock, so that the
# bars, the hours of the day and the years all follow it.
#
# Each pair's quotes are then aggregated into bars of the lengths studied, and
# only the bars are kept.

LENGTHS = {"eurchf": [60, 120, 720], "usdjpy": [60]}
PAPER_MINUTES = pd.Index([60, 120, 240, 480, 720], name="minutes")
TIME_SHIFT = pd.Timedelta(hours=6)

bars = {}
quotes_per_year = {}
for pair, lengths in LENGTHS.items():
    quotes = load_histdata(pair, range(2010, 2022), "data")
    quotes.index = quotes.index + TIME_SHIFT
    quotes_per_year[pair] = quotes.groupby(quotes.index.year).size()
    for minutes in lengths:
        bars[pair, minutes] = resample_bars(
            quotes, f"{minutes}min", anchor=dt.time(5)
        )
del quotes

# %%
# Most years hold roughly 340,000 to 375,000 one-minute bars: about 24
# hours of trading on each of the five weekdays, minus holidays and the
# minutes without a quote. USD/JPY has fewer in 2010 and 2011, the years
# with the most minutes missing.

pd.DataFrame(quotes_per_year).rename_axis("year")

# %%
# The aggregated bars, as an example EUR/CHF at 60 minutes. The ``count``
# column gives the number of one-minute bars each bar was built from.

bars["eurchf", 60]

# %%
# Target
# ------
# The models classify whether the next bar closes above the current one,
# "buy", or not, "sell". A close equal to the current one counts as "sell".
# Below, the share of "buy" in the training years, 2010 to 2019, for each
# bar length and pair.


def buy_share(bars: pd.DataFrame) -> float:
    """Share of bars in 2010 to 2019 whose next close is higher."""
    buy = (bars["close"].shift(-1) > bars["close"]).iloc[:-1]
    return float(buy[buy.index.year <= 2019].mean())

table_1 = pd.Series(
    {key: buy_share(frame) for key, frame in bars.items()}
).rename_axis(["pair", "minutes"])
table_1.unstack("pair").round(2)

# %%
# Moves smaller than the cost
# ---------------------------
# The data has no bid-ask spread, so the paper charges each trade a fixed
# spread: 2 pips for EUR/CHF and 1.5 for USD/JPY, where a pip is 0.0001 for
# EUR/CHF and 0.01 for USD/JPY. Below, the share of bar-to-bar moves of the
# close smaller than that cost over 2010 to 2021, moves which no strategy
# trading every bar can profit from, for each bar length and pair.

SPREAD_PIPS = {"eurchf": 2.0, "usdjpy": 1.5}

def pip(pair: str) -> float:
    """Size of a pip of a pair, in units of its price."""
    return 0.01 if pair.endswith("jpy") else 0.0001

def spread(pair: str) -> float:
    """The paper's spread for a pair, in units of its price."""
    return SPREAD_PIPS[pair] * pip(pair)

def share_below_cost(bars: pd.DataFrame, pair: str) -> float:
    """Percentage of bar-to-bar moves of the close smaller than the cost."""
    moves = bars["close"].diff().abs().dropna()
    return float(100 * (moves < spread(pair)).mean())

table_2 = pd.Series(
    {
        (pair, m): share_below_cost(frame, pair)
        for (pair, m), frame in bars.items()
    }
).rename_axis(["pair", "minutes"])
table_2.unstack("pair").round(1)

# %%
# Features
# --------
# Each bar is described by the features the paper lists, computed from that
# bar and the ones before it:
#
# - its open, high, low and close;
# - simple and exponential moving averages and the standard deviation of
#   the close over 3, 5, 10, 13 and 20 bars;
# - the stochastic oscillator, :math:`\%K` and :math:`\%D`;
# - the relative strength index over 14 and over 10 bars;
# - the MACD line, its signal line and their difference;
# - Williams %R;
# - Bollinger bands two standard deviations wide, over 5 bars;
# - the return since the previous close;
# - the sine and cosine of the hour and of the weekday.
#
# That makes 35 features. The paper counts 40 but does not name the other
# five, so we left them out.
#
# The hour :math:`h` is encoded with the paper's formula,
# :math:`\sin(2\pi h / 23)` and :math:`\cos(2\pi h / 23)`, which divides by
# the largest hour, 23, rather than by the 24 hours of a day. The weekday
# :math:`d`, from 0 on Monday to 6 on Sunday, is encoded the same way,
# divided by its largest value, 6.

AVERAGES = [3, 5, 10, 13, 20]

def model_features(bars: pd.DataFrame) -> pd.DataFrame:
    """The paper's features of each bar."""
    high, low, close = bars["high"], bars["low"], bars["close"]
    time = pd.DatetimeIndex(bars.index)
    features = bars[["open", "high", "low", "close"]].copy()
    for n in AVERAGES:
        features[f"sma_{n}"] = close.rolling(n).mean()
        features[f"ema_{n}"] = close.ewm(span=n, adjust=False).mean()
        features[f"std_{n}"] = close.rolling(n).std()
    features[["stochastic_k", "stochastic_d"]] = stochastic_oscillator(
        high, low, close, window=14, smoothing=3
    )
    features["rsi_14"] = relative_strength_index(close, window=14)
    features["rsi_10"] = relative_strength_index(close, window=10)
    features[["macd", "macd_signal", "macd_histogram"]] = macd(
        close, fast=12, slow=26, signal=9
    )
    features["williams_r"] = williams_r(high, low, close, window=14)
    features[["bollinger_lower", "bollinger_middle", "bollinger_upper"]] = (
        bollinger_bands(close, window=5, width=2.0)
    )
    features["return"] = close.pct_change()
    features[["hour_sin", "hour_cos"]] = cyclical_encoding(time.hour, 23)
    features[["weekday_sin", "weekday_cos"]] = cyclical_encoding(
        time.weekday, 6
    )
    return features

features = {key: model_features(frame) for key, frame in bars.items()}
features["eurchf", 60].tail(3).T

# %%
# Model inputs
# ------------
# A sample is a window of 96 consecutive bars, four trading days at 60
# minutes, that ends at the bar whose next close is predicted. Its label is
# 1, "buy", if that close is higher and 0, "sell", otherwise. The year of
# its last bar places it in the training set, 2010 to 2019, the validation
# set, 2020, or the test set, 2021. The first 19 bars of each series, where
# some indicator lacks enough history, are dropped.
#
# Each feature is then standardized with the mean and standard deviation of
# the training bars, and the same values are applied to the validation and
# test bars.

WINDOW = 96

def model_inputs(
    bars: pd.DataFrame, features: pd.DataFrame
) -> tuple[pd.DataFrame, pd.Series, np.ndarray]:
    """Standardized features, label and set of each bar with a next close."""
    table = features.iloc[:-1].dropna()
    label = (bars["close"].shift(-1) > bars["close"]).loc[table.index]
    year = pd.DatetimeIndex(table.index).year
    split = np.select(
        [year <= 2019, year == 2020], ["train", "validation"], "test"
    )
    train = table[split == "train"]
    standardized = (table - train.mean()) / train.std(ddof=0)
    return standardized, label.astype("int8"), split


# %%
# The inputs are saved in ``data/inputs/``, one file per pair and bar
# length, for the training script, ``training/train.py``. It runs outside
# this notebook, since training takes far longer than a documentation
# build, and writes its predictions to ``results/``, where the notebook
# reads them. Each file holds, for every bar, the standardized features,
# the label, the set and the time. The script builds the windows with
# :func:`~quantmathlab.features.sliding_windows`, and each window takes the
# label and the set of its last bar. The number of windows in each set:

directory = Path("data", "inputs")
directory.mkdir(exist_ok=True)
windows = {}
for (pair, minutes), frame in bars.items():
    table, label, split = model_inputs(frame, features[pair, minutes])
    np.savez(
        directory / f"{pair}_{minutes}.npz",
        features=table.to_numpy(np.float32),
        label=label.to_numpy(),
        split=split,
        time=table.index.to_numpy(),
        names=table.columns.to_numpy(str),
    )
    windows[pair, minutes] = pd.DataFrame(
        {"label": label, "set": split}, index=table.index
    ).iloc[WINDOW - 1 :]

pd.DataFrame(
    {key: frame["set"].value_counts() for key, frame in windows.items()}
).T.rename_axis(["pair", "minutes"])[["train", "validation", "test"]]

# %%
# For EUR/CHF at 60 minutes, the windows the model receives: one for each bar
# from the 96th on, of 96 bars by 35 features.

inputs = np.load(directory / "eurchf_60.npz")
sliding_windows(inputs["features"], WINDOW).shape

# %%
# Predictions
# -----------
# The models are the paper's Transformer, one for each pair and bar length.
# Trainable positional encodings are added to the features, which pass
# through four blocks of multi-head attention, with 4 heads whose queries,
# keys and values have size 64, and of a feed-forward layer of 128 units
# with ReLU, each followed by a residual connection and layer normalization.
# Global average pooling over the window and a linear layer then give the
# probabilities of "sell" and "buy". Dropout of 0.25 acts on the attention
# weights and after the feed-forward layer's activation. Each model is
# trained with Adam on batches of 64 to minimize the cross-entropy of the
# two classes, from the same random seed, for at most 100 epochs, stopping
# once the validation accuracy has not improved for 30, and keeps the
# weights with the best accuracy on the validation set.
#
# One choice departs from the paper. At its learning rate of 0.001 the
# 60-minute models give every window the same prediction: their training
# loss stays at that of a coin flip, :math:`\ln 2`, and their validation
# accuracy at the share of the more frequent class. The learning rate is
# therefore 0.0001, reached by rising linearly over the first epoch, with
# gradients clipped to a norm of 1.
#
# For every validation and test window, ``training/train.py`` saves in
# ``results/`` the probability of "buy" given by the trained model. A pair
# and bar length not trained yet gets placeholder predictions instead: a
# probability of 0.5 for every window, from a model with no view on the
# direction.

RESULTS = Path("results")

def predictions(pair: str, minutes: int, windows: pd.DataFrame) -> pd.Series:
    """Probability of "buy" of each validation and test window."""
    evaluated = windows.index[windows["set"] != "train"]
    path = RESULTS / f"{pair}_{minutes}.csv"
    if not path.exists():
        return pd.Series(0.5, index=evaluated)
    saved = pd.read_csv(path, index_col="time", parse_dates=["time"])
    probability = saved["probability"].reindex(evaluated)
    if len(saved) != len(evaluated) or probability.isna().any():
        raise ValueError(f"{path} does not match the model inputs")
    return probability

test = {}
for (pair, minutes), frame in windows.items():
    close = bars[pair, minutes]["close"]
    evaluated = frame.assign(
        probability=predictions(pair, minutes, frame),
        close=close,
        next_close=close.shift(-1),
    )
    test[pair, minutes] = evaluated[evaluated["set"] == "test"]

pd.Series(
    {
        (pair, minutes): (RESULTS / f"{pair}_{minutes}.csv").exists()
        for pair, minutes in windows
    },
    name="trained",
).rename_axis(["pair", "minutes"]).to_frame()

# %%
# Accuracy
# --------
# The paper's Table 3 measures each model on the test year, 2021, by its
# accuracy, predicting "buy" when the probability is above one half, and
# by the area under its ROC curve, which uses the probabilities themselves.
# Each pair and bar length shows ours next to the paper's Transformer.

PAPER_TABLE_3 = """\
pair   minutes accuracy auroc
eurchf 60      0.55     0.56
eurchf 120     0.55     0.56
eurchf 240     0.52     0.52
eurchf 480     0.56     0.56
eurchf 720     0.60     0.60
usdjpy 60      0.51     0.51
usdjpy 120     0.50     0.52
usdjpy 240     0.52     0.52
usdjpy 480     0.57     0.56
usdjpy 720     0.53     0.53
"""

paper_table_3 = pd.read_csv(
    io.StringIO(PAPER_TABLE_3), sep=r"\s+", index_col=["pair", "minutes"]
)
table_3 = pd.DataFrame(
    {
        key: {
            "accuracy": accuracy(frame["label"], frame["probability"] > 0.5),
            "auroc": roc_auc(frame["label"], frame["probability"]),
        }
        for key, frame in test.items()
    }
).T.rename_axis(["pair", "minutes"])
pd.concat(
    {
        "ours": table_3.round(2),
        "paper": paper_table_3.reindex(table_3.index),
    },
    axis=1,
).swaplevel(axis=1).sort_index(axis=1)

# %%
# For EUR/CHF the models reach the paper's accuracy: at 60 and 120 minutes to
# within a hundredth, with an area under the ROC curve slightly above the
# paper's, and at 720 minutes a few hundredths below it. USD/JPY at 60 minutes
# learns no lasting signal.
#
# These figures carry noise. Each model is trained once, from a single seed,
# and the test year holds about 6,200 windows at 60 minutes, 3,100 at 120 and
# 570 at 720, so the accuracy alone has a standard error of about 0.006, 0.009
# and 0.02. Differences of a few hundredths from the paper are within or close
# to that noise.

# %%
# Trading
# -------
# The paper trades on the predictions with a band of probabilities around
# one half. Above the band it holds a long position until the next close,
# below it a short one, and inside it none, closing any position held. Six
# bands are tested, from 0.5-0.5, always in the market, to 0.25-0.75. Each
# strategy starts with a capital of 100, all of it invested in every
# position, without leverage, and its returns compound from bar to bar.
#
# Trades pay the spreads used above. A position bought and later sold loses
# one spread, the gap between the price it is bought at and the price it is
# sold at; the backtest charges half of it when the position is opened and
# half when it is closed, so switching from long to short costs a whole one.
# A position still open at the end of 2021 is closed then.

BANDS = [
    (0.5, 0.5),
    (0.45, 0.55),
    (0.4, 0.6),
    (0.35, 0.65),
    (0.3, 0.7),
    (0.25, 0.75),
]
THRESHOLDS = [f"{lower}-{upper}" for lower, upper in BANDS]

def positions(probability: pd.Series, lower: float, upper: float) -> pd.Series:
    """1 for long above the band, -1 for short below it, 0 inside it."""
    return pd.Series(
        np.select([probability > upper, probability < lower], [1, -1], 0),
        index=probability.index,
    )

def equity(position: pd.Series, test: pd.DataFrame, cost: float) -> pd.Series:
    """Capital after each bar, from 100, paying a spread of ``cost``."""
    traded = position.diff().fillna(position).abs()
    traded.iloc[-1] += abs(position.iloc[-1])
    gross = position * (test["next_close"] / test["close"] - 1)
    net = gross - traded * cost / 2 / test["close"]
    return 100 * (1 + net).cumprod()

def trading(
    test: pd.DataFrame, position: pd.Series, cost: float
) -> dict[str, float]:
    """Accuracy, time in the market and final capital of a strategy."""
    held = position != 0
    return {
        "accuracy": (
            accuracy(test["label"][held], position[held] > 0)
            if held.any()
            else np.nan
        ),
        "time": held.mean(),
        "net": equity(position, test, cost).iloc[-1],
    }

table_5 = pd.DataFrame(
    {
        (pair, minutes, f"{lower}-{upper}"): trading(
            frame,
            positions(frame["probability"], lower, upper),
            spread(pair),
        )
        for (pair, minutes), frame in test.items()
        for lower, upper in BANDS
    }
).T.rename_axis(["pair", "minutes", "threshold"])

# %%
# The paper reports, in its Table 5a, the final capital, the accuracy of
# the positions taken and the share of the year spent in the market for
# both pairs, with a dash where no probability went past the band.

PAPER_TABLE_5A = """\
0.5-0.5   accuracy 0.55  0.55  0.52  0.56  0.60  0.51  0.50  0.52  0.57  0.53
0.5-0.5   time     1.00  1.00  1.00  1.00  1.00  1.00  1.00  1.00  1.00  1.00
0.5-0.5   net      98.2  98.1  91.9  99.9  107.8 81.6  88.1  94.4  105.9 104.0
0.45-0.55 accuracy 0.63  0.64  0.54  0.57  0.72  0.56  0.53  0.53  0.64  0.59
0.45-0.55 time     0.27  0.36  0.49  0.63  0.21  0.26  0.21  0.14  0.14  0.38
0.45-0.55 net      101.1 106.5 94.5  99.7  104.0 94.4  95.8  98.8  100.8 102.0
0.4-0.6   accuracy 0.71  0.69  0.56  0.60  0.77  0.60  0.63  0.54  0.90  0.68
0.4-0.6   time     0.11  0.21  0.23  0.41  0.07  0.10  0.07  0.03  0.01  0.11
0.4-0.6   net      105.0 105.1 97.1  100.7 101.6 100.9 100.9 99.9  101.2 102.4
0.35-0.65 accuracy 0.79  0.79  0.65  0.62  0.69  0.67  0.74  0.67  0.00  0.78
0.35-0.65 time     0.06  0.13  0.10  0.23  0.02  0.04  0.02  0.00  0.00  0.02
0.35-0.65 net      105.2 105.3 100.7 100.0 100.4 100.8 101.2 100.4 99.9  100.5
0.3-0.7   accuracy 0.84  0.83  0.71  0.66  -     0.69  0.82  -     -     -
0.3-0.7   time     0.03  0.07  0.04  0.13  -     0.02  0.01  -     -     -
0.3-0.7   net      102.9 103.1 100.5 101.2 -     100.3 100.5 -     -     -
0.25-0.75 accuracy 0.88  0.91  0.68  0.74  -     0.80  0.89  -     -     -
0.25-0.75 time     0.01  0.03  0.02  0.06  -     0.01  0.00  -     -     -
0.25-0.75 net      101.1 101.8 100.0 101.4 -     100.5 100.4 -     -     -
"""

paper_table_5 = pd.read_csv(
    io.StringIO(PAPER_TABLE_5A),
    sep=r"\s+",
    header=None,
    index_col=[0, 1],
    na_values="-",
)
paper_table_5.index.names = ["threshold", "metric"]
paper_table_5.columns = pd.MultiIndex.from_product(
    [["eurchf", "usdjpy"], PAPER_MINUTES], names=["pair", "minutes"]
)
paper_table_5 = (
    paper_table_5.stack(["pair", "minutes"])
    .unstack("metric")
    .reorder_levels(["pair", "minutes", "threshold"])
)

def compare(metric: str) -> pd.DataFrame:
    """Our values of a metric next to the paper's, by threshold."""
    ours = table_5[metric].unstack("threshold")[THRESHOLDS]
    paper = paper_table_5[metric].unstack("threshold")[THRESHOLDS]
    return pd.concat(
        {"ours": ours, "paper": paper.reindex(ours.index)}, axis=1
    ).swaplevel(axis=1)[THRESHOLDS]

# %%
# The end result: the capital at the end of 2021, by pair, bar length and
# threshold.

compare("net").round(1)

# %%
# The accuracy of the positions taken:

compare("accuracy").round(2)

# %%
# The share of the year spent in the market:

compare("time").round(2)

# %%
# For EUR/CHF the capital at the end of 2021 stays within about five points of
# the paper's at every threshold, and at 60 minutes it peaks, as there, around
# 0.35-0.65 at about 105. The paper's claim that the model is more accurate
# when it is more confident holds at 60 and 120 minutes, where the accuracy of
# the positions taken rises steadily as the threshold gets stricter, but not
# clearly at 720 minutes, where few positions are taken at the stricter
# thresholds. Our models spread their probabilities more widely than the
# paper's, so at the middle thresholds they spend more of the year in the
# market. The USD/JPY model only trades at 0.5-0.5, where it is short all year.

# %%
# As in the paper's Figure 4, costs decide whether trading on these
# predictions pays. Below, the capital through 2021 for EUR/CHF at 60 and
# 720 minutes, each at a threshold that trades well, without costs, with
# the spread of 2 pips used above and with twice that. Without costs both
# strategies end the year well ahead; the spread of 2 pips takes half or
# more of the gain, and twice that leaves the 60-minute strategy with a
# loss, as in the paper, where it ends at 110.7 without costs, 105.2 with
# 2 pips and 99.9 with 4.

FIGURE_4 = [(60, (0.35, 0.65)), (720, (0.5, 0.5))]

fig, axes = plt.subplots(1, 2, figsize=(10, 3.5), layout="constrained")
for ax, (minutes, (lower, upper)) in zip(axes, FIGURE_4, strict=True):
    frame = test["eurchf", minutes]
    position = positions(frame["probability"], lower, upper)
    for pips in [0, 2, 4]:
        ax.plot(
            equity(position, frame, pips * pip("eurchf")),
            label=f"{pips} pips",
        )
    ax.set_title(f"EURCHF, {minutes} minutes, {lower}-{upper}")
    ax.set_ylabel("capital")
    ax.xaxis.set_major_locator(mdates.MonthLocator(interval=3))
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m"))
axes[0].legend()
plt.show()

# %%
# Misleading accuracy
# -------------------
# The results below confirm the paper's main warning, from its Section 5:
# accuracy and backtests can mislead. For EUR/CHF at 60 minutes the model is no
# more accurate than a naive rule that predicts, for each hour of the day, the
# direction most frequent at that hour in the training years. Its correct
# predictions crowd into three hours, 21:00 to midnight, the hours the paper
# shows to have the widest spreads of the day, when New York's session has
# closed and only Sydney trades. Without those hours its accuracy falls close
# to that of a coin flip, and at the thresholds where it trades most its
# capital ends the year well below where it started. The model has mostly
# learned a pattern of the late evening that the backtest's fixed spreads
# make look profitable but that the real spreads of those hours would not let
# anyone trade.
#
# Moreover, in those hours the naive rule is even more accurate than the model.
# The pattern is a regular one: most bars starting at 21:00 close lower and
# most starting at 23:00 close higher, so predicting the same direction at each
# of those hours every day is right about 85% of the time. The naive rule is
# exactly that pattern, while the model learns it from the hour features but
# mixes in its other features, which sometimes overrule it. The model's edge is
# therefore not a skill of its own but a weaker copy of the naive rule's. The
# moves themselves are most likely not real trading: the data records one side
# of the quote, and its price falls as dealers widen their spreads in the late
# evening and recovers as they narrow them, a move no one could profit from
# after paying the spread.
#
# The figure shows accuracy by hour for EUR/CHF at 60 and 720 minutes, at the
# threshold 0.5-0.5. At 720 minutes the naive rule falls below 50%, well under
# the model, as in the paper.

HIGH_SPREAD_HOURS = [21, 22, 23]

def naive_predictions(windows: pd.DataFrame) -> pd.Series:
    """Most frequent direction at each window's hour in the training years."""
    hour = pd.DatetimeIndex(windows.index).hour
    train = (windows["set"] == "train").to_numpy()
    share = windows["label"][train].groupby(hour[train]).mean()
    return pd.Series(
        (share.reindex(hour) > 0.5).astype("int8").to_numpy(),
        index=windows.index,
    )

def accuracy_by_hour(
    test: pd.DataFrame, naive: pd.Series, position: pd.Series
) -> pd.DataFrame:
    """Accuracy of the model's positions and of the naive rule, by hour."""
    held = (position != 0).to_numpy()
    hour = pd.DatetimeIndex(test.index).hour
    model = (position[held] > 0) == (test["label"][held] == 1)
    rule = naive == test["label"]
    return pd.DataFrame(
        {
            "model": model.groupby(hour[held]).mean(),
            "naive": rule.groupby(hour).mean(),
        }
    ).reindex(sorted(set(hour)))

def plot_by_hour(ax: plt.Axes, table: pd.DataFrame, title: str) -> None:
    """Bars of the model's and the naive rule's accuracy by hour."""
    x = np.arange(len(table))
    ax.bar(x - 0.2, table["model"], width=0.4, label="model")
    ax.bar(x + 0.2, table["naive"], width=0.4, label="naive")
    ax.set_xticks(x, [f"{hour:02d}:00" for hour in table.index], rotation=90)
    ax.set_ylim(0, 1)
    ax.set_ylabel("accuracy")
    ax.set_title(title)

naive = {
    key: naive_predictions(frame).loc[test[key].index]
    for key, frame in windows.items()
}

fig, axes = plt.subplots(
    1, 2, figsize=(10, 4), width_ratios=[3, 1], layout="constrained"
)
for ax, minutes in zip(axes, [60, 720], strict=True):
    frame = test["eurchf", minutes]
    plot_by_hour(
        ax,
        accuracy_by_hour(
            frame,
            naive["eurchf", minutes],
            positions(frame["probability"], 0.5, 0.5),
        ),
        f"EURCHF, {minutes} minutes",
    )
axes[0].legend()
plt.show()

# %%
# Trading EUR/CHF at 60 and 120 minutes again without those three hours,
# holding no position in the bars that start in them, repeats the paper's
# Table 6, next to the results with all hours. As in the paper, the late
# evening is where the strategies' edge lies: without it, accuracy at
# 0.5-0.5 falls close to a coin flip, the capital falls at every
# threshold, and where the strategies trade most it ends the year below
# where it started. What looked like a profitable model is, for the most
# part, that one pattern of the late evening.

PAPER_TABLE_6 = """\
0.5-0.5   accuracy 0.55  0.55  0.52  0.50
0.5-0.5   time     1.00  1.00  0.87  0.83
0.5-0.5   net      98.2  98.1  85.5  85.1
0.45-0.55 accuracy 0.63  0.64  0.55  0.51
0.45-0.55 time     0.27  0.36  0.17  0.21
0.45-0.55 net      101.1 106.5 90.5  95.5
0.4-0.6   accuracy 0.71  0.69  0.55  0.45
0.4-0.6   time     0.11  0.21  0.04  0.08
0.4-0.6   net      105.0 105.1 97.0  96.6
0.35-0.65 accuracy 0.79  0.79  0.65  0.48
0.35-0.65 time     0.06  0.13  0.01  0.03
0.35-0.65 net      105.2 105.3 99.6  98.8
0.3-0.7   accuracy 0.84  0.83  0.67  0.39
0.3-0.7   time     0.03  0.07  0.00  0.01
0.3-0.7   net      102.9 103.1 99.9  99.7
0.25-0.75 accuracy 0.88  0.91  1.00  0.33
0.25-0.75 time     0.01  0.03  0.00  0.00
0.25-0.75 net      101.1 101.8 100.0 100.0
"""

paper_table_6 = pd.read_csv(
    io.StringIO(PAPER_TABLE_6), sep=r"\s+", header=None, index_col=[0, 1]
)
paper_table_6.index.names = ["threshold", "metric"]
paper_table_6.columns = pd.MultiIndex.from_product(
    [["all", "excluded"], [60, 120]], names=["hours", "minutes"]
)

table_6 = {}
for minutes in [60, 120]:
    frame = test["eurchf", minutes]
    allowed = ~pd.DatetimeIndex(frame.index).hour.isin(HIGH_SPREAD_HOURS)
    for lower, upper in BANDS:
        position = positions(frame["probability"], lower, upper)
        for hours, kept in [
            ("all", position),
            ("excluded", position.where(allowed, 0)),
        ]:
            table_6[hours, minutes, f"{lower}-{upper}"] = trading(
                frame, kept, spread("eurchf")
            )

table_6 = (
    pd.DataFrame(table_6)
    .rename_axis(index="metric", columns=["hours", "minutes", "threshold"])
    .stack("threshold")
    .reorder_levels(["threshold", "metric"])
    .reindex(paper_table_6.index)
)
pd.concat({"ours": table_6, "paper": paper_table_6}, axis=1).reorder_levels(
    [1, 2, 0], axis=1
).sort_index(axis=1).round(2)

# %%
# The paper's Figure 8 shows that the pattern differs from pair to pair.
# For USD/JPY at 60 minutes and the threshold 0.45-0.55, its model beats the
# naive rule, with its correct predictions spread over the day, so each pair
# has to be checked on its own. This part cannot be replicated here, because
# our USD/JPY model does not learn a lasting signal: its training loss falls,
# but its validation accuracy never improves on the early epochs in which it
# predicts "sell" for almost every window, so what it learns from 2010 to
# 2019 does not hold in 2020. Its probabilities for 2021 then stay in a
# narrow band below one half, it holds no position at 0.45-0.55, and the
# model's side of the comparison is empty. The paper's own model fared
# little better on this pair, with an accuracy and an area under the ROC
# curve of 0.51 in its Table 3. The naive rule, which does not depend on the
# model, still matches the paper's. The overall accuracy of each, ours and
# the paper's:

frame = test["usdjpy", 60]
position = positions(frame["probability"], 0.45, 0.55)
held = (position != 0).to_numpy()
pd.DataFrame(
    {
        "ours": [
            ((position[held] > 0) == (frame["label"][held] == 1)).mean(),
            (naive["usdjpy", 60] == frame["label"]).mean(),
        ],
        "paper": [0.56, 0.508],
    },
    index=["model", "naive"],
)

# %%
# Summary
# -------
# For EUR/CHF the replication reproduces the paper's results. With a lower
# learning rate than the paper's, its Transformer reaches the same accuracy,
# about 0.55, trading on it ends 2021 close to the paper's capital, and at 60
# and 120 minutes it is more accurate the more confident it is. Even with the
# paper's fixed spreads the profits are small: doubling the spread is enough to
# turn the 60-minute strategy's gain into a loss.
#
# It also reproduces the paper's warning. The success rests on a pattern of the
# late evening that a naive rule based only on the hour matches or beats, in
# hours whose real spreads, as the paper shows, would not let it be traded;
# without them, accuracy falls close to a coin flip and the profits disappear.
# For USD/JPY at 60 minutes the model learns no lasting signal, in line with
# the paper's own weak result there, so its counterexample cannot be checked.
