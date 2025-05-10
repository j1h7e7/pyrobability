from fractions import Fraction
import logging
from pyrobability.outcomes import Outcomes

logger = logging.getLogger(__name__)


class Manager:
    def __init__(self):
        self.outcomes = Outcomes()

    def coinflip(self, prob: Fraction | float | str):
        if not isinstance(prob, Fraction):
            prob = Fraction(prob)
        return CoinFlip(self.outcomes, prob)


class ProbabilityContextManager:
    def __init__(self, outcomes: Outcomes, prob: Fraction):
        self.outcomes = outcomes
        self.prob = prob

    def __enter__(self):
        logger.info("Entered context")
        self.outcomes._add_level(self.prob)

    def __exit__(self, _exc_type, _exc_value, _traceback):
        logger.info("Exiting context")
        self.outcomes._remove_level()


class CoinFlip:
    heads: ProbabilityContextManager
    tails: ProbabilityContextManager

    def __init__(self, outcomes: Outcomes, prob: Fraction):
        self.prob = prob
        self.heads = ProbabilityContextManager(outcomes, prob)
        self.tails = ProbabilityContextManager(outcomes, 1 - prob)
