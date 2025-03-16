import pytest
import numpy
import numpy.typing

from vc.stark.airs.fibonacci import fib, get_air, field, get_bound_constraints


@pytest.mark.parametrize(
    "n, expected",
    [
        (
            1,
            field(
                [
                    [0, 1],
                ]
            ),
        ),
        (
            2,
            field(
                [
                    [0, 1],
                    [1, 1],
                ]
            ),
        ),
        (
            3,
            field(
                [
                    [0, 1],
                    [1, 1],
                    [1, 2],
                ]
            ),
        ),
        (
            4,
            field(
                [
                    [0, 1],
                    [1, 1],
                    [1, 2],
                    [2, 3],
                ]
            ),
        ),
    ],
)
def test_get_air(
    n: int,
    expected: numpy.typing.ArrayLike,
) -> None:
    result = get_air(n)
    assert numpy.all(result == expected)


@pytest.mark.parametrize(
    "n, expected",
    [
        (0, 0),
        (1, 1),
        (2, 1),
        (3, 2),
        (4, 3),
        (5, 5),
        (40, 102334155),
    ],
)
def test_fib(
    n: int,
    expected: int,
) -> None:
    result = fib(n)
    assert result == expected


@pytest.mark.parametrize(
    "n, fn, expected",
    [
        (
            1,
            fib(1),
            field(
                [
                    [0, 0, 0],
                    [0, 1, 1],
                ],
            ),
        ),
        (
            40,
            fib(40),
            field(
                [
                    [0, 0, 0],
                    [39, 1, fib(40)],
                ],
            ),
        ),
    ],
)
def test_bound_constraints(
    n: int,
    fn: int,
    expected: numpy.typing.ArrayLike,
) -> None:
    result = get_bound_constraints(n, fn)
    assert numpy.all(result == expected)
