import logging
import galois
import numpy

from vc.constants import LOGGER_MATH


logger = logging.getLogger(LOGGER_MATH)


def quotient(g: galois.Poly, xs: galois.Array) -> galois.Poly:
    return g // galois.Poly.Roots(xs)


def degree_correct(g: galois.Poly, randomness: int, n: int) -> galois.Poly:
    random_polynomial = galois.Poly([randomness ** power for power in range(n + 1)], field=g.field)
    return g * random_polynomial


def stack(evaluations: galois.Array, folding_factor: int) -> galois.Array:
    return evaluations.reshape((folding_factor, -1)).swapaxes(0, 1)


def fold(g: galois.Poly, randomness: int, folding_factor: int) -> galois.Poly:
    # TODO: This function fails if the polynomial being passed is constant.
    #       This can happen after folding.
    # assert g.degree > 1, 'NOT SUPPORTED YET. polynomial degree must be at least 2'

    weights = g.field([randomness ** power for power in range(folding_factor)])
    fold_matrix = g.coefficients(order='asc').reshape((-1, folding_factor))
    folded_coefficients = numpy.dot(fold_matrix, weights)

    return galois.Poly(folded_coefficients, order='asc', field=g.field)


# TODO: Maybe rewrite and make more useful.
def is_colinear(points: galois.Array) -> bool:
    assert points.shape[1] == 2, 'invalid points array shape. expected (*, 2)'
    interpolation_polynomial = galois.lagrange_poly(points[:, 0], points[:, 1])
    return interpolation_polynomial.degree < 2
