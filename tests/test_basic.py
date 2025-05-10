from fractions import Fraction
import pytest
from pyrobability.manager import Manager


def test_simple_coin_flip():
    m = Manager()
    o = m.outcomes

    flip = m.coinflip(0.5)
    with flip.heads:
        o.heads += 1
    with flip.tails:
        o.tails += 1

    assert o.get_prob("heads") == 0.5
    assert o.get_prob("tails") == 0.5


def test_nested_coin_flip():
    m = Manager()
    o = m.outcomes

    flip1 = m.coinflip(0.5)
    flip2 = m.coinflip(0.5)

    with flip1.heads:
        with flip2.heads:
            o.HH += 1
        with flip2.tails:
            o.HT += 1
    with flip1.tails:
        with flip2.heads:
            o.TH += 1
        with flip2.tails:
            o.TT += 1

    assert o.get_prob("HH") == 0.25
    assert o.get_prob("HT") == 0.25
    assert o.get_prob("TH") == 0.25
    assert o.get_prob("TT") == 0.25


@pytest.mark.parametrize(
    "probability", [Fraction(1, 10), Fraction(1, 5), Fraction(9, 10)]
)
def test_biased_coin(probability):
    m = Manager()
    o = m.outcomes

    flip = m.coinflip(probability)
    with flip.heads:
        o.heads += 1
    with flip.tails:
        o.tails += 1

    assert o.get_prob("heads") == probability
    assert o.get_prob("tails") == 1 - probability
