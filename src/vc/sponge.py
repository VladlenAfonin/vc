from __future__ import annotations

import dataclasses
import hashlib
import logging
import pickle
import typing

import galois
import numpy

from vc.logging import function_begin, function_end, parameter_received


logger = logging.getLogger(__name__)
BYTE_SIZE_BITS = 8


@dataclasses.dataclass(init=False, slots=True)
class Sponge:
    """Sponge."""

    _field: type[galois.FieldArray]
    """Field for elements sampling."""
    _objects: typing.List[object]
    """Current objects array."""
    _len: int
    """Length of current objects array."""
    _additional_state: int
    """Additional Sponge state. This is used so that consecutive squeezes produce different results."""

    def __init__(self, field: type[galois.FieldArray]) -> None:
        """Initialize new Sponge.

        :param field: Field to use when sampling field elements.
        :type field: type[galois.FieldArray]
        """

        self._objects = []
        self._field = field
        self._len = 0
        self._additional_state = 0

    def _serialize(self) -> bytes:
        """Serialize current state into byte array."""

        return pickle.dumps(self._objects)

    def absorb(self, obj: typing.Any) -> None:
        """Push data to the proof stream.

        :param obj: Arbitrary data to push.
        :type obj: typing.Any
        """

        logger.debug(function_begin(self.absorb.__name__))
        logger.debug(parameter_received("obj", obj))

        self._additional_state = 0

        self._len += 1
        self._objects.append(obj)

        logger.debug(function_end(self.absorb.__name__))

    def squeeze(self, n: int = 32) -> bytes:
        """Sample random data. This function is to be called by the prover.

        :param n: Number of bytes to squeeze, defaults to 32.
        :type n: int, optional
        :return: Squeezed bytes.
        :rtype: bytes
        """

        logger.debug(function_begin(self.squeeze.__name__))
        result = self._squeeze(n)
        logger.debug(function_end(self.squeeze.__name__, result))

        return result

    def squeeze_field_element(self, n: int = 32) -> galois.FieldArray:
        """Sample random field element. This function is to be called by the prover.

        :param n: Number of bytes to squeeze, defaults to 32.
        :type n: int, optional
        :return: Squeezed field element.
        :rtype: galois.FieldArray
        """

        logger.debug(function_begin(self.squeeze_field_element.__name__))
        result = self._squeeze_field_element(n)
        logger.debug(function_end(self.squeeze_field_element.__name__, result))

        return result

    def squeeze_index(self, upper_bound: int, n: int = 32) -> int:
        """Squeeze index.

        :param upper_bound: Upper bound.
        :type upper_bound: int
        :param n: Number of bytes to use when squeezing, defaults to 32.
        :type n: int, optional
        :return: Squeezed index.
        :rtype: int
        """

        logger.debug(function_begin(self.squeeze_index.__name__))
        result = self._squeeze_number(upper_bound, n)
        logger.debug(function_end(self.squeeze_index.__name__, result))

        return result

    def squeeze_indices(
        self,
        amount: int,
        upper_bound: int,
        n: int = 32,
    ) -> numpy.ndarray:
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

        logger.debug(function_begin(self.squeeze_indices.__name__))

        assert amount <= upper_bound, "not enough integers to sample indices from"

        if amount == upper_bound:
            return numpy.sort(numpy.array(range(upper_bound)))

        result = []
        i = 0
        result_length = 0
        while result_length < amount:
            random_number = self._squeeze_number(upper_bound, n, postfix=bytes(i))
            if random_number not in result:
                result_length += 1
                result.append(random_number)

            i += 1

        result = numpy.sort(numpy.array(result))

        logger.debug(function_end(self.squeeze_indices.__name__, result))

        return result

    def _squeeze_field_element(self, n: int) -> galois.FieldArray:
        """Squeeze a field element.

        :param n: Number of bytes to use when squeezing.
        :type n: int
        :return: Field element.
        :rtype: galois.Array
        """

        logger.debug(function_begin(self._squeeze_field_element.__name__))

        random_number = self._squeeze_number(self._field.order, n)
        result = self._field(random_number)

        logger.debug(function_end(self._squeeze_field_element.__name__, result))

        return result

    def _squeeze_number(self, upper_bound: int, n: int, postfix: bytes = b"") -> int:
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

        logger.debug(function_begin(self._squeeze_number.__name__))

        random_bytes = self._squeeze(n, postfix=postfix)

        accumulator = 0
        for random_byte in random_bytes:
            accumulator = (accumulator << BYTE_SIZE_BITS) ^ int(random_byte)

        result = accumulator % upper_bound

        logger.debug(function_end(self._squeeze_number.__name__, result))

        return result

    def _squeeze(self, n: int, postfix: bytes = b"") -> bytes:
        """Squeeze bytes.
        This uses Fiat-Shamir sampling base on current verifier view.

        :param n: Number of bytes to squeeze.
        :type n: int
        :param postfix: Additional postfix to use when sampling.
        :type postfix: bytes
        :return: Squeezed bytes.
        :rtype: bytes
        """

        logger.debug(function_begin(self._squeeze.__name__))

        self._additional_state += n

        current_state = self._serialize()
        result = hashlib.shake_256(
            current_state + self._additional_state.to_bytes(4) + postfix
        ).digest(n)

        logger.debug(function_end(self._squeeze.__name__))

        return result
