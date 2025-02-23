import random

from vc.constants import FIELD_193
from vc.sponge import Sponge


NBYTES = 32


def test_same():
    sponge1 = Sponge(FIELD_193)
    sponge2 = Sponge(FIELD_193)

    random_bytes = random.randbytes(NBYTES)

    sponge1.absorb(random_bytes)
    sponge1.absorb(random_bytes)

    sponge2.absorb(random_bytes)
    sponge2.absorb(random_bytes)

    assert sponge1.squeeze_field_element() == sponge2.squeeze_field_element()
