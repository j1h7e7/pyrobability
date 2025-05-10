from collections import Counter
from fractions import Fraction
from pyrobability.manager import CoinFlip, RandomVariable
from pyrobability.outcomes import GlobalOutcomes
from pyrobability.types import EventNameType


class Manager:
    """
    Interface for easier instantiation of RandomVariables
    """

    def __init__(self):
        self.outcomes = GlobalOutcomes()

    def coinflip(self, prob: Fraction | float | str = 0.5):
        if not isinstance(prob, Fraction):
            prob = Fraction(prob)
        return CoinFlip(self.outcomes, prob)

    def dice(self, sides: int):
        if sides < 1:
            raise ValueError
        return RandomVariable(
            self.outcomes, {i: Fraction(1, sides) for i in range(1, sides + 1)}
        )

    def selection(self, possibilites: list[EventNameType]):
        c = Counter(possibilites)
        n = len(possibilites)

        return RandomVariable(
            self.outcomes, {name: Fraction(val, n) for name, val in c.items()}
        )
