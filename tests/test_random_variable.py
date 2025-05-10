from fractions import Fraction
from pyrobability.manager import Manager, NumericRandomVariable, RandomVariable


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


def test_random_variable_or():
    m = Manager()
    o = m.outcomes

    rv = RandomVariable(
        o, {"e1": Fraction(1, 2), "e2": Fraction(1, 4), "e3": Fraction(1 / 4)}
    )

    with rv.event("e1") | rv.event("e2"):
        o.hit += 1

    assert o.get_prob("hit") == 0.75


def test_numeric_random_variable():
    m = Manager()
    o = m.outcomes

    rv = NumericRandomVariable(o, {1: Fraction(1, 2), 2: Fraction(1, 2)})

    o.hit += rv

    assert o.get_prob("hit") == 1.5
