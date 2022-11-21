import pandas as pd
import backend.DataPreperation.Commands.CleaningCommands as cc


def test_trim():
    """ Test that spaces at the beginning and end are removed but that spaces
        in the middle are kept.
    """
    series = pd.Series([" abc   ", "  def    ", " abc  def  "])

    trim_command = cc.CleaningCommand_Trim(series)
    result = trim_command.execute()
    assert result.equals(pd.Series(["abc", "def", "abc  def"]))


def test_string_to_float():
    """ Very simple test of string to float.
    """
    series = pd.Series([" +10.0   ", "  -20.5    ", "3.1415"])

    tofloat_command = cc.CleaningCommand_StringToFloat(series)
    result = tofloat_command.execute()

    assert result.equals(pd.Series([10.0,-20.5, 3.1415]))
