"""Folding related functions."""


import typing
import galois
import numpy

from vc.base import is_pow2


# TODO: Rename.
def fold_sort_generate(
        query_indices: typing.List[int],
        query_indices_range: int,
        unordered_folded_values: galois.Array
        ) -> typing.Tuple:
    # Get array of tuples [(new_query_index, check_index, folded_value)]
    temp_collected_array = list(
    #    |-Next query index,        |-Check index,              |-Value.
    #    V                          V                           V
        (ids % query_indices_range, ids // query_indices_range, ufv)
        for ids, ufv in zip(query_indices, unordered_folded_values))

    # Sort array of tuples by new query index.
    temp_sorted_array = sorted(temp_collected_array, key=lambda x: x[0])

    seen = []
    deduped_array = []
    for element in temp_sorted_array:
        if element[0] in seen:
            continue

        seen.append(element[0])
        deduped_array.append(element)

    return zip(*deduped_array)

def fold_indices(
        indices: numpy.ndarray[int],
        indices_range: int
        ) -> numpy.ndarray[int]:
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


def extend_indices(
        indices: typing.Iterable[int],
        domain_length: int,
        folding_factor: int
        ) -> typing.List[typing.List[int]]:
    """Extend indices to be used for interpolation of stacked evaluations.

    :param indices: Indices corresponding to stacked evaluations rows.
    :type indices: typing.List[int]
    :param domain_length: Domain length.
    :type domain_length: int
    :param folding_factor: Folding factor.
    :type folding_factor: int
    :return: Extended indices.
    :rtype: typing.List[typing.List[int]]

    Examples
    --------

    .. code:: python
        assert all([[0, 8], [2, 10]] == extend_indices([0, 2], 8, 2))
    """

    return [
        [
            i + j*domain_length//folding_factor
            for j in range(folding_factor)
        ] for i in indices
    ]


def fold_polynomial(
        g: galois.Poly,
        randomness: int,
        folding_factor: int
        ) -> galois.Poly:
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

    new_domain = domain[:domain.size // folding_factor] ** folding_factor
    assert (domain.size // new_domain.size) == folding_factor

    return new_domain
