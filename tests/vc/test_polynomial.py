import galois
import pytest

from vc.constants import TEST_FIELD
import vc.polynomial


@pytest.mark.parametrize(
    'expected, polynomial_coefficients, randomness, folding_factor',
    [
        ([2], [1, 1], 1, 2),
        ([3, 3], [1, 2, 2, 1], 1, 2)
    ])
def test_fold(expected: galois.Array, polynomial_coefficients: galois.Array, randomness: int, folding_factor: int) -> None:
    g = galois.Poly(polynomial_coefficients, field=TEST_FIELD)
    g_folded = vc.polynomial.fold(g, randomness, folding_factor)

    assert g_folded == galois.Poly(expected, field=g.field)


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
