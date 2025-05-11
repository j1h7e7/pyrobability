from fractions import Fraction
from pyrobability.experiments import SimpleEvent, Experiment

from abc import ABC, abstractmethod
from typing import Any, Collection, Union

from pyrobability.types import EventNameType


class BaseRandomVariable(ABC):
    def __init__(self, events: dict[EventNameType, Fraction]):
        self.experiment = Experiment(events)
        self.events = self._initalize_events(self.experiment)

    @abstractmethod
    def _initalize_events(
        self, experiment: Experiment
    ) -> dict[EventNameType, "BaseProbabilityContextManager"]: ...

    def event(self, name: EventNameType) -> "BaseProbabilityContextManager":
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
    def add_events(self, events: list[SimpleEvent]): ...

    @abstractmethod
    def remove_events(self, events: list[SimpleEvent]): ...

    @property
    @abstractmethod
    def _active_experiments(self) -> Collection[Experiment]: ...

    @abstractmethod
    def _get_experiment_current_active_event(
        self, experiment: Experiment
    ) -> SimpleEvent: ...


class BaseProbabilityContextManager(ABC):
    def __init__(self, *, outcomes: BaseGlobalOutcomes):
        self.outcomes = outcomes
        # TODO: should we bind the event at RV creation time, or at __enter__ time?
        # currently we do it at __enter__, which allows you to "pre-flip" coins

    @abstractmethod
    def __enter__(self): ...

    @abstractmethod
    def __exit__(self, exc_type, exc_value, traceback): ...

    def __and__(self, other):
        if not isinstance(other, BaseProbabilityContextManager):
            raise TypeError

        return UnionProbabilityContextManager(self, other, outcomes=self.outcomes)


class UnionProbabilityContextManager(BaseProbabilityContextManager):
    def __init__(
        self,
        *others: BaseProbabilityContextManager,
        outcomes: BaseGlobalOutcomes,
    ):
        super().__init__(outcomes=outcomes)
        self.others = others

    def __enter__(self):
        for other in self.others:
            other.__enter__()

    def __exit__(self, exc_type, exc_value, traceback):
        for other in self.others:
            other.__exit__(exc_type, exc_value, traceback)
