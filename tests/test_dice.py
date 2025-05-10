from fractions import Fraction

import pytest
from pyrobability import Manager


def test_d6():
    m = Manager()
    o = m.outcomes

    roll = m.dice(6)

    with roll.event(1):
        o.one += 1

    assert o.get_prob("one") == Fraction(1, 6)


@pytest.mark.parametrize("sides", [0, -1])
def test_invalid_die(sides):
    m = Manager()

    with pytest.raises(ValueError):
        m.dice(sides)
