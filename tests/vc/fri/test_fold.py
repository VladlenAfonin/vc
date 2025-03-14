import galois
import numpy
import pytest

from vc.constants import FIELD_193
from vc.fri.fold import (
    extend_indices,
    fold_domain,
    fold_polynomial,
    fold_sort_generate,
    stack,
)


@pytest.mark.parametrize(
    "expected, polynomial_coefficients, randomness, folding_factor",
    [
        # x + 1 = [1, 1] -> 1 + 1*1 = 2
        ([2], [1, 1], 1, 2),
        # x^3 + 2x^2 + 2x + 1 = [1, 2, 2, 1] -> [[1, 2], [2, 1]] -> [1 + 1*2, 2 + 1*1] = [3, 3]
        ([3, 3], [1, 2, 2, 1], 1, 2),
        # 1 + ... + 8x^7 = [1, 2, 3, 4, 5, 6, 7, 8] -> [[1, 2], [3, 4], [5, 6], [7, 8]] ->
        # [1 + 2*2, 3 + 2*4, 5 + 2*6, 7 + 2*8] = [5, 11, 17, 23]
        ([5, 11, 17, 23], [1, 2, 3, 4, 5, 6, 7, 8], 2, 2),
    ],
)
def test_fold(
    expected: galois.Array,
    polynomial_coefficients: galois.Array,
    randomness: int,
    folding_factor: int,
) -> None:
    g = galois.Poly(polynomial_coefficients, field=FIELD_193, order="asc")
    g_folded = fold_polynomial(g, randomness, folding_factor)

    assert g_folded == galois.Poly(expected, field=g.field, order="asc")


@pytest.mark.parametrize(
    "expected, evaluations, folding_factor",
    [
        #                       [[1, 4],
        # [1, 2, 3, 4, 5, 6] ->  [2, 5],
        #                        [3, 6]]
        (FIELD_193([[1, 4], [2, 5], [3, 6]]), FIELD_193([1, 2, 3, 4, 5, 6]), 2)
    ],
)
def test_stack(expected, evaluations, folding_factor):
    result = stack(evaluations, folding_factor)
    assert numpy.all(result == expected)


def test_consistency_check():
    field = FIELD_193
    coefficients_length_log = 4
    folding_factor = 2
    expansion_factor = 4
    query_indices = [8, 25]

    folding_randomness = 14
    coefficients_length = 1 << coefficients_length_log

    # 62 +
    # 107 * x^2 +
    # 46 * x^3 +
    # 171 * x^4 +
    # 87 * x^5 +
    # 127 * x^6 +
    # 10 * x^7 +
    # 86 * x^8 +
    # 100 * x^9 +
    # 8 * x^10 +
    # 119 * x^11 +
    # 31 * x^12 +
    # 37 * x^13 +
    # 22 * x^14 +
    # 52 * x^15

    initial_polynomial = galois.Poly(
        [62, 0, 107, 46, 171, 87, 127, 10, 86, 100, 8, 119, 31, 37, 22, 52],
        order="asc",
        field=field,
    )
    initial_evaluation_domain_length = coefficients_length * expansion_factor
    omega = field.primitive_root_of_unity(initial_evaluation_domain_length)
    initial_evaluation_domain = field(
        [(omega**i) for i in range(initial_evaluation_domain_length)]
    )
    query_indices_range = initial_evaluation_domain_length // folding_factor

    initial_evaluations = initial_polynomial(initial_evaluation_domain)
    initial_stacked_evaluations = stack(initial_evaluations, folding_factor)

    folded_polynomial = fold_polynomial(
        initial_polynomial, folding_randomness, folding_factor
    )
    folded_domain = fold_domain(initial_evaluation_domain, folding_factor)
    folded_evaluations = folded_polynomial(folded_domain)

    # This line yields wrong result.
    folded_stacked_evaluations = stack(folded_evaluations, folding_factor)

    query_ys = initial_stacked_evaluations[query_indices]

    extended_indices = extend_indices(
        query_indices, initial_evaluation_domain_length, folding_factor
    )

    unordered_folded_answers = []
    for ids, ys in zip(extended_indices, query_ys):
        xs = initial_evaluation_domain[ids]
        unordered_folded_answers.append(
            galois.lagrange_poly(xs, ys)(folding_randomness)
        )

    query_indices_range //= folding_factor
    query_indices, check_indices, folded_answers = fold_sort_generate(
        query_indices, query_indices_range, unordered_folded_answers
    )

    for check_index, computed_answer, ys in zip(
        check_indices, folded_answers, folded_stacked_evaluations[list(query_indices)]
    ):
        assert computed_answer == ys[check_index]
