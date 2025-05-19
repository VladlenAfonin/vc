import dataclasses
import logging

import galois

from vc.stark.proof import StarkProof
from vc.fri.verifier import FriVerifier
from vc.fri.parameters import FriParameters
from vc.logging import logging_mark


logger = logging.getLogger(__name__)


@dataclasses.dataclass(slots=True)
class StarkVerifier:
    @dataclasses.dataclass(slots=True)
    class StarkVerifierState:
        fri_verifier: FriVerifier
        fri_parameters: FriParameters
        omicron: galois.FieldArray

    state: StarkVerifierState

    @logging_mark(logger)
    def verify(self, proof: StarkProof) -> bool:
        if not all(
            self.state.fri_verifier.verify(x) for x in proof.boundary_quotient_proofs
        ):
            logger.error("invalid boundary quotient proof")
            return False

        if not all(
            self.state.fri_verifier.verify(x) for x in proof.transition_quotient_proofs
        ):
            logger.error("invalid transition quotient proof")
            return False

        if not self.state.fri_verifier.verify(proof.omicron_zerofier_proof):
            logger.error("invalid omicron zerofier proof")
            return False

        # INFO: Check consistency.

        return True
