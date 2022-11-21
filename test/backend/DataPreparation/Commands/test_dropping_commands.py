import pandas as pd
import random
import backend.DataPreperation.Commands.DroppingCommands as dc


def test_drop_lower_bound():
    series = pd.Series(["a", "b", "c", "d", "d", "c", "b", "a"])
    drop_command = dc.DroppingCommand_LowerBound(series, 2)
    result = drop_command.execute()
    assert result is series

    drop_command = dc.DroppingCommand_LowerBound(series, 4)
    result = drop_command.execute()
    assert result is series

    drop_command = dc.DroppingCommand_LowerBound(series, 5)
    result = drop_command.execute()
    assert result is None


def test_upper_bound():
    series = pd.Series(["a", "b", "c", "d", "d", "c", "b", "a"])
    drop_command = dc.DroppingCommand_UpperBound(series, 2)
    result = drop_command.execute()
    assert result is None

    drop_command = dc.DroppingCommand_UpperBound(series, 3)
    result = drop_command.execute()
    assert result is None

    drop_command = dc.DroppingCommand_UpperBound(series, 4)
    result = drop_command.execute()
    assert result is series


def test_uniqueness_bound():
    values = ["a"] * 90 + ["b"] * 5 + ["c"] * 5
    random.shuffle(values)
    series = pd.Series(values)

    drop_command = dc.DroppingCommand_UniquenessBound(series, 0.85)
    result = drop_command.execute()
    assert result is None

    drop_command = dc.DroppingCommand_UniquenessBound(series, 0.90)
    result = drop_command.execute()
    assert result is series

    drop_command = dc.DroppingCommand_UniquenessBound(series, 0.99)
    result = drop_command.execute()
    assert result is series
