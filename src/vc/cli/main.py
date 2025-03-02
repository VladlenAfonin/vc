import dataclasses
import logging
import logging.config
import sys
import argparse
import time

import galois

from vc.constants import FIELD_GOLDILOCKS, LOGGER_FRI
from vc.fri.prover import FriProver
from vc.fri.parameters import FriParameters
from vc.fri.verifier import FriVerifier


logger = logging.getLogger(LOGGER_FRI)
logging_config = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "simple": {
            "format": "%(levelname)s:%(name)s:%(funcName)s():%(message)s"
        }
    },
    "handlers": {
        "stdout": {
            "class": "logging.StreamHandler",
            "formatter": "simple",
            "stream": "ext://sys.stdout"
        }
    },
    "loggers": {
        "vc": { "level": "DEBUG", "handlers": ["stdout"] }
    }
}


class FriOptionsDefault:
    folding_factor_log_default: int = 3
    field_default: int = FIELD_GOLDILOCKS.order
    initial_degree_log_default: int = 10
    final_degree_log_default: int = 2
    security_level_bits_default: int = 5
    expansion_factor_log_default: int = 3


@dataclasses.dataclass(slots=True)
class FriOptions:
    """Command line options."""

    folding_factor_log: int
    """Folding factor."""
    field: int
    """Prime field modulus."""
    initial_degree_log: int
    """Initial polynomial degree."""
    final_degree_log: int
    """Degree at which to stop."""
    security_level_bits: int
    """Number of verifier repetitions."""
    expansion_factor_log: int
    """Expansion factor. Code rate reciprocal."""


def parse_arguments() -> FriOptions:
    parser = argparse.ArgumentParser(
        prog='vc',
        description='FRI polynomial commitment scheme experimentation program')

    parser.add_argument(
        '--ff',
        '--folding-factor-log',
        action='store',
        dest='folding_factor_log',
        help=f'folding factor. default: {FriOptionsDefault.folding_factor_log_default}',
        nargs=1,
        default=[FriOptionsDefault.folding_factor_log_default],
        required=False,
        metavar='FACTOR',
        type=int)

    parser.add_argument(
        '--ef',
        '--expansion-factor-log',
        action='store',
        dest='expansion_factor_log',
        help=f'expansion factor. default: {FriOptionsDefault.expansion_factor_log_default}',
        nargs=1,
        default=[FriOptionsDefault.expansion_factor_log_default],
        required=False,
        metavar='FACTOR',
        type=int)

    parser.add_argument(
        '-f',
        '--field',
        action='store',
        dest='field',
        help=f'prime field size. default: {FriOptionsDefault.field_default}',
        nargs=1,
        default=[FriOptionsDefault.field_default],
        required=False,
        metavar='MODULUS',
        type=int)

    parser.add_argument(
        '--fd',
        '--final-degree-log',
        action='store',
        dest='final_degree_log',
        help=f'number of coefficients when to stop the protocol. default: {FriOptionsDefault.final_degree_log_default}',
        nargs=1,
        default=[FriOptionsDefault.final_degree_log_default],
        required=False,
        metavar='N',
        type=int)

    parser.add_argument(
        '--id',
        '--initial-degree-log',
        action='store',
        dest='initial_degree_log',
        help=f'initial number of coefficients. default: {FriOptionsDefault.initial_degree_log_default}',
        nargs=1,
        default=[FriOptionsDefault.initial_degree_log_default],
        required=False,
        metavar='N',
        type=int)

    parser.add_argument(
        '--sl',
        '--security-level-bits',
        action='store',
        dest='security_level_bits',
        help=f'desired security level in bits. default: {FriOptionsDefault.security_level_bits_default}',
        nargs=1,
        default=[FriOptionsDefault.security_level_bits_default],
        required=False,
        metavar='LEVEL',
        type=int)

    namespace = parser.parse_args()

    # TODO: Add argument verification.

    return FriOptions(
        folding_factor_log=namespace.folding_factor_log[0],
        field=namespace.field[0],
        final_degree_log=namespace.final_degree_log[0],
        initial_degree_log=namespace.initial_degree_log[0],
        security_level_bits=namespace.security_level_bits[0],
        expansion_factor_log=namespace.expansion_factor_log[0])


def main() -> int:
    logging.config.dictConfig(logging_config)

    options = parse_arguments()
    field = galois.GF(options.field)
    g = galois.Poly.Random((1 << options.initial_degree_log) - 1, field=field)

    fri_parameters = FriParameters(
        folding_factor_log=options.folding_factor_log,
        expansion_factor_log=options.expansion_factor_log,
        security_level_bits=options.security_level_bits,
        final_coefficients_length_log=options.final_degree_log,
        initial_coefficients_length_log=options.initial_degree_log,
        field=field)

    logger.info(f'fri parameters:{fri_parameters}')

    try:
        begin = time.time()
        prover = FriProver(fri_parameters)
        proof = prover.prove(g)
        end = time.time()
        logger.info(f'prover time: {end - begin:.2f} s')
        logger.info(f'proof:{proof}')

        begin = time.time()
        verifier = FriVerifier(fri_parameters)
        verification_result = verifier.verify(proof)
        end = time.time()
        logger.info(f'verifier time: {(end - begin) * 1000:.0f} ms')
        logger.info(f'verification result: {verification_result}')
    except Exception as exception:
        logger.error(f'coefficients of the polynomial which caused an error (in ascending order): {g.coefficients(order='asc')}')
        logger.exception(f'error message: {exception}')
        raise

    return 0


if __name__ == '__main__':
    sys.exit(main())
