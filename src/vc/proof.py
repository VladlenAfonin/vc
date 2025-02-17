from __future__ import annotations

import dataclasses
import hashlib
import pickle
import typing

import galois


BYTE_SIZE_BITS = 8


@dataclasses.dataclass(init=False, slots=True)
class ProofStream:
    _field: galois.FieldArray
    _objects: typing.List[object]
    _read_index: int
    _len: int

    def __init__(self, field: galois.FieldArray, objects: typing.List[typing.Any] = []) -> None:
        self._objects = objects
        self._field = field
        self._read_index = 0
        self._len = 0

    def serialize(self, until_read_index: bool = False) -> bytes:
        data_to_serialize = self._objects[:self._read_index] \
            if until_read_index else self._objects
        return pickle.dumps(data_to_serialize)

    @staticmethod
    def from_data(data: bytes) -> ProofStream:
        objects = pickle.loads(data)
        return ProofStream(objects=objects)

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

    def sample_prover(self, n: int = 32):
        """Sample random data. This function is to be called by the prover."""
        return self._sample(False, n)

    def sample_verifier(self, n: int = 32):
        """Sample random data. This function is to be called by the verifier."""
        return self._sample(True, n)

    def sample_field_prover(self, n: int = 32):
        """Sample random field element. This function is to be called by the prover."""
        return self._sample_field(False, n)

    def sample_field_verifier(self, n: int = 32):
        """Sample random field element. This function is to be called by the prover."""
        return self._sample_field(True, n)

    def sample_index_prover(self, upper_bound, n: int = 32) -> int:
        return self._sample_number(upper_bound, False, n)

    def sample_index_verifier(self, upper_bound, n: int = 32) -> int:
        return self._sample_number(upper_bound, True, n)

    def _sample_field(self, until_read_index: bool, n: int):
        random_number = self._sample_number(self._field.order, until_read_index, n)
        return self._field(random_number)

    def _sample_number(self, upper_bound: int, until_read_index: bool, n: int) -> int:
        random_bytes = self._sample(until_read_index, n)

        accumulator = 0
        for random_byte in random_bytes:
            accumulator = (accumulator << BYTE_SIZE_BITS) ^ int(random_byte)

        return accumulator % upper_bound

    def _sample(self, until_read_index: bool, n: int):
        """Fiat-Shamir sampling base on current verifier view."""

        current_verifier_view = self.serialize(until_read_index)
        return hashlib.shake_256(current_verifier_view).digest(n)
