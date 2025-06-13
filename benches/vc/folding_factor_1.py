from dataclasses import dataclass
from time import time_ns
import random
import sys

import galois
import numpy
from tqdm import tqdm

from vc.constants import FIELD_GOLDILOCKS
from vc.fri.parameters import FriParameters
from vc.fri.prover import FriProver
from vc.fri.verifier import FriVerifier


@dataclass(slots=True, init=False)
class TestCase:
    seed: int
    polynomial: galois.Poly
    prover: FriProver
    verifier: FriVerifier

    def __init__(self, fri_parameters: FriParameters, seed: int) -> None:
        self.seed = seed
        self.polynomial = galois.Poly.Random(
            fri_parameters.initial_coefficients_length - 1,
            field=fri_parameters.field,
            seed=seed,
        )
        self.prover = FriProver(fri_parameters)
        self.verifier = FriVerifier(fri_parameters)


def generate_random_seed() -> int:
    return random.getrandbits(64)


def main() -> int:
    # TODO: Get these from command line arguments.
    ff_logs = [1, 2, 3, 4]
    n_tests = 1

    fri_parameter_cases = [
        FriParameters(
            folding_factor_log=ff_log,
            expansion_factor_log=1,
            security_level_bits=5,
            final_coefficients_length_log=ff_log,
            initial_coefficients_length_log=16,
            field=FIELD_GOLDILOCKS,
        )
        for ff_log in ff_logs
    ]

    print(fri_parameter_cases)

    seeds = [generate_random_seed() for _ in range(n_tests)]

    prover_times = []
    verifier_times = []
    for fri_parameters in fri_parameter_cases:
        test_case_prover_times = []
        test_case_verifier_times = []
        for seed in seeds:
            test_case = TestCase(fri_parameters, seed)

            begin = time_ns()
            proof = test_case.prover.prove(test_case.polynomial)
            end = time_ns()

            test_case_prover_times.append(end - begin)

            begin = time_ns()
            result = test_case.verifier.verify(proof)
            end = time_ns()
            assert result == True, "generated invalid proof"

            test_case_verifier_times.append(end - begin)

        prover_times.append(
            numpy.array(test_case_prover_times).mean(),
        )
        verifier_times.append(
            numpy.array(test_case_verifier_times).mean(),
        )

    print(prover_times)
    print(verifier_times)

    return 0


if __name__ == "__main__":
    sys.exit(main())
