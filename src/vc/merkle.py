import binascii
import dataclasses
import logging
import pickle
import typing

import galois
import pymerkle

from vc.constants import LOGGER_MATH


logger = logging.getLogger(LOGGER_MATH)


@dataclasses.dataclass(init=False, slots=True)
class MerkleTree:
    _tree: pymerkle.BaseMerkleTree

    def __init__(self, algorithm='sha3_512'):
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

    def verify_field_element(self, field_element, root, proof) -> bool:
        field_element_bytes = pickle.dumps(field_element)
        base = self._tree.hash_buff(field_element_bytes)

        try:
            pymerkle.verify_inclusion(base, root, proof)
            return True
        except pymerkle.InvalidProof:
            return False
