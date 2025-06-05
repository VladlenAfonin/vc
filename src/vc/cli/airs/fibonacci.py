import pickle
import random
import argparse
from dataclasses import dataclass
import sys
import time
import typing

from vc.base import get_nearest_power_of_two_ext
from vc.constants import FIELD_GOLDILOCKS
from vc.fri.parameters import FriParameters
from vc.fri.prover import FriProver
from vc.fri.verifier import FriVerifier
from vc.stark.airs.fibonacci import (
    fib,
    get_aet,
    get_boundary_constraints,
    get_transition_constraints,
)
from vc.stark.parameters import StarkParameters
from vc.stark.prover import StarkProver
from vc.stark.verifier import StarkVerifier


field = FIELD_GOLDILOCKS


@dataclass(slots=True)
class StarkFriConfiguration:
    expansion_factor_log: int
    folding_factor_log: int
    security_level_bits: int
    final_coefficients_length_log: int


def get_stark(
    aet_height: int,
    fri_config: StarkFriConfiguration,
) -> typing.Tuple[StarkProver, StarkVerifier]:
    aet_height_pow2, aet_height_log = get_nearest_power_of_two_ext(aet_height)
    omicron = field.primitive_root_of_unity(aet_height_pow2)

    fri_parameters = FriParameters(
        folding_factor_log=fri_config.folding_factor_log,
        expansion_factor_log=fri_config.expansion_factor_log,
        security_level_bits=fri_config.security_level_bits,
        initial_coefficients_length_log=(
            aet_height_log + fri_config.expansion_factor_log
        ),
        final_coefficients_length_log=fri_config.final_coefficients_length_log,
        field=field,
    )
    fri_prover = FriProver(fri_parameters)
    fri_verifier = FriVerifier(fri_parameters)

    stark_parameters = StarkParameters(omicron=omicron, field=field)
    return (
        StarkProver(
            stark_parameters=stark_parameters,
            fri_prover=fri_prover,
            state=StarkProver.StarkProverState(
                field=field,
                omicron=omicron,
                aet_height=aet_height,
            ),
            fri_parameters=fri_parameters,
        ),
        StarkVerifier(
            state=StarkVerifier.StarkVerifierState(
                fri_verifier=fri_verifier,
                fri_parameters=fri_parameters,
                omicron=omicron,
            )
        ),
    )


def generate_random_seed() -> int:
    return random.getrandbits(64)


def run(args: argparse.Namespace) -> int:
    # TODO: Generate seed. This will be needed for ZK.

    fri_config = StarkFriConfiguration(
        expansion_factor_log=args.expansion_factor_log[0],
        folding_factor_log=args.folding_factor_log[0],
        security_level_bits=args.security_level_bits[0],
        final_coefficients_length_log=args.final_degree_log[0],
    )

    # TODO: Extract into a function that parses the number.
    if len(args.air_arguments) != 1 or int(args.air_arguments[0]) is None:
        print(
            "expected one integer: index of a fibonacci number. fibonacci numbers = {0, 1, 1, 2, ...}",
            file=sys.stderr,
        )
        return 1

    n = int(args.air_arguments[0])

    aet_height = n
    stark_prover, stark_verifier = get_stark(aet_height, fri_config)

    result = fib(n)
    print(f"proving that {n}-th fibonacci number is {result}")

    aet = get_aet(n)
    print(f"AET shape: {aet.shape}")

    boundary_constraints = get_boundary_constraints(n, result)
    print(f"number of boundary constraints: {len(boundary_constraints)}")

    transition_constraints = get_transition_constraints()
    print(f"number of transition constraints: {len(transition_constraints)}")

    print()
    print(f"fri parameters: {stark_prover.fri_parameters}")

    begin = time.time()
    proof = stark_prover.prove(
        aet,
        transition_constraints,
        boundary_constraints,
    )
    end = time.time()
    print(f"prover time: {end - begin:.2f} s")
    print(f"proof size: {len(pickle.dumps(proof)) // 1024} KB")

    begin = time.time()
    verification_result = stark_verifier.verify(
        proof,
        transition_constraints,
        boundary_constraints,
        aet.shape[1],
        aet.shape[0],
    )
    end = time.time()
    print(f"verifier time: {(end - begin) * 1000:.0f} ms")
    print(f"verification result: {verification_result}")

    return 0
