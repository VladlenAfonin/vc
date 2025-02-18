import logging
import galois
import numpy


logger = logging.getLogger('vc')


def quotient(g: galois.Poly, xs: galois.Array) -> galois.Poly:
    return g // galois.Poly.Roots(xs)


def degree_correct(g: galois.Poly, randomness: int, n: int) -> galois.Poly:
    logger.debug(f'polynomial.degree_correct(): begin')
    logger.debug(f'polynomial.degree_correct(): {g = }')
    logger.debug(f'polynomial.degree_correct(): {randomness = }')

    logger.debug(f'polynomial.degree_correct(): generate random polynomial')
    random_polynomial = galois.Poly([randomness ** power for power in range(n + 1)], field=g.field)
    logger.debug(f'polynomial.degree_correct(): {random_polynomial = }')

    logger.debug(f'polynomial.degree_correct(): correct degree')
    result = g * random_polynomial
    logger.debug(f'polynomial.degree_correct(): {result = }')

    logger.debug(f'polynomial.degree_correct(): end')

    return result


def fold(g: galois.Poly, randomness: int, folding_factor: int) -> galois.Poly:
    # TODO: This function fails if the polynomial being passed is constant.
    #       This can happen after folding.
    # assert g.degree > 1, 'NOT SUPPORTED YET. polynomial degree must be at least 2'

    logger.debug(f'polynomial.fold(): begin')
    logger.debug(f'polynomial.fold(): {g = }')
    logger.debug(f'polynomial.fold(): {randomness = }')
    logger.debug(f'polynomial.fold(): {folding_factor = }')

    logger.debug(f'polynomial.fold(): construct weights')
    weights = g.field([randomness ** power for power in range(folding_factor)])
    logger.debug(f'polynomial.fold(): {weights = }')

    logger.debug(f'polynomial.fold(): construct fold matrix')
    fold_matrix = g.coefficients(order='asc').reshape((-1, folding_factor))
    logger.debug(f'polynomial.fold(): {fold_matrix = }')

    logger.debug(f'polynomial.fold(): get folded coefficients')
    folded_coefficients = numpy.dot(fold_matrix, weights)
    logger.debug(f'polynomial.fold(): {folded_coefficients = }')

    result = galois.Poly(folded_coefficients, order='asc', field=g.field)
    logger.debug(f'polynomial.fold(): {result = }')

    logger.debug(f'polynomial.fold(): end')

    return result


def is_colinear(points: galois.Array) -> bool:
    logger.debug(f'polynomial.is_colinear(): begin')
    logger.debug(f'polynomial.is_colinear(): {points = }')

    assert points.shape[1] == 2, 'invalid points array shape. expected (*, 2)'

    logger.debug(f'polynomial.is_colinear(): interpolate points')
    interpolation_polynomial = galois.lagrange_poly(points[:, 0], points[:, 1])
    logger.debug(f'polynomial.is_colinear(): {interpolation_polynomial = }')

    logger.debug(f'polynomial.is_colinear(): check degree')
    result = interpolation_polynomial.degree < 2
    logger.debug(f'polynomial.is_colinear(): {result = }')

    logger.debug(f'polynomial.is_colinear(): end')

    return result
