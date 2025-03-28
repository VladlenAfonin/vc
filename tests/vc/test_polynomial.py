import typing
import galois
import pytest

from vc.constants import FIELD_193
from vc.polynomial import MPoly


TEST_FIELD = FIELD_193


@pytest.mark.parametrize(
    "coeffs, point, expected",
    [
        (
            {
                (1, 1): 2,
                (1, 2): 1,
            },  # 2xy + xy^2
            [1, 2],
            8,  # 2*1*2 + 1*2^2 = 4+4 = 8
        ),
        (
            {
                (2, 1): 2,
                (1, 2): 1,
            },  # 2x^2 y + xy^2
            [2, 2],
            24,  # 2*(2^2)*2 + 2*2^2 = 16+8 = 24
        ),
    ],
)
def test_evaluate_mpoly(
    coeffs: typing.Dict[typing.Tuple[int, ...], int],
    point: typing.List[int],
    expected: int,
) -> None:
    mpoly = MPoly(coeffs, TEST_FIELD)
    result = mpoly.eval(TEST_FIELD(point))
    expected_element = TEST_FIELD(expected)
    assert expected_element == result


@pytest.mark.parametrize(
    "coeffs, point, expected",
    [
        (
            {
                (1, 1): 2,
                (1, 2): 1,
            },  # 2xy + xy^2
            [
                galois.Poly([1, 0], field=TEST_FIELD),
                galois.Poly([1, 1, 0], field=TEST_FIELD),
            ],  # x, x^2 + x
            # 2*x*(x^2 + x) + x*(x^2 + x)^2 =
            # 2x^3 + 2x^2 + x*(x^4 + 2x^3 + x^2) =
            # 2x^3 + 2x^2 + x^5 + 2x^4 + x^3 =
            # x^5 + 2x^4 + 3x^3 + 2x^2 =
            # [1, 2, 3, 2, 0, 0], deg = 5, ncoeffs = 6
            galois.Poly([1, 2, 3, 2, 0, 0], field=TEST_FIELD),
        ),
    ],
)
def test_evaluate_symbolic_mpoly(
    coeffs: typing.Dict[typing.Tuple[int, ...], int],
    point: typing.List[galois.Poly],
    expected: galois.Poly,
) -> None:
    mpoly = MPoly(coeffs, TEST_FIELD)
    result = mpoly.evals(point)
    assert expected == result
