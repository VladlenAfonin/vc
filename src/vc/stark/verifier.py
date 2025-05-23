import dataclasses
import logging
import typing

import galois
import numpy

from vc.fri.fold import extend_indices, stack
from vc.merkle import MerkleTree
from vc.polynomial import MPoly
from vc.sponge import Sponge
from vc.stark.boundary import Boundaries, BoundaryConstraint
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
        boundaries = self.get_boundaries(
            n_registers,
            boundary_constraints,
        )

        n_weights = len(transition_constraints) + len(boundaries.zerofiers)
        weights = [sponge.squeeze_field_element() for _ in range(n_weights)]

        # INFO: Verify FRI proof for the combination polynomial.
        if not self.state.fri_verifier.verify(
            proof.combination_polynomial_proof,
            sponge,
        ):
            logger.error("invalid combination polynomial proof")
            return False

        extended_indices = extend_indices(
            proof.combination_polynomial_proof.round_proofs[0].indices,
            self.state.fri_parameters.initial_coefficients_length
            // self.state.fri_parameters.folding_factor,
            self.state.fri_parameters.folding_factor,
        )

        extended_xs = stack(
            self.state.fri_parameters.initial_evaluation_domain[extended_indices],
            self.state.fri_parameters.folding_factor,
        )

        for bq_stacked_evaluations, bz, bp in zip(
            proof.bq_stacked_evaluations,
            boundaries.zerofiers,
            boundaries.polynomials,
        ):
            trace_polynomial_stacked_evaluations = bq_stacked_evaluations * bz(
                extended_xs
            ) + bp(extended_xs)

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

    @logging_mark(logger)
    def get_boundaries(
        self,
        n_registers: int,
        boundary_constraints: typing.List[BoundaryConstraint],
    ) -> Boundaries:
        polynomials = []
        zerofiers = []

        for j in range(n_registers):
            current_boundary_constraints = [
                bc for bc in boundary_constraints if bc.j == j
            ]

            xs = self.state.fri_parameters.field(
                [self.state.omicron**x.i for x in current_boundary_constraints]
            )
            ys = self.state.fri_parameters.field(
                [bc.value for bc in current_boundary_constraints]
            )

            zerofiers.append(
                galois.Poly.Roots(xs, field=self.state.fri_parameters.field)
            )
            polynomials.append(galois.lagrange_poly(xs, ys))

        return Boundaries(
            constraints=boundary_constraints,
            polynomials=polynomials,
            zerofiers=zerofiers,
        )
