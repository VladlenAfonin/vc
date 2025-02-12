import dataclasses
import sys
import argparse

import galois

from vc import polynomial
from vc.prover import Prover, ProverOptions


@dataclasses.dataclass(slots=True)
class Options:
    """Command line options."""
    folding_factor: int
    """Folding factor."""
    field: int
    """Prime field modulus."""
    initial_degree: int
    """Initial polynomial degree."""
    final_degree: int
    """Degree at which to stop."""
    verifier_repetitions: int
    """Number of verifier repetitions."""


def parse_arguments() -> Options:
    parser = argparse.ArgumentParser(
        prog='vc',
        description='FRI polynomial commitment scheme experimentation program')

    parser.add_argument('--folding-factor',
        action='store',
        dest='folding_factor',
        help='folding factor',
        nargs='+',
        default=2,
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

    parser.add_argument('--final-degree',
        action='store',
        dest='final_degree',
        help='degree when to stop the protocol',
        nargs='+',
        default=0,
        required=False,
        metavar='DEGREE',
        type=int)

    parser.add_argument('--initial-degree',
        action='store',
        dest='initial_degree',
        help='initial polynomial degree',
        nargs='+',
        default=4,
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

    # TODO: Check arguments are correct.

    return Options(
        folding_factor=namespace.folding_factor,
        field=namespace.field,
        final_degree=namespace.final_degree,
        initial_degree=namespace.initial_degree,
        verifier_repetitions=namespace.verifier_repetitions)


def main() -> int:
    options = parse_arguments()

    # TODO: Replace by logger.
    print(f'{options = }')

    field = galois.GF(options.field)
    g = polynomial.random(options.initial_degree, field)

    print(f'{g = }')

    prover_options = ProverOptions(folding_factor=options.folding_factor)
    prover = Prover(prover_options)
    proof = prover.prove(g)

    # TODO: Initialize Verifier.

    return 0


if __name__ == '__main__':
    sys.exit(main())
