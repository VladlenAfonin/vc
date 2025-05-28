import dataclasses
import logging
import logging.config
import random
import sys
import argparse
import time

import galois

from vc.fri.prover import FriProver
from vc.fri.parameters import FriParameters
from vc.fri.verifier import FriVerifier
from vc.constants import FIELD_GOLDILOCKS
from vc.logging import (
    current_value,
    logging_mark,
    parameter_received,
)


logging_config = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "simple": {
            "format": "%(levelname)s:%(name)s:%(funcName)s():%(message)s",
        }
    },
    "handlers": {
        "stdout": {
            "class": "logging.StreamHandler",
            "formatter": "simple",
            "stream": "ext://sys.stdout",
        }
    },
    "loggers": {
        # "vc.cli.main": {"level": "INFO", "handlers": ["stdout"]},
        # "vc.fri.prover": {"level": "DEBUG", "handlers": ["stdout"]},
        # "vc.fri.verifier": {"level": "DEBUG", "handlers": ["stdout"]},
    },
}

logger = logging.getLogger(__name__)
logging.config.dictConfig(logging_config)


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
    seed: int | None = None
    """Randomness seed."""


@logging_mark(logger)
def parse_arguments() -> FriOptions:
    parser = argparse.ArgumentParser(
        prog="vc",
        description="Verifiable Computations (VC) experimentation program",
    )

    subparsers = parser.add_subparsers()
    fri = subparsers.add_parser("fri")
    stark = subparsers.add_parser("stark")

    fri.add_argument(
        "--ff",
        "--folding-factor-log",
        action="store",
        dest="folding_factor_log",
        help=f"folding factor. default: {FriOptionsDefault.folding_factor_log_default}",
        nargs=1,
        default=[FriOptionsDefault.folding_factor_log_default],
        required=False,
        metavar="NUMBER",
        type=int,
    )

    fri.add_argument(
        "--ef",
        "--expansion-factor-log",
        action="store",
        dest="expansion_factor_log",
        help=f"expansion factor. default: {FriOptionsDefault.expansion_factor_log_default}",
        nargs=1,
        default=[FriOptionsDefault.expansion_factor_log_default],
        required=False,
        metavar="NUMBER",
        type=int,
    )

    fri.add_argument(
        "-f",
        "--field",
        action="store",
        dest="field",
        help=f"prime field size. default: {FriOptionsDefault.field_default}",
        nargs=1,
        default=[FriOptionsDefault.field_default],
        required=False,
        metavar="NUMBER",
        type=int,
    )

    fri.add_argument(
        "--fd",
        "--final-degree-log",
        action="store",
        dest="final_degree_log",
        help=f"number of coefficients when to stop the protocol. default: {FriOptionsDefault.final_degree_log_default}",
        nargs=1,
        default=[FriOptionsDefault.final_degree_log_default],
        required=False,
        metavar="NUMBER",
        type=int,
    )

    fri.add_argument(
        "--id",
        "--initial-degree-log",
        action="store",
        dest="initial_degree_log",
        help=f"initial number of coefficients. default: {FriOptionsDefault.initial_degree_log_default}",
        nargs=1,
        default=[FriOptionsDefault.initial_degree_log_default],
        required=False,
        metavar="NUMBER",
        type=int,
    )

    fri.add_argument(
        "--sl",
        "--security-level-bits",
        action="store",
        dest="security_level_bits",
        help=f"desired security level in bits. default: {FriOptionsDefault.security_level_bits_default}",
        nargs=1,
        default=[FriOptionsDefault.security_level_bits_default],
        required=False,
        metavar="NUMBER",
        type=int,
    )

    fri.add_argument(
        "-s",
        "--seed",
        action="store",
        dest="seed",
        help=f"randomness seed. default: 64 bit integer chosen at random",
        nargs=1,
        default=[None],
        required=False,
        metavar="NUMBER",
        type=int,
    )

    namespace = parser.parse_args()

    # TODO: Add argument verification.

    return FriOptions(
        folding_factor_log=namespace.folding_factor_log[0],
        field=namespace.field[0],
        final_degree_log=namespace.final_degree_log[0],
        initial_degree_log=namespace.initial_degree_log[0],
        security_level_bits=namespace.security_level_bits[0],
        expansion_factor_log=namespace.expansion_factor_log[0],
        seed=namespace.seed[0],
    )


def generate_random_seed() -> int:
    return random.getrandbits(64)


@logging_mark(logger)
def main() -> int:
    options = parse_arguments()
    logger.debug(parameter_received("cli_options", options))

    if options.seed is None:
        logger.debug(f"seed was not provided. generating seed")
        options.seed = generate_random_seed()
        print(f"seed: {options.seed}")
        logger.debug(current_value("seed", options.seed))

    field = galois.GF(options.field)
    g = galois.Poly.Random(
        (1 << options.initial_degree_log) - 1,
        field=field,
        seed=options.seed,
    )

    logger.debug(current_value("polynomial to be proven", g))

    fri_parameters = FriParameters(
        folding_factor_log=options.folding_factor_log,
        expansion_factor_log=options.expansion_factor_log,
        security_level_bits=options.security_level_bits,
        final_coefficients_length_log=options.final_degree_log,
        initial_coefficients_length_log=options.initial_degree_log,
        field=field,
    )

    print(f"fri parameters: {fri_parameters}")

    try:
        begin = time.time()
        prover = FriProver(fri_parameters)
        proof = prover.prove(g)
        end = time.time()
        print(f"prover time: {end - begin:.2f} s")
        print(f"proof:{proof}")

        begin = time.time()
        verifier = FriVerifier(fri_parameters)
        verification_result = verifier.verify(proof)
        end = time.time()
        print(f"verifier time: {(end - begin) * 1000:.0f} ms")
        print(f"verification result: {verification_result}")
    except Exception as exception:
        print(
            f"coefficients of the polynomial which caused an error "
            + "(in ascending order): {g.coefficients(order='asc')}",
            file=sys.stderr,
        )
        logger.exception(f"error message: {exception}")
        raise

    return 0


if __name__ == "__main__":
    sys.exit(main())
