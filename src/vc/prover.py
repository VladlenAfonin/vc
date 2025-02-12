import dataclasses

import galois

from vc.proof import Proof


@dataclasses.dataclass(slots=True)
class Prover:
    @dataclasses.dataclass(slots=True)
    class ProverState:
        pass

    _state: ProverState

    def prove(f: galois.Poly) -> Proof:
        pass
