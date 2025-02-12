from __future__ import annotations

import dataclasses

import galois

from vc import polynomial, domain
from vc.proof import Proof


@dataclasses.dataclass(slots=True)
class ProverOptions:
    """Prover options."""
    folding_factor: int
    """Folding factor."""


@dataclasses.dataclass(init=False, slots=True)
class Prover:
    """Prover."""

    @dataclasses.dataclass(slots=True)
    class State:
        """Current prover state."""
        domain: galois.Array
        """Current evaluation domain."""
        polynomial: galois.Poly
        """Current polynomial."""

    @dataclasses.dataclass(slots=True)
    class ProofBuilder:
        """Proof builder."""
        pass

    _options: ProverOptions

    _state: Prover.State | None = None
    _proof_builder: Prover.ProofBuilder | None = None

    def __init__(self, options: ProverOptions) -> None:
        assert options is not None

        self._options = options
        self._state = None
        self._proof_builder = None

    def prove(self, f: galois.Poly) -> Proof:
        evaluation_domain = domain.construct(f.field, f.degree)
        self._state = Prover.State(
            domain=evaluation_domain,
            polynomial=f)

    def round(self) -> None:
        assert self._state is not None
        assert self._proof_builder is not None

        # TODO: Get randomness from the random oracle.
        randomness = self._state.polynomial.field.Random()

        new_polynomial = polynomial.fold(self._state.polynomial, randomness, self._options.folding_factor)
        new_domain = domain.fold(self._state.domain, self._options.folding_factor)

        self._state.polynomial = new_polynomial
        self._state.domain = new_domain
