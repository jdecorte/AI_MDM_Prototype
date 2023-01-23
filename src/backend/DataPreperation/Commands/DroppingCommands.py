from abc import ABC, abstractmethod
import pandas as pd
# pd.set_option('mode.chained_assignment', None)


class DroppingCommand(ABC):

    @abstractmethod
    def execute(self) -> pd.DataFrame():
        raise Exception("Not implemented Exception")


class DroppingCommand_DropNan(DroppingCommand):

    def __init__(self, dataframe: pd.DataFrame, col:str, boolean_in_string: str) -> None:
        self.dataframe = dataframe
        self.boolean_in_string = eval(boolean_in_string)
        self.col = col

    def execute(self) -> None:
        if self.boolean_in_string:
            self.dataframe.loc[:, self.col] =  self.dataframe.loc[:, self.col].dropna()
        else:
            pass
        print('Beep')


class DroppingCommand_UniquenessBound(DroppingCommand):

    def __init__(self, dataframe: pd.DataFrame, col:str, uniqueness_bound: float) -> None:
        self.dataframe = dataframe
        self.uniqueness_bound = uniqueness_bound
        self.col = col

    def execute(self) -> None:
        if (self.dataframe[self.col].value_counts(normalize=True).max()
           > self.uniqueness_bound):
            self.dataframe[self.col] = None


class DroppingCommand_LowerBound(DroppingCommand):

    def __init__(self, dataframe: pd.DataFrame, col:str, lower_bound: int) -> None:
        self.dataframe = dataframe
        self.lower_bound = lower_bound
        self.col = col

    def execute(self) -> None:
        if self.dataframe[self.col].nunique() < self.lower_bound:
            self.dataframe[self.col] = None


class DroppingCommand_UpperBound(DroppingCommand):

    def __init__(self, dataframe: pd.DataFrame, col:str, upper_bound: int) -> None:
        self.dataframe = dataframe
        self.upper_bound = upper_bound
        self.col = col

    def execute(self) -> None:
        if self.dataframe[self.col].nunique() > self.upper_bound:
            self.dataframe[self.col] = None
        else:
            pass
