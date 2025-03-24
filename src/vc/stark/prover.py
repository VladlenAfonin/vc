import dataclasses
import typing

import galois
import numpy
import numpy.typing

from vc.base import get_nearest_power_of_two, is_pow2
from vc.polynomial import MPoly
from vc.stark.proof import StarkProof
from vc.stark.parameters import StarkParameters
from vc.fri.prover import FriProver
from vc.constants import FIELD_GOLDILOCKS


field = FIELD_GOLDILOCKS


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
    fri_prover: FriProver
    state: StarkProverState

    # def prove(
    #     self,
    #     aet: galois.FieldArray,
    #     transition_constraints: typing.List[MPoly],
    #     boundary_constraints: galois.Field,
    # ) -> StarkProof: ...

    def get_trace_polynomials(self, aet: galois.FieldArray) -> typing.List[galois.Poly]:
        # TODO: This does not yet support "not power of two" AET heights.
        return [galois.lagrange_poly(self.state.omicron_domain, col) for col in aet.T]
