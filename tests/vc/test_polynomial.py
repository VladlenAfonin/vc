import galois
import numpy as np
import pytest

from vc.constants import TEST_FIELD
import vc.polynomial


@pytest.mark.parametrize(
    'expected, polynomial_coefficients, randomness, folding_factor',
    [
        # x + 1 = [1, 1] -> 1 + 1*1 = 2
        ([2], [1, 1], 1, 2),
        # x^3 + 2x^2 + 2x + 1 = [1, 2, 2, 1] -> [[1, 2], [2, 1]] -> [1 + 1*2, 2 + 1*1] = [3, 3]
        ([3, 3], [1, 2, 2, 1], 1, 2),
        # 1 + ... + 8x^7 = [1, 2, 3, 4, 5, 6, 7, 8] -> [[1, 2], [3, 4], [5, 6], [7, 8]] ->
        # [1 + 2*2, 3 + 2*4, 5 + 2*6, 7 + 2*8] = [5, 11, 17, 23]
        ([5, 11, 17, 23], [1, 2, 3, 4, 5, 6, 7, 8], 2, 2)
    ])
def test_fold(expected: galois.Array, polynomial_coefficients: galois.Array, randomness: int, folding_factor: int) -> None:
    g = galois.Poly(polynomial_coefficients, field=TEST_FIELD, order='asc')
    g_folded = vc.polynomial.fold(g, randomness, folding_factor)

    assert g_folded == galois.Poly(expected, field=g.field, order='asc')


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
