import galois


LOGGER_FRI = "vc.fri"
LOGGER_MATH = "vc.math"

MEKRLE_HASH_ALGORITHM = "sha3_256"

FIELD_BABYBEAR = galois.GF((1 << 31) - (1 << 27) + 1)
FIELD_GOLDILOCKS = galois.GF((1 << 64) - (1 << 32) + 1)
FIELD_193 = galois.GF(193)
