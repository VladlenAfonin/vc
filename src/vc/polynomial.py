import galois
import numpy


def polynomial_quotient(g: galois.Poly, xs: galois.Array) -> galois.Poly:
    return g // galois.Poly.Roots(xs)


def degree_correct(g: galois.Poly, randomness: int, n: int) -> galois.Poly:
    random_polynomial = galois.Poly([randomness ** power for power in range(n + 1)], field=g.field)
    return g * random_polynomial


def fold(g: galois.Poly, randomness: int, folding_factor: int) -> galois.Poly:
    weights = g.field([randomness ** power for power in range(folding_factor)])
    fold_matrix = g.coefficients().reshape((-1, folding_factor))
    folded_coefficients = numpy.dot(fold_matrix, weights)

    return galois.Poly(folded_coefficients, field=g.field)
