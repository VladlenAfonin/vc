import dataclasses
import logging
import typing
import functools

import galois

from vc.base import get_nearest_power_of_two
from vc.fri.parameters import FriParameters
from vc.fri.fold import stack
from vc.sponge import Sponge
from vc.polynomial import MPoly, scale
from vc.stark.boundary import Boundaries, BoundaryConstraint
from vc.stark.proof import StarkProof
from vc.stark.parameters import StarkParameters
from vc.fri.prover import FriProver
from vc.constants import FIELD_GOLDILOCKS
from vc.merkle import MerkleTree
from vc.logging import logging_mark


field = FIELD_GOLDILOCKS
logger = logging.getLogger(__name__)


@dataclasses.dataclass(slots=True)
class StarkProver:
    @dataclasses.dataclass(slots=True, init=False)
    class StarkProverState:
        omicron_domain: galois.FieldArray

        def __init__(
            self,
            field: type[galois.FieldArray],
            omicron: galois.FieldArray,
            aet_height: int,
        ) -> None:
            nearest_power_of_two = get_nearest_power_of_two(aet_height)
            self.omicron_domain = field(
                [omicron**i for i in range(nearest_power_of_two)]
            )

    stark_parameters: StarkParameters
    fri_parameters: FriParameters
    fri_prover: FriProver
    state: StarkProverState

    @logging_mark(logger)
    def prove(
        self,
        aet: galois.FieldArray,
        transition_constraints: typing.List[MPoly],
        boundary_constraints: typing.List[BoundaryConstraint],
    ) -> StarkProof:
        sponge = Sponge(self.fri_parameters.field)

        trace_polynomials = self.get_trace_polynomials(aet)
        n_registers = len(trace_polynomials)

        boundaries = self.get_boundaries(n_registers, boundary_constraints)
        boundary_quotients = [
            (tp - bp) // bz
            for tp, bp, bz in zip(
                trace_polynomials,
                boundaries.polynomials,
                boundaries.zerofiers,
            )
        ]

        for boundary_quotient in boundary_quotients:
            evaluations = boundary_quotient(
                self.fri_parameters.initial_evaluation_domain
            )
            stacked_evaluations = stack(
                evaluations,
                self.fri_parameters.folding_factor,
            )
            merkle_tree = MerkleTree()
            merkle_tree.append_bulk(stacked_evaluations)
            merkle_tree_root = merkle_tree.get_root()
            sponge.absorb(merkle_tree_root)

        scaled_trace_polynomials = [
            scale(tp, int(self.stark_parameters.omicron)) for tp in trace_polynomials
        ]
        transition_polynomials = [
            tc.evals(trace_polynomials + scaled_trace_polynomials)
            for tc in transition_constraints
        ]

        omicron_zerofier = galois.Poly.Roots(
            self.state.omicron_domain[0 : aet.shape[0] - 1]
        )

        # INFO: Transition polynomials are expected to equal 0 at omicron
        #       domain, so we only need to divide out the zerofier.
        transition_quotients = [tp // omicron_zerofier for tp in transition_polynomials]

        commited_polynomials = transition_quotients + boundary_quotients
        n_weights = len(commited_polynomials)
        weights = [sponge.squeeze_field_element() for _ in range(n_weights)]

        combination_polynomial = functools.reduce(
            lambda x, y: x + y,
            (p * w for p, w in zip(commited_polynomials, weights)),
            galois.Poly.Zero(field=self.fri_parameters.field),
        )

        fri_proof = self.fri_prover.prove(combination_polynomial)

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

            xs = self.state.omicron_domain[
                [bc.i for bc in current_boundary_constraints]
            ]
            ys = self.stark_parameters.field(
                [bc.value for bc in current_boundary_constraints]
            )

            zerofiers.append(galois.Poly.Roots(xs))
            polynomials.append(galois.lagrange_poly(xs, ys))

        return Boundaries(
            constraints=boundary_constraints,
            polynomials=polynomials,
            zerofiers=zerofiers,
        )

    def get_trace_polynomials(self, aet: galois.FieldArray) -> typing.List[galois.Poly]:
        # TODO: This does not yet support "not power of two" AET heights.
        return [galois.lagrange_poly(self.state.omicron_domain, col) for col in aet.T]
