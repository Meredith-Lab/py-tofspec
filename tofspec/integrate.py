#!/usr/bin/env python
# -*- coding: utf-8 -*-

import numpy as np


def find_indices(x, xlower, xupper):
    """
    Given an array and a value range, return the indices that most nearly match up with that value range.

    :param x: array of one-dimensional numeric data
    :type x: array-like
    :param xlower: lower bound
    :type xlower: int/float
    :param xupper: upper bound
    :type xupper: int/float
    :return indices: indices that match up with input value range
    :rtype: tuple
    """
    limits = np.array([xlower, xupper])
    indices = np.searchsorted(x, limits)

    try:
        candidates = x[np.stack((indices - 1, indices), axis=0)]
    except:
        return [0,0]
    indices += np.abs(candidates - limits).argmin(axis=0) - 1

    return indices

def integrate_peak(y, x, indices):
    """
    Integrate along the given axis in a certain x-range using the composite trapezoidal rule.

    :param y: Input array to integrate.
    :type y: array_like
    :param x: array of x-values corresponding to y
    :type x: array-like
    :param indices: indices that match up with input value range
    :type indices: tuple
    :return trapz: Definite integral of y = n-dimensional array as approximated along a
                 single axis by the trapezoidal rule.
    :rtype: float
    """

    s = slice(indices[0], indices[1] + 1)

    return np.trapz(y[:, s], x[s])