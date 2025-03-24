from __future__ import annotations

import dataclasses
import logging
import typing

import galois

from vc.base import is_pow2
from vc.constants import LOGGER_FRI
from vc.fri.fold import fold_domain, fold_indices, fold_polynomial, stack
from vc.fri.proof import FriProof, RoundProof
from vc.sponge import Sponge
from vc.merkle import MerkleTree
from vc.fri.parameters import FriParameters


logger = logging.getLogger(LOGGER_FRI)


@dataclasses.dataclass(init=False, slots=True)
class FriProver:
    """FRI Prover."""

    @dataclasses.dataclass(init=False, slots=True)
    class State:
        """Current prover state."""

        evaluation_domain: galois.FieldArray
        """Current evaluation domain."""
        omega: galois.FieldArray
        """Current domain generator. This is a root of unity."""
        offset: galois.FieldArray
        """Domain offset. This is typically F* generator."""
        polynomial: galois.Poly
        """Current polynomial."""
        sponge: Sponge
        """Proof stream to be filled."""
        merkle_trees: typing.List[MerkleTree]
        """Merkle trees for all rounds."""
        evaluations: typing.List[galois.FieldArray]
        """Evaluations of the current polynomial over current domain."""
        merkle_roots: typing.List[bytes]
        """Merkle root of current evaluations."""

        def __init__(self, f: galois.Poly, options: FriParameters) -> None:
            coefficients_length = f.degree + 1
            assert is_pow2(
                coefficients_length
            ), "number of coefficients in polynomial must be a power of two"

            self.polynomial = f
            field = f.field

            self.omega = options.omega
            self.offset = options.offset
            self.evaluation_domain = options.initial_evaluation_domain
            self.sponge = Sponge(field)
            self.merkle_trees = []
            self.merkle_roots = []
            self.evaluations = []

    _parameters: FriParameters
    """Public Prover options."""
    _state: FriProver.State | None
    """Internal Prover state."""

    def __init__(self, parameters: FriParameters) -> None:
        """Initialize new Prover.

        :param options: Public prover options.
        """

        assert parameters is not None, "options cannot be None"

        self._parameters = parameters
        self._state = None

    def prove(self, f: galois.Poly) -> FriProof:
        """Prover that polynomial f is close to RS-code.

        :param f: Polynomial to be proven.
        """

        self._state = FriProver.State(f, self._parameters)

        initial_round_evaluations = self._state.polynomial(
            self._state.evaluation_domain
        )
        stacked_evaluations = stack(
            initial_round_evaluations,
            self._parameters.folding_factor,
        )
        self._state.evaluations.append(stacked_evaluations)

        merkle_tree = MerkleTree()
        merkle_tree.append_bulk(stacked_evaluations)
        merkle_root = merkle_tree.get_root()

        self._state.sponge.absorb(merkle_root)
        self._state.merkle_roots.append(merkle_root)
        self._state.merkle_trees.append(merkle_tree)

        for i in range(self._parameters.number_of_rounds):
            self._round()

        round_proofs: typing.List[RoundProof] = []

        query_indices_range = (
            self._parameters.initial_evaluation_domain_length
            // self._parameters.folding_factor
        )
        query_indices = self._state.sponge.squeeze_indices(
            self._parameters.number_of_repetitions,
            query_indices_range,
        )
        query_evaluations = self._state.evaluations[0][query_indices]

        merkle_proofs = self._state.merkle_trees[0].prove_bulk(query_indices)
        round_proofs.append(RoundProof(query_evaluations, merkle_proofs))

        for i in range(self._parameters.number_of_rounds):
            query_indices_range //= self._parameters.folding_factor
            query_indices = fold_indices(query_indices, query_indices_range)
            query_evaluations = self._state.evaluations[i + 1][query_indices]

            merkle_proofs = self._state.merkle_trees[i + 1].prove_bulk(query_indices)
            round_proofs.append(RoundProof(query_evaluations, merkle_proofs))

        # The final polynomial does not need any proofs.
        final_randomness = self._state.sponge.squeeze_field_element()
        final_polynomial = fold_polynomial(
            self._state.polynomial,
            final_randomness,
            self._parameters.folding_factor,
        )

        result = FriProof(round_proofs, self._state.merkle_roots, final_polynomial)

        return result

    def _round(self) -> None:
        verifier_randomness = self._state.sponge.squeeze_field_element()
        new_polynomial = fold_polynomial(
            self._state.polynomial,
            verifier_randomness,
            self._parameters.folding_factor,
        )
        new_evaluation_domain = fold_domain(
            self._state.evaluation_domain,
            self._parameters.folding_factor,
        )

        new_round_evaluations = new_polynomial(new_evaluation_domain)
        stacked_evaluations = stack(
            new_round_evaluations,
            self._parameters.folding_factor,
        )
        self._state.evaluations.append(stacked_evaluations)

        merkle_tree = MerkleTree()
        merkle_tree.append_bulk(stacked_evaluations)
        merkle_root = merkle_tree.get_root()

        self._state.sponge.absorb(merkle_root)
        self._state.merkle_roots.append(merkle_root)
        self._state.merkle_trees.append(merkle_tree)

        self._state.polynomial = new_polynomial
        self._state.evaluation_domain = new_evaluation_domain
