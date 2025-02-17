import binascii
import dataclasses
import logging
import pickle

import galois
import pymerkle


logger = logging.getLogger(__name__)


@dataclasses.dataclass(init=False, slots=True)
class MerkleTree:
    _tree: pymerkle.BaseMerkleTree

    def __init__(self, algorithm='sha3_512'):
        self._tree = pymerkle.InmemoryTree(algorithm=algorithm)

    def append_field_elements(self, field_elements: galois.FieldArray):
        logger.info(f'MerkleTree.append_field_elements(): begin')
        logger.info(f'MerkleTree.append_field_elements(): {field_elements = }')

        for field_element in field_elements:
            logger.info(f'MerkleTree.append_field_elements(): {field_element = }')

            field_element_bytes = pickle.dumps(field_element)
            # logger.info(f'MerkleTree.append_field_elements(): {field_element_bytes = }')

            self._tree.append_entry(field_element_bytes)

        logger.info(f'MerkleTree.append_field_elements(): end')

    def append_field_element(self, field_element: galois.FieldArray):
        logger.info(f'MerkleTree.append_field_element(): begin')
        logger.info(f'MerkleTree.append_field_element(): {field_element = }')

        field_element_bytes = pickle.dumps(field_element)
        # logger.info(f'MerkleTree.append_field_element(): {field_element_bytes = }')

        self._tree.append_entry(field_element_bytes)
        logger.info(f'MerkleTree.append_field_element(): end')

    def get_root(self):
        logger.info(f'MerkleTree.get_root(): begin')
        result = self._tree.get_state()
        logger.info(f'MerkleTree.get_root(): {binascii.hexlify(result) = }')
        logger.info(f'MerkleTree.get_root(): end')

        return result
