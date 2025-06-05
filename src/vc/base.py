import typing


def is_pow2(n: int) -> bool:
    return n & (n - 1) == 0


def get_nearest_power_of_two(n: int) -> int:
    if is_pow2(n):
        return n

    return 2 ** n.bit_length()


def get_nearest_power_of_two_ext(n: int) -> typing.Tuple[int, int]:
    power = n.bit_length()

    if is_pow2(n):
        return (n, power)

    return 2**power, power
