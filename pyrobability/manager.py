from fractions import Fraction
import logging
from pyrobability.abcs import (
    BaseGlobalOutcomes,
    BaseProbabilityContextManager,
    BaseRandomVariable,
)
from pyrobability.experiments import Event
from pyrobability.types import EventNameType, ProbabilityNumber

logger = logging.getLogger(__name__)


class ProbabilityContextManager(BaseProbabilityContextManager):
    def __init__(self, outcomes: BaseGlobalOutcomes, events: list[Event]):
        super().__init__(outcomes)
        self.events = events

    def __enter__(self):
        logger.info("Entered context")
        self.outcomes.add_events(self.events)

    def __exit__(self, exc_type, exc_value, traceback):
        logger.info("Exiting context")
        self.outcomes.remove_events(self.events)


class RandomVariable(BaseRandomVariable):
    def __init__(
        self, outcomes: BaseGlobalOutcomes, events: dict[EventNameType, Fraction]
    ):
        self.outcomes = outcomes
        super().__init__(events)

    def _initalize_events(self, experiment):
        return {
            event_name: ProbabilityContextManager(
                outcomes=self.outcomes, events=[event]
            )
            for event_name, event in experiment.events.items()
        }


class NumericRandomVariable(RandomVariable):
    events: dict[int, Fraction]

    def __init__(self, outcomes, events):
        super().__init__(outcomes, events)

    def __radd__(self, other):
        if not isinstance(other, ProbabilityNumber):
            raise TypeError

        outcome_name = other.outcome_name

        if self.experiment in self.outcomes._active_experiments:
            event = self.outcomes._get_experiment_current_active_event(self.experiment)
            setattr(self.outcomes, outcome_name, event.name)
            return other

        for event_key, event in self.experiment.events.items():
            self.outcomes.add_events([event])
            setattr(self.outcomes, outcome_name, event_key)
            self.outcomes.remove_events([event])

        return other


class CoinFlip(RandomVariable):
    heads: ProbabilityContextManager
    tails: ProbabilityContextManager

    def __init__(self, outcomes: BaseGlobalOutcomes, prob: Fraction):
        super().__init__(outcomes, {"heads": prob, "tails": 1 - prob})
        self.prob = prob
        self.heads = self.event("heads")
        self.tails = self.event("tails")
