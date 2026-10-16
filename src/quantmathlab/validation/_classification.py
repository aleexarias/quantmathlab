"""Accuracy metrics for classifiers."""

import numpy as np
import numpy.typing as npt
import pandas as pd

__all__ = ["accuracy", "roc_auc"]


def _one_dimensional(
    name: str, values: npt.ArrayLike
) -> npt.NDArray[np.generic]:
    array = np.asarray(values)
    if array.ndim != 1 or len(array) == 0:
        raise ValueError(f"{name} must be a non-empty one-dimensional array")
    return array


def accuracy(labels: npt.ArrayLike, predictions: npt.ArrayLike) -> float:
    r"""Share of predictions that match the labels.

    .. math::

       \frac{1}{n} \sum_{i=1}^{n} \mathbf{1}\{\hat{y}_i = y_i\}.

    Parameters
    ----------
    labels : array_like
        True classes :math:`y_i`.
    predictions : array_like
        Predicted classes :math:`\hat{y}_i`, one per label.

    Returns
    -------
    float
        Between 0 and 1.

    Raises
    ------
    ValueError
        If either is empty or not one-dimensional, or their lengths differ.
    """
    truth = _one_dimensional("labels", labels)
    predicted = _one_dimensional("predictions", predictions)
    if len(truth) != len(predicted):
        raise ValueError("predictions must have one value per label")
    return float(np.mean(truth == predicted))


def roc_auc(labels: npt.ArrayLike, scores: npt.ArrayLike) -> float:
    r"""Area under the ROC curve of a binary classifier.

    The probability that a positive example scores higher than a negative
    one, both drawn at random, with ties counting one half. As shown by
    :footcite:t:`hanley+mcneil_1982_meaning`, it equals the area under the
    receiver operating characteristic curve, and it follows from the ranks
    of the scores:

    .. math::

       \mathrm{AUC} = \frac{R_1 - n_1 (n_1 + 1) / 2}{n_1 n_0},

    where :math:`n_1` and :math:`n_0` are the numbers of positive and
    negative examples and :math:`R_1` is the sum of the ranks of the
    positive ones among all scores, tied scores sharing their average rank.
    A value of 0.5 means the scores do not separate the classes, 1 that
    every positive scores above every negative.

    Parameters
    ----------
    labels : array_like
        True classes, 1 for positive and 0 for negative.
    scores : array_like
        Scores, such as predicted probabilities of the positive class, one
        per label; only their order matters.

    Returns
    -------
    float
        Between 0 and 1.

    Raises
    ------
    ValueError
        If the labels are not all 0 or 1 or lack one of the classes, the
        scores are not finite, or their lengths differ.

    References
    ----------
    .. footbibliography::
    """
    classes = _one_dimensional("labels", labels)
    values = _one_dimensional("scores", scores).astype(np.float64)
    if not np.isin(classes, [0, 1]).all():
        raise ValueError("labels must be 0 or 1")
    if len(values) != len(classes):
        raise ValueError("scores must have one value per label")
    if not np.isfinite(values).all():
        raise ValueError("scores must be finite")
    positive = classes.astype(bool)
    n_1 = int(positive.sum())
    n_0 = len(positive) - n_1
    if n_1 == 0 or n_0 == 0:
        raise ValueError("labels must include both classes")
    ranks = pd.Series(values).rank().to_numpy()
    return float((ranks[positive].sum() - n_1 * (n_1 + 1) / 2) / (n_1 * n_0))
