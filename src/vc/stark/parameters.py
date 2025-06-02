import dataclasses
import galois


@dataclasses.dataclass(slots=True)
class StarkParameters:
    field: type[galois.FieldArray]
    omicron: galois.FieldArray
