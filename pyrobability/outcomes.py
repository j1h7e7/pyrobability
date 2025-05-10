from collections import defaultdict
from fractions import Fraction
import logging
from typing import Any, MutableMapping

from pyrobability.experiments import Event, Experiment, get_probability

logger = logging.getLogger(__name__)


class EventSet:
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


class ProbabilityNumber(Fraction):
    """
    Subclass of Fraction that remembers the name of the outcome
    """

    outcome_name: str

    # we use __new__ here since Fraction uses slots
    def __new__(cls, *args, outcome_name: str, **kwargs):
        self = super(ProbabilityNumber, cls).__new__(cls, *args, **kwargs)
        self.outcome_name = outcome_name
        return self


class GlobalOutcomes:
    """
    "global" outcomes object. Used so that consumers can hold onto a single reference
    to this object, and have the underlying OutcomesLayer changed on the fly
    when entering a ProbabilityContextManager
    """

    def __init__(self):
        self._active_events: EventSet = EventSet()
        self._outcomes: MutableMapping[
            str, list[tuple[tuple[Event, ...], Fraction]]
        ] = defaultdict(list)

    def __getattr__(self, name: str):
        return ProbabilityNumber(outcome_name=name)

    def __setattr__(self, name: str, value: Any):
        if name.startswith("_"):  # to avoid infinite loops
            return object.__setattr__(self, name, value)
        # implict "else"

        current_events = tuple(self._active_events)
        self._outcomes[name].append((current_events, value))

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

    def get_prob(self, name: str):
        outcomes = self._outcomes[name]

        return sum(value * get_probability(events) for events, value in outcomes)
