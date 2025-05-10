from fractions import Fraction

from pyrobability import Manager


def test_basic_selection():
    m = Manager()
    o = m.outcomes

    choice = m.selection(["heads", "tails"])

    with choice.event("heads"):
        o["heads"] += 1

    assert o.get_prob("heads") == Fraction(1, 2)


def test_advanced_selection():
    m = Manager()
    o = m.outcomes

    choice = m.selection(["a", "a", "a", 2, 2])

    with choice.event("a"):
        o["a"] += 1
    with choice.event(2):
        o["b"] += 1

    assert o.get_prob("a") == Fraction(3, 5)
    assert o.get_prob("b") == Fraction(2, 5)
