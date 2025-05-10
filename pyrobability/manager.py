from fractions import Fraction
import logging
from pyrobability.outcomes import GlobalOutcomes, ProbabilityNumber
from pyrobability.types import EventNameType

logger = logging.getLogger(__name__)


class Manager:
    def __init__(self):
        self.outcomes = GlobalOutcomes()

    def coinflip(self, prob: Fraction | float | str):
        if not isinstance(prob, Fraction):
            prob = Fraction(prob)
        return CoinFlip(self.outcomes, prob)


class ProbabilityContextManager:
    def __init__(self, outcomes: GlobalOutcomes, prob: Fraction, name: EventNameType):
        self.outcomes = outcomes
        self.prob = prob
        self.name = name
        # TODO: should we bind the event at RV creation time, or at __enter__ time?
        # currently we do it at __enter__, which allows you to "pre-flip" coins

    def __enter__(self):
        logger.info("Entered context")
        self._enclosing_scope = self.outcomes._active

        self.outcomes._active = self.outcomes._active.new_layer(
            prob=self.prob, name=self.name
        )

    def __exit__(self, _exc_type, _exc_value, _traceback):
        logger.info("Exiting context")

        self.outcomes._active = self._enclosing_scope

    def __or__(self, other):
        if not isinstance(other, ProbabilityContextManager):
            raise TypeError

        return ProbabilityContextManager(
            outcomes=self.outcomes, prob=self.prob + other.prob, name=""
        )


class RandomVariable:
    def __init__(self, outcomes: GlobalOutcomes, events: dict[EventNameType, Fraction]):
        self.outcomes = outcomes
        self.events = {
            event_name: ProbabilityContextManager(
                outcomes=outcomes, prob=prob, name=event_name
            )
            for event_name, prob in events.items()
        }

    def event(self, name: EventNameType):
        return self.events[name]


class NumericRandomVariable(RandomVariable):
    events: dict[int, Fraction]

    def __init__(self, outcomes, events):
        super().__init__(outcomes, events)

    def __radd__(self, other):
        if not isinstance(other, ProbabilityNumber):
            raise TypeError

        outcomes_layer = other.outcomes_layer
        for event_name, event in self.events.items():
            if event_name not in outcomes_layer.children:
                outcomes_layer.new_layer(event.prob, event_name)

            _, layer = outcomes_layer.children[event_name]
            outcome_name = other.outcome_name
            layer.probs[outcome_name] += event_name

        return other


class CoinFlip(RandomVariable):
    heads: ProbabilityContextManager
    tails: ProbabilityContextManager

    def __init__(self, outcomes: GlobalOutcomes, prob: Fraction):
        super().__init__(outcomes, {"heads": prob, "tails": 1 - prob})
        self.prob = prob
        self.heads = self.event("heads")
        self.tails = self.event("tails")
