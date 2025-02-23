import dataclasses
import logging
import logging.config
import sys
import argparse
import time

import galois

from vc.constants import LOGGER_FRI
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
    security_level_log: int
    """Number of verifier repetitions."""
    expansion_factor_log: int
    """Expansion factor. Code rate reciprocal."""


def parse_arguments() -> Options:
    parser = argparse.ArgumentParser(
        prog='vc',
        description='FRI polynomial commitment scheme experimentation program')

    parser.add_argument('--folding-factor-log',
        action='store',
        dest='folding_factor_log',
        help='folding factor',
        nargs='?',
        default=3,
        required=False,
        metavar='FACTOR',
        type=int)

    parser.add_argument('--expansion-factor-log',
        action='store',
        dest='expansion_factor_log',
        help='expansion factor',
        nargs='?',
        default=3,
        required=False,
        metavar='FACTOR',
        type=int)

    parser.add_argument('--field',
        action='store',
        dest='field',
        help='prime field size',
        nargs='?',
        default=18446744069414584321,
        required=False,
        metavar='MODULUS',
        type=int)

    parser.add_argument('--final-degree-log',
        action='store',
        dest='final_degree_log',
        help='number of coefficients when to stop the protocol',
        nargs='?',
        default=2,
        required=False,
        metavar='N',
        type=int)

    parser.add_argument('--initial-degree-log',
        action='store',
        dest='initial_degree_log',
        help='initial number of coefficients',
        nargs='?',
        default=10,
        required=False,
        metavar='N',
        type=int)

    parser.add_argument('--security-level-log',
        action='store',
        dest='security_level_log',
        help='desired security level',
        nargs='?',
        default=5,
        required=False,
        metavar='LEVEL',
        type=int)

    namespace = parser.parse_args()

    # TODO: Add argument verification.

    return Options(
        folding_factor_log=namespace.folding_factor_log,
        field=namespace.field,
        final_degree_log=namespace.final_degree_log,
        initial_degree_log=namespace.initial_degree_log,
        security_level_log=namespace.security_level_log,
        expansion_factor_log=namespace.expansion_factor_log)


def main() -> int:
    logging.config.dictConfig(logging_config)

    options = parse_arguments()

    field = galois.GF(options.field)

    g = galois.Poly.Random((1 << options.initial_degree_log) - 1, field=field)

    fri_parameters = FriParameters(
        folding_factor_log=options.folding_factor_log,
        expansion_factor_log=options.expansion_factor_log,
        security_level_log=options.security_level_log,
        final_coefficients_length_log=options.final_degree_log,
        initial_coefficients_length_log=options.initial_degree_log,
        field=field)

    logger.info(f'fri parameters:{fri_parameters}')

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

    return 0


if __name__ == '__main__':
    sys.exit(main())
