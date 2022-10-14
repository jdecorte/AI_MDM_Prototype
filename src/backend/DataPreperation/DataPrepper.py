import numpy as np
import pandas as pd
from src.backend.DataPreperation.DataPrepperCommandFactory import DataPrepperCommandFactory
from typing import List, Set, Dict
from src.shared.Enums.BinningEnum import BinningEnum
from src.shared.Enums.DroppingEnum import DroppingEnum

class DataPrepper:
    def __init__(self) -> None:
        self.data_prepper_command_factory = DataPrepperCommandFactory()


    def clean_data_frame(self, dirty_df: pd.DataFrame, cleaning_json_string: str) -> pd.DataFrame:

        clusters_ = self._find_duplicate_columns(dirty_df)
        deduped_df = self._dedupe_dataframe_columns(clusters_, dirty_df)

        dataframe_with_commands = self.data_prepper_command_factory.parse_cleaning_options_from_JSONstring(cleaning_json_string, deduped_df)

        # EXECUTE CLEANING COMMANDS FROM JSON
        [x.execute() for x in dataframe_with_commands["cleaning_command"].values()]

        # EXECUTE BINNING COMMANDS FROM JSON
        [x.execute() for x in dataframe_with_commands["binning_command"].values()]

        # EXECUTE DROPPING COMMANDS FROM JSON
        list_of_remaining_series_with_none = [x.execute() for x in dataframe_with_commands["list_of_dropping_commands"].values()]
        list_of_remaining_series = [x for x in list_of_remaining_series_with_none if x != None]
        debinned_dropped_df = pd.concat(list_of_remaining_series, axis=1).reset_index()

        return debinned_dropped_df
        

    def transform_data_frame_to_OHE(self, non_OHE_df: pd.DataFrame, drop_nan:bool) -> pd.DataFrame:

        # Omvormen naar String Dataframe:
        # str_non_OHE_df  = non_OHE_df.astype(str)
        str_non_OHE_df  = non_OHE_df

        # Compute the one hot encoded dataframe
        df_dummy = pd.get_dummies(str_non_OHE_df, dtype=np.bool8)

        # Dropping columns that had a NaN value
        if drop_nan:
            df_dummy = df_dummy.loc[:,~df_dummy.columns.str.endswith('nan')]

        return df_dummy


    def _dedupe_dataframe_columns(clusters_,df):
        cols_to_remove = []
        for cluster in clusters_:
            # Drop all but the first column from the columns we have to use
            cols_to_remove.extend(list(sorted(cluster))[1:])
        cols_to_use = list( set(cols_to_use) - set(cols_to_remove))

        return df[cols_to_use]

    def _find_duplicate_columns(df: pd.DataFrame) -> List[Set[str]]:
        """ Find identical columns in the dataframe.

            df: the DataFrame to be examined. Should NOT be in one-hot-encoded form.

            returns: List of Set of str, where each set represents a group of identical 
            columns.
        """
        duplicates : Dict[str, Set[str]] = {}
        dup_cache = set() # Cache of all columns that are duplicate
        for i in range(df.shape[1] - 1):
            col = df.iloc[:, i] # i-th column
            if df.columns[i] in dup_cache:
                continue

            for j in range(i + 1, df.shape[1]):
                other_col =  df.iloc[:, j] # j-th column
                if col.equals(other_col):
                    if not df.columns[i] in duplicates:
                        duplicates[df.columns[i]] = set([df.columns[i]])
                        dup_cache.add(df.columns[i])
                    duplicates[df.columns[i]].add(df.columns[j])
                    dup_cache.add(df.columns[j])
                
        
        return [v for (_ , v) in duplicates.items()]
