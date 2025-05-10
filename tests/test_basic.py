from fractions import Fraction
import pytest
from pyrobability.manager import Manager


def test_simple_coin_flip():
    m = Manager()
    o = m.outcomes

    heads, tails = m.coinflip(0.5)
    with heads:
        o.heads += 1
    with tails:
        o.tails += 1

    assert o.probs["heads"] == 0.5
    assert o.probs["tails"] == 0.5


def test_nested_coin_flip():
    m = Manager()
    o = m.outcomes

    h1, t1 = m.coinflip(0.5)
    h2, t2 = m.coinflip(0.5)

    with h1:
        with h2:
            o.HH += 1
        with t2:
            o.HT += 1
    with t1:
        with h2:
            o.TH += 1
        with t2:
            o.TT += 1

    assert o.probs["HH"] == 0.25
    assert o.probs["HT"] == 0.25
    assert o.probs["TH"] == 0.25
    assert o.probs["TT"] == 0.25


@pytest.mark.parametrize("probability", [Fraction(0.1), Fraction(0.2), Fraction(0.9)])
def test_biased_coin(probability):
    m = Manager()
    o = m.outcomes

    heads, tails = m.coinflip(probability)

    with heads:
        o.heads += 1
    with tails:
        o.tails += 1

    assert o.probs["heads"] == probability
    assert o.probs["tails"] == 1 - probability
