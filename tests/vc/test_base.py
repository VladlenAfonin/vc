import pytest

from vc.base import get_nearest_power_of_two


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
