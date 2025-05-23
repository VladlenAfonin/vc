import dataclasses
import logging
import typing

import galois

from vc.merkle import MerkleTree
from vc.polynomial import MPoly
from vc.sponge import Sponge
from vc.stark.boundary import BoundaryConstraint
from vc.stark.proof import StarkProof
from vc.fri.verifier import FriVerifier
from vc.fri.parameters import FriParameters
from vc.logging import logging_mark


logger = logging.getLogger(__name__)


@dataclasses.dataclass(slots=True)
class StarkVerifier:
    @dataclasses.dataclass(slots=True)
    class StarkVerifierState:
        fri_verifier: FriVerifier
        fri_parameters: FriParameters
        omicron: galois.FieldArray

    state: StarkVerifierState

    @logging_mark(logger)
    def verify(
        self,
        proof: StarkProof,
        transition_constraints: typing.List[MPoly],
        boundary_constraints: typing.List[BoundaryConstraint],
    ) -> bool:
        sponge = Sponge(self.state.fri_parameters.field)

        # INFO: Verify boundary quotient openings.
        for stacked_evaluations, merkle_proofs, merkle_root in zip(
            proof.bq_stacked_evaluations,
            proof.bq_merkle_proofs,
            proof.bq_merkle_roots,
        ):
            merkle_verification_result = MerkleTree.verify_bulk(
                stacked_evaluations,
                merkle_root,
                merkle_proofs,
            )
            sponge.absorb(merkle_root)
            if not merkle_verification_result:
                logger.error("invalid merkle proof for boundary quotient")
                return False

        # ERROR: The second term is not correct. It must be n_unique(bq_js).
        n_weights = len(transition_constraints) + len(boundary_constraints)
        weights = [sponge.squeeze_field_element() for _ in range(n_weights)]

        # INFO: Verify FRI proof for the combination polynomial.
        if not self.state.fri_verifier.verify(
            proof.combination_polynomial_proof,
            sponge,
        ):
            logger.error("invalid combination polynomial proof")
            return False

        for bq_stacked_evaluations in proof.bq_stacked_evaluations:
            pass

        return True
