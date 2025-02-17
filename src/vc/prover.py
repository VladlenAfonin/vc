from __future__ import annotations

import binascii
import dataclasses
import logging
import typing

import galois
from pymerkle import InmemoryTree
import pymerkle

from vc import polynomial, domain
from vc.base import is_pow2
from vc.proof import ProofStream
from vc.merkle import MerkleTree


logger = logging.getLogger(__name__)


@dataclasses.dataclass(init=False, slots=True)
class ProverOptions:
    """Prover options."""
    folding_factor: int
    """Folding factor."""
    expansion_factor: int
    """Expansion factor."""

    def __init__(self, folding_factor_log: int, expansion_factor_log: int) -> None:
        assert folding_factor_log > 0, 'folding factor log must be at least 1'
        assert expansion_factor_log > 0, 'expansion factor log must be at least 1'

        self.folding_factor = 1 << folding_factor_log
        self.expansion_factor = 1 << expansion_factor_log

        logger.info(f'ProverOption.init(): {self.folding_factor = }')
        logger.info(f'ProverOption.init(): {self.expansion_factor = }')


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
        proof_stream: ProofStream
        """Proof stream to be filled."""
        merkle_trees: typing.List[pymerkle.BaseMerkleTree]
        """Merkle trees for all rounds."""

        def __init__(self, f: galois.Poly, options: ProverOptions) -> None:
            logger.info('Prover.State.init(): begin')

            coefficients_length = f.degree + 1
            logger.info(f'Prover.State.init(): {coefficients_length = }')

            assert is_pow2(coefficients_length), 'number of coefficients in polynomial must be a power of two'

            field = f.field

            domain_length = coefficients_length * options.expansion_factor
            logger.info(f'Prover.State.init(): {domain_length = }')

            self.domain_generator = field.primitive_root_of_unity(domain_length)
            logger.info(f'Prover.State.init(): {self.domain_generator = }')

            self.offset = field.primitive_element
            logger.info(f'Prover.State.init(): {self.offset = }')

            self.evaluation_domain = field([self.offset * (self.domain_generator ** i) for i in range(domain_length)])
            logger.info(f'Prover.State.init(): {self.evaluation_domain = }')

            self.proof_stream = ProofStream(field)
            logger.info(f'Prover.State.init(): initialized empty ProofStream')

            self.polynomial = f
            logger.info(f'Prover.State.init(): {f = }')

            self.merkle_trees = []
            logger.info(f'Prover.State.init(): initialized empty merkle tree array')

            logger.info('Prover.State.init(): end')

    _options: ProverOptions
    """Public Prover options."""
    _state: Prover.State | None = None
    """Internal Prover state."""

    def __init__(self, options: ProverOptions) -> None:
        """Initialize new Prover.

        :param options: Public prover options.
        """

        assert options is not None, 'options cannot be None'

        self._options = options
        self._state = None

    def prove(self, f: galois.Poly) -> ProofStream:
        """Prover that polynomial f is close to RS-code.
        
        :param f: Polynomial to be proven.
        """

        logger.info(f'Prover.prove(): begin')
        logger.info(f'Prover.prove(): create prover state')

        self._state = Prover.State(f, self._options)

        evaluations = self._state.polynomial(self._state.evaluation_domain)
        logger.info(f'Prover.prove(): {evaluations = }')

        logger.info(f'Prover.prove(): begin create merkle tree')
        merkle_tree = MerkleTree(algorithm='sha3_256')
        merkle_tree.append_field_elements(evaluations)

        merkle_root = merkle_tree.get_root()
        logger.info(f'Prover.prove(): {binascii.hexlify(merkle_root) = }')

        self._state.merkle_trees.append(merkle_tree)

        # TODO: Do first iteration here.
        # TODO: Get number of rounds.

        # self.round()
        logger.info(f'Prover.prove(): end')

    def round(self) -> None:
        logger.info(f'Prover.round(): begin')

        assert self._state is not None, 'state is not initialized'

        verifier_randomness = self._state.proof_stream.sample_field_prover()
        logger.info(f'Prover.round(): {verifier_randomness = }')

        new_polynomial = polynomial.fold(
            self._state.polynomial,
            verifier_randomness,
            self._options.folding_factor)
        logger.info(f'Prover.round(): {new_polynomial = }')

        new_evaluation_domain = domain.fold(
            self._state.evaluation_domain,
            self._options.folding_factor)
        logger.info(f'Prover.round(): {new_evaluation_domain = }')

        new_evaluations = new_polynomial(new_evaluation_domain)

        self._state.polynomial = new_polynomial
        self._state.evaluation_domain = new_evaluation_domain

        logger.info(f'Prover.round(): end')
