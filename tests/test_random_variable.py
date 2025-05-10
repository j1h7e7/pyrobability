from fractions import Fraction
from pyrobability.manager import Manager, RandomVariable


def test_basic_random_variable():
    m = Manager()
    o = m.outcomes

    rv = RandomVariable(
        o, {"e1": Fraction(1, 2), "e2": Fraction(1, 4), "e3": Fraction(1 / 4)}
    )

    with rv.event("e1"):
        o.e1 += 1
    with rv.event("e2"):
        o.e2 += 1
    with rv.event("e3"):
        o.e3 += 1

    assert o.get_prob("e1") == 0.5
    assert o.get_prob("e2") == 0.25
    assert o.get_prob("e3") == 0.25
