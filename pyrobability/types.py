from fractions import Fraction


EventNameType = str | int


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
