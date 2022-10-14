import numpy as np
import pandas as pd
import json

from src.shared.Enums.BinningEnum import BinningEnum
from src.shared.Enums.DroppingEnum import DroppingEnum
from src.shared.Enums.CleaningEnum import CleaningEnum
from src.backend.DataPreperation.Commands.BinningCommands import *
from src.backend.DataPreperation.Commands.DroppingCommands import *
from src.backend.DataPreperation.Commands.CleaningCommands import *

class DataPrepperCommandFactory:
    def __init__(self) -> None:
        pass

    def parse_cleaning_options_from_JSONstring(self,cleaning_json_string: str, dirty_df: pd.DataFrame) -> pd.DataFrame:

        df_to_return = pd.DataFrame({
            "column":[],
            "cleaning_command":[],
            "binning_command":[],
            "list_of_dropping_commands":[],
        })


        """Inlezen van CleaningOptions"""
        cleaning_json_object = json.loads(cleaning_json_string)
        for k,v in cleaning_json_object.items():
            

            """Creatie Van BinningCommand"""
            binning_command_object_k, binning_command_object_v  = v["binning"]

            if binning_command_object_k == BinningEnum.EQUAL_BINS:
                binning_command_object_to_add = BinningCommand_EqualBins(number_of_bins=binning_command_object_v, series=dirty_df[k])
            elif binning_command_object_k  == BinningEnum.K_MEANS:
                binning_command_object_to_add = BinningCommand_KMeans(number_of_bins=binning_command_object_v, series=dirty_df[k])
            else:
                raise Exception("Invalid Parsing of BinningCommand")


            """Creatie Van Lijst van DroppingCommands"""
            dropping_command_object = v["dropping"]
            list_of_dropping_commands = []
            for inner_k, inner_v in dropping_command_object.items():
                if inner_k == DroppingEnum.DROP_WITH_UNIQUENESS_BOUND:
                    list_of_dropping_commands.append(DroppingCommand_UniquenessBound(uniqueness_bound=inner_v, series=dirty_df[k]))
                elif inner_k == DroppingEnum.DROP_WITH_LOWER_BOUND:
                    list_of_dropping_commands.append(DroppingCommand_LowerBound(lower_bound=inner_v, series=dirty_df[k]))
                elif inner_k == DroppingEnum.DROP_WITH_UPPER_BOUND:
                    list_of_dropping_commands.append(DroppingCommand_UpperBound(upper_bound=inner_v, series=dirty_df[k]))
                else:
                    raise Exception("Invalid Parsing of DroppingCommand")


            """Creatie Van Lijst van CleaningCommands"""
            cleaning_command_object = v["cleaning"]
            list_of_cleaning_commands = []
            for inner_k, inner_v in cleaning_command_object.items():
                if inner_k == CleaningEnum.STRING_TO_FLOAT:
                    list_of_cleaning_commands.append(CleaningCommand_StringToFloat(series=dirty_df[k]))
                elif inner_k == CleaningEnum.TRIM:
                    list_of_cleaning_commands.append(CleaningCommand_Trim(series=dirty_df[k]))
                else:
                    raise Exception("Invalid Parsing of CleaningCommand")
            
            
            df_to_return.loc[len(df_to_return)] = [k, binning_command_object_to_add, list_of_dropping_commands, list_of_cleaning_commands]

        return df_to_return
