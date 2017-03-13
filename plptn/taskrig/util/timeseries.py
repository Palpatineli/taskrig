import numpy as np
from numpy import abs, logical_and, logical_xor
try:
    from numba import jit
except ImportError as s:
    jit = None

BIG_THRESH = 2e6
ABS_THRESH = 2e8


def conditional_jit(function):
    if jit:
        return jit(function, nopython=True, cache=True, nogil=True)
    else:
        return function


@conditional_jit
def despike(data: np.ndarray) -> np.ndarray:
    for idx in np.nonzero(np.greater(abs(data), ABS_THRESH))[0]:
        if abs(data[idx - 1]) < ABS_THRESH:
            data[idx] = data[idx - 1]
        elif abs(data[idx + 1]) < ABS_THRESH:
            data[idx] = data[idx + 1]
    diff = np.diff(data)
    sign = diff > 0
    is_big = abs(diff) > BIG_THRESH
    flux = logical_and(logical_xor(sign[0:-1], sign[1:]),
                       logical_and(is_big[0:-1], is_big[1:]))
    for idx in np.nonzero(flux)[0]:
        data[idx + 1] = (data[idx] + data[idx + 2]) // 2
    return data
