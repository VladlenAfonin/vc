import logging

from vc.constants import LOGGER_FRI
from vc.proof import Proof


logger = logging.getLogger(LOGGER_FRI)


class Verifier:
    def verify(proof: Proof) -> bool:
        pass
