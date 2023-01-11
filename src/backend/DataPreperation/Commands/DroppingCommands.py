from abc import ABC, abstractmethod
import pandas as pd


class DroppingCommand(ABC):

    @abstractmethod
    def execute(self, df: pd.Series, relevant_column: str) -> pd.DataFrame():
        raise Exception("Not implemented Exception")


class DroppingCommand_DropNan(DroppingCommand):

    def __init__(self, series: pd.Series, boolean_in_string: str) -> None:
        self.series = series
        self.boolean_in_string = bool(boolean_in_string)

    def execute(self) -> pd.Series:
        if self.boolean_in_string:
            return self.series.dropna()
        else:
            return self.series


class DroppingCommand_UniquenessBound(DroppingCommand):

    def __init__(self, series: pd.Series, uniqueness_bound: float) -> None:
        self.series = series
        self.uniqueness_bound = uniqueness_bound

    def execute(self) -> pd.Series:
        if (self.series.value_counts(normalize=True).max()
           > self.uniqueness_bound):
            return None
        else:
            return self.series


class DroppingCommand_LowerBound(DroppingCommand):

    def __init__(self, series: pd.Series, lower_bound: int) -> None:
        self.series = series
        self.lower_bound = lower_bound

    def execute(self) -> pd.Series:
        if self.series.nunique() < self.lower_bound:
            return None
        else:
            return self.series


class DroppingCommand_UpperBound(DroppingCommand):

    def __init__(self, series: pd.Series, upper_bound: int) -> None:
        self.series = series
        self.upper_bound = upper_bound

    def execute(self) -> pd.Series:
        if self.series.nunique() > self.upper_bound:
            return None
        else:
            return self.series
