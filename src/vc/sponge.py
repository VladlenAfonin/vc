from __future__ import annotations

import dataclasses
import hashlib
import logging
import pickle
import typing

import galois
import numpy

from vc.constants import LOGGER_MATH


logger = logging.getLogger(LOGGER_MATH)
BYTE_SIZE_BITS = 8


@dataclasses.dataclass(init=False, slots=True)
class Sponge:
    """Sponge."""

    _field: galois.FieldArray
    _objects: typing.List[object]
    _len: int

    def __init__(self, field: galois.FieldArray) -> None:
        """Initialize new Sponge.

        :param field: Field to use when sampling field elements.
        :type field: galois.FieldArray
        """

        self._objects = []
        self._field = field
        self._len = 0

    def _serialize(self) -> bytes:
        """Serialize current state into byte array."""

        return pickle.dumps(self._objects)

    def absorb(self, obj: typing.Any) -> None:
        """Push data to the proof stream.

        :param obj: Arbitrary data to push.
        :type obj: typing.Any
        """

        self._len += 1
        self._objects.append(obj)

    def squeeze(self, n: int = 32) -> bytes:
        """Sample random data. This function is to be called by the prover.

        :param n: Number of bytes to squeeze, defaults to 32.
        :type n: int, optional
        :return: Squeezed bytes.
        :rtype: bytes
        """

        return self._squeeze(n)

    def squeeze_field_element(self, n: int = 32) -> galois.FieldArray:
        """Sample random field element. This function is to be called by the prover."""

        return self._squeeze_field_element(n)

    def squeeze_index(self, upper_bound: int, n: int = 32) -> int:
        """Squeeze index.

        :param upper_bound: Upper bound.
        :type upper_bound: int
        :param n: Number of bytes to use when squeezing, defaults to 32.
        :type n: int, optional
        :return: Squeezed index.
        :rtype: int
        """

        return self._squeeze_number(upper_bound, n)

    def squeeze_indices(self, amount: int, upper_bound: int, n: int = 32) -> numpy.ndarray[int]:
        """Sample an array of distinct random numbers up to upper bound.

        :param amount: Number of indices to squeeze.
        :type amount: int
        :param upper_bound: Upper bound of indices.
        :type upper_bound: int
        :param n: Number of bytes to use when squeezing, defaults to 32.
        :type n: int, optional
        :return: Array of indices.
        :rtype: typing.List[int]
        """

        assert amount <= upper_bound, 'not enough integers to sample indices from'

        if amount == upper_bound:
            return list(range(upper_bound))
 
        result = []
        i = 0
        result_length = 0
        while result_length < amount:
            random_number = self._squeeze_number(upper_bound, n, postfix=bytes(i))
            if random_number not in result:
                result_length += 1
                result.append(random_number)

            i += 1

        return numpy.sort(numpy.array(result))

    def _squeeze_field_element(self, n: int) -> galois.Array:
        """Squeeze a field element.

        :param n: Number of bytes to use when squeezing.
        :type n: int
        :return: Field element.
        :rtype: galois.Array
        """

        random_number = self._squeeze_number(self._field.order, n)
        return self._field(random_number)

    def _squeeze_number(
            self,
            upper_bound: int,
            n: int,
            postfix: bytes = b'') -> int:
        """Squeeze a number.

        :param upper_bound: Upper bound.
        :type upper_bound: int
        :param n: Number of bytes to squeeze from the hash function.
        :type n: int
        :param postfix: Postfix to add when squeezing, defaults to b''.
        :type postfix: bytes, optional
        :return: Squeezed number.
        :rtype: int
        """

        random_bytes = self._squeeze(n, postfix=postfix)

        accumulator = 0
        for random_byte in random_bytes:
            accumulator = (accumulator << BYTE_SIZE_BITS) ^ int(random_byte)

        return accumulator % upper_bound

    def _squeeze(self, n: int, postfix: bytes = b'') -> bytes:
        """Squeeze bytes.
        This uses Fiat-Shamir sampling base on current verifier view.
        
        :param n: Number of bytes to squeeze.
        :type n: int
        :param postfix: Additional postfix to use when sampling.
        :type postfix: bytes
        :return: Squeezed bytes.
        :rtype: bytes
        """

        current_state = self._serialize()
        result = hashlib.shake_256(current_state + postfix).digest(n)

        return result
