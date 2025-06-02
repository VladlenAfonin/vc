"""Factorial AIR. n! = 1*2*...*n."""

import typing

import galois
import numpy

from vc.constants import FIELD_GOLDILOCKS
from vc.polynomial import MPoly
from vc.stark.boundary import BoundaryConstraint


def get_transition_constraints() -> typing.List[MPoly]:
    return [
        MPoly(
            {  # y1 - x1 - 1
                (0, 0, 1, 0): FIELD_GOLDILOCKS(0),
                (1, 0, 0, 0): FIELD_GOLDILOCKS(FIELD_GOLDILOCKS.order - 1),
                (0, 0, 0, 0): FIELD_GOLDILOCKS(FIELD_GOLDILOCKS.order - 1),
            },
            FIELD_GOLDILOCKS,
        ),
        MPoly(
            {  # y2 - y1*x2
                (0, 0, 0, 1): FIELD_GOLDILOCKS(0),
                (0, 1, 1, 0): FIELD_GOLDILOCKS(FIELD_GOLDILOCKS.order - 1),
            },
            FIELD_GOLDILOCKS,
        ),
    ]


def get_aet(n: int) -> galois.FieldArray:
    aet = numpy.empty((n + 1, 2), dtype=int)
    aet[0] = [0, 1]

    for i in range(1, n + 1):
        aet[i, 0] = aet[i - 1, 0] + 1
        aet[i, 1] = aet[i - 1, 1] * aet[i, 0]

    return FIELD_GOLDILOCKS(aet)


def get_boundary_constraints(n: int, result: int) -> typing.List[BoundaryConstraint]:
    return [
        BoundaryConstraint(i=0, j=0, value=FIELD_GOLDILOCKS(0)),
        BoundaryConstraint(i=0, j=1, value=FIELD_GOLDILOCKS(1)),
        BoundaryConstraint(i=1, j=0, value=FIELD_GOLDILOCKS(1)),
        BoundaryConstraint(i=1, j=1, value=FIELD_GOLDILOCKS(1)),
        BoundaryConstraint(i=n, j=0, value=FIELD_GOLDILOCKS(n)),
        BoundaryConstraint(i=n, j=1, value=FIELD_GOLDILOCKS(result)),
    ]
