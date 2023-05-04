import numpy as np
import pandas as pd
from src.backend.DataPreperation.DataPrepperCommandFactory import DataPrepperCommandFactory
from typing import List, Set, Dict

class DataPrepper:
    def __init__(self) -> None:
        self.data_prepper_command_factory = DataPrepperCommandFactory()


    def clean_data_frame(self, dirty_df: pd.DataFrame, cleaning_json_string: str) -> pd.DataFrame:

        
        try:
            clusters_ = self._find_duplicate_columns(dirty_df)
            deduped_df = self._dedupe_dataframe_columns(clusters_, dirty_df)
        except Exception as e:
            print(e)

        dataframe_with_commands = self.data_prepper_command_factory.parse_cleaning_options_from_JSONstring(cleaning_json_string, deduped_df)
        print(f"length of original dataframe: {len(deduped_df)} ; Amount of columns of original dataframe: {len(deduped_df.columns)}")
        # # EXECUTE CLEANING COMMANDS FROM JSON
        # [x.execute() for x in dataframe_with_commands["cleaning_command"].values()]

        # EXECUTE BINNING COMMANDS FROM JSON
        [x.execute() for x in dataframe_with_commands["binning_command"].values if x is not None]
    

        # EXECUTE DROPPING COMMANDS FROM JSON
        try:
            # list_of_remaining_series_with_none = [[y.execute() for y in x if y is not None] for x in dataframe_with_commands["list_of_dropping_commands"].values if x is not None]
            list_of_remaining_series_with_none = [[y.execute() for y in x if y is not None] for x in dataframe_with_commands["list_of_dropping_commands"].values if x is not None]
            # list_of_remaining_series = [x for x in list_of_remaining_series_with_none if len(x) != 0]
            # debinned_dropped_df = pd.concat(list_of_remaining_series, axis=1, join="inner").reset_index()
        except Exception as e:
            print(e)

        print(f"length of new dataframe: {len(deduped_df)} ; cols of new dataframe: {len(deduped_df.columns)}")
        return deduped_df
        

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


    def _dedupe_dataframe_columns(self, clusters_,df):
        cols_to_remove = []
        for cluster in clusters_:
            # Drop all but the first column from the columns we have to use
            cols_to_remove.extend(list(sorted(cluster))[1:])
        cols_to_use = list( set(df.columns) - set(cols_to_remove))

        return df[cols_to_use]

    def _find_duplicate_columns(self, df: pd.DataFrame) -> List[Set[str]]:
        """ Find identical columns in the dataframe.

            df: the DataFrame to be examined. Should NOT be in one-hot-encoded form.

            returns: List of Set of str, where each set represents a group of identical 
            columns.
        """
        # df = df.astype(str)
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
