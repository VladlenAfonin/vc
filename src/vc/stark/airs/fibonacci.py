"""Fibonacci sequence AIR.
Fibonacci sequence = {0, 1, 1, ...}, indexation is from 0.
"""

import typing
import numpy
import numpy.typing

from vc.constants import FIELD_GOLDILOCKS
from vc.polynomial import MPoly


# TODO: Refactor into some state or options.
field = FIELD_GOLDILOCKS


def get_transition_constraints() -> typing.List[MPoly]:
    return [
        MPoly(
            {  # y1 - x2
                (0, 0, 1, 0): FIELD_GOLDILOCKS(1),
                (0, 1, 0, 0): FIELD_GOLDILOCKS(FIELD_GOLDILOCKS.order - 1),
            },
            FIELD_GOLDILOCKS,
        ),
        MPoly(
            {  # y2 - x1 - x2
                (0, 0, 0, 1): FIELD_GOLDILOCKS(1),
                (1, 0, 0, 0): FIELD_GOLDILOCKS(FIELD_GOLDILOCKS.order - 1),
                (0, 1, 0, 0): FIELD_GOLDILOCKS(FIELD_GOLDILOCKS.order - 1),
            },
            FIELD_GOLDILOCKS,
        ),
    ]


def get_aet(
    n: int,
) -> numpy.ndarray:
    """Get AIR for Fibonacci numbers.

    :param n: Index of the Fibonacci number to build AIR for.
    :type n: int
    :return: AIR for n-th Fibonacci number.
    :rtype: numpy.typing.ArrayLike
    """

    assert n > 0, "unable to create AIR for n < 1"

    aet = numpy.empty((n, 2), dtype=int)
    aet[0] = [0, 1]

    for i in range(1, n):
        aet[i, 0] = aet[i - 1, 1]
        aet[i, 1] = aet[i - 1, 0] + aet[i - 1, 1]

    return field(aet)


def get_bound_constraints(
    n: int,
    result: int,
) -> numpy.ndarray:
    """Get bound constraints."""

    assert n > 0, "unable to create bound constrainst for n < 1"

    bc = field(
        [
            [0, 0, 0],
            [n - 1, 1, result],
        ]
    )

    return bc


def fib(
    n: int,
) -> int:
    assert n > -1, "invalid Fibonacci number index"

    memo = {}
    result: int = 0

    for i in range(n + 1):
        if i < 2:
            result = i
        else:
            result = memo[i - 1] + memo[i - 2]

        memo[i] = result

    return result
