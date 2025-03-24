import math
import pytest

from vc.base import get_nearest_power_of_two
from vc.fri.parameters import FriParameters
from vc.fri.prover import FriProver
from vc.stark.airs.fibonacci import get_aet
from vc.stark.parameters import StarkParameters
from vc.stark.prover import StarkProver
from vc.constants import FIELD_GOLDILOCKS


TEST_FIELD = FIELD_GOLDILOCKS


def get_test_stark_prover(n: int) -> StarkProver:
    expansion_factor_log = 1
    expansion_factor = 1 << expansion_factor_log

    aet_height = get_nearest_power_of_two(n)
    aet_height_log = math.ceil(math.log2(aet_height))

    omega_domain_len_log = aet_height + expansion_factor_log
    omega = TEST_FIELD.primitive_root_of_unity(1 << omega_domain_len_log)
    omicron = omega**expansion_factor

    stark_parameters = StarkParameters(omega, omicron)
    fri_parameters = FriParameters(
        folding_factor_log=1,
        expansion_factor_log=expansion_factor_log,
        security_level_bits=5,
        initial_coefficients_length_log=aet_height_log + expansion_factor_log,
        final_coefficients_length_log=0,
        field=TEST_FIELD,
    )
    fri_prover = FriProver(fri_parameters)

    stark_prover_state = StarkProver.StarkProverState(
        field=TEST_FIELD,
        omicron=omicron,
        aet_height=n,
    )
    return StarkProver(
        stark_parameters=stark_parameters,
        fri_prover=fri_prover,
        state=stark_prover_state,
    )


def test_get_trace_polynomials():
    stark_prover = get_test_stark_prover(4)
    aet = get_aet(4)
    trace_polynomials = stark_prover.get_trace_polynomials(aet)

    # Test first row of the AET.
    assert trace_polynomials[0](TEST_FIELD(1)) == 0
    assert trace_polynomials[1](TEST_FIELD(1)) == 1

    # Test last row of the AET.
    assert trace_polynomials[0](stark_prover.stark_parameters.omicron**3) == 2
    assert trace_polynomials[1](stark_prover.stark_parameters.omicron**3) == 3
