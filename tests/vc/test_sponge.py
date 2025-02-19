import random

import galois
import pytest

from vc.sponge import Sponge


FIELD = galois.GF(193)
NBYTES = 32


def test_same():
    sponge1 = Sponge(FIELD)
    sponge2 = Sponge(FIELD)

    random_bytes = random.randbytes(NBYTES)

    sponge1.absorb(random_bytes)
    sponge1.absorb(random_bytes)

    sponge2.absorb(random_bytes)
    sponge2.absorb(random_bytes)

    assert sponge1.squeeze_field_element() == sponge2.squeeze_field_element()
