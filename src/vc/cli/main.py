import dataclasses
import logging
import logging.config
import sys
import argparse
import time

import galois

from vc.constants import FIELD_GOLDILOCKS, LOGGER_FRI
from vc.prover import Prover
from vc.parameters import FriParameters
from vc.verifier import Verifier


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


@dataclasses.dataclass(slots=True)
class Options:
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


def parse_arguments() -> Options:
    parser = argparse.ArgumentParser(
        prog='vc',
        description='FRI polynomial commitment scheme experimentation program')

    parser.add_argument(
        '--ff',
        '--folding-factor-log',
        action='store',
        dest='folding_factor_log',
        help='folding factor. default: 3',
        nargs=1,
        default=[3],
        required=False,
        metavar='FACTOR',
        type=int)

    parser.add_argument(
        '--ef',
        '--expansion-factor-log',
        action='store',
        dest='expansion_factor_log',
        help='expansion factor. default: 3',
        nargs=1,
        default=[3],
        required=False,
        metavar='FACTOR',
        type=int)

    parser.add_argument(
        '-f',
        '--field',
        action='store',
        dest='field',
        help='prime field size. default: 18446744069414584321 (goldilocks field)',
        nargs=1,
        default=[18446744069414584321],
        required=False,
        metavar='MODULUS',
        type=int)

    parser.add_argument(
        '--fd',
        '--final-degree-log',
        action='store',
        dest='final_degree_log',
        help='number of coefficients when to stop the protocol. default: 2',
        nargs=1,
        default=[2],
        required=False,
        metavar='N',
        type=int)

    parser.add_argument(
        '--id',
        '--initial-degree-log',
        action='store',
        dest='initial_degree_log',
        help='initial number of coefficients. default: 10',
        nargs=1,
        default=[10],
        required=False,
        metavar='N',
        type=int)

    parser.add_argument(
        '--sl',
        '--security-level-bits',
        action='store',
        dest='security_level_bits',
        help='desired security level in bits. default: 5',
        nargs=1,
        default=[5],
        required=False,
        metavar='LEVEL',
        type=int)

    namespace = parser.parse_args()

    # TODO: Add argument verification.

    return Options(
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
        prover = Prover(fri_parameters)
        proof = prover.prove(g)
        end = time.time()
        logger.info(f'prover time: {end - begin:.2f} s')
        logger.info(f'proof:{proof}')

        begin = time.time()
        verifier = Verifier(fri_parameters)
        verification_result = verifier.verify(proof)
        end = time.time()
        logger.info(f'verifier time: {(end - begin) * 1000:.0f} ms')
        logger.info(f'verification result: {verification_result}')
    except Exception as exception:
        logger.error(f'coefficients of the polynomial which caused an error (in ascending order): {g.coefficients(order='asc')}')
        logger.error(f'{exception}')
        raise

    return 0


if __name__ == '__main__':
    sys.exit(main())
