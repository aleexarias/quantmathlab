"""Train the paper's Transformer on the inputs saved by the notebook.

Training takes far longer than a documentation build, so it runs from this
script and the notebook only reads its results. It needs PyTorch, which is
not a dependency of quantmathlab. After the notebook has saved
the model inputs in ``data/inputs/``, run from the paper's folder or
anywhere else:

    python training/train.py
    python training/train.py --pairs eurchf --minutes 60 720

The series are those the notebook studies: EUR/CHF at 60, 120 and 720
minutes, and USD/JPY at 60. For each, a model is trained on the windows of
2010 to 2019, keeping the weights with the best accuracy on 2020, and
predicts the validation and test windows. The predictions are written to
``results/<pair>_<minutes>.csv``, and series that already have results are
skipped unless ``--overwrite`` is given. Model weights go to the git-ignored
``data/models/``, and the progress printed. A GPU is used when PyTorch finds
one.
"""

import argparse
from collections.abc import Iterator
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

import numpy as np
import numpy.typing as npt
import pandas as pd
import torch
import torch.nn as nn
import torch.nn.functional as F

from quantmathlab.features import sliding_windows
from quantmathlab.validation import accuracy

PAPER = Path(__file__).resolve().parents[1]
INPUTS = PAPER / "data" / "inputs"
MODELS = PAPER / "data" / "models"
LOG = PAPER / "data" / "training.log"
RESULTS = PAPER / "results"

SERIES = [("eurchf", 60), ("eurchf", 120), ("eurchf", 720), ("usdjpy", 60)]
WINDOW = 96
SEED = 0
DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")

BLOCKS = 4
HEADS = 4
KEY_SIZE = 64
DENSE_UNITS = 128
DROPOUT = 0.25
LEARNING_RATE = 0.0001
BATCH_SIZE = 64

EPOCHS = 100
PATIENCE = 30
WARMUP_EPOCHS = 1
MAX_GRADIENT_NORM = 1.0


@dataclass(frozen=True)
class Series:
    """The windows of one pair and bar length, with their labels.

    Window ``i`` holds the standardized features of 96 consecutive bars,
    and takes the label (1 if the next close is higher), set and time of
    the last of them.
    """

    windows: npt.NDArray[np.float32]
    label: npt.NDArray[np.int8]
    split: npt.NDArray[np.str_]
    time: npt.NDArray[np.datetime64]

    def rows(self, *sets: str) -> npt.NDArray[np.intp]:
        """Indices of the windows in the given sets, in time order."""
        return np.flatnonzero(np.isin(self.split, sets))


class Attention(nn.Module):
    """Multi-head self-attention whose key size is set apart from the width.

    Each head projects the inputs to queries, keys and values of size
    ``key_size``, and the heads' outputs are projected back to the width.
    """

    def __init__(
        self, width: int, heads: int, key_size: int, dropout: float
    ) -> None:
        super().__init__()
        self.heads = heads
        self.key_size = key_size
        self.dropout = dropout
        self.projection = nn.Linear(width, 3 * heads * key_size)
        self.output = nn.Linear(heads * key_size, width)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        batch, length, _ = x.shape
        query, key, value = (
            self.projection(x)
            .view(batch, length, 3, self.heads, self.key_size)
            .permute(2, 0, 3, 1, 4)
        )
        attended = F.scaled_dot_product_attention(
            query,
            key,
            value,
            dropout_p=self.dropout if self.training else 0.0,
        )
        output: torch.Tensor = self.output(
            attended.transpose(1, 2).reshape(batch, length, -1)
        )
        return output


class Block(nn.Module):
    """Attention and a feed-forward layer, each with residual and norm."""

    def __init__(self, width: int) -> None:
        super().__init__()
        self.attention = Attention(width, HEADS, KEY_SIZE, DROPOUT)
        self.attention_norm = nn.LayerNorm(width)
        self.dense = nn.Sequential(
            nn.Linear(width, DENSE_UNITS),
            nn.ReLU(),
            nn.Dropout(DROPOUT),
            nn.Linear(DENSE_UNITS, width),
        )
        self.dense_norm = nn.LayerNorm(width)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        x = self.attention_norm(x + self.attention(x))
        output: torch.Tensor = self.dense_norm(x + self.dense(x))
        return output


class Transformer(nn.Module):
    """The paper's classifier: logits of "sell" and "buy" for each window."""

    def __init__(self, width: int) -> None:
        super().__init__()
        self.position = nn.Parameter(torch.zeros(WINDOW, width))
        self.blocks = nn.Sequential(*(Block(width) for _ in range(BLOCKS)))
        self.linear = nn.Linear(width, 2)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        encoded = self.blocks(x + self.position)
        logits: torch.Tensor = self.linear(encoded.mean(dim=1))
        return logits


def log(message: str) -> None:
    """Print a progress message and append it to the log file."""
    print(message, flush=True)
    with LOG.open("a") as file:
        print(message, file=file)


def load_series(pair: str, minutes: int) -> Series:
    """The windows of a pair and bar length, from the saved inputs."""
    inputs = np.load(INPUTS / f"{pair}_{minutes}.npz")
    last = slice(WINDOW - 1, None)
    return Series(
        windows=sliding_windows(inputs["features"], WINDOW),
        label=inputs["label"][last],
        split=inputs["split"][last],
        time=inputs["time"][last],
    )


