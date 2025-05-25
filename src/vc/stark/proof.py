import dataclasses
import typing

import galois
import pymerkle

from vc.fri.proof import FriProof


@dataclasses.dataclass(slots=True)
class BoundaryQuotientProof:
    merkle_proofs: typing.List[typing.List[pymerkle.MerkleProof]]
    merkle_roots: typing.List[bytes]
    stacked_evaluations: typing.List[galois.FieldArray]


@dataclasses.dataclass(slots=True)
class StarkProof:
    combination_polynomial_proof: FriProof
    bq_current: BoundaryQuotientProof
    bq_next: BoundaryQuotientProof
