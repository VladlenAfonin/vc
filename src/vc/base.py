def is_pow2(n: int) -> bool:
    return n & (n - 1) == 0


def get_nearest_power_of_two(n: int) -> int:
    if is_pow2(n):
        return n

    return 2 ** n.bit_length()
