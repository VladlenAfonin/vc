import galois
import pytest

from vc.constants import TEST_FIELD
from vc.fold import fold_polynomial


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
    g_folded = fold_polynomial(g, randomness, folding_factor)

    assert g_folded == galois.Poly(expected, field=g.field, order='asc')
