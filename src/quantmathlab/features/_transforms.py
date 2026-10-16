"""Transformations of feature tables into model inputs."""

import numpy as np
import numpy.typing as npt
from numpy.lib.stride_tricks import sliding_window_view

from quantmathlab._typing import FloatArray

__all__ = ["cyclical_encoding", "sliding_windows"]


def cyclical_encoding(values: npt.ArrayLike, period: float) -> FloatArray:
    r"""Encode a cyclical quantity as points on the unit circle.

    Maps each value :math:`v` to

    .. math::

       \left(\sin \frac{2\pi v}{p},\ \cos \frac{2\pi v}{p}\right),

    so that values a whole period :math:`p` apart coincide and the end of
    one cycle lies next to the start of the next, as 23:00 lies next to
    midnight.

    Parameters
    ----------
    values : array_like
        Values of the quantity, such as hours of the day.
    period : float
        Length :math:`p` of a cycle, such as 24 for hours.

    Returns
    -------
    FloatArray
        Array with the shape of ``values`` plus a last axis of length 2,
        holding the sine and the cosine.

    Raises
    ------
    ValueError
        If ``period`` is not positive.
    """
    if not period > 0:
        raise ValueError("period must be positive")
    angle = 2.0 * np.pi * np.asarray(values, dtype=np.float64) / period
    return np.stack([np.sin(angle), np.cos(angle)], axis=-1)


def sliding_windows[T: np.generic](
    values: npt.NDArray[T], length: int
) -> npt.NDArray[T]:
    r"""Overlapping windows of consecutive rows of a table.

    Window :math:`i` holds rows :math:`i` to :math:`i + m - 1`, for a
    window length :math:`m`: at each time step, the stretch of history a
    sequence model reads. The windows are a read-only view of ``values``,
    so they take no memory of their own however many there are.

    Parameters
    ----------
    values : numpy.ndarray
        Table with one row per time step, of shape ``(n, k)`` or ``(n,)``.
    length : int
        Number of rows :math:`m` in each window, between 1 and ``n``.

    Returns
    -------
    numpy.ndarray
        Array of shape ``(n - length + 1, length, k)``, or
        ``(n - length + 1, length)`` for one-dimensional values, with the
        dtype of ``values``.

    Raises
    ------
    ValueError
        If ``length`` is not between 1 and the number of rows.
    """
    if not 1 <= length <= len(values):
        raise ValueError("length must be between 1 and the number of rows")
    return np.moveaxis(sliding_window_view(values, length, axis=0), -1, 1)
