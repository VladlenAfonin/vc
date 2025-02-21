import galois
import numpy as np
import pytest

from vc.constants import TEST_FIELD
from vc.fold import fold_polynomial
import vc.polynomial


@pytest.mark.parametrize(
    'expected, evaluations, folding_factor',
    [
        #                       [[1, 4],
        # [1, 2, 3, 4, 5, 6] ->  [2, 5],
        #                        [3, 6]]
        (TEST_FIELD([[1, 4], [2, 5], [3, 6]]), TEST_FIELD([1, 2, 3, 4, 5, 6]), 2)
    ])
def test_stack(expected, evaluations, folding_factor):
    result = vc.polynomial.stack(evaluations, folding_factor)
    assert np.all(result == expected)


@pytest.mark.parametrize(
    'expected, points',
    [
        (True, TEST_FIELD([[0, 0], [1, 1], [2, 2]])),
        (True, TEST_FIELD([[0, 0], [1, 2], [2, 4]])),
        (False, TEST_FIELD([[0, 0], [1, 1], [2, 3]]))
    ])
def test_is_colinear(expected: bool, points: galois.Array) -> None:
    result = vc.polynomial.is_colinear(points)
    assert result == expected
