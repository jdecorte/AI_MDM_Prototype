import pandas as pd
import numpy as np
import config as cfg
import pprint
import json
from typing import Dict, Sequence
from src.shared.Views.ColumnRuleView import ColumnRuleView

class ColumnRule:
    def __init__(self, rule_string : str, original_df = None,value_mapping = None,  confidence = None):
        self.value_mapping = value_mapping
        # Test of het wel stringified is
        self.original_df = original_df
        self.rule_string = rule_string
        antecedent_string = rule_string.split(" => ")
        if antecedent_string[0] == "/":
            self.antecedent_set = frozenset()
        else:
            self.antecedent_set = frozenset(antecedent_string[0].split(","))
        self.consequent_set = set(rule_string.split(" => ")[1].split(","))
        
        if value_mapping is not None:
            self.df_to_correct = self._create_dataframe_to_be_corrected()
            self.mapping_df = self._create_mapping_df()        

        if confidence is None:
            self.confidence = 1.0 - self.df_to_correct.shape[0]/original_df.shape[0]
        else:
            self.confidence = confidence
        
   
    def __str__(self):
         return self.rule_string +" (" + str(self.confidence) + ")" + ", met als mapping: " + str(self.value_mapping)


    def _create_dataframe_to_be_corrected(self):

        temp_value_mapping = {}
        df_to_be_corrected = pd.DataFrame()
        counter = 0
        for k,v in self.value_mapping.items():
            counter+=1
            temp_value_mapping[k] = v
            if (counter % 50 == 0) or (counter == len(self.value_mapping)):
                temp_df = self.original_df.query(ColumnRule._create_df_query(temp_value_mapping) , engine='python')
                df_to_be_corrected = pd.concat([df_to_be_corrected, temp_df])
                temp_value_mapping = {}
                


        cfg.logger.debug(f"The df with the possible errors has shape: {df_to_be_corrected.shape}")


        """
        Adds additional columns to the DataFrame indicating which rule was used, 
        which value was found and which value was expected.


        rule_string: string of the form "A,B => C"
        value_mapping: dictionary mapping antecedents with value to consequents
        df_to_be_corrected: dataframe containing possibly faulty rows 

        """
        found_values = []
        suggested_values = []

        for _, row in df_to_be_corrected.iterrows():
            antecedent_set = set([])
            for antecedent in self.antecedent_set:
                antecedent_set.add(f"{antecedent}_{row[antecedent]}")            
            
            suggested_values.append(self.value_mapping[frozenset(antecedent_set)].split("_")[1])
                    
            #   Look up the value that was found
            found_values.append(row[list(self.consequent_set)[0]])

        # Do not add columns if nothing was found, i.e. the dataframe was empty to begin with
        # if len(found_values) > 0:            
        df_to_be_corrected.insert(0, "SUGGEST_CON", suggested_values)
        df_to_be_corrected.insert(0, "FOUND_CON", found_values)
        df_to_be_corrected.insert(0, "RULESTRING", self.rule_string)

        return df_to_be_corrected

    @staticmethod
    def _create_df_query(mapping_dict: Dict[Sequence[str], str]) -> str:
        """
        Create a query string that can be used to retrieve all the rows in the one-hot-encoded
        dataframe that do not satisty the mapping specified in the dictionary.

        Each item in the mapping dictionary maps a FrozenSet of str to str. Each such string
        is of the form "A_a" where A is the column and 'a' is the attribute value.
        """
        return " | ".join([f"{ColumnRule._create_single_query_string(a,c)}"  for a, c in mapping_dict.items()])

    @staticmethod
    def _create_single_query_string(antecedents: Sequence[str], consequent: str) -> str:
        """
        Create a string that can be used to `query` the dataframe, in order to filter out
        the rows that do not satisfy the mapping. 

        antecedents: sequence of str of the form "A_a",
        consequent: single string of the form "C_c"

        We are looking for the rows that satisfy all the antecedents, but not the consequent.

        """
        return  "(" +  " & ".join([f'(`{a.split("_")[0]}` == "{a.split("_")[1]}")' for a in antecedents] 
            + [f'(`{consequent.split("_")[0]}` != "{consequent.split("_")[1]}")']) + ")"

    def show_value_mapping(self) -> None:
        pprint.pprint(self.value_mapping)


    def _create_mapping_df(self) -> pd.DataFrame:
        """
        Create DataFrame of the mapping stored in self.mappingDict.
        """
        column_names = list(self.antecedent_set) + list(self.consequent_set)

        columnnames_2_values = {c : [] for c in column_names}

        for k, v in self.value_mapping.items():
            # k and v are frozenset
            for column_value in k:
                column, value = column_value.split('_')
                columnnames_2_values[column].append(value)
            
            column, value = v.split('_')
            columnnames_2_values[column].append(value)
        
        return pd.DataFrame(columnnames_2_values)
        cfg.logger.debug(f"The mapping for {self.rule_string} is")
        cfg.logger.debug(f"{self.mapping_df}")
            
    def predict(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        df: input DataFrame, NOT one-hot-encoded

        Returns a DataFrame consisting of the relevant columns (i.e. columns participating
        in this rule). 
        The antecedent columns are filled with the original values in the DataFrame, 
        the consequent column, however, is filled with the predictions made by this rule.
        """

        if len(self.antecedent_set) != 0:
            df_relevant = df[list(self.antecedent_set)] # Get dataframe with only the columns in the antecedent
        else:
            df_relevant = pd.DataFrame(index=df.index)
        
        if self.mapping_df is None:
            self._create_mapping_df()

        cfg.logger.debug("Will merge the following two dataframes. First DataFrame")
        cfg.logger.debug(df_relevant)
        cfg.logger.debug("Second DataFrame")
        cfg.logger.debug(self.mapping_df)

        # cfg.logger.debug("The result is ")
        # cfg.logger.debug(f'{df_relevant.merge(self.mapping_df, how="left", on=list(self.antecedentSet) if self.antecedentSet else None)}')
        # cfg.logger.debug(f'{df_relevant.merge(self.mapping_df, how="left", on=list(self.antecedentSet))}')


        if len(self.antecedent_set) != 0:
            return df_relevant.merge(self.mapping_df, how="left", on=list(self.antecedent_set))
        else:
            df_relevant[list(self.consequent_set)[0]] = self.mapping_df.iloc[0,0]
            return df_relevant


    def status(self, df: pd.DataFrame) -> np.ndarray:
        """
        df: input DataFrame, NOT one-hot-encoded

        Return a series with the same number of entries as the DataFrame `df` has rows.
        Each entry is either +1 is the rule is satisfied by the corresponding row, 
        -1 if the rule is not satisfied by the corresponding row 
        """
        cfg.logger.debug(f"Determining status for the following DataFrame")
        cfg.logger.debug(df)
        # Get predictions
        predictions = self.predict(df)

        assert predictions.shape[0] == df.shape[0], "Something wrong with predict!"

        consequent_col_name = list(self.consequent_set)[0]

        cfg.logger.debug(f"{predictions[consequent_col_name].index} versus {df[consequent_col_name].index}")

        cfg.logger.debug(f"The predictions are {predictions[consequent_col_name]}")
        cfg.logger.debug(f"The actual values are {df[consequent_col_name]}")

        return np.where(
            predictions[consequent_col_name].reset_index(drop=True) == 
            df[consequent_col_name].reset_index(drop=True), +1, -1)


    def parse_self_to_view(self) -> ColumnRuleView:
        return ColumnRuleView(rule_string=self.rule_string, idx_to_correct=json.dumps(self.df_to_correct.index.tolist()), confidence=self.confidence, value_mapping=self.mapping_df.to_json())