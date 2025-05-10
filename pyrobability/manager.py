from collections import defaultdict, deque
from fractions import Fraction
import logging
from typing import Any

logger = logging.getLogger(__name__)


class Manager:
    def __init__(self):
        self.outcomes = Outcomes()

    def coinflip(self, prob: Fraction | float | str):
        prob = Fraction(prob)
        heads = ProbabilityContextManager(self.outcomes, prob)
        tails = ProbabilityContextManager(self.outcomes, 1 - prob)
        return heads, tails


class Outcomes:
    def __init__(self):
        self._outcomes_stack = deque([defaultdict(Fraction)])

    @property
    def probs(self):
        return self._outcomes_stack[-1]

    def __getattr__(self, name: str):
        return self.probs[name]

    def __setattr__(self, name: str, value: Any):
        if name.startswith("_"):
            return object.__setattr__(self, name, value)
        else:
            self.probs[name] = value

    def _add_level(self):
        self._outcomes_stack.append(defaultdict(Fraction))

    def _remove_level(self, prob: Fraction):
        if len(self._outcomes_stack) < 2:
            logger.error("Tried to remove the lowest layer")
            raise ValueError

        old_probs = self._outcomes_stack.pop()
        for k, v in old_probs.items():
            self.probs[k] += v * prob


class ProbabilityContextManager:
    def __init__(self, outcomes: Outcomes, prob: Fraction):
        self.outcomes = outcomes
        self.prob = prob

    def __enter__(self):
        logger.info("Entered context")
        self.outcomes._add_level()

    def __exit__(self, _exc_type, _exc_value, _traceback):
        logger.info("Exiting context")
        self.outcomes._remove_level(self.prob)
