import typing

import pytest

from vc.constants import TEST_FIELD
from vc.merkle import MerkleTree


MERKLE_TREE_LEAVES_LENGTH = 4


@pytest.mark.parametrize(
    'index',
    [
        (0),
        (1),
        (2),
        (3)
    ])
def test_verify_valid(index: int):
    merkle_tree = MerkleTree()
    field_elements = TEST_FIELD.Random(MERKLE_TREE_LEAVES_LENGTH)
    merkle_tree.append_field_elements(field_elements)
    root = merkle_tree.get_root()
    proof = merkle_tree.prove_index(index)

    verifier_merkle_tree = MerkleTree()
    result = verifier_merkle_tree.verify_field_element(field_elements[index], root, proof)

    assert result == True


@pytest.mark.parametrize(
    'indices',
    [
        ([0]),
        ([1]),
        ([0, 1]),
        ([0, 1, 2]),
        ([0, 1, 3]),
        ([2, 3]),
        ([1, 0])
    ])
def test_verify_multiple_valid(indices: typing.List[int]):
    merkle_tree = MerkleTree()
    field_elements = TEST_FIELD.Random(MERKLE_TREE_LEAVES_LENGTH)
    merkle_tree.append_field_elements(field_elements)
    root = merkle_tree.get_root()
    proofs = merkle_tree.prove_indices(indices)

    verifier_merkle_tree = MerkleTree()
    result = verifier_merkle_tree.verify_field_elements(field_elements[indices], root, proofs)

    assert result == True


@pytest.mark.parametrize(
    'root',
    [
        (b''),
        (b'\xff')
    ])
def test_verify_invalid(root: bytes):
    merkle_tree = MerkleTree()
    field_elements = TEST_FIELD.Random(MERKLE_TREE_LEAVES_LENGTH)
    merkle_tree.append_field_element(field_elements)
    proof = merkle_tree.prove_index(0)

    result = merkle_tree.verify_field_element(field_elements[0], root, proof)

    assert result == False
