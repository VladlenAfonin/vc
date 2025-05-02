import dataclasses
import typing

from vc.fri.proof import FriProof


@dataclasses.dataclass(slots=True)
class StarkProof:
    omicron_zerofier_proof: FriProof
    boundary_quotient_proofs: typing.List[FriProof]
    transition_quotient_proofs: typing.List[FriProof]
