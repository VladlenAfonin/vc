import dataclasses
import logging
import math

import galois

from vc.base import is_pow2
from vc.constants import LOGGER_FRI


logger = logging.getLogger(LOGGER_FRI)


@dataclasses.dataclass(init=False, slots=True)
class FriParameters:
    """Prover options."""
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
    initial_evaluation_domain: galois.Array
    """Initial evaluation domain."""
    security_level: int
    """Security level logarithm."""
    number_of_repetitions: int
    """Number of Verifier checks."""
    number_of_rounds: int
    """Number of FRI rounds."""
    field: galois.FieldArray
    """Field."""
    omega: galois.Array
    """Root of unity for initial domain generation."""
    offset: galois.Array
    """Multiplicative group generator."""

    def __init__(
            self,
            folding_factor_log: int,
            expansion_factor_log: int,
            security_level_log: int,
            initial_coefficients_length_log: int,
            final_coefficients_length_log: int,
            field: galois.FieldArray) -> None:
        logger.debug(f'FriParameters.init(): begin')

        assert folding_factor_log > 0, 'folding factor log must be at least 1'
        assert expansion_factor_log > 0, 'expansion factor log must be at least 1'

        self.folding_factor = 1 << folding_factor_log
        logger.debug(f'FriParameters.init(): {self.folding_factor = }')

        self.expansion_factor_log = expansion_factor_log
        logger.debug(f'FriParameters.init(): {self.expansion_factor_log = }')

        self.expansion_factor = 1 << expansion_factor_log
        logger.debug(f'FriParameters.init(): {self.expansion_factor = }')

        self.security_level = 1 << security_level_log
        logger.debug(f'FriParameters.init(): {self.security_level = }')

        self.initial_coefficients_length_log = initial_coefficients_length_log
        logger.debug(f'FriParameters.init(): {self.initial_coefficients_length_log = }')

        self.initial_coefficients_length = 1 << initial_coefficients_length_log
        logger.debug(f'FriParameters.init(): {self.initial_coefficients_length = }')

        self.final_coefficients_length_log = final_coefficients_length_log
        logger.debug(f'FriParameters.init(): {self.final_coefficients_length_log = }')

        self.final_coefficients_length = 1 << final_coefficients_length_log
        logger.debug(f'FriParameters.init(): {self.final_coefficients_length = }')

        self.number_of_repetitions = self._get_number_of_repetitions(
            self.security_level,
            self.expansion_factor_log)
        logger.debug(f'FriParameters.init(): {self.number_of_repetitions = }')

        self.number_of_rounds = self._get_number_of_rounds(
            self.initial_coefficients_length,
            self.final_coefficients_length,
            self.folding_factor)
        logger.debug(f'FriParameters.init(): {self.number_of_repetitions = }')

        self.field = field
        logger.debug(f'FriParameters.init(): {self.field = }')

        self.initial_evaluation_domain_length = self.initial_coefficients_length * self.expansion_factor
        logger.debug(f'FriParameters.init(): {self.initial_evaluation_domain_length = }')

        self.omega = field.primitive_root_of_unity(self.initial_evaluation_domain_length)
        logger.debug(f'FriParameters.init(): {self.omega = }')

        self.offset = field.primitive_element
        logger.debug(f'FriParameters.init(): {self.offset = }')

        self.initial_evaluation_domain = field(
            [self.offset * (self.omega ** i) for i in range(self.initial_evaluation_domain_length)])
        logger.debug(f'FriParameters.init(): {self.initial_evaluation_domain = }')

        logger.debug(f'FriParameters.init(): end')

    @staticmethod
    def _get_number_of_repetitions(
            security_level: int,
            expansion_factor_log: int) -> int:
        logger.debug(f'FriParameters._get_number_of_repetitions(): begin')

        quotient = security_level / expansion_factor_log
        logger.debug(f'FriParameters._get_number_of_repetitions(): {quotient = }')

        result = math.ceil(quotient)
        logger.debug(f'FriParameters._get_number_of_repetitions(): {result = }')

        logger.debug(f'FriParameters._get_number_of_repetitions(): end')

        return result

    @staticmethod
    def _get_number_of_rounds(
            initial_coefficients_length,
            final_coefficients_length,
            folding_factor) -> int:
        logger.debug(f'Prover._get_number_of_rounds(): begin')

        assert is_pow2(initial_coefficients_length), 'initial coefficients length must be a power of two'
        assert is_pow2(final_coefficients_length), 'final coefficients length must be a power of two'
        assert is_pow2(folding_factor), 'folding factor must be a power of two'

        current_coefficients_length = initial_coefficients_length
        accumulator: int = 0
        while final_coefficients_length < current_coefficients_length:
            logger.debug(f'Prover._get_number_of_rounds(): current {accumulator = }')
            current_coefficients_length //= folding_factor
            accumulator += 1

        # This is done in the STIR codebase. Not sure, why exactly.
        # Probably this is needed there because the initial round is out of the "rounds loop".
        # Or maybe because the last round does not need the proof. This is my use-case.
        logger.debug(f'Prover._get_number_of_rounds(): subtract 1 from accumulator')
        accumulator -= 1

        logger.debug(f'Prover._get_number_of_rounds(): final {accumulator = }')
        logger.debug(f'Prover._get_number_of_rounds(): end')

        return accumulator
