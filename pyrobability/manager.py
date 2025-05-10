from fractions import Fraction
import logging
from pyrobability.experiments import Event, Experiment
from pyrobability.outcomes import GlobalOutcomes, ProbabilityNumber
from pyrobability.types import EventNameType

logger = logging.getLogger(__name__)


class Manager:
    """
    Interface for easier instantiation of RandomVariables
    """

    def __init__(self):
        self.outcomes = GlobalOutcomes()

    def coinflip(self, prob: Fraction | float | str):
        if not isinstance(prob, Fraction):
            prob = Fraction(prob)
        return CoinFlip(self.outcomes, prob)


class ProbabilityContextManager:
    def __init__(self, outcomes: GlobalOutcomes, events: list[Event]):
        self.outcomes = outcomes
        self.events = events
        # TODO: should we bind the event at RV creation time, or at __enter__ time?
        # currently we do it at __enter__, which allows you to "pre-flip" coins

    def __enter__(self):
        logger.info("Entered context")
        self.outcomes.add_events(self.events)

    def __exit__(self, _exc_type, _exc_value, _traceback):
        logger.info("Exiting context")
        self.outcomes.remove_events(self.events)


class RandomVariable:
    def __init__(self, outcomes: GlobalOutcomes, events: dict[EventNameType, Fraction]):
        self.experiment = Experiment(events)
        self.outcomes = outcomes
        self.events = {
            event_name: ProbabilityContextManager(outcomes=outcomes, events=[event])
            for event_name, event in self.experiment.events.items()
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

    def __init__(self, outcomes: GlobalOutcomes, prob: Fraction):
        super().__init__(outcomes, {"heads": prob, "tails": 1 - prob})
        self.prob = prob
        self.heads = self.event("heads")
        self.tails = self.event("tails")
