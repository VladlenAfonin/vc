import typing

import pytest

from vc.constants import FIELD_193
from vc.merkle import MerkleTree
from vc.fold import stack


def test_append_single():
    field = FIELD_193
    merkle_tree = MerkleTree()
    folding_factor = 2
    field_elements = field.Random(folding_factor)
    stacked_evaluations = stack(field_elements, folding_factor)
    merkle_tree.append(stacked_evaluations[0])
    root = merkle_tree.get_root()
    proof = merkle_tree.prove(0)

    result = MerkleTree.verify(field_elements, root, proof)
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
def test_append_bulk(indices: typing.List[int]):
    field = FIELD_193
    merkle_tree = MerkleTree()
    folding_factor = 2
    field_elements = field.Random(8)
    stacked_evaluations = stack(field_elements, folding_factor)
    merkle_tree.append_bulk(stacked_evaluations)
    root = merkle_tree.get_root()
    proof = merkle_tree.prove_bulk(indices)

    result = MerkleTree.verify_bulk(stacked_evaluations[indices], root, proof)
    assert result == True
