import galois
import pytest

from vc.constants import TEST_FIELD
from vc.fold import extend_indices, fold_domain, fold_polynomial, fold_sort_generate
from vc.polynomial import stack


@pytest.mark.parametrize(
    'expected, polynomial_coefficients, randomness, folding_factor',
    [
        # x + 1 = [1, 1] -> 1 + 1*1 = 2
        ([2], [1, 1], 1, 2),
        # x^3 + 2x^2 + 2x + 1 = [1, 2, 2, 1] -> [[1, 2], [2, 1]] -> [1 + 1*2, 2 + 1*1] = [3, 3]
        ([3, 3], [1, 2, 2, 1], 1, 2),
        # 1 + ... + 8x^7 = [1, 2, 3, 4, 5, 6, 7, 8] -> [[1, 2], [3, 4], [5, 6], [7, 8]] ->
        # [1 + 2*2, 3 + 2*4, 5 + 2*6, 7 + 2*8] = [5, 11, 17, 23]
        ([5, 11, 17, 23], [1, 2, 3, 4, 5, 6, 7, 8], 2, 2)
    ])
def test_fold(
        expected: galois.Array,
        polynomial_coefficients: galois.Array,
        randomness: int,
        folding_factor: int
        ) -> None:
    g = galois.Poly(polynomial_coefficients, field=TEST_FIELD, order='asc')
    g_folded = fold_polynomial(g, randomness, folding_factor)

    assert g_folded == galois.Poly(expected, field=g.field, order='asc')


def test_consistency_check():
    seed = 2
    field = TEST_FIELD
    coefficients_length_log = 3
    folding_factor = 2
    expansion_factor = 2
    query_indices = [1]

    folding_randomness = field.Random(seed=seed)
    coefficients_length = 1 << coefficients_length_log
    degree = coefficients_length - 1
    initial_polynomial = galois.Poly.Random(degree, field=field, seed=seed)
    initial_evaluation_domain_length = coefficients_length * expansion_factor
    offset = field.primitive_element
    omega = field.primitive_root_of_unity(initial_evaluation_domain_length)
    initial_evaluation_domain = field(
        [offset * (omega ** i) for i in range(initial_evaluation_domain_length)])
    query_indices_range = initial_evaluation_domain_length // folding_factor

    initial_evaluations = initial_polynomial(initial_evaluation_domain)
    initial_stacked_evaluations = stack(initial_evaluations, folding_factor)

    folded_polynomial = fold_polynomial(
        initial_polynomial,
        folding_randomness,
        folding_factor)
    # folded_evaluations = folded_polynomial(initial_evaluation_domain)
    # folded_stacked_evaluations = stack(folded_evaluations, folding_factor)
    folded_domain_length = initial_evaluation_domain_length // folding_factor
    folded_domain = fold_domain(initial_evaluation_domain, folding_factor)
    folded_evaluations = folded_polynomial(folded_domain)
    folded_stacked_evaluations = stack(folded_evaluations, folding_factor)

    query_xs = initial_evaluation_domain[query_indices]
    query_ys = initial_stacked_evaluations[query_indices]

    extended_indices = extend_indices(
        query_indices,
        initial_evaluation_domain_length,
        folding_factor)

    unordered_folded_answers = []
    for ids, ys in zip(extended_indices, query_ys):
        xs = initial_evaluation_domain[ids]
        unordered_folded_answers.append(
            galois.lagrange_poly(xs, ys)(folding_randomness))

    query_indices_range //= folding_factor
    query_indices, check_indices, folded_answers = fold_sort_generate(
        query_indices, query_indices_range, unordered_folded_answers)

    for check_index, computed_answer, ys in zip(
            check_indices, folded_answers, folded_stacked_evaluations[list(query_indices)]):
        result = computed_answer == ys[check_index]

    pass
