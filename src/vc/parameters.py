import dataclasses
import logging
import math


logger = logging.getLogger('vc')


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
    security_level: int
    """Security level logarithm."""
    number_of_repetitions: int
    """Number of Verifier checks."""

    def __init__(
            self,
            folding_factor_log: int,
            expansion_factor_log: int,
            security_level_log: int,
            initial_coefficients_length_log: int,
            final_coefficients_length_log: int) -> None:

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

        logger.debug(f'FriParameters.init(): end')

    @staticmethod
    def _get_number_of_repetitions(security_level: int, expansion_factor_log: int) -> int:
        logger.debug(f'FriParameters._get_number_of_repetitions(): begin')

        quotient = security_level / expansion_factor_log
        logger.debug(f'FriParameters._get_number_of_repetitions(): {quotient = }')

        result = math.ceil(quotient)
        logger.debug(f'FriParameters._get_number_of_repetitions(): {result = }')

        logger.debug(f'FriParameters._get_number_of_repetitions(): end')

        return result
