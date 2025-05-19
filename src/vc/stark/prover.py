import dataclasses
import logging
import typing

import galois

from vc.base import get_nearest_power_of_two
from vc.fri.parameters import FriParameters
from vc.polynomial import MPoly, scale
from vc.stark.boundary import Boundaries, BoundaryConstraint
from vc.stark.proof import StarkProof
from vc.stark.parameters import StarkParameters
from vc.fri.prover import FriProver
from vc.constants import FIELD_GOLDILOCKS


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

    def prove(
        self,
        aet: galois.FieldArray,
        transition_constraints: typing.List[MPoly],
        boundary_constraints: typing.List[BoundaryConstraint],
    ) -> StarkProof:
        trace_polynomials = self.get_trace_polynomials(aet)
        n_registers = len(trace_polynomials)

        boundaries = self.get_boundary_polynomials(
            n_registers,
            boundary_constraints,
        )
        boundary_quotients = [
            (tp - bp) // bz
            for tp, bp, bz in zip(
                trace_polynomials,
                boundaries.polynomials,
                boundaries.zerofiers,
            )
        ]
        boundary_quotient_proofs = []
        for boundary_quotient in boundary_quotients:
            boundary_quotient_proofs.append(
                self.fri_prover.prove(boundary_quotient),
            )

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
        omicron_zerofier_proof = self.fri_prover.prove(omicron_zerofier)

        # INFO: Transition polynomials are expected to equal 0 at omicron
        #       domain, so we only need to divide out the zerofier.
        transition_quotients = [tp // omicron_zerofier for tp in transition_polynomials]
        transition_quotient_proofs = []
        for transition_quotient in transition_quotients:
            transition_quotient_proofs.append(
                self.fri_prover.prove(transition_quotient),
            )

        return StarkProof(
            omicron_zerofier_proof=omicron_zerofier_proof,
            boundary_quotient_proofs=boundary_quotient_proofs,
            transition_quotient_proofs=transition_quotient_proofs,
        )

    def get_boundary_polynomials(
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
