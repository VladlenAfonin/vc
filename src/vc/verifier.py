from __future__ import annotations

import dataclasses
import logging
import typing

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
        self._parameters = parameters
        sponge = Sponge(parameters.field)
        self._state = Verifier.State(
            sponge=sponge,
            initial_evaluation_domain=parameters.initial_evaluation_domain)

    def verify(self, proof: Proof) -> bool:
        if proof.final_polynomial.degree + 1 > self._parameters.final_coefficients_length:
            logger.error(f'invalid final polynomial degree')
            return False

        for merkle_root, round_proof in zip(proof.merkle_roots, proof.round_proofs):
            if not MerkleTree.verify_bulk(round_proof.evaluations, merkle_root, round_proof.proofs):
                logger.error(f'invalid merkle tree proofs')
                return False

        folding_randomness_array = []
        for i in range(self._parameters.number_of_rounds + 1):
            self._state.sponge.absorb(proof.merkle_roots[i])
            folding_randomness_array.append(self._state.sponge.squeeze_field_element())

        query_indices_range = self._parameters.initial_evaluation_domain_length // self._parameters.folding_factor
        query_indices = self._state.sponge.squeeze_indices(
            self._parameters.number_of_repetitions,
            query_indices_range)
        extended_indices = self._extend_indices(query_indices, self._parameters.folding_factor * query_indices_range)
        logger.debug(f'{extended_indices = }')

        evaluation_domain = self._parameters.initial_evaluation_domain
        folded_values = None
        for i in range(self._parameters.number_of_rounds + 1):
            # TODO: Add intermediate consistency checks.

            folded_values = []
            for indices, ys in zip(extended_indices, proof.round_proofs[i].evaluations):
                xs = evaluation_domain[indices]
                folded_polynomial = galois.lagrange_poly(xs, ys)
                folded_values.append(folded_polynomial(folding_randomness_array[i]))
            logger.debug(f'{folded_values = }')

            query_indices_range //= self._parameters.folding_factor
            query_indices = list(set(j % query_indices_range for j in query_indices))
            logger.debug(f'{query_indices = }')
            evaluation_domain = domain.fold(evaluation_domain, self._parameters.folding_factor)
            extended_indices = self._extend_indices(query_indices, self._parameters.folding_factor * query_indices_range)
            logger.debug(f'{extended_indices = }')

        final_polynomial_answers = proof.final_polynomial(evaluation_domain[query_indices])
        logger.debug(f'{final_polynomial_answers = }')
        return True

    def _extend_indices(self, indices: typing.List[int], indices_range) -> typing.List[typing.List[int]]:
        return [
                [
                    i + j*indices_range//self._parameters.folding_factor
                    for j in range(self._parameters.folding_factor)
                ] for i in indices
            ]
