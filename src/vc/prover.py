from __future__ import annotations

import dataclasses
import logging
import typing

import galois
import pymerkle

from vc import polynomial, domain
from vc.base import is_pow2
from vc.proof import ProofStream
from vc.merkle import MerkleTree
from vc.parameters import FriParameters


logger = logging.getLogger('vc')


@dataclasses.dataclass(init=False, slots=True)
class Prover:
    """FRI Prover."""

    HASH_ALGORITHM = 'sha3_256'
    """Hash algorithm to use in Merkle trees."""

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
        proof_stream: ProofStream
        """Proof stream to be filled."""
        merkle_trees: typing.List[MerkleTree]
        """Merkle trees for all rounds."""

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

            self.proof_stream = ProofStream(field)
            logger.debug(f'Prover.State.init(): initialized empty ProofStream')

            self.merkle_trees = []
            logger.debug(f'Prover.State.init(): initialized empty merkle tree array')

            logger.debug('Prover.State.init(): end')

    _options: FriParameters
    """Public Prover options."""
    _state: Prover.State | None = None
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

    def _get_number_of_rounds(self, initial_domain_length: int) -> int:
        logger.debug(f'Prover._get_number_of_rounds(): begin')

        assert is_pow2(initial_domain_length), 'initial domain length must be a power of two'

        current_domain_length = initial_domain_length
        accumulator: int = 0
        while self._options.expansion_factor < current_domain_length:
            logger.debug(f'Prover._get_number_of_rounds(): current {accumulator = }')
            current_domain_length //= self._options.folding_factor
            accumulator += 1

        logger.debug(f'Prover._get_number_of_rounds(): final {accumulator = }')
        logger.debug(f'Prover._get_number_of_rounds(): end')

        return accumulator

    def prove(self, f: galois.Poly) -> ProofStream:
        """Prover that polynomial f is close to RS-code.

        :param f: Polynomial to be proven.
        """

        logger.debug(f'Prover.prove(): begin')

        logger.debug(f'Prover.prove(): create prover state')
        self._state = Prover.State(f, self._options)

        logger.debug(f'Prover.prove(): compute initial evaluations')
        evaluations = self._state.polynomial(self._state.evaluation_domain)
        logger.debug(f'Prover.prove(): {evaluations = }')

        logger.debug(f'Prover.prove(): create merkle tree')
        merkle_tree = MerkleTree(algorithm=self.HASH_ALGORITHM)
        merkle_tree.append_field_elements(evaluations)

        merkle_root = merkle_tree.get_root()

        logger.debug(f'Prover.prove(): push root into proof stream')
        self._state.proof_stream.push(merkle_root)

        logger.debug(f'Prover.prove(): append merkle tree to the list of merkle trees')
        self._state.merkle_trees.append(merkle_tree)

        logger.debug(f'Prover.prove(): get number of rounds')
        number_of_rounds = self._get_number_of_rounds(self._state.evaluation_domain.size)

        for i in range(number_of_rounds):
            logger.debug(f'Prover.prove(): commit round {i + 1}')
            self._round()

        proofs = []

        logger.debug(f'Prover.prove(): sample query indices')
        indices_range = self._options.initial_coefficients_length
        logger.debug(f'Prover.prove(): {indices_range = }')
        indices = self._state.proof_stream.sample_indices_prover(
            self._options.number_of_repetitions,
            indices_range)
        logger.debug(f'Prover.prove(): {indices = }')

        logger.debug(f'Prover.prove(): prove first round')
        round_proofs = self._state.merkle_trees[0].prove_indices(indices)
        proofs.append(round_proofs)

        for i in range(number_of_rounds):
            logger.debug(f'Prover.prove(): query round {i + 1}')

            indices_range //= self._options.folding_factor
            logger.debug(f'Prover.prove(): {indices_range = }')

            indices = list(set(i % indices_range for i in indices))
            logger.debug(f'Prover.prove(): {indices = }')

            round_proofs = self._state.merkle_trees[i + 1].prove_indices(indices)
            proofs.append(round_proofs)

        logger.debug(f'Prover.prove(): end')

    def _round(self) -> None:
        logger.debug(f'Prover._round(): begin')

        assert self._state is not None, 'state is not initialized'

        verifier_randomness = self._state.proof_stream.sample_field_prover()
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

        new_evaluations = new_polynomial(new_evaluation_domain)
        logger.debug(f'Prover._round(): {new_evaluations = }')

        logger.debug(f'Prover._round(): create merkle tree')
        merkle_tree = MerkleTree(algorithm=self.HASH_ALGORITHM)
        merkle_tree.append_field_elements(new_evaluations)

        logger.debug(f'Prover._round(): append merkle tree to the list of merkle trees')
        self._state.merkle_trees.append(merkle_tree)

        merkle_root = merkle_tree.get_root()

        logger.debug(f'Prover._round(): push root into proof stream')
        self._state.proof_stream.push(merkle_root)

        logger.debug(f'Prover._round(): set new polynomial')
        self._state.polynomial = new_polynomial
        logger.debug(f'Prover._round(): set new evaluation domain')
        self._state.evaluation_domain = new_evaluation_domain

        logger.debug(f'Prover._round(): end')
