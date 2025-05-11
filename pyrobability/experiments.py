from abc import ABC, abstractmethod
from dataclasses import dataclass
from fractions import Fraction
import functools
import logging
from typing import Collection
import uuid
from pyrobability.types import EventNameType


logger = logging.getLogger(__name__)


class BaseEvent(ABC):
    experiment: "Experiment"

    @abstractmethod
    def get_probability(self) -> Fraction: ...

    @abstractmethod
    def __hash__(self): ...


@dataclass(frozen=True)
class SimpleEvent(BaseEvent):
    probability: Fraction
    experiment: "Experiment"
    name: EventNameType

    def get_probability(self):
        return self.probability


class ExperimentOrEvent(BaseEvent):
    def __init__(self, events: list[SimpleEvent]):
        experiments = {event.experiment for event in events}
        if len(experiments) > 1:
            raise TypeError("All events must be from the same experiment")

        self.experiment = experiments.pop()
        self.events = events
        self.name = " OR ".join(event.name for event in events)

    def __hash__(self):
        return hash(sum(hash(e) for e in self.events))

    def get_probability(self):
        return sum(e.get_probability() for e in self.events)


class Experiment:
    events: dict[EventNameType, SimpleEvent]

    def __init__(self, events: dict[EventNameType, Fraction]):
        self._experiment_id = uuid.uuid4()
        self.events = {}
        for event_name, event_probability in events.items():
            self.events[event_name] = SimpleEvent(
                probability=event_probability,
                experiment=self,
                name=event_name,
            )

    def __hash__(self):
        return hash(self._experiment_id)


def get_probability(events: Collection[BaseEvent]):
    logger.info(f"Calculating probability of {events=}")
    experiments = [event.experiment for event in events]

    # check if all experiments are unique
    if len(set(experiments)) < len(experiments):
        raise ValueError(
            "Cannot determine joint probability of two events from the same experiment"
        )

    probabilities = [event.get_probability() for event in events]
    return functools.reduce(Fraction.__mul__, probabilities, Fraction(1))
