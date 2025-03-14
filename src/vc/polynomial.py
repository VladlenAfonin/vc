import logging

import galois

from vc.constants import LOGGER_MATH


logger = logging.getLogger(LOGGER_MATH)


def quotient(g: galois.Poly, xs: galois.Array) -> galois.Poly:
    """Get a polynomial quotient over a vanishing set of a polynomial.

    :param g: Polynomial.
    :type g: galois.Poly
    :param xs: Set of points to get a quotient over.
    :type xs: galois.Array
    :return: Quotient polynomial.
    :rtype: galois.Poly
    """

    # MAYBE: (g - galois.lagrange_poly(g(xs))) // galois.Poly.Roots(xs)
    return g // galois.Poly.Roots(xs)


def degree_correct(g: galois.Poly, randomness: int, n: int) -> galois.Poly:
    """Correct the degree of a given polynomial using a random polynomial.

    :param g: Polynomial to be degree-corrected.
    :type g: galois.Poly
    :param randomness: Randomness to create a random polynomial.
    :type randomness: int
    :param n: Degree of a random polynomial.
    :type n: int
    :return: Degree-corrected polynomial.
    :rtype: galois.Poly
    """

    random_polynomial = galois.Poly(
        [randomness**power for power in range(n + 1)], field=g.field
    )
    return g * random_polynomial
