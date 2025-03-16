import dataclasses
import galois


@dataclasses.dataclass(
    slots=True,
    init=False,
)
class StarkParameters:
    field: type[galois.FieldArray]
    omega: galois.FieldArray
    omicron: galois.FieldArray

    def __init__(
        self,
        omega: galois.FieldArray,
        omicron: galois.FieldArray,
    ) -> None:
        self.omega = omega
        self.omicron = omicron
        self.field = omega.field
