import dataclasses
import logging
import pickle
import typing

import galois
import pymerkle

from vc.constants import LOGGER_MATH, MEKRLE_HASH_ALGORITHM


logger = logging.getLogger(LOGGER_MATH)
hash_buff = pymerkle.InmemoryTree(MEKRLE_HASH_ALGORITHM).hash_buff


@dataclasses.dataclass(init=False, slots=True)
class MerkleTree:
    _tree: pymerkle.BaseMerkleTree

    def __init__(self, algorithm=MEKRLE_HASH_ALGORITHM):
        self._tree = pymerkle.InmemoryTree(algorithm=algorithm)

    def append(self, field_elements: galois.FieldArray):
        field_elements_bytes = pickle.dumps(field_elements)
        self._tree.append_entry(field_elements_bytes)

    def append_bulk(self, stack: galois.FieldArray):
        for row in stack:
            self.append(row)

    @staticmethod
    def verify(field_elements: galois.FieldArray, root: bytes, proof: pymerkle.MerkleProof):
        field_elements_bytes = pickle.dumps(field_elements)
        base = hash_buff(field_elements_bytes)

        try:
            pymerkle.verify_inclusion(base, root, proof)
            result = True
        except pymerkle.InvalidProof:
            result = False

        return result

    @staticmethod
    def verify_bulk(stacked_evaluations: galois.FieldArray, root: bytes, proofs: typing.List[pymerkle.MerkleProof]):
        return all(
            MerkleTree.verify(field_elements, root, proof)
            for field_elements, proof in zip(stacked_evaluations, proofs))

    def get_root(self) -> bytes:
        result = self._tree.get_state()
        return result

    def prove(self, index: int) -> pymerkle.MerkleProof:
        pymerkle_index = index + 1
        proof = self._tree.prove_inclusion(pymerkle_index)

        return proof

    def prove_bulk(self, indices: typing.List[int]) -> typing.List[pymerkle.MerkleProof]:
        proofs = []
        for index in indices:
            proof = self.prove(index)
            proofs.append(proof)

        return proofs
