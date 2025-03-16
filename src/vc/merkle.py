"""Merkle tree implementation."""

import dataclasses
import logging
import pickle
import typing

import galois
import galois.typing
import numpy
import pymerkle

from vc.constants import LOGGER_MATH, MEKRLE_HASH_ALGORITHM


logger = logging.getLogger(LOGGER_MATH)
hash_buff = pymerkle.InmemoryTree(MEKRLE_HASH_ALGORITHM).hash_buff


# TODO: Rewrite to custom implementation deriving from the pymerkle.BaseMerkleTree.
@dataclasses.dataclass(
    init=False,
    slots=True,
)
class MerkleTree:
    """Merkle tree for field stacked evaluations."""

    _tree: pymerkle.BaseMerkleTree
    """Internal pymerkle Merkle tree."""

    def __init__(self, algorithm: str = MEKRLE_HASH_ALGORITHM) -> None:
        """Initialize a new Merkle tree with a given hashing algorithm.

        :param algorithm: Hashing algorithm, defaults to MEKRLE_HASH_ALGORITHM.
        :type algorithm: str, optional
        """

        self._tree = pymerkle.InmemoryTree(algorithm=algorithm)

    def append(
        self,
        field_elements: galois.FieldArray,
    ) -> None:
        """Append a single stacked evaluation to the Merkle tree.

        :param field_elements: Single stacked evaluation.
        :type field_elements: galois.FieldArray
        """

        field_elements_bytes = pickle.dumps(field_elements)

        # Ignore the returned index as we don't need it.
        _ = self._tree.append_entry(field_elements_bytes)

    def append_bulk(
        self,
        stack: galois.FieldArray,
    ) -> None:
        """Append multiple stacked evaluations to the Merkle tree.

        :param stack: Multiple stacked evaluations.
        :type stack: galois.FieldArray
        """

        for row in stack:
            self.append(row)

    @staticmethod
    def verify(
        field_elements: galois.FieldArray,
        root: bytes,
        proof: pymerkle.MerkleProof,
    ) -> bool:
        """Verify that a given single stacked evaluation is included in the Merkle tree.

        :param field_elements: Stacked evaluation.
        :type field_elements: galois.FieldArray
        :param root: Merkle root.
        :type root: bytes
        :param proof: Corresponding Merkle proof.
        :type proof: pymerkle.MerkleProof
        :return: ``True`` if the check was successful. ``False`` otherwise.
        :rtype: bool
        """

        field_elements_bytes = pickle.dumps(field_elements)
        base = hash_buff(field_elements_bytes)

        try:
            pymerkle.verify_inclusion(base, root, proof)
            result = True
        except pymerkle.InvalidProof:
            result = False

        return result

    @staticmethod
    def verify_bulk(
        stacked_evaluations: galois.FieldArray,
        root: bytes,
        proofs: typing.List[pymerkle.MerkleProof],
    ) -> bool:
        """Verify multiple evaluations given a Merkle tree root and corresponding proofs.

        :param stacked_evaluations: Stacked evaluations.
        :type stacked_evaluations: galois.FieldArray
        :param root: Merkle root.
        :type root: bytes
        :param proofs: List of corresponding Merkle proofs.
        :type proofs: typing.List[pymerkle.MerkleProof]
        :return: ``True`` if the all the checks were successful. ``False`` otherwise.
        :rtype: bool
        """

        return all(
            MerkleTree.verify(field_elements, root, proof)
            for field_elements, proof in zip(stacked_evaluations, proofs)
        )

    def get_root(self) -> bytes:
        """Get current Merkle tree root.

        :return: Current Merkle tree root.
        :rtype: bytes
        """

        result = self._tree.get_state()
        return result

    def prove(
        self,
        index: int,
    ) -> pymerkle.MerkleProof:
        """Generate a Merkle proof for given index.

        :param index: Index to generate the proof for.
        :type index: int
        :return: Proof.
        :rtype: pymerkle.MerkleProof
        """

        pymerkle_index = index + 1
        proof = self._tree.prove_inclusion(pymerkle_index)

        return proof

    def prove_bulk(
        self,
        indices: numpy.ndarray,
    ) -> typing.List[pymerkle.MerkleProof]:
        """Generate a list of Merkle proofs for given indices.

        :param indices: Indices to generate the proofs for.
        :type indices: numpy.ndarray[int]
        :return: List of proofs for corresponding indices.
        :rtype: typing.List[pymerkle.MerkleProof]
        """

        proofs = []
        for index in indices:
            proof = self.prove(index)
            proofs.append(proof)

        return proofs
