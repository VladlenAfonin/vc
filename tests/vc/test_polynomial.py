import typing
import galois
import pytest

from vc.constants import FIELD_193
from vc.polynomial import (
    MPoly,
    expand_to_nearest_power_of_two,
    expand_to_nearest_power_of_two2,
    scale,
)


TEST_FIELD = FIELD_193


@pytest.mark.parametrize(
    "g, a, expected",
    [
        (
            galois.Poly([1, 2, 3], order="asc", field=TEST_FIELD),
            1,
            galois.Poly([1, 2, 3], order="asc", field=TEST_FIELD),
        ),
        (
            galois.Poly([1, 2, 3], order="asc", field=TEST_FIELD),
            2,
            galois.Poly([1, 2 * 2, 3 * (2**2)], order="asc", field=TEST_FIELD),
        ),
        (
            galois.Poly([1, 2, 3], order="asc", field=TEST_FIELD),
            3,
            galois.Poly([1, 2 * 3, 3 * (3**2)], order="asc", field=TEST_FIELD),
        ),
    ],
)
def test_scale(g: galois.Poly, a: int, expected: galois.Poly) -> None:
    result = scale(g, a)
    assert expected == result


@pytest.mark.parametrize(
    "g, a, b, expected",
    [
        (
            galois.Poly([1], field=TEST_FIELD, order="asc"),  # 1
            0,
            1,
            galois.Poly([1], field=TEST_FIELD, order="asc"),  # 1
        ),
        (
            galois.Poly([0, 0, 1], field=TEST_FIELD, order="asc"),  # x^2
            0,
            1,
            galois.Poly([0, 0, 0, 1], field=TEST_FIELD, order="asc"),  # x^3
        ),
        (
            galois.Poly([0, 0, 1], field=TEST_FIELD, order="asc"),  # x^2
            2,
            1,
            galois.Poly([0, 0, 2, 1], field=TEST_FIELD, order="asc"),  # x^3 + 2x^2
        ),
        (
            galois.Poly([0, 0, 0, 0, 1], field=TEST_FIELD, order="asc"),  # x^4
            3,
            2,
            galois.Poly(
                [0, 0, 0, 0, 3, 0, 0, 2],
                field=TEST_FIELD,
                order="asc",
            ),  # 2x^7 + 3x^4
        ),
    ],
)
def test_expand_to_nearest_power_of_two(
    g: galois.Poly,
    a: int | None,
    b: int | None,
    expected: galois.Poly,
) -> None:
    result = expand_to_nearest_power_of_two(g, a, b)
    assert expected == result


@pytest.mark.parametrize(
    "g, r, expected",
    [
        (
            galois.Poly([1], field=TEST_FIELD, order="asc"),  # 1
            1,
            galois.Poly([1], field=TEST_FIELD, order="asc"),  # 1
        ),
        (
            galois.Poly([0, 0, 1], field=TEST_FIELD, order="asc"),  # x^2
            1,  # yields 1 + x
            galois.Poly(
                [0, 0, 1, 1],
                field=TEST_FIELD,
                order="asc",
            ),  # x^2 * (1 + x) = x^3 + x^2
        ),
        (
            galois.Poly([0, 0, 1], field=TEST_FIELD, order="asc"),  # x^2
            2,  # yields 1 + 2x
            galois.Poly(
                [0, 0, 1, 2],
                field=TEST_FIELD,
                order="asc",
            ),  # x^2 * (1 + 2x) = 2x^3 + x^2
        ),
        # (
        #     galois.Poly([0, 0, 1], field=TEST_FIELD, order="asc"),  # x^2
        #     1,
        #     galois.Poly([0, 0, 2, 1], field=TEST_FIELD, order="asc"),  # x^3 + 2x^2
        # ),
        # (
        #     galois.Poly([0, 0, 0, 0, 1], field=TEST_FIELD, order="asc"),  # x^4
        #     1,
        #     galois.Poly(
        #         [0, 0, 0, 0, 3, 0, 0, 2],
        #         field=TEST_FIELD,
        #         order="asc",
        #     ),  # 2x^7 + 3x^4
        # ),
    ],
)
def test_expand_to_nearest_power_of_two2(
    g: galois.Poly,
    r: int,
    expected: galois.Poly,
) -> None:
    result = expand_to_nearest_power_of_two2(g, r)
    assert expected == result


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


# def test_evalv_mpoly()
#     mpoly =
