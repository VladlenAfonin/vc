import dataclasses
import typing

import galois
import pymerkle

from vc.fri.proof import FriProof


@dataclasses.dataclass(slots=True)
class StarkProof:
    combination_polynomial_proof: FriProof
    bq_merkle_proofs: typing.List[typing.List[pymerkle.MerkleProof]]
    bq_merkle_roots: typing.List[bytes]
    bq_stacked_evaluations: typing.List[galois.FieldArray]
