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
        n_registers: int,
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

        # INFO: This also provides the number of boundary quotients.
        boundary_zerofiers = self.get_boundary_zerofiers(
            n_registers,
            boundary_constraints,
        )

        n_weights = len(transition_constraints) + len(boundary_zerofiers)
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

    @logging_mark(logger)
    def get_boundary_zerofiers(
        self,
        n_registers,
        boundary_constraints: typing.List[BoundaryConstraint],
    ) -> typing.List[galois.Poly]:
        zerofiers = []
        for j in range(n_registers):
            current_boundary_constraints = [x for x in boundary_constraints if x.j == j]

            xs = [self.state.omicron**x.i for x in current_boundary_constraints]

            zerofier = galois.Poly.Roots(xs, field=self.state.fri_parameters.field)
            zerofiers.append(zerofier)

        return zerofiers
