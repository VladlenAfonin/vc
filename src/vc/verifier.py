from __future__ import annotations

import dataclasses
import logging

import galois

from vc import domain
from vc.constants import LOGGER_FRI, MEKRLE_HASH_ALGORITHM
from vc.merkle import MerkleTree
from vc.parameters import FriParameters
from vc.proof import Proof
from vc.sponge import Sponge


logger = logging.getLogger(LOGGER_FRI)


@dataclasses.dataclass(init=False, slots=True)
class Verifier:
    """FRI Verifier."""

    @dataclasses.dataclass(slots=True)
    class State:
        """FRI Verifier state."""

        sponge: Sponge
        """Sponge."""
        initial_evaluation_domain: galois.Array
        """Initial evaluation domain."""

    _parameters: FriParameters
    _state: Verifier.State

    def __init__(self, parameters: FriParameters) -> None:
        logger.debug(f'Verifier.init(): begin')

        self._parameters = parameters
        logger.debug(f'Verifier.init(): {self._parameters = }')
        sponge = Sponge(parameters.field)
        self._state = Verifier.State(
            sponge=sponge,
            initial_evaluation_domain=parameters.initial_evaluation_domain)
        logger.debug(f'Verifier.init(): {self._state = }')

        logger.debug(f'Verifier.init(): end')

    def verify(self, proof: Proof) -> bool:
        logger.debug(f'Verifier.verify(): begin')
        logger.debug(f'Verifier.verify(): {proof = }')

        logger.debug(f'Verifier.verify(): check polynomial degree')
        logger.debug(f'Verifier.verify(): {proof.final_polynomial.degree + 1 = }')
        logger.debug(f'Verifier.verify(): {self._parameters.final_coefficients_length = }')
        if proof.final_polynomial.degree + 1 > self._parameters.final_coefficients_length:
            return False

        logger.debug(f'Verifier.verify(): check merkle trees in round proofs')

        # Create an empty Merkle tree used only for verification.
        merkle_tree = MerkleTree(algorithm=MEKRLE_HASH_ALGORITHM)
        for i, (merkle_root, round_proof) in enumerate(zip(proof.merkle_roots, proof.round_proofs)):
            logger.debug(f'Verifier.verify(): begin merkle tree check round {i = }')
            logger.debug(f'Verifier.verify(): {merkle_root = }')
            logger.debug(f'Verifier.verify(): {round_proof = }')

            merkle_result = merkle_tree.verify_field_elements(
                round_proof.evaluations,
                merkle_root,
                round_proof.proofs)
            logger.debug(f'Verifier.verify(): {merkle_result = }')

            logger.debug(f'Verifier.verify(): end merkle tree check round {i = }')

            if not merkle_result:
                logger.debug(f'Verifier.verify(): end')
                return False

        logger.debug(f'Verifier.verify(): verify folds')
        logger.debug(f'Verifier.verify(): get folding randomness array')
        folding_randomness_array = []
        for i in range(self._parameters.number_of_rounds + 1):
            self._state.sponge.absorb(proof.merkle_roots[i])
            folding_randomness_array.append(self._state.sponge.squeeze_field_element())
        logger.debug(f'Verifier.verify(): {folding_randomness_array = }')

        logger.debug(f'Verifier.verify(): get query indices')
        query_indices_range = self._parameters.initial_evaluation_domain_length
        logger.debug(f'Verifier.verify(): {query_indices_range = }')
        query_indices = self._state.sponge.squeeze_indices(
            self._parameters.number_of_repetitions,
            query_indices_range)
        logger.debug(f'Verifier.verify(): {query_indices = }')

        evaluation_domain = self._parameters.initial_evaluation_domain
        folded_values = None
        for i in range(self._parameters.number_of_rounds + 1):
            logger.debug(f'Verifier.verify(): begin iteration {i = }')

            # TODO: Add intermediate consistency checks.
            # if folded_values is not None:
            #     if not all(folded_value == evaluation for folded_value, evaluation in zip([folded_values], proof.round_proofs[i].evaluations)):
            #         return False

            xs = evaluation_domain[query_indices]
            logger.debug(f'Verifier.verify(): {xs = }')
            ys = proof.round_proofs[i].evaluations
            logger.debug(f'Verifier.verify(): {ys = }')

            folded_polynomial = galois.lagrange_poly(xs, ys)
            folded_values = folded_polynomial(folding_randomness_array[i])
            logger.debug(f'Verifier.verify(): {folded_values = }')

            # folded_values = []
            # for x, y in zip(xs, ys):
            #     logger.debug(f'Verifier.verify(): {x = }')
            #     folded_values.append(galois.lagrange_poly(self._parameters.field(x), self._parameters.field(y))(folding_randomness_array[i]))
            # logger.debug(f'Verifier.verify(): {folded_values = }')

            query_indices_range //= self._parameters.folding_factor
            logger.debug(f'Verifier.verify(): {query_indices_range = }')
            query_indices = list(set(i % query_indices_range for i in query_indices))
            logger.debug(f'Verifier.verify(): {query_indices = }')
            evaluation_domain = domain.fold(evaluation_domain, self._parameters.folding_factor)

            logger.debug(f'Verifier.verify(): end iteration {i = }')

        final_polynomial_answers = proof.final_polynomial(evaluation_domain[query_indices])
        logger.debug(f'Verifier.verify(): {final_polynomial_answers = }')

        logger.debug(f'Verifier.verify(): end')
        return True
