from collections import defaultdict
from fractions import Fraction
import logging
from typing import Any, MutableMapping

from pyrobability.abcs import BaseGlobalOutcomes, BaseRandomVariable, OutcomeType
from pyrobability.experiments import Event, Experiment, get_probability
from pyrobability.types import ProbabilityNumber


logger = logging.getLogger(__name__)


class EventSet:
    """
    Implementation of a multiset to allow the same event multiple times
    """

    def __init__(self):
        self.counts: dict[Event, int] = {}

    def add(self, value: Event):
        if value not in self.counts:
            self.counts[value] = 0
        self.counts[value] += 1

    def remove(self, value: Event):
        self.counts[value] -= 1
        if self.counts[value] == 0:
            del self.counts[value]

    def __iter__(self):
        return iter(self.counts.keys())


class GlobalOutcomes(BaseGlobalOutcomes):
    """
    "global" outcomes object. Used so that consumers can hold onto a single reference
    to this object, and have the context managers handle the events
    """

    def __init__(self):
        super().__init__()
        self._active_events: EventSet = EventSet()
        self._outcomes: MutableMapping[
            str, list[tuple[tuple[Event, ...], Fraction]]
        ] = defaultdict(list)

    def _get_outcome(self, name: OutcomeType):
        return ProbabilityNumber(outcome_name=name)

    def _set_outcome(self, name: OutcomeType, value: Any):
        current_events = tuple(self._active_events)

        if isinstance(name, BaseRandomVariable):
            return self._set_outcome_random_variable(name, value)

        self._outcomes[name].append((current_events, value))

    def _set_outcome_random_variable(self, rv: BaseRandomVariable, value: Any):
        logger.info("Using random variable as an outcome")
        if rv.experiment in self._active_experiments:
            event = self._get_experiment_current_active_event(rv.experiment)
            name = event.name
            self._set_outcome(name, value)
        else:
            for event in rv.experiment.events.values():
                self._active_events.add(event)
                self._set_outcome(event.name, value)
                self._active_events.remove(event)

    @property
    def _active_experiments(self):
        return set(event.experiment for event in self._active_events)

    def _get_experiment_current_active_event(self, experiment: Experiment):
        for event in self._active_events:
            if event.experiment == experiment:
                return event
        raise ValueError

    def add_events(self, events: list[Event]):
        for event in events:
            self._active_events.add(event)

    def remove_events(self, events: list[Event]):
        for event in events:
            self._active_events.remove(event)

    @property
    def outcomes(self):
        return self._outcomes.keys()

    def get_prob(self, name: str):
        outcomes = self._outcomes[name]

        return sum(value * get_probability(events) for events, value in outcomes)
