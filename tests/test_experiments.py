from fractions import Fraction
import pytest

from pyrobability.experiments import Experiment, get_probability


def test_simple_experiment():
    experiment = Experiment({"heads": Fraction(1, 2), "tails": Fraction(1, 2)})

    heads = experiment.events["heads"]

    assert get_probability([heads]) == 0.5


def test_multiple_events():
    experiment1 = Experiment({"heads": Fraction(1, 2), "tails": Fraction(1, 2)})
    experiment2 = Experiment({"heads": Fraction(1, 2), "tails": Fraction(1, 2)})

    heads1 = experiment1.events["heads"]
    heads2 = experiment2.events["tails"]

    assert get_probability([heads1]) == 0.5
    assert get_probability([heads2]) == 0.5
    assert get_probability([heads1, heads2]) == 0.25


def test_conflicting_events():
    experiment = Experiment({"heads": Fraction(1, 2), "tails": Fraction(1, 2)})

    heads = experiment.events["heads"]
    tails = experiment.events["tails"]

    with pytest.raises(ValueError):
        get_probability([heads, tails])
