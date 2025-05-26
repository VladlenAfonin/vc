from __future__ import annotations

import dataclasses
import typing
import logging

import numpy
import galois

from vc.base import get_nearest_power_of_two, is_pow2


logger = logging.getLogger(__name__)


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


def _get_degree_correction_polynomial(
    g: galois.Poly,
    randomness: galois.FieldArray,
    n: int,
) -> galois.Poly:
    """Get the random polynomial for degree correction.

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
        [randomness**power for power in range(n + 1)],
        field=g.field,
        order="asc",
    )

    return random_polynomial


def degree_correct(
    g: galois.Poly,
    randomness: galois.FieldArray,
    n: int,
) -> galois.Poly:
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

    random_polynomial = _get_degree_correction_polynomial(g, randomness, n)
    return g * random_polynomial


def _degree_correct(g: galois.Poly, r: galois.Poly) -> galois.Poly:
    return g * r


def expand_ext(g: galois.Poly, randomness: galois.FieldArray, target_n_coeffs: int):
    n_coeffs = g.degree + 1
    assert (
        target_n_coeffs >= n_coeffs
    ), "you cannot ask for less coefficients than you have"

    r = _get_degree_correction_polynomial(g, randomness, target_n_coeffs - n_coeffs)
    return (g * r, r)


def expand_to_nearest_power_of_two(
    g: galois.Poly,
    a: int | None,
    b: int | None,
) -> galois.Poly:
    n_coeffs = g.degree + 1
    if is_pow2(n_coeffs):
        return g

    assert a is not None, "a cannot be None when n_coeffs != pow2"
    assert b is not None, "b cannot be None when n_coeffs != pow2"

    nearest_power_of_two = get_nearest_power_of_two(n_coeffs)
    factor = galois.Poly([0, 1], order="asc", field=g.field) ** (
        nearest_power_of_two - n_coeffs
    )

    return a * g + b * g * factor


def expand_to_nearest_power_of_two2_ext(
    g: galois.Poly,
    r: galois.FieldArray,
) -> typing.Tuple[galois.Poly, galois.Poly]:
    n_coeffs = g.degree + 1
    if is_pow2(n_coeffs):
        return (r * g, galois.Poly([r], field=g.field, order="asc"))

    nearest_power_of_two = get_nearest_power_of_two(n_coeffs)
    degree_correction_polynomial = _get_degree_correction_polynomial(
        g,
        r,
        nearest_power_of_two - n_coeffs,
    )

    return (
        _degree_correct(g, degree_correction_polynomial),
        degree_correction_polynomial,
    )


def expand_to_nearest_power_of_two2(
    g: galois.Poly,
    r: galois.FieldArray,
) -> galois.Poly:
    n_coeffs = g.degree + 1
    if is_pow2(n_coeffs):
        return r * g

    nearest_power_of_two = get_nearest_power_of_two(n_coeffs)
    return degree_correct(g, r, nearest_power_of_two - n_coeffs)


def scale(g: galois.Poly, a: int) -> galois.Poly:
    """Scale polynomial by a number. This transforms g(x) to g(a*x).

    :param g: Polynomial to be scaled.
    :type g: galois.Poly
    :param a: Scaling factor.
    :type a: int
    :return: Scaled polynomial.
    :rtype: galois.Poly
    """

    new_coefficients = [c * (a**i) for i, c in enumerate(g.coefficients(order="asc"))]
    return galois.Poly(new_coefficients, order="asc", field=g.field)


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

        assert point.size == self.n_coeffs, "Dimension mismatch"

        result = self.field(0)
        for exp, coeff in self.terms.items():
            term_value = coeff * self.field(
                numpy.prod([p**e for p, e in zip(point, exp)])
            )
            result += term_value

        return result

    def evalv(self, points: galois.FieldArray) -> galois.FieldArray:
        assert points.shape[-1] == self.n_coeffs
        return self.field(
            numpy.apply_along_axis(self.eval, axis=-1, arr=points),
        )

    def evals(self, polys: typing.List[galois.Poly]) -> galois.Poly:
        """
        Symbolically evaluates the polynomial by substituting univariate polynomials in place of variables.

        :param polys: List of `galois.Poly` objects corresponding to variables.
        :type polys: typing.List[galois.Poly]
        :return: Symbolic evaluation of the given multivariate polynomial.
        :rtype: galois.Poly
        """

        assert len(polys) == self.n_coeffs, "Dimension mismatch"

        result_poly = galois.Poly.Zero(self.field)
        for exp, coeff in self.terms.items():
            term_poly = galois.Poly([coeff], self.field)
            for poly, e in zip(polys, exp):
                term_poly *= poly**e
            result_poly += term_poly

        return result_poly

    @property
    def n_coeffs(self) -> int:
        return len(next(iter(self.terms.keys()), ()))
