from __future__ import annotations

import dataclasses
import logging
import typing

import galois

from vc import polynomial, domain
from vc.base import is_pow2
from vc.constants import MEKRLE_HASH_ALGORITHM, LOGGER_FRI
from vc.proof import Proof, RoundProof
from vc.sponge import Sponge
from vc.merkle import MerkleTree
from vc.parameters import FriParameters


logger = logging.getLogger(LOGGER_FRI)


@dataclasses.dataclass(init=False, slots=True)
class Prover:
    """FRI Prover."""

    @dataclasses.dataclass(init=False, slots=True)
    class State:
        """Current prover state."""
        evaluation_domain: galois.Array
        """Current evaluation domain."""
        domain_generator: galois.Array
        """Current domain generator. This is a root of unity."""
        offset: galois.Array
        """Domain offset. This is typically F* generator."""
        polynomial: galois.Poly
        """Current polynomial."""
        sponge: Sponge
        """Proof stream to be filled."""
        merkle_trees: typing.List[MerkleTree]
        """Merkle trees for all rounds."""
        evaluations: typing.List[galois.Array]
        """Evaluations of the current polynomial over current domain."""
        merkle_roots: typing.List[bytes]
        """Merkle root of current evaluations."""

        def __init__(self, f: galois.Poly, options: FriParameters) -> None:
            logger.debug('Prover.State.init(): begin')

            coefficients_length = f.degree + 1
            logger.debug(f'Prover.State.init(): {coefficients_length = }')

            assert is_pow2(coefficients_length), 'number of coefficients in polynomial must be a power of two'

            self.polynomial = f
            logger.debug(f'Prover.State.init(): {f = }')

            field = f.field

            domain_length = coefficients_length * options.expansion_factor
            logger.debug(f'Prover.State.init(): {domain_length = }')

            self.domain_generator = field.primitive_root_of_unity(domain_length)
            logger.debug(f'Prover.State.init(): {self.domain_generator = }')

            self.offset = field.primitive_element
            logger.debug(f'Prover.State.init(): {self.offset = }')

            self.evaluation_domain = field([self.offset * (self.domain_generator ** i) for i in range(domain_length)])
            logger.debug(f'Prover.State.init(): {self.evaluation_domain = }')

            self.sponge = Sponge(field)
            logger.debug(f'Prover.State.init(): initialized empty Sponge')

            self.merkle_trees = []
            logger.debug(f'Prover.State.init(): initialized empty merkle tree array')

            self.merkle_roots = []
            logger.debug(f'Prover.State.init(): initialized empty merkle roots array')

            self.evaluations = []
            logger.debug(f'Prover.State.init(): initialized empty evaluations array')

            logger.debug('Prover.State.init(): end')

    _options: FriParameters
    """Public Prover options."""
    _state: Prover.State | None
    """Internal Prover state."""

    def __init__(self, options: FriParameters) -> None:
        """Initialize new Prover.

        :param options: Public prover options.
        """

        logger.debug(f'Prover.init(): begin')

        assert options is not None, 'options cannot be None'

        self._options = options
        self._state = None

        logger.debug(f'Prover.init(): end')

    def prove(self, f: galois.Poly) -> Proof:
        """Prover that polynomial f is close to RS-code.

        :param f: Polynomial to be proven.
        """

        logger.debug(f'Prover.prove(): begin')

        logger.debug(f'Prover.prove(): create prover state')
        self._state = Prover.State(f, self._options)

        logger.debug(f'Prover.prove(): compute initial evaluations')
        initial_round_evaluations = self._state.polynomial(self._state.evaluation_domain)
        logger.debug(f'Prover.prove(): {initial_round_evaluations = }')

        logger.debug(f'Prover.prove(): append evaluations to evaluations list')
        self._state.evaluations.append(initial_round_evaluations)

        logger.debug(f'Prover.prove(): create merkle tree')
        merkle_tree = MerkleTree(algorithm=MEKRLE_HASH_ALGORITHM)
        merkle_tree.append_field_elements(initial_round_evaluations)

        merkle_root = merkle_tree.get_root()

        logger.debug(f'Prover.prove(): append initial merkle root to merkle roots list')
        self._state.merkle_roots.append(merkle_root)

        logger.debug(f'Prover.prove(): push root into sponge')
        self._state.sponge.push(merkle_root)

        logger.debug(f'Prover.prove(): append merkle tree to the list of merkle trees')
        self._state.merkle_trees.append(merkle_tree)

        for i in range(self._options.number_of_rounds):
            logger.debug(f'Prover.prove(): commit round {i + 1}')
            self._round()

        round_proofs: typing.List[RoundProof] = []

        logger.debug(f'Prover.prove(): sample query indices')
        query_indices_range = self._options.initial_coefficients_length
        logger.debug(f'Prover.prove(): {query_indices_range = }')
        query_indices = self._state.sponge.sample_indices_prover(
            self._options.number_of_repetitions,
            query_indices_range)
        logger.debug(f'Prover.prove(): {query_indices = }')

        logger.debug(f'Prover.prove(): get initial query evaluations')
        query_evaluations = self._state.evaluations[0][query_indices]
        logger.debug(f'Prover.prove(): {query_evaluations = }')

        logger.debug(f'Prover.prove(): prove first round')
        merkle_proofs = self._state.merkle_trees[0].prove_indices(query_indices)
        round_proofs.append(RoundProof(query_evaluations, merkle_proofs))

        # Create an empty Merkle tree used only for verification.
        verifier_merkle_tree = MerkleTree(algorithm=MEKRLE_HASH_ALGORITHM)
        assert verifier_merkle_tree.verify_field_elements(
            round_proofs[0].evaluations,
            self._state.merkle_roots[0],
            round_proofs[0].proofs), 'generated invalid merkle proof'

        for i in range(self._options.number_of_rounds):
            logger.debug(f'Prover.prove(): query round {i + 1}')

            query_indices_range //= self._options.folding_factor
            logger.debug(f'Prover.prove(): {query_indices_range = }')

            query_indices = list(set(i % query_indices_range for i in query_indices))
            logger.debug(f'Prover.prove(): {query_indices = }')

            logger.debug(f'Prover.prove(): get initial query evaluations')
            query_evaluations = self._state.evaluations[i + 1][query_indices]
            logger.debug(f'Prover.prove(): {query_evaluations = }')

            merkle_proofs = self._state.merkle_trees[i + 1].prove_indices(query_indices)
            round_proofs.append(RoundProof(query_evaluations, merkle_proofs))
            assert verifier_merkle_tree.verify_field_elements(
                round_proofs[i + 1].evaluations,
                self._state.merkle_roots[i + 1],
                round_proofs[i + 1].proofs), 'generated invalid merkle proof'

        # As far as I understand, final polynomial does not need any proofs.
        final_randomness = self._state.sponge.sample_field_prover()
        final_polynomial = polynomial.fold(
            self._state.polynomial,
            final_randomness,
            self._options.folding_factor)

        logger.debug(f'Prover.prove(): finalize the proof')
        result = Proof(round_proofs, self._state.merkle_roots, final_polynomial)

        logger.debug(f'Prover.prove(): end')

        return result

    def _round(self) -> None:
        logger.debug(f'Prover._round(): begin')

        assert self._state is not None, 'state is not initialized'

        verifier_randomness = self._state.sponge.sample_field_prover()
        logger.debug(f'Prover._round(): {verifier_randomness = }')

        new_polynomial = polynomial.fold(
            self._state.polynomial,
            verifier_randomness,
            self._options.folding_factor)
        logger.debug(f'Prover._round(): {new_polynomial = }')

        new_evaluation_domain = domain.fold(
            self._state.evaluation_domain,
            self._options.folding_factor)
        logger.debug(f'Prover._round(): {new_evaluation_domain = }')

        new_round_evaluations = new_polynomial(new_evaluation_domain)
        logger.debug(f'Prover._round(): {new_round_evaluations = }')

        logger.debug(f'Prover._round(): append evaluations to evaluations list')
        self._state.evaluations.append(new_round_evaluations)

        logger.debug(f'Prover._round(): create merkle tree')
        merkle_tree = MerkleTree(algorithm=MEKRLE_HASH_ALGORITHM)
        merkle_tree.append_field_elements(new_round_evaluations)

        logger.debug(f'Prover._round(): append merkle tree to the list of merkle trees')
        self._state.merkle_trees.append(merkle_tree)

        merkle_root = merkle_tree.get_root()

        logger.debug(f'Prover._round(): append merkle root to merkle roots list')
        self._state.merkle_roots.append(merkle_root)

        logger.debug(f'Prover._round(): push root into sponge')
        self._state.sponge.push(merkle_root)

        logger.debug(f'Prover._round(): set new polynomial')
        self._state.polynomial = new_polynomial
        logger.debug(f'Prover._round(): set new evaluation domain')
        self._state.evaluation_domain = new_evaluation_domain

        logger.debug(f'Prover._round(): end')
