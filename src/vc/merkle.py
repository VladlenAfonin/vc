import binascii
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

    def __init__(self, algorithm='sha3_256'):
        logger.debug(f'MerkleTree.init(): begin')
        logger.debug(f'MerkleTree.init(): create InmemoryTree with {algorithm = }')
        self._tree = pymerkle.InmemoryTree(algorithm=algorithm)
        logger.debug(f'MerkleTree.init(): end')

    def append_field_elements(self, field_elements: galois.FieldArray):
        logger.debug(f'MerkleTree.append_field_elements(): begin')
        logger.debug(f'MerkleTree.append_field_elements(): {field_elements = }')

        for field_element in field_elements:
            logger.debug(f'MerkleTree.append_field_elements(): appending {field_element = }')
            logger.debug(f'MerkleTree.append_field_elements(): serialize to bytes {field_element = }')
            field_element_bytes = pickle.dumps(field_element)
            logger.debug(f'MerkleTree.append_field_elements(): append to merkle tree {field_element = }')
            self._tree.append_entry(field_element_bytes)

        logger.debug(f'MerkleTree.append_field_elements(): end')

    def append_single(self, field_elements: galois.FieldArray):
        field_elements_bytes = pickle.dumps(field_elements)
        self._tree.append_entry(field_elements_bytes)

    def append_stacked(self, stack: galois.FieldArray):
        for row in stack:
            self.append_single(row)

    @staticmethod
    def verify_single(field_elements: galois.FieldArray, root: bytes, proof: pymerkle.MerkleProof):
        base = hash_buff(field_elements)

        try:
            pymerkle.verify_inclusion(base, root, proof)
            result = True
        except pymerkle.InvalidProof:
            result = False

        return result

    def append_field_element(self, field_element: galois.FieldArray):
        logger.debug(f'MerkleTree.append_field_element(): begin')
        logger.debug(f'MerkleTree.append_field_element(): {field_element = }')

        logger.debug(f'MerkleTree.append_field_element(): serialize to bytes {field_element = }')
        field_element_bytes = pickle.dumps(field_element)

        logger.debug(f'MerkleTree.append_field_element(): append to merkle tree {field_element = }')
        self._tree.append_entry(field_element_bytes)
        logger.debug(f'MerkleTree.append_field_element(): end')

    def get_root(self) -> bytes:
        logger.debug(f'MerkleTree.get_root(): begin')
        result = self._tree.get_state()
        logger.debug(f'MerkleTree.get_root(): {binascii.hexlify(result) = }')
        logger.debug(f'MerkleTree.get_root(): end')

        return result

    def prove_index(self, index: int) -> pymerkle.MerkleProof:
        pymerkle_index = index + 1
        proof = self._tree.prove_inclusion(pymerkle_index)

        return proof

    def prove_indices(self, indices: typing.List[int]) -> typing.List[pymerkle.MerkleProof]:
        proofs = []
        for index in indices:
            proof = self.prove_index(index)
            proofs.append(proof)

        return proofs

    def verify_field_element(
            self,
            field_element: galois.FieldArray,
            root: bytes,
            proof: pymerkle.MerkleProof) -> bool:
        logger.debug(f'MerkleTree.verify_field_element(): begin')
        logger.debug(f'MerkleTree.verify_field_element(): {field_element = }')
        logger.debug(f'MerkleTree.verify_field_element(): {root = }')
        logger.debug(f'MerkleTree.verify_field_element(): {proof = }')

        field_element_bytes = pickle.dumps(field_element)
        base = self._tree.hash_buff(field_element_bytes)

        try:
            pymerkle.verify_inclusion(base, root, proof)
            result = True
        except pymerkle.InvalidProof:
            result = False

        logger.debug(f'MerkleTree.verify_field_element(): {result = }')
        logger.debug(f'MerkleTree.verify_field_element(): end')
        return result

    def verify_field_elements(
            self,
            field_elements: galois.FieldArray,
            root: bytes,
            proofs: typing.List[pymerkle.MerkleProof]) -> bool:
        logger.debug(f'MerkleTree.verify_field_elements(): begin')

        result = all(
            self.verify_field_element(field_element, root, proof)
            for field_element, proof in zip(field_elements, proofs))

        logger.debug(f'MerkleTree.verify_field_elements(): end')

        return result
