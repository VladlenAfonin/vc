from __future__ import annotations

import dataclasses
import logging
import typing

import galois
import numpy

from vc.constants import LOGGER_FRI
from vc.fold import extend_indices, fold_domain, fold_sort_generate
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
        """Verify proof.

        :param proof: Proof for some polynomial.
        :type proof: Proof
        :return: ``True`` if ``proof`` is valid. ``False`` otherwise.
        :rtype: bool
        """

        if proof.final_polynomial.degree + 1 > self._parameters.final_coefficients_length:
            logger.error(f'invalid final polynomial degree')
            return False

        for merkle_root, round_proof in zip(proof.merkle_roots, proof.round_proofs):
            if not MerkleTree.verify_bulk(round_proof.stacked_evaluations, merkle_root, round_proof.proofs):
                logger.error(f'invalid merkle tree proofs')
                return False

        folding_randomness_array: typing.List[galois.Array] = []
        for i in range(self._parameters.number_of_rounds + 1):
            self._state.sponge.absorb(proof.merkle_roots[i])
            folding_randomness_array.append(self._state.sponge.squeeze_field_element())

        evaluation_domain = self._parameters.initial_evaluation_domain
        evaluation_domain_length = self._parameters.initial_evaluation_domain_length

        query_indices_range = \
            self._parameters.initial_evaluation_domain_length // \
            self._parameters.folding_factor
        query_indices = self._state.sponge.squeeze_indices(
            self._parameters.number_of_repetitions,
            query_indices_range)
        extended_indices = extend_indices(
            query_indices,
            evaluation_domain_length,
            self._parameters.folding_factor)

        unordered_folded_values = None
        check_indices = None
        folded_values = None
        for i in range(self._parameters.number_of_rounds + 1):
            if check_indices is not None:
                assert folded_values is not None

                for j, se in enumerate(proof.round_proofs[i].stacked_evaluations):
                    temp_result = folded_values[j] == se[check_indices[j]]
                    if not temp_result:
                        logger.error(f'consistency check failed')
                        return False

            unordered_folded_values = []
            for indices, ys in zip(extended_indices, proof.round_proofs[i].stacked_evaluations):
                xs = evaluation_domain[indices]
                folded_polynomial = galois.lagrange_poly(xs, ys)
                unordered_folded_values.append(folded_polynomial(folding_randomness_array[i]))

            query_indices_range //= self._parameters.folding_factor
            query_indices, check_indices, folded_values = fold_sort_generate(
                query_indices, query_indices_range, unordered_folded_values)

            evaluation_domain_length //= self._parameters.folding_factor
            evaluation_domain = fold_domain(evaluation_domain, self._parameters.folding_factor)

            extended_indices = extend_indices(
                query_indices,
                evaluation_domain_length,
                self._parameters.folding_factor)

        # TODO: Refactor without Numpy.
        query_indices = numpy.array(query_indices)
        check_indices = numpy.array(check_indices)

        final_polynomial_answers = proof.final_polynomial(
            evaluation_domain[list(query_indices + query_indices_range * check_indices)])
        final_check = all(folded_values == final_polynomial_answers)

        if not final_check:
            logger.error(f'final check failed')

        return final_check
