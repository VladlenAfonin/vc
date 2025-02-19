import random

from vc.constants import TEST_FIELD
from vc.sponge import Sponge


NBYTES = 32


def test_same():
    sponge1 = Sponge(TEST_FIELD)
    sponge2 = Sponge(TEST_FIELD)

    random_bytes = random.randbytes(NBYTES)

    sponge1.absorb(random_bytes)
    sponge1.absorb(random_bytes)

    sponge2.absorb(random_bytes)
    sponge2.absorb(random_bytes)

    assert sponge1.squeeze_field_element() == sponge2.squeeze_field_element()
