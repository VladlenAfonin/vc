from __future__ import annotations

import dataclasses
import logging
import pickle
import typing

import galois
import pymerkle

from vc.constants import LOGGER_FRI


logger = logging.getLogger(LOGGER_FRI)


@dataclasses.dataclass(slots=True)
class RoundProof:
    stacked_evaluations: galois.Array
    proofs: typing.List[pymerkle.MerkleProof]


@dataclasses.dataclass(slots=True)
class FriProof:
    round_proofs: typing.List[RoundProof]
    merkle_roots: typing.List[bytes]
    final_polynomial: galois.Poly

    def serialize(self) -> bytes:
        return pickle.dumps(self)

    def __repr__(self) -> str:
        return f"""
    final polynomial: {self.final_polynomial}
    proof size: {len(self.serialize()) // 1024} KB
"""
