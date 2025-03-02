import dataclasses

import numpy

from vc.stark.proof import StarkProof


@dataclasses.dataclass(slots=True)
class StarkProver:
    def prove(self, trace: numpy.ndarray[int]) -> StarkProof:
        pass
