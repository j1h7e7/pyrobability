from dataclasses import dataclass
from fractions import Fraction
import functools
import uuid
from pyrobability.types import EventNameType


@dataclass
class Event:
    probability: Fraction
    experiment: "Experiment"


class Experiment:
    events: dict[EventNameType, Event]

    def __init__(self, events: dict[EventNameType, Fraction]):
        self._experiment_id = uuid.uuid4()
        self.events = {}
        for event_name, event_probability in events.items():
            self.events[event_name] = Event(
                probability=event_probability, experiment=self
            )

    def __hash__(self):
        return hash(self._experiment_id)


def get_probability(events: list[Event]):
    experiments = [event.experiment for event in events]

    # check if all experiments are unique
    if len(set(experiments)) < len(experiments):
        raise ValueError(
            "Cannot determine joint probability of two events from the same experiment"
        )

    probabilities = [event.probability for event in events]
    return functools.reduce(Fraction.__mul__, probabilities, Fraction(1))
