import pytest

import galois

from vc.merkle import MerkleTree


FIELD = galois.GF(193)


def test_verify_valid():
    merkle_tree = MerkleTree()
    field_element = FIELD.Random()
    merkle_tree.append_field_element(field_element)
    root = merkle_tree.get_root()
    proof = merkle_tree.prove_index(0)

    result = merkle_tree.verify_field_element(field_element, root, proof)

    assert result == True


@pytest.mark.parametrize('root',
    [
        (b''),
        (b'\xff')
    ])
def test_verify_invalid(root: bytes):
    merkle_tree = MerkleTree()
    field_element = FIELD.Random()
    merkle_tree.append_field_element(field_element)
    proof = merkle_tree.prove_index(0)

    result = merkle_tree.verify_field_element(field_element, root, proof)

    assert result == False
