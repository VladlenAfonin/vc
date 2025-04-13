import dataclasses
import typing
import galois


@dataclasses.dataclass(slots=True)
class BoundaryConstraint:
    x: int
    y: int
    value: galois.FieldArray


@dataclasses.dataclass(slots=True)
class Boundaries:
    constraints: typing.List[BoundaryConstraint]
    polynomials: typing.List[galois.Poly]
    zerofiers: typing.List[galois.Poly]
