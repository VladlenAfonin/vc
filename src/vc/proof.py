from __future__ import annotations

import dataclasses
import logging
import typing

import galois
import pymerkle


logger = logging.getLogger('vc')


@dataclasses.dataclass(slots=True)
class RoundProof:
    evaluations: galois.Array
    proofs: typing.List[pymerkle.MerkleProof]

    def check(self) -> bool:
        # TODO: Implement.
        raise NotImplementedError()


@dataclasses.dataclass(slots=True)
class Proof:
    round_proofs: typing.List[RoundProof]
    merkle_roots: typing.List[bytes]
    final_polynomial: galois.Poly
