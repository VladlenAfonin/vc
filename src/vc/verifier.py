from __future__ import annotations

import dataclasses
import logging
import typing

import galois
import numpy

from vc.constants import LOGGER_FRI, MEKRLE_HASH_ALGORITHM
from vc.fold import fold_domain, fold_indices
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

        query_indices_range = self._parameters.initial_evaluation_domain_length // self._parameters.folding_factor
        query_indices = self._state.sponge.squeeze_indices(
            self._parameters.number_of_repetitions,
            query_indices_range)
        extended_indices = self._extend_indices(query_indices, evaluation_domain_length)

        # logger.debug(f'{query_indices = }')
        # logger.debug(f'{extended_indices = }')

        unordered_folded_values = None
        check_indices = None
        folded_values = None
        for i in range(self._parameters.number_of_rounds + 1):
            if check_indices is not None:
                assert folded_values is not None

                # logger.debug(f'{folded_values = }')
                # logger.debug(f'{proof.round_proofs[i].stacked_evaluations = }')
                # logger.debug(f'{check_indices = }')

                for j, se in enumerate(proof.round_proofs[i].stacked_evaluations):
                    temp_result = folded_values[j] == se[check_indices[j]]
                    logger.debug(f'{temp_result = }')

            unordered_folded_values = []
            for indices, ys in zip(extended_indices, proof.round_proofs[i].stacked_evaluations):
                xs = evaluation_domain[indices]
                # logger.debug(f'{indices = }')
                # logger.debug(f'{xs = }')
                # logger.debug(f'{ys = }')
                # logger.debug(f'{folding_randomness_array[i] = }')
                folded_polynomial = galois.lagrange_poly(xs, ys)
                unordered_folded_values.append(folded_polynomial(folding_randomness_array[i]))

            query_indices_range //= self._parameters.folding_factor
            temp_sorted_array = sorted(
                # |-Next query index,        |-Check index,              |-Value.
                # V                          V                           V
                ((ids % query_indices_range, ids // query_indices_range, ufv)
                    for ids, ufv in zip(query_indices, unordered_folded_values)),
                # Sort by new query index.
                key=lambda x: x[0])
            # logger.debug(f'{temp_sorted_array = }')
            query_indices, check_indices, folded_values = zip(*temp_sorted_array)
            query_indices = numpy.unique_values(query_indices)

            logger.debug(f'{query_indices = }')
            logger.debug(f'{check_indices = }')
            logger.debug(f'{folded_values = }')

            # query_indices = fold_indices(query_indices, query_indices_range)

            evaluation_domain_length //= self._parameters.folding_factor
            evaluation_domain = fold_domain(evaluation_domain, self._parameters.folding_factor)

            extended_indices = self._extend_indices(query_indices, evaluation_domain_length)

            logger.debug(f'=========================================================')

            # logger.debug(f'{query_indices = }')
            # logger.debug(f'{extended_indices = }')

        final_polynomial_answers = proof.final_polynomial(evaluation_domain[query_indices])
        final_check = all(unordered_folded_values == final_polynomial_answers)

        # logger.debug(f'{final_polynomial_answers = }')
        # logger.debug(f'{unordered_folded_values = }')

        # if not final_check:
        #     logger.error(f'final check failed')

        # return final_check

        return True

    def _extend_indices(self, indices: typing.List[int], domain_length: int) -> typing.List[typing.List[int]]:
        """Extend indices to be used for interpolation of stacked evaluations.

        :param indices: Indices corresponding to stacked evaluations rows.
        :type indices: typing.List[int]
        :param domain_length: Domain length.
        :type domain_length: int
        :return: Extended indices.
        :rtype: typing.List[typing.List[int]]

        Examples
        --------

        .. code:: python
            # Say, folding_factor = 2.
            assert all([[0, 8], [2, 10]] == self._extend_indices([0, 2], 8))
        """

        return [
            [
                i + j*domain_length//self._parameters.folding_factor
                for j in range(self._parameters.folding_factor)
            ] for i in indices
        ]
