"""Arithmetic proof checks for the project's integer minimization objectives."""

import math


def integer_bound_proves_value(value: int, best_bound: float,
                              integer_lower_bound: int | None = None) -> bool:
    """Use native integer proof evidence while preserving the raw double bound.

    A double may lie one representable step above or below the integer optimum.
    With native integer evidence, exact integer equality establishes the proof;
    a tiny double discrepancy is only a consistency check, never its basis.
    Legacy records without it require v-1 < lower_bound <= v, excluding every
    better integer. Callers also check status, input binding and the independently
    measured incumbent. No objective, stored bound or solver gap is rounded.
    """
    if not (type(value) is int and abs(value) <= 2**53
            and type(best_bound) in (int, float)
            and -2**53 <= best_bound <= 2**53 and math.isfinite(best_bound)):
        return False
    if integer_lower_bound is not None:
        return (type(integer_lower_bound) is int and integer_lower_bound == value
                and abs(best_bound - value) <= min(1e-9, 4 * math.ulp(float(value))))
    return value - 1 < best_bound <= value
