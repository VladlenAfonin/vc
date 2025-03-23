from __future__ import annotations

import dataclasses
import typing
import logging

import numpy
import galois

from vc.constants import LOGGER_MATH


logger = logging.getLogger(LOGGER_MATH)


def quotient(g: galois.Poly, xs: galois.FieldArray) -> galois.Poly:
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


@dataclasses.dataclass(slots=True, init=False)
class MPoly:
    terms: typing.Dict[typing.Tuple[int, ...], galois.FieldArray]
    field: type[galois.FieldArray]

    def __init__(
        self,
        terms: typing.Dict[typing.Tuple[int, ...], galois.FieldArray],
        field: type[galois.FieldArray],
    ) -> None:
        """
        Initializes a multivariate polynomial.

        :param terms: Dictionary mapping monomials (tuples of exponents) to coefficients.
        :type terms: typing.Dict[typing.Tuple[int, ...], galois.FieldArray]
        :param field: Dictionary mapping monomials (tuples of exponents) to coefficients.
        :type field: type[galois.FieldArray]
        """

        self.terms = {k: v for k, v in terms.items() if v != 0}  # Remove zero terms
        self.field = field

    def __repr__(self):
        return " + ".join([f"{v}*x^{k}" for k, v in self.terms.items()]) or "0"

    def eval(self, point: galois.FieldArray) -> galois.FieldArray:
        """
        Evaluates the polynomial at a given point.

        :param point: List or tuple of values corresponding to variables.
        :type polys: galois.FieldArray
        :return: Evaluation of the given multivariate polynomial.
        :rtype: galois.FieldArray
        """

        assert point.size == len(
            next(iter(self.terms.keys()), ())
        ), "Dimension mismatch"

        result = self.field(0)
        for exp, coeff in self.terms.items():
            term_value = coeff * self.field(
                numpy.prod([p**e for p, e in zip(point, exp)])
            )
            result += term_value

        return result

    def evals(self, polys: typing.List[galois.Poly]) -> galois.Poly:
        """
        Symbolically evaluates the polynomial by substituting univariate polynomials in place of variables.

        :param polys: List of `galois.Poly` objects corresponding to variables.
        :type polys: typing.List[galois.Poly]
        :return: Symbolic evaluation of the given multivariate polynomial.
        :rtype: galois.Poly
        """

        assert len(polys) == len(
            next(iter(self.terms.keys()), ())
        ), "Dimension mismatch"

        result_poly = galois.Poly.Zero(self.field)
        for exp, coeff in self.terms.items():
            term_poly = galois.Poly([coeff], self.field)
            for poly, e in zip(polys, exp):
                term_poly *= poly**e
            result_poly += term_poly

        return result_poly
