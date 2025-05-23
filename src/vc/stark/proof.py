import dataclasses
import typing

import pymerkle

from vc.fri.proof import FriProof


@dataclasses.dataclass(slots=True)
class StarkProof:
    combination_polynomial_proof: FriProof
    boundary_quotient_proofs: typing.List[typing.List[pymerkle.MerkleProof]]
