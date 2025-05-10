from collections import defaultdict
from fractions import Fraction
import logging
from typing import Any, Optional

logger = logging.getLogger(__name__)


class Manager:
    def __init__(self):
        self.outcomes = Outcomes()

    def coinflip(self, prob: Fraction | float | str):
        if not isinstance(prob, Fraction):
            prob = Fraction(prob)
        heads = ProbabilityContextManager(self.outcomes, prob)
        tails = ProbabilityContextManager(self.outcomes, 1 - prob)
        return heads, tails


class OutcomesLayer:
    def __init__(self, parent: Optional["OutcomesLayer"]):
        self.parent = parent
        self.probs = defaultdict(Fraction)
        self.children: list[tuple[Fraction, OutcomesLayer]] = []

    def new_layer(self, prob: Fraction):
        x = OutcomesLayer(self)
        self.children.append((prob, x))
        return x

    def get_prob(self, name: str):
        ans = 0
        ans += self.probs[name]
        for prob, child in self.children:
            ans += prob * child.get_prob(name)
        return ans


class Outcomes:
    def __init__(self):
        self._root = OutcomesLayer(None)
        self._active = self._root

    def __getattr__(self, name: str):
        return self._root.probs[name]

    def __setattr__(self, name: str, value: Any):
        if name.startswith("_"):
            return object.__setattr__(self, name, value)
        else:
            self._active.probs[name] = value

    def _add_level(self, prob: Fraction):
        self._active = self._active.new_layer(prob)

    def _remove_level(self):
        if not self._active.parent:
            logger.error("Tried to remove the lowest layer")
            raise ValueError

        self._active = self._active.parent

    def get_prob(self, name):
        return self._root.get_prob(name)


class ProbabilityContextManager:
    def __init__(self, outcomes: Outcomes, prob: Fraction):
        self.outcomes = outcomes
        self.prob = prob

    def __enter__(self):
        logger.info("Entered context")
        self.outcomes._add_level(self.prob)

    def __exit__(self, _exc_type, _exc_value, _traceback):
        logger.info("Exiting context")
        self.outcomes._remove_level()
