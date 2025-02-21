"""Folding related functions."""


import galois
import numpy

from vc.base import is_pow2


def fold_indices(indices: numpy.ndarray[int], indices_range: int) -> numpy.ndarray[int]:
    """Fold indices preserving sorted state.

    :param indices: Indices to fold.
    :type indices: numpy.ndarray[int]
    :param indices_range: New indices range used for folding.
    :type indices_range: int
    :return: Sorted folded indices.
    :rtype: numpy.ndarray[int]
    """

    assert is_pow2(indices_range), 'indices range must be a power of two'
    return numpy.sort(numpy.unique_values(indices % indices_range))


def fold_polynomial(g: galois.Poly, randomness: int, folding_factor: int) -> galois.Poly:
    """Fold polynomial.

    :param g: Polynomial to fold.
    :type g: galois.Poly
    :param randomness: Verifier's randomness.
    :type randomness: int
    :param folding_factor: Folding factor.
    :type folding_factor: int
    :return: Folded polynomial.
    :rtype: galois.Poly
    """

    # TODO: This function fails if the polynomial being passed is constant.
    #       This can happen after folding.
    # assert g.degree > 1, 'NOT SUPPORTED YET. polynomial degree must be at least 2'

    assert is_pow2(g.degree + 1), 'polynomial degree must be a power of two'
    assert is_pow2(folding_factor), 'folding factor must be a power of two'

    weights = g.field([randomness ** power for power in range(folding_factor)])
    fold_matrix = g.coefficients(order='asc').reshape((-1, folding_factor))
    folded_coefficients = numpy.dot(fold_matrix, weights)

    return galois.Poly(folded_coefficients, order='asc', field=g.field)


def fold_domain(domain: galois.Array, folding_factor: int) -> galois.Array:
    """Fold domain.

    :param domain: Evaluation domain to fold.
    :type domain: galois.Array
    :param folding_factor: Folding factor.
    :type folding_factor: int
    :return: Folded evaluation domain.
    :rtype: galois.Array
    """

    assert is_pow2(domain.size), 'domain size must be a power of two'
    assert is_pow2(folding_factor), 'folding factor must be a power of two'

    new_domain = numpy.unique_values(domain ** folding_factor)
    assert (domain.size // new_domain.size) == folding_factor

    return new_domain
