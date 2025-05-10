from fractions import Fraction
import logging
from pyrobability.outcomes import GlobalOutcomes

logger = logging.getLogger(__name__)


class Manager:
    def __init__(self):
        self.outcomes = GlobalOutcomes()

    def coinflip(self, prob: Fraction | float | str):
        if not isinstance(prob, Fraction):
            prob = Fraction(prob)
        return CoinFlip(self.outcomes, prob)


class ProbabilityContextManager:
    def __init__(self, outcomes: GlobalOutcomes, prob: Fraction):
        self.outcomes = outcomes
        self.prob = prob
        # TODO: should we bind the event at RV creation time, or at __enter__ time?
        # currently we do it at __enter__, which allows you to "pre-flip" coins

    def __enter__(self):
        logger.info("Entered context")
        self._enclosing_scope = self.outcomes._active

        self.outcomes._active = self.outcomes._active.new_layer(self.prob)

    def __exit__(self, _exc_type, _exc_value, _traceback):
        logger.info("Exiting context")

        self.outcomes._active = self._enclosing_scope

    def __or__(self, other):
        if not isinstance(other, ProbabilityContextManager):
            raise TypeError

        return ProbabilityContextManager(
            outcomes=self.outcomes, prob=self.prob + other.prob
        )


class RandomVariable:
    def __init__(self, outcomes: GlobalOutcomes, events: dict[str, Fraction]):
        self.outcomes = outcomes
        self.events = {
            event_name: ProbabilityContextManager(outcomes, prob)
            for event_name, prob in events.items()
        }

    def event(self, name: str):
        return self.events[name]


class CoinFlip(RandomVariable):
    heads: ProbabilityContextManager
    tails: ProbabilityContextManager

    def __init__(self, outcomes: GlobalOutcomes, prob: Fraction):
        super().__init__(outcomes, {"heads": prob, "tails": 1 - prob})
        self.prob = prob
        self.heads = self.event("heads")
        self.tails = self.event("tails")
