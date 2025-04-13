import pytest
import galois

from vc.constants import FIELD_GOLDILOCKS
from vc.fri.parameters import FriParameters
from vc.fri.prover import FriProver
from vc.fri.verifier import FriVerifier


TEST_FIELD = FIELD_GOLDILOCKS


def test_fri_pow2() -> None:
    initial_coefficients_length_log = 3

    fri_parameters = FriParameters(
        folding_factor_log=1,
        expansion_factor_log=1,
        security_level_bits=5,
        final_coefficients_length_log=0,
        initial_coefficients_length_log=initial_coefficients_length_log,
        field=TEST_FIELD,
    )

    prover = FriProver(fri_parameters)
    verifier = FriVerifier(fri_parameters)

    f = galois.Poly.Random(
        (1 << initial_coefficients_length_log) - 1,
        field=TEST_FIELD,
        seed=42,
    )

    proof = prover.prove(f)
    result = verifier.verify(proof)

    assert result


@pytest.mark.parametrize(
    "initial_coefficients_length_log, polynomial_degree, seed",
    [
        (3, 6, 43),
        (4, 6, 44),
        (5, 6, 45),
        (6, 6, 46),
    ],
)
def test_fri_not_pow2(
    initial_coefficients_length_log: int,
    polynomial_degree: int,
    seed: int,
) -> None:
    fri_parameters = FriParameters(
        folding_factor_log=1,
        expansion_factor_log=1,
        security_level_bits=5,
        final_coefficients_length_log=0,
        initial_coefficients_length_log=initial_coefficients_length_log,
        field=TEST_FIELD,
    )

    prover = FriProver(fri_parameters)
    verifier = FriVerifier(fri_parameters)

    f = galois.Poly.Random(polynomial_degree, field=TEST_FIELD, seed=seed)

    proof = prover.prove(f)
    result = verifier.verify(proof)

    assert result
