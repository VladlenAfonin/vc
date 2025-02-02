import galois


def polynomial_quotient(g: galois.Poly, xs: galois.Array) -> galois.Poly:
    return g // galois.Poly.Roots(xs)


def degree_correct(g: galois.Poly, r: int, n: int) -> galois.Poly:
    # Generate polynomial 1 + rx + (rx)^2 + ... + (rx)^n.
    random_polynomial = galois.Poly([r ** power for power in range(n + 1)], field=g.field)
    return g * random_polynomial
