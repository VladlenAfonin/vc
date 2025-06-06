import typing
import pytest

from vc.base import get_nearest_power_of_two, get_nearest_power_of_two_ext


@pytest.mark.parametrize(
    "n, expected",
    [
        (1, 1),
        (2, 2),
        (3, 4),
        (4, 4),
        (5, 8),
    ],
)
def test_get_nearest_power_of_two(n: int, expected: int):
    result = get_nearest_power_of_two(n)
    assert expected == result


@pytest.mark.parametrize(
    "n, expected",
    [
        (1, (1, 0)),
        (2, (2, 1)),
        (3, (4, 2)),
        (4, (4, 2)),
        (5, (8, 3)),
    ],
)
def test_get_nearest_power_of_two_ext(n: int, expected: typing.Tuple[int, int]):
    result = get_nearest_power_of_two_ext(n)
    assert expected == result
