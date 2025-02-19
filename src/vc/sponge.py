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
    _read_index: int
    _len: int

    def __init__(
            self,
            field: galois.FieldArray,
            objects: typing.List[typing.Any] = []) -> None:
        logger.debug(f'Sponge.init(): begin')

        self._objects = objects
        logger.debug(f'Sponge.init(): {self._objects = }')

        self._field = field
        logger.debug(f'Sponge.init(): {self._field = }')

        self._read_index = 0
        logger.debug(f'Sponge.init(): {self._read_index = }')

        self._len = 0
        logger.debug(f'Sponge.init(): {self._len = }')

        logger.debug(f'Sponge.init(): end')

    def serialize(self, until_read_index: bool = False) -> bytes:
        data_to_serialize = self._objects[:self._read_index] \
            if until_read_index else self._objects
        return pickle.dumps(data_to_serialize)

    @staticmethod
    def from_data(field: galois.FieldArray, data: bytes) -> Sponge:
        objects = pickle.loads(data)
        return Sponge(field, objects=objects)

    def push(self, obj: typing.Any) -> None:
        """Push data to the proof stream."""

        self._len += 1
        self._objects.append(obj)

    def pull[T](self) -> T:
        """Get next element from the proof stream."""

        assert self._read_index < self._len, 'no more data to read'

        result = self._objects[self._read_index]
        self._read_index += 1
        return result

    def sample_prover(self, n: int = 32) -> bytes:
        """Sample random data. This function is to be called by the prover."""
        return self._sample(False, n)

    def sample_verifier(self, n: int = 32) -> bytes:
        """Sample random data. This function is to be called by the verifier."""
        return self._sample(True, n)

    def sample_field_prover(self, n: int = 32) -> galois.FieldArray:
        """Sample random field element. This function is to be called by the prover."""
        return self._sample_field(False, n)

    def sample_field_verifier(self, n: int = 32) -> galois.FieldArray:
        """Sample random field element. This function is to be called by the prover."""
        return self._sample_field(True, n)

    def sample_index_prover(self, upper_bound, n: int = 32) -> int:
        return self._sample_number(upper_bound, False, n)

    def sample_index_verifier(self, upper_bound, n: int = 32) -> int:
        return self._sample_number(upper_bound, True, n)

    def sample_indices_prover(self, amount: int, upper_bound, n: int = 32) -> typing.List[int]:
        """Sample an array of distinct random numbers up to upper bound."""

        logger.debug(f'Sponge.sample_indices_prover(): begin')
        logger.debug(f'Sponge.sample_indices_prover(): {amount = }')
        logger.debug(f'Sponge.sample_indices_prover(): {upper_bound = }')
        logger.debug(f'Sponge.sample_indices_prover(): {n = }')

        assert amount <= upper_bound, 'not enough integers to sample indices from'

        if amount == upper_bound:
            logger.debug(f'Sponge.sample_indices_prover(): return all numbers up to upper bound')
            return list(range(upper_bound))
 
        logger.debug(f'Sponge.sample_indices_prover(): sample random numbers')
        result = []
        i = 0
        result_length = 0
        while result_length < amount:
            logger.debug(f'Sponge.sample_indices_prover(): begin intermediate iteration {i = }')
            random_number = self._sample_number(upper_bound, False, n, postfix=bytes(i))
            logger.debug(f'Sponge.sample_indices_prover(): intermediate {random_number = }')
            if random_number not in result:
                logger.debug(f'Sponge.sample_indices_prover(): intermediate appending {random_number = }')
                result_length += 1
                logger.debug(f'Sponge.sample_indices_prover(): intermediate {result_length = }')
                result.append(random_number)
                logger.debug(f'Sponge.sample_indices_prover(): intermediate {result = }')
            else:
                logger.debug(f'Sponge.sample_indices_prover(): intermediate skipping {random_number = }')

            logger.debug(f'Sponge.sample_indices_prover(): end intermediate iteration {i = }')
            i += 1

        logger.debug(f'Sponge.sample_indices_prover(): final {result_length = }')
        logger.debug(f'Sponge.sample_indices_prover(): final {result = }')
        logger.debug(f'Sponge.sample_indices_prover(): end')

        return result

    def _sample_field(self, until_read_index: bool, n: int):
        random_number = self._sample_number(self._field.order, until_read_index, n)
        return self._field(random_number)

    def _sample_number(
            self,
            upper_bound: int,
            until_read_index: bool,
            n: int,
            postfix: bytes = b'') -> int:
        random_bytes = self._sample(until_read_index, n, postfix=postfix)

        accumulator = 0
        for random_byte in random_bytes:
            accumulator = (accumulator << BYTE_SIZE_BITS) ^ int(random_byte)

        return accumulator % upper_bound

    def _sample(self, until_read_index: bool, n: int, postfix: bytes = b'') -> bytes:
        """Fiat-Shamir sampling base on current verifier view."""

        current_verifier_view = self.serialize(until_read_index)
        result = hashlib.shake_256(current_verifier_view + postfix).digest(n)

        return result
