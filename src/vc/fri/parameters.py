import dataclasses
import logging
import math

import galois

from vc.base import is_pow2


logger = logging.getLogger(__name__)


@dataclasses.dataclass(init=False, slots=True, repr=False)
class FriParameters:
    """Prover options."""

    folding_factor_log: int
    """Folding factor logarithm."""
    folding_factor: int
    """Folding factor."""
    expansion_factor_log: int
    """Expansion factor logarithm."""
    expansion_factor: int
    """Expansion factor."""
    initial_coefficients_length_log: int
    """Number of coefficients in initial polynomial logarithm."""
    initial_coefficients_length: int
    """Number of coefficients in initial polynomial."""
    final_coefficients_length_log: int
    """Number of coefficients in final polynomial logarithm."""
    final_coefficients_length: int
    """Number of coefficients in final polynomial."""
    initial_evaluation_domain_length: int
    """Length of the initial evaluation domain."""
    initial_evaluation_domain: galois.FieldArray
    """Initial evaluation domain."""
    security_level_bits: int
    """Security level in bits."""
    number_of_repetitions: int
    """Number of Verifier checks."""
    number_of_rounds: int
    """Number of FRI rounds."""
    field: type[galois.FieldArray]
    """Field."""
    omega: galois.FieldArray
    """Root of unity for initial domain generation."""
    offset: galois.FieldArray
    """Multiplicative group generator."""

    def __repr__(self) -> str:
        return f"""
    expansion factor = {self.expansion_factor} (2^{self.expansion_factor_log})
    folding factor = {self.folding_factor} (2^{self.folding_factor_log})
    initial coefficients length = {self.initial_coefficients_length} (2^{self.initial_coefficients_length_log})
    final coefficients length = {self.final_coefficients_length} (2^{self.final_coefficients_length_log})
    initial evaluation domain length = {self.initial_evaluation_domain_length} (2^{math.log2(self.initial_evaluation_domain_length):.0f})

    security level = {self.security_level_bits} bits
    number of rounds = {self.number_of_rounds}
    number of query indices = {self.number_of_repetitions}
"""

    def __init__(
        self,
        folding_factor_log: int,
        expansion_factor_log: int,
        security_level_bits: int,
        initial_coefficients_length_log: int,
        final_coefficients_length_log: int,
        field: type[galois.FieldArray],
    ) -> None:
        assert folding_factor_log > 0, "folding factor log must be at least 1"
        assert expansion_factor_log > 0, "expansion factor log must be at least 1"

        self.field = field
        self.security_level_bits = security_level_bits
        self.folding_factor_log = folding_factor_log
        self.folding_factor = 1 << folding_factor_log
        self.expansion_factor_log = expansion_factor_log
        self.expansion_factor = 1 << expansion_factor_log
        self.initial_coefficients_length_log = initial_coefficients_length_log
        self.initial_coefficients_length = 1 << initial_coefficients_length_log
        self.final_coefficients_length_log = final_coefficients_length_log
        self.final_coefficients_length = 1 << final_coefficients_length_log
        self.initial_evaluation_domain_length = (
            self.initial_coefficients_length * self.expansion_factor
        )

        self.offset = field.primitive_element
        self.omega = field.primitive_root_of_unity(
            self.initial_evaluation_domain_length
        )
        self.initial_evaluation_domain = field(
            [
                self.offset * (self.omega**i)
                for i in range(self.initial_evaluation_domain_length)
            ]
        )

        self.number_of_repetitions = self._get_number_of_repetitions(
            self.security_level_bits, self.expansion_factor_log
        )

        self.number_of_rounds = self._get_number_of_rounds(
            self.initial_coefficients_length,
            self.final_coefficients_length,
            self.folding_factor,
        )

    @staticmethod
    def _get_number_of_repetitions(
        security_level_bits: int,
        expansion_factor_log: int,
    ) -> int:
        quotient = security_level_bits / expansion_factor_log
        return math.ceil(quotient)

    @staticmethod
    def _get_number_of_rounds(
        initial_coefficients_length,
        final_coefficients_length,
        folding_factor,
    ) -> int:
        assert is_pow2(
            initial_coefficients_length
        ), "initial coefficients length must be a power of two"
        assert is_pow2(
            final_coefficients_length
        ), "final coefficients length must be a power of two"
        assert is_pow2(folding_factor), "folding factor must be a power of two"

        current_coefficients_length = initial_coefficients_length
        accumulator: int = 0
        while final_coefficients_length < current_coefficients_length:
            current_coefficients_length //= folding_factor
            accumulator += 1

        # This is done in the STIR codebase. Not sure, why exactly.
        # Probably this is needed there because the initial round is out of the "rounds loop".
        # Or maybe because the last round does not need the proof. This is my use-case.
        accumulator -= 1

        return accumulator
