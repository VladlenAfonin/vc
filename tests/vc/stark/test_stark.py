import math
import typing
import pytest

from vc.base import get_nearest_power_of_two
from vc.fri.parameters import FriParameters
from vc.fri.prover import FriProver
from vc.fri.verifier import FriVerifier
from vc.stark.airs import counter, factorial
from vc.stark.airs.fibonacci import (
    fib,
    get_aet,
    get_boundary_constraints,
    get_transition_constraints,
)
from vc.stark.parameters import StarkParameters
from vc.stark.prover import StarkProver
from vc.constants import FIELD_GOLDILOCKS
from vc.stark.verifier import StarkVerifier


TEST_FIELD = FIELD_GOLDILOCKS


def get_test_stark(aet_height: int) -> typing.Tuple[StarkProver, StarkVerifier]:
    expansion_factor_log = 1
    expansion_factor = 1 << expansion_factor_log

    aet_height_pow2 = get_nearest_power_of_two(aet_height)
    aet_height_log = math.ceil(math.log2(aet_height_pow2))

    # INFO: This omega is not the same that is used in FRI.
    #       The FRI omega is also shifted by the generator.
    omega_domain_len = aet_height_pow2 * expansion_factor
    omega = TEST_FIELD.primitive_root_of_unity(omega_domain_len)
    omicron = omega**expansion_factor

    stark_parameters = StarkParameters(omicron=omicron, field=TEST_FIELD)
    fri_parameters = FriParameters(
        folding_factor_log=1,
        expansion_factor_log=expansion_factor_log,
        security_level_bits=5,
        initial_coefficients_length_log=aet_height_log + expansion_factor_log,
        final_coefficients_length_log=0,
        field=TEST_FIELD,
    )
    fri_prover = FriProver(fri_parameters)
    fri_verifier = FriVerifier(fri_parameters)

    return (
        StarkProver(
            stark_parameters=stark_parameters,
            fri_prover=fri_prover,
            state=StarkProver.StarkProverState(
                field=TEST_FIELD,
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


@pytest.mark.parametrize("n", [4, 8, 16])
def test_get_trace_polynomials(n: int):
    stark_prover, _ = get_test_stark(n)
    aet = get_aet(n)

    trace_polynomials = stark_prover.get_trace_polynomials(aet)

    # Test first row of the AET.
    assert trace_polynomials[0](TEST_FIELD(1)) == 0, "invalid first row"
    assert trace_polynomials[1](TEST_FIELD(1)) == 1, "invalid first row"

    # Test last row of the AET.
    assert trace_polynomials[0](
        stark_prover.stark_parameters.omicron ** (n - 1)
    ) == fib(n - 1), "invalid last row"
    assert trace_polynomials[1](
        stark_prover.stark_parameters.omicron ** (n - 1)
    ) == fib(n), "invalid first row"


@pytest.mark.parametrize("n", [8, 13, 16, 17, 63, 65])
def test_stark(n: int):
    result = fib(n)
    aet = get_aet(n)
    boundary_constraints = get_boundary_constraints(n, result)
    transition_constraints = get_transition_constraints()

    stark_prover, stark_verifier = get_test_stark(aet.shape[0])
    proof = stark_prover.prove(
        aet,
        transition_constraints,
        boundary_constraints,
    )
    result = stark_verifier.verify(
        proof,
        transition_constraints,
        boundary_constraints,
        aet.shape[1],
        aet.shape[0],
    )

    assert result, "invalid proof"


@pytest.mark.parametrize("n", [8])
def test_stark_counter(n: int):
    result = n - 1
    aet = counter.get_aet(n)
    boundary_constraints = counter.get_boundary_constraints(n)
    transition_constraints = counter.get_transition_constraints()

    stark_prover, stark_verifier = get_test_stark(aet.shape[0])
    proof = stark_prover.prove(
        aet,
        transition_constraints,
        boundary_constraints,
    )
    result = stark_verifier.verify(
        proof,
        transition_constraints,
        boundary_constraints,
        aet.shape[1],
        aet.shape[0],
    )

    assert result, "invalid proof"


@pytest.mark.parametrize("n", [5])
def test_stark_factorial(n: int):
    result = math.factorial(n)
    aet = factorial.get_aet(n)
    boundary_constraints = factorial.get_boundary_constraints(n, result)
    transition_constraints = factorial.get_transition_constraints()

    stark_prover, stark_verifier = get_test_stark(aet.shape[0])
    proof = stark_prover.prove(
        aet,
        transition_constraints,
        boundary_constraints,
    )
    result = stark_verifier.verify(
        proof,
        transition_constraints,
        boundary_constraints,
        aet.shape[1],
        aet.shape[0],
    )

    assert result, "invalid proof"
