"""Tests for quantmathlab.validation: accuracy metrics for classifiers."""

import numpy as np
import pytest
from hypothesis import given
from hypothesis import strategies as st

from quantmathlab.validation import accuracy, roc_auc


def _pairwise_auc(labels: list[int], scores: list[int]) -> float:
    positives = [s for s, y in zip(scores, labels, strict=True) if y == 1]
    negatives = [s for s, y in zip(scores, labels, strict=True) if y == 0]
    wins = sum((p > n) + 0.5 * (p == n) for p in positives for n in negatives)
    return wins / (len(positives) * len(negatives))


def test_accuracy_counts_matching_predictions() -> None:
    """Accuracy is the share of predictions equal to their label."""
    assert accuracy([1, 0, 1, 1], [1, 1, 1, 0]) == 0.5
    assert accuracy(np.array([True, False]), [1, 0]) == 1.0
    with pytest.raises(ValueError, match="one value per label"):
        accuracy([1, 0, 1], [1, 0])
    with pytest.raises(ValueError, match="non-empty"):
        accuracy([], [])


def test_roc_auc_matches_hand_computed_values() -> None:
    """AUROC counts the pairs a positive wins, ties counting one half."""
    assert roc_auc([0, 0, 1, 1], [0.1, 0.4, 0.35, 0.8]) == 0.75
    assert roc_auc([0, 1, 0, 1], [0.2, 0.9, 0.3, 0.6]) == 1.0
    assert roc_auc([0, 1, 0, 1], [0.5, 0.5, 0.5, 0.5]) == 0.5


@pytest.mark.parametrize(
    ("labels", "scores", "message"),
    [
        ([0, 1, 2], [0.1, 0.2, 0.3], "0 or 1"),
        ([1, 1], [0.1, 0.2], "both classes"),
        ([0, 1], [0.1, np.nan], "finite"),
        ([0, 1], [0.1, 0.2, 0.3], "one value per label"),
    ],
)
def test_roc_auc_rejects_invalid_input(
    labels: list[int], scores: list[float], message: str
) -> None:
    """Non-binary labels, one class, missing scores or a mismatch raise."""
    with pytest.raises(ValueError, match=message):
        roc_auc(labels, scores)


@given(
    data=st.lists(
        st.tuples(st.integers(0, 1), st.integers(0, 5)), min_size=2
    ).filter(lambda pairs: len({label for label, _ in pairs}) == 2)
)
def test_roc_auc_counts_winning_pairs(data: list[tuple[int, int]]) -> None:
    """AUROC equals the share of winning pairs, and reverses with scores.

    Scores from a few integers make ties frequent. Both sides divide the
    same count of pairs won, a multiple of one half, so they agree exactly.
    """
    labels = [label for label, _ in data]
    scores = [score for _, score in data]
    auc = roc_auc(labels, scores)
    assert auc == _pairwise_auc(labels, scores)
    assert roc_auc(labels, [-score for score in scores]) == pytest.approx(
        1 - auc, abs=1e-12
    )
