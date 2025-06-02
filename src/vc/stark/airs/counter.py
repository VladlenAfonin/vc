"""Counter counting from 0 to N-1: {0, 1, 2, ...}."""

import typing

import galois
import numpy

from vc.constants import FIELD_GOLDILOCKS
from vc.polynomial import MPoly
from vc.stark.boundary import BoundaryConstraint


def get_transition_constraints() -> typing.List[MPoly]:
    return [
        MPoly(
            {  # y - x - 1
                (0, 1): FIELD_GOLDILOCKS(1),
                (1, 0): FIELD_GOLDILOCKS(FIELD_GOLDILOCKS.order - 1),
                (0, 0): FIELD_GOLDILOCKS(FIELD_GOLDILOCKS.order - 1),
            },
            FIELD_GOLDILOCKS,
        )
    ]


def get_aet(n: int) -> galois.FieldArray:
    assert n > 0, "unable to create Counter AIR for n < 1"

    aet = numpy.empty((n, 1), dtype=int)
    aet[0] = [0]

    for i in range(1, n):
        aet[i, 0] = 1 + aet[i - 1, 0]

    return FIELD_GOLDILOCKS(aet)


def get_boundary_constraints(n: int) -> typing.List[BoundaryConstraint]:
    assert n > 0, "unable to create Counter AIR for n < 1"

    return [
        BoundaryConstraint(i=0, j=0, value=FIELD_GOLDILOCKS(0)),
        BoundaryConstraint(i=n - 1, j=0, value=FIELD_GOLDILOCKS(n - 1)),
    ]
