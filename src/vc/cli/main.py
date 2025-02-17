import dataclasses
import logging
import sys
import argparse

import galois

from vc.prover import Prover, ProverOptions


logger = logging.getLogger(__name__)


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
    verifier_repetitions: int
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
        nargs='+',
        default=1,
        required=False,
        metavar='FACTOR',
        type=int)

    parser.add_argument('--expansion-factor-log',
        action='store',
        dest='expansion_factor_log',
        help='expansion factor',
        nargs='+',
        default=1,
        required=False,
        metavar='FACTOR',
        type=int)

    parser.add_argument('--field',
        action='store',
        dest='field',
        help='prime field size',
        nargs='+',
        default=17,
        required=False,
        metavar='MODULUS',
        type=int)

    parser.add_argument('--final-degree-log',
        action='store',
        dest='final_degree_log',
        help='degree when to stop the protocol',
        nargs='+',
        default=0,
        required=False,
        metavar='DEGREE',
        type=int)

    parser.add_argument('--initial-degree-log',
        action='store',
        dest='initial_degree_log',
        help='initial polynomial degree',
        nargs='+',
        default=2,
        required=False,
        metavar='DEGREE',
        type=int)

    parser.add_argument('--verifier-repetitions',
        action='store',
        dest='verifier_repetitions',
        help='number of verifier repetitions',
        nargs='+',
        default=1,
        required=False,
        metavar='N',
        type=int)

    namespace = parser.parse_args()

    # TODO: Add argument verification.

    return Options(
        folding_factor_log=namespace.folding_factor_log,
        field=namespace.field,
        final_degree_log=namespace.final_degree_log,
        initial_degree_log=namespace.initial_degree_log,
        verifier_repetitions=namespace.verifier_repetitions,
        expansion_factor_log=namespace.expansion_factor_log)


def main() -> int:
    logging.basicConfig(level=logging.INFO)

    options = parse_arguments()
    logger.info(f'main(): {options = }')

    field = galois.GF(options.field)
    logger.info(f'main(): {field = }')

    g = galois.Poly.Random((1 << options.initial_degree_log) - 1, field=field)
    logger.info(f'main(): {g = }')

    prover_options = ProverOptions(
        folding_factor_log=options.folding_factor_log,
        expansion_factor_log=options.expansion_factor_log)
    logger.info(f'main(): {prover_options = }')

    prover = Prover(prover_options)
    proof = prover.prove(g)

    # TODO: Initialize Verifier.

    return 0


if __name__ == '__main__':
    sys.exit(main())
