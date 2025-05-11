from fractions import Fraction
from pyrobability.experiments import Event, Experiment

from abc import ABC, abstractmethod
from typing import Any, Collection, Union

from pyrobability.types import EventNameType


class BaseRandomVariable(ABC):
    def __init__(self, events: dict[EventNameType, Fraction]):
        self.experiment = Experiment(events)
        self.events = self._initalize_events(self.experiment)

    @abstractmethod
    def _initalize_events(self, experiment: Experiment): ...

    def event(self, name: EventNameType):
        return self.events[name]


OutcomeType = Union[str, BaseRandomVariable]


class BaseGlobalOutcomes(ABC):
    @abstractmethod
    def _get_outcome(self, name: OutcomeType): ...

    @abstractmethod
    def _set_outcome(self, name: OutcomeType, value: Any): ...

    def __getattr__(self, name: OutcomeType):
        return self._get_outcome(name)

    def __setattr__(self, name: OutcomeType, value: Any):
        if name.startswith("_"):  # to avoid infinite loops
            return object.__setattr__(self, name, value)
        else:
            return self._set_outcome(name, value)

    def __getitem__(self, name: OutcomeType):
        return self._get_outcome(name)

    def __setitem__(self, name: OutcomeType, value: Any):
        return self._set_outcome(name, value)

    @abstractmethod
    def add_events(self, events: list[Event]): ...

    @abstractmethod
    def remove_events(self, events: list[Event]): ...

    @property
    @abstractmethod
    def _active_experiments(self) -> Collection[Experiment]: ...

    @abstractmethod
    def _get_experiment_current_active_event(self, experiment: Experiment) -> Event: ...
