from fractions import Fraction
import logging
from typing import Any

from pyrobability.types import EventNameType

logger = logging.getLogger(__name__)


class CustomDefaultDict:
    """
    Reimplementation of defaultdict, used to make sure we can initialize the values
    with a reference to their key
    """

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
        # represents all outcomes at this layer
        self.probs = CustomDefaultDict(self)
        # represents all sub-events
        self.children: dict[EventNameType, tuple[Fraction, OutcomesLayer]] = {}

    def new_layer(self, prob: Fraction, name: EventNameType):
        x = OutcomesLayer()
        # store the sub-event by name, with the sub-probability included
        self.children[name] = (prob, x)
        return x

    def get_prob(self, name: str):
        ans = 0
        # get contribution from this layer
        ans += self.probs[name]
        # get contribution from sub-layers
        for prob, child in self.children.values():
            ans += prob * child.get_prob(name)
        return ans


class ProbabilityNumber(Fraction):
    """
    Subclass of Fraction that remembers the current OutcomeLayer it is attached to,
    as well as the name of the outcome
    """

    outcomes_layer: OutcomesLayer
    outcome_name: str

    # we use __new__ here since Fraction uses slots
    def __new__(cls, *args, outcomes_layer: OutcomesLayer, outcome_name: str, **kwargs):
        self = super(ProbabilityNumber, cls).__new__(cls, *args, **kwargs)
        self.outcomes_layer = outcomes_layer
        self.outcome_name = outcome_name
        return self


class GlobalOutcomes:
    """
    "global" outcomes object. Used so that consumers can hold onto a single reference
    to this object, and have the underlying OutcomesLayer changed on the fly
    when entering a ProbabilityContextManager
    """

    def __init__(self):
        self._root = OutcomesLayer()
        self._active = self._root

    def __getattr__(self, name: str):
        # get the count of an outcome from (only) the current layer
        return self._root.probs[name]

    def __setattr__(self, name: str, value: Any):
        if name.startswith("_"):  # to avoid infinite loops
            return object.__setattr__(self, name, value)
        else:
            # set the count of an outcome to (only) the current layer
            self._active.probs[name] = value

    def get_prob(self, name):
        # will calculate from the root
        if self._root is not self._active:
            logger.warning("Executing get_prob while inside an event.")

        return self._root.get_prob(name)
