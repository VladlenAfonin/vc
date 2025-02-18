import galois
import numpy as np

from vc.base import is_pow2


def construct(field: galois.FieldArray, n: int) -> galois.Array:
    assert is_pow2(n)

    omega = field.primitive_root_of_unity()
    return field([omega ** i for i in range(n)])


def fold(domain: galois.Array, folding_factor: int) -> galois.Array:
    assert is_pow2(domain.size), 'domain size must be a power of two'
    assert is_pow2(folding_factor), 'folding factor must be a power of two'

    new_domain = np.unique_values(domain ** folding_factor)
    assert domain.size // new_domain.size == folding_factor

    return new_domain