def batches(
    series: Series,
    rows: npt.NDArray[np.intp],
    rng: np.random.Generator | None,
) -> Iterator[tuple[torch.Tensor, torch.Tensor]]:
    """Mini-batches of windows and their labels, on the training device.

    Shuffled when a random generator is given, in time order otherwise.
    Each batch is copied out of the windows, which are a read-only view.
    """
    order = rng.permutation(rows) if rng is not None else rows
    for start in range(0, len(order), BATCH_SIZE):
        chosen = order[start : start + BATCH_SIZE]
        windows = np.ascontiguousarray(series.windows[chosen])
        yield (
            torch.from_numpy(windows).to(DEVICE),
            torch.from_numpy(series.label[chosen]).long().to(DEVICE),
        )


@torch.no_grad()
def predict(
    model: Transformer, series: Series, rows: npt.NDArray[np.intp]
) -> npt.NDArray[np.float64]:
    """Probability of "buy" the model gives each of the windows."""
    model.eval()
    probabilities = [
        F.softmax(model(windows), dim=1)[:, 1].cpu().numpy()
        for windows, _ in batches(series, rows, None)
    ]
    return np.concatenate(probabilities).astype(np.float64)


def train_and_predict(
    series: Series, weights: Path, rng: np.random.Generator
) -> npt.NDArray[np.float64]:
    """Train a model and predict the validation and test windows.

    Trains on shuffled batches of the training windows, saving to
    ``weights`` the model with the best accuracy on the validation
    windows, and returns that model's probability of "buy" for each window
    in ``series.rows("validation", "test")``.
    """
    torch.manual_seed(SEED)
    model = Transformer(series.windows.shape[2]).to(DEVICE)
    train = series.rows("train")
    validation = series.rows("validation")
    optimizer = torch.optim.Adam(model.parameters(), lr=LEARNING_RATE)
    warmup = WARMUP_EPOCHS * -(-len(train) // BATCH_SIZE)
    scheduler = torch.optim.lr_scheduler.LambdaLR(
        optimizer, lambda step: min(1.0, (step + 1) / warmup)
    )
    best, stale = -1.0, 0
    for epoch in range(1, EPOCHS + 1):
        model.train()
        losses = []
        for windows, labels in batches(series, train, rng):
            loss = F.cross_entropy(model(windows), labels)
            optimizer.zero_grad()
            torch.autograd.backward(loss)
            nn.utils.clip_grad_norm_(model.parameters(), MAX_GRADIENT_NORM)
            optimizer.step()
            scheduler.step()
            losses.append(loss.item())
        score = accuracy(
            series.label[validation], predict(model, series, validation) > 0.5
        )
        log(
            f"  epoch {epoch:3d}: loss {np.mean(losses):.4f}, "
            f"validation accuracy {score:.4f}"
        )
        if score > best:
            best, stale = score, 0
            torch.save(model.state_dict(), weights)
        else:
            stale += 1
            if stale == PATIENCE:
                break
    model.load_state_dict(torch.load(weights, map_location=DEVICE))
    return predict(model, series, series.rows("validation", "test"))


def save_predictions(
    pair: str,
    minutes: int,
    series: Series,
    rows: npt.NDArray[np.intp],
    probability: npt.NDArray[np.float64],
) -> None:
    """Write the predicted probability of "buy" of each window."""
    if len(probability) != len(rows):
        raise ValueError("expected one probability per window")
    RESULTS.mkdir(exist_ok=True)
    pd.DataFrame(
        {
            "time": series.time[rows],
            "set": series.split[rows],
            "probability": probability,
        }
    ).to_csv(
        RESULTS / f"{pair}_{minutes}.csv", index=False, float_format="%.6f"
    )


def main() -> None:
    """Train and predict every requested series."""
    pairs = sorted({pair for pair, _ in SERIES})
    lengths = sorted({minutes for _, minutes in SERIES})
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("--pairs", nargs="+", choices=pairs, default=pairs)
    parser.add_argument(
        "--minutes", nargs="+", type=int, choices=lengths, default=lengths
    )
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="retrain series that already have results",
    )
    arguments = parser.parse_args()
    MODELS.mkdir(parents=True, exist_ok=True)
    log(
        f"{datetime.now():%Y-%m-%d %H:%M}: training on {DEVICE}, "
        f"learning rate {LEARNING_RATE}, patience {PATIENCE}"
    )
    for pair, minutes in SERIES:
        if pair not in arguments.pairs or minutes not in arguments.minutes:
            continue
        if (RESULTS / f"{pair}_{minutes}.csv").exists() and not (
            arguments.overwrite
        ):
            log(f"{pair} {minutes} min: has results, skipped")
            continue
        log(f"{datetime.now():%H:%M} {pair} {minutes} min: training")
        series = load_series(pair, minutes)
        rows = series.rows("validation", "test")
        probability = train_and_predict(
            series,
            MODELS / f"{pair}_{minutes}.pt",
            np.random.default_rng(SEED),
        )
        save_predictions(pair, minutes, series, rows, probability)
        log(f"{datetime.now():%H:%M} {pair} {minutes} min: results saved")


if __name__ == "__main__":
    main()
