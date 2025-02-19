from __future__ import annotations

import dataclasses
import hashlib
import logging
import pickle
import typing

import galois

from vc.constants import LOGGER_MATH


logger = logging.getLogger(LOGGER_MATH)
BYTE_SIZE_BITS = 8


@dataclasses.dataclass(init=False, slots=True)
class Sponge:
    _field: galois.FieldArray
    _objects: typing.List[object]
    _len: int

    def __init__(
            self,
            field: galois.FieldArray,
            objects: typing.List[typing.Any] = []) -> None:
        logger.debug(f'Sponge.init(): begin')

        # MAYBE: Investigate, why this line uses existing objects from the Sponge created earlier.
        # self._objects = objects

        self._objects = []
        logger.debug(f'Sponge.init(): {self._objects = }')

        self._field = field
        logger.debug(f'Sponge.init(): {self._field = }')

        self._len = 0
        logger.debug(f'Sponge.init(): {self._len = }')

        logger.debug(f'Sponge.init(): end')

    def serialize(self) -> bytes:
        return pickle.dumps(self._objects)

    def absorb(self, obj: typing.Any) -> None:
        """Push data to the proof stream."""

        logger.debug(f'Sponge.absorb(): begin')

        self._len += 1
        self._objects.append(obj)

        logger.debug(f'Sponge.absorb(): new {self._len = }')
        logger.debug(f'Sponge.absorb(): new {self._objects = }')

        logger.debug(f'Sponge.absorb(): end')

    def squeeze(self, n: int = 32) -> bytes:
        """Sample random data. This function is to be called by the prover."""
        return self._squeeze(n)

    def squeeze_field_element(self, n: int = 32) -> galois.FieldArray:
        """Sample random field element. This function is to be called by the prover."""
        return self._squeeze_field_element(n)

    def squeeze_index(self, upper_bound, n: int = 32) -> int:
        return self._squeeze_number(upper_bound, n)

    def squeeze_indices(self, amount: int, upper_bound, n: int = 32) -> typing.List[int]:
        """Sample an array of distinct random numbers up to upper bound."""

        logger.debug(f'Sponge.squeeze_indices(): begin')
        logger.debug(f'Sponge.squeeze_indices(): {amount = }')
        logger.debug(f'Sponge.squeeze_indices(): {upper_bound = }')
        logger.debug(f'Sponge.squeeze_indices(): {n = }')

        assert amount <= upper_bound, 'not enough integers to sample indices from'

        if amount == upper_bound:
            logger.debug(f'Sponge.squeeze_indices(): return all numbers up to upper bound')
            return list(range(upper_bound))
 
        logger.debug(f'Sponge.squeeze_indices(): sample random numbers')
        result = []
        i = 0
        result_length = 0
        while result_length < amount:
            logger.debug(f'Sponge.squeeze_indices(): begin intermediate iteration {i = }')
            random_number = self._squeeze_number(upper_bound, n, postfix=bytes(i))
            logger.debug(f'Sponge.squeeze_indices(): intermediate {random_number = }')
            if random_number not in result:
                logger.debug(f'Sponge.squeeze_indices(): intermediate appending {random_number = }')
                result_length += 1
                logger.debug(f'Sponge.squeeze_indices(): intermediate {result_length = }')
                result.append(random_number)
                logger.debug(f'Sponge.squeeze_indices(): intermediate {result = }')
            else:
                logger.debug(f'Sponge.squeeze_indices(): intermediate skipping {random_number = }')

            logger.debug(f'Sponge.squeeze_indices(): end intermediate iteration {i = }')
            i += 1

        logger.debug(f'Sponge.squeeze_indices(): final {result_length = }')
        logger.debug(f'Sponge.squeeze_indices(): final {result = }')
        logger.debug(f'Sponge.squeeze_indices(): end')

        return result

    def _squeeze_field_element(self, n: int):
        random_number = self._squeeze_number(self._field.order, n)
        return self._field(random_number)

    def _squeeze_number(
            self,
            upper_bound: int,
            n: int,
            postfix: bytes = b'') -> int:
        random_bytes = self._squeeze(n, postfix=postfix)

        accumulator = 0
        for random_byte in random_bytes:
            accumulator = (accumulator << BYTE_SIZE_BITS) ^ int(random_byte)

        return accumulator % upper_bound

    def _squeeze(self, n: int, postfix: bytes = b'') -> bytes:
        """Fiat-Shamir sampling base on current verifier view."""

        logger.debug(f'Sponge._squeeze(): begin')
        logger.debug(f'Sponge._squeeze(): {self._objects = }')

        current_verifier_view = self.serialize()
        result = hashlib.shake_256(current_verifier_view + postfix).digest(n)

        logger.debug(f'Sponge._squeeze(): end')

        return result
