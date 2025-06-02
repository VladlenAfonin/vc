import dataclasses
import functools
import logging
import typing

import galois
import numpy

from vc.fri.fold import extend_indices
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
        n_rows,
    ) -> bool:
        sponge = Sponge(self.state.fri_parameters.field)

        # TODO: Refactor, move out to a function.
        # INFO: Verify boundary quotient openings.
        for stacked_evaluations, merkle_proofs, merkle_root in zip(
            proof.bq_current.stacked_evaluations,
            proof.bq_current.merkle_proofs,
            proof.bq_current.merkle_roots,
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

        # TODO: Refactor, move out to a function.
        # INFO: Verify boundary quotient openings.
        for stacked_evaluations, merkle_proofs, merkle_root in zip(
            proof.bq_next.stacked_evaluations,
            proof.bq_next.merkle_proofs,
            proof.bq_next.merkle_roots,
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
            self.state.fri_parameters.initial_evaluation_domain_length,
            self.state.fri_parameters.folding_factor,
        )

        extended_xs_current = self.state.fri_parameters.field(
            self.state.fri_parameters.initial_evaluation_domain[extended_indices],
        )
        extended_xs_next = extended_xs_current * self.state.omicron

        tracep_se_current = self.state.fri_parameters.field(
            numpy.stack(
                [
                    bq * bz(extended_xs_current) + bp(extended_xs_current)
                    for bq, bz, bp in zip(
                        proof.bq_current.stacked_evaluations,
                        boundaries.zerofiers,
                        boundaries.polynomials,
                    )
                ],
                axis=2,
            )
        )

        # print(tracep_se_current[:, :, 1])

        tracep_se_next = self.state.fri_parameters.field(
            numpy.stack(
                [
                    bq * bz(extended_xs_next) + bp(extended_xs_next)
                    for bq, bz, bp in zip(
                        proof.bq_next.stacked_evaluations,
                        boundaries.zerofiers,
                        boundaries.polynomials,
                    )
                ],
                axis=2,
            )
        )

        points = self.state.fri_parameters.field(
            numpy.concatenate([tracep_se_current, tracep_se_next], axis=2)
        )

        omicron_zerofier = self.get_transition_zerofier(n_rows)
        tq_ses = [
            tc.evalv(points) // omicron_zerofier(extended_xs_current)
            for tc in transition_constraints
        ]

        # print(tq_ses[0])

        commited_evaluations = [tq for tq in tq_ses] + [
            bq for bq in proof.bq_current.stacked_evaluations
        ]

        combination_evaluations = functools.reduce(
            lambda x, y: x + y,
            (p * w for p, w in zip(commited_evaluations, weights)),
            self.state.fri_parameters.field(0),
        )

        # print(combination_evaluations)
        # print(proof.combination_polynomial_proof.round_proofs[0].stacked_evaluations)

        return bool(
            numpy.all(
                combination_evaluations
                == proof.combination_polynomial_proof.round_proofs[
                    0
                ].stacked_evaluations
            )
        )

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

    def get_transition_zerofier(self, n_rows) -> galois.Poly:
        field = self.state.fri_parameters.field
        omicron_domain = field([self.state.omicron**i for i in range(n_rows - 1)])

        return galois.Poly.Roots(omicron_domain, field=field)
