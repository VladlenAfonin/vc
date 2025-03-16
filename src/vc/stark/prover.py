import dataclasses
import typing

import galois
import numpy
import numpy.typing

from vc.stark.proof import StarkProof
from vc.stark.parameters import StarkParameters
from vc.fri.prover import FriProver
from vc.constants import FIELD_GOLDILOCKS


field = FIELD_GOLDILOCKS


@dataclasses.dataclass(slots=True)
class StarkProver:
    stark_parameters: StarkParameters
    fri_prover: FriProver

    @dataclasses.dataclass(slots=True)
    class ProverState:
        omicron: numpy.ndarray

    def prove(
        self,
    ) -> StarkProof: ...

    # def get_trace_polynomials(
    #     self,
    #     aet: numpy.ndarray,
    # ) -> typing.List[galois.Poly]:
    #     return [
    #         galois.lagrange_poly(self.stark_parameters.omicron_domain, col)
    #         for col in aet.T
    #     ]
