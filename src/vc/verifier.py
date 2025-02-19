from __future__ import annotations

import dataclasses
import logging

from vc.constants import LOGGER_FRI, MEKRLE_HASH_ALGORITHM
from vc.merkle import MerkleTree
from vc.parameters import FriParameters
from vc.proof import Proof
from vc.sponge import Sponge


logger = logging.getLogger(LOGGER_FRI)


@dataclasses.dataclass(init=False, slots=True)
class Verifier:
    """FRI Verifier."""

    @dataclasses.dataclass(slots=True)
    class State:
        """FRI Verifier state."""

        sponge: Sponge
        """Sponge."""

    _parameters: FriParameters
    _state: Verifier.State

    def __init__(self, parameters: FriParameters) -> None:
        self._parameters = parameters
        self._state = Verifier.State(Sponge(parameters.field))

    def verify(self, proof: Proof) -> bool:
        logger.debug(f'Verifier.verify(): begin')

        logger.debug(f'Verifier.verify(): check polynomial degree')
        if proof.final_polynomial.degree + 1 > self._parameters.final_coefficients_length:
            return False

        logger.debug(f'Verifier.verify(): check merkle trees in round proofs')

        # Create an empty Merkle tree used only for verification.
        merkle_tree = MerkleTree(algorithm=MEKRLE_HASH_ALGORITHM)
        for i, (merkle_root, round_proof) in enumerate(zip(proof.merkle_roots, proof.round_proofs)):
            logger.debug(f'Verifier.verify(): begin merkle tree check round {i = }')
            logger.debug(f'Verifier.verify(): {merkle_root = }')
            logger.debug(f'Verifier.verify(): {round_proof = }')

            merkle_result = merkle_tree.verify_field_elements(
                round_proof.evaluations,
                merkle_root,
                round_proof.proofs)
            logger.debug(f'Verifier.verify(): {merkle_result = }')

            logger.debug(f'Verifier.verify(): end merkle tree check round {i = }')

            if not merkle_result:
                logger.debug(f'Verifier.verify(): end')
                return False

        logger.debug(f'Verifier.verify(): verify folds')

        logger.debug(f'Verifier.verify(): end')
        return True

        # logger.debug('Verifier.verify(): push initial merkle root into sponge')
        # self._state.sponge.push(proof.merkle_roots[0])
        # folding_randomness = self._state.sponge.sample_field_prover()
