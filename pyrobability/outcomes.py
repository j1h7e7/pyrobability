from fractions import Fraction
import logging
from typing import Any

from pyrobability.types import EventNameType

logger = logging.getLogger(__name__)


class CustomDefaultDict:
    def __init__(self, outcomes_layer: "OutcomesLayer"):
        self.data = {}
        self.outcomes_layer = outcomes_layer

    def __getitem__(self, key):
        if key in self.data:
            return self.data[key]

        new_entry = ProbabilityNumber(
            outcomes_layer=self.outcomes_layer, outcome_name=key
        )
        self.data[key] = new_entry
        return new_entry

    def __setitem__(self, key, val):
        logger.info(f"Setting {key=} to {val=}")
        # if not isinstance(val, ProbabilityNumber):
        #     val = (
        #         ProbabilityNumber(outcomes_layer=self.outcomes_layer, outcome_name=key)
        #         + val
        #     )

        self.data[key] = val


class OutcomesLayer:
    def __init__(self):
        self.probs = CustomDefaultDict(self)
        self.children: dict[EventNameType, tuple[Fraction, OutcomesLayer]] = {}

    def new_layer(self, prob: Fraction, name: EventNameType):
        x = OutcomesLayer()
        self.children[name] = (prob, x)
        return x

    def get_prob(self, name: str):
        ans = 0
        ans += self.probs[name]
        for prob, child in self.children.values():
            ans += prob * child.get_prob(name)
        return ans


class ProbabilityNumber(Fraction):
    outcomes_layer: OutcomesLayer
    outcome_name: str

    def __new__(cls, *args, outcomes_layer: OutcomesLayer, outcome_name: str, **kwargs):
        self = super(ProbabilityNumber, cls).__new__(cls, *args, **kwargs)
        self.outcomes_layer = outcomes_layer
        self.outcome_name = outcome_name
        return self


class GlobalOutcomes:
    def __init__(self):
        self._root = OutcomesLayer()
        self._active = self._root

    def __getattr__(self, name: str):
        return self._root.probs[name]

    def __setattr__(self, name: str, value: Any):
        if name.startswith("_"):
            return object.__setattr__(self, name, value)
        else:
            self._active.probs[name] = value

    def get_prob(self, name):
        return self._root.get_prob(name)
