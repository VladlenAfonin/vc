import argparse
from dataclasses import dataclass
from time import time_ns
import random
import sys

import galois
import numpy
from tqdm import tqdm
from matplotlib import pyplot as plt
import scienceplots

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


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "-s",
        "--skip",
        dest="skip",
        help="skip computations and use the data in file",
        action="store_true",
    )

    return parser.parse_args()


PROVER_DATA = "./benches/results/data/final-degree-prover.txt"
VERIFIER_DATA = "./benches/results/data/final-degree-verifier.txt"
DEGREE_DATA = "./benches/results/data/final-degree-degrees.txt"
FIGURE = "./benches/results/fig/final-degree.pdf"


def main() -> int:
    args = parse_args()

    if not args.skip:
        # TODO: Get these from command line arguments.
        final_degree_logs = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
        n_tests = 8

        fri_parameter_cases = [
            FriParameters(
                folding_factor_log=1,
                expansion_factor_log=1,
                security_level_bits=5,
                final_coefficients_length_log=fd_log,
                initial_coefficients_length_log=13,
                field=FIELD_GOLDILOCKS,
            )
            for fd_log in final_degree_logs
        ]

        seeds = [generate_random_seed() for _ in range(n_tests)]

        prover_times = []
        verifier_times = []
        for fri_parameters in tqdm(fri_parameter_cases):
            test_case_prover_times = []
            test_case_verifier_times = []
            for seed in tqdm(seeds, leave=False):
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
                numpy.array(test_case_prover_times).mean() // 1_000_000,
            )

            verifier_times.append(
                numpy.array(test_case_verifier_times).mean() // 1_000_000,
            )

        numpy.savetxt(PROVER_DATA, prover_times)
        numpy.savetxt(VERIFIER_DATA, verifier_times)
        numpy.savetxt(DEGREE_DATA, final_degree_logs)
    else:
        prover_times = numpy.loadtxt(PROVER_DATA)
        verifier_times = numpy.loadtxt(VERIFIER_DATA)
        final_degree_logs = numpy.loadtxt(DEGREE_DATA)

    plt.style.use(["science", "russian-font"])

    fig, ax = plt.subplots()
    # ax.set_yscale("log")
    ax.set_xlabel("Степень финального многочлена")
    ax.set_ylabel("Время выполнения, мс")
    ax.set_xticks([2**x for x in final_degree_logs[-4:]])
    ax.set_xticklabels([f"$2^{{{x:.0f}}}$" for x in final_degree_logs[-4:]])
    ax.plot([2**x for x in final_degree_logs], prover_times, label="Доказывающий")
    # ax.plot([2**x for x in final_degree_logs], verifier_times, label="Проверяющий")
    ax.legend()
    fig.subplots_adjust(bottom=0.15, left=0.14, top=0.94, right=0.94)

    # TODO: Use some sort of a root folder.
    plt.savefig("./benches/results/fig/final-degree-prover.jpg", dpi=300)
    plt.savefig("./benches/results/fig/final-degree-prover.pdf")

    return 0


if __name__ == "__main__":
    sys.exit(main())
