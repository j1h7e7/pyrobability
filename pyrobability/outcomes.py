from collections import defaultdict
from fractions import Fraction
import logging
from typing import Any

logger = logging.getLogger(__name__)


class OutcomesLayer:
    def __init__(self):
        self.probs = defaultdict(Fraction)
        self.children: list[tuple[Fraction, OutcomesLayer]] = []

    def new_layer(self, prob: Fraction):
        x = OutcomesLayer()
        self.children.append((prob, x))
        return x

    def get_prob(self, name: str):
        ans = 0
        ans += self.probs[name]
        for prob, child in self.children:
            ans += prob * child.get_prob(name)
        return ans


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
