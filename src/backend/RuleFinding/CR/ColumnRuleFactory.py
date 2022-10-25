import pandas as pd
import numpy as np
import math
import config as cfg
from src.backend.RuleFinding.CR.ColumnRule import ColumnRule
from typing import Sequence, List, Dict, FrozenSet
from src.backend.RuleFinding.AR.AssociationRuleFinder import AssociationRuleFinder

class ColumnRuleFactory:

    def __init__(self, df_dummy, original_df) -> None:
        self.df_dummy = df_dummy
        self.original_df = original_df

    def create_dict_of_dict_of_column_rules_from_list_of_strings(self,list_of_column_rule_strings) -> Dict[str, Sequence[ColumnRule]]:
        rule_list = []
        
        # For progress bar
        index_mod = len(list_of_column_rule_strings) // 10 + 1

        for index, rule in enumerate(list_of_column_rule_strings):
            
            # Log progress
            if index % index_mod == 0:
                cfg.logger.info(f" {index} / {len(list_of_column_rule_strings)}")

            rule_list.append(self.expand_single_column_rule(rule))

        return self.transform_list_of_column_rules_to_dict_of_column_rules(rule_list)   


    def transform_list_of_column_rules_to_dict_of_column_rules(self, column_rules : Sequence[ColumnRule]) -> Dict[str, Sequence[ColumnRule]]:
        """
        Get all the 'definitions' from the column_rules. These are rules of the form A => B and B => A that
        both have a confidence of one.

        column_rules: the ColumnRule to check
        returns: dictionary containing two keys: 'Definitions' and 'NoDefinitions' each mapping to 
        a sequence of rules
        """

        cfg.logger.info(f"get_definitions received {len(column_rules)} column rules")
        cfg.logger.debug(f"The column rules are {';'.join(str(cr) for cr in column_rules)}")


        result = {
            "Definitions" : {},
            "NoDefinitions" : {}
        }
        # Cache of rules with confidence one
        rules_with_confidence_one: Dict[str, ColumnRule] = {}

        for column_rule in column_rules:
            if math.isclose(column_rule.confidence, 1.0):
                inverse_rule_string = column_rule.rule_string.split(" => ")[1] + " => " + column_rule.rule_string.split(" => ")[0]
                if inverse_rule_string in rules_with_confidence_one:
                    # result["Definitions"].append(column_rule)
                    # result["Definitions"].append(rules_with_confidence_one[inverse_rule_string])
                    result["Definitions"][column_rule.rule_string] = column_rule
                    result["Definitions"][rules_with_confidence_one[inverse_rule_string].rule_string] = rules_with_confidence_one[inverse_rule_string]
                    del rules_with_confidence_one[inverse_rule_string]
                else: # No proof yet that it is a definition
                    rules_with_confidence_one[column_rule.rule_string] = column_rule
            else:
                # result["NoDefinitions"].append(column_rule)
                result["NoDefinitions"][column_rule.rule_string] = column_rule

        # Add all remaining rules in `rules_with_confidence_one` to the NoDefitions list  
        for k,v in  rules_with_confidence_one.items():
            result["NoDefinitions"][k] = v
        # result["NoDefinitions"].extend(rules_with_confidence_one.values())
            
        cfg.logger.info(f"Number of definitions found: {len(result['Definitions'])}")
        cfg.logger.debug(f"Definitions are: {';'.join(str(cr) for cr in result['Definitions'])}")




        # Voeg ook de columnRules toe met een lege antecedent (Als ze aan de voorwaarde voldoen), Zijn trouwens sowieso geen definities
        result["NoDefinitions"] = {**result["NoDefinitions"], **self._get_dict_of_columnrules_with_empty_antecedent(cols_to_use=self.original_df.columns, df=self.original_df)}
        # result["NoDefinitions"].extend(self._get_list_of_columnrules_with_empty_antecedent(cols_to_use=self.original_df.columns, df=self.original_df)) 
        return result


    def _get_dict_of_columnrules_with_empty_antecedent(self, cols_to_use, df) -> Dict[str, Sequence[ColumnRule]]:
        """
        DF needs to be One-Hot Encoded
        Creates ColumnRules of the form ' {} -> X ', to make sure that 'almost-constant' columns ( ex. column uniqueness of 95%) are not added in the consequent set of the other rules.
        """
        dict_of_columnrules_with_empty_antecedent = {}
        for e in cols_to_use:
            vc = df[e].value_counts(normalize=True)
            vcim = vc.idxmax()
            vcm = vc.max()
            mappingDict = {frozenset(): f"{e}_{vcim}"}
            # query = ColumnRule._create_df_query(mappingDict)
            # query= f"`{e}` != `{vcim}`"
            # df_to_be_corrected = df.query(query, engine='python')
            cr = ColumnRule(rule_string="/ => " + e, value_mapping=mappingDict, original_df=df,  confidence = float(vcm))
            dict_of_columnrules_with_empty_antecedent[cr.rule_string] = cr

        return dict_of_columnrules_with_empty_antecedent



    def expand_single_column_rule(self,rule_string: str) -> ColumnRule:
        """
            rule_string: a rule string of the form "A_a,B_b => C_c"
            df_dummy: the one-hot-encoded DataFrame
            df: the orginal DataFrame (with all string data types)
        """
        cfg.logger.debug(f"Expanding  single column rule for '{rule_string}'")

        # Determine the relevant columns in the one hot encoded dataframe
        dummy_cols_to_use = self.get_columns_for_mini_fp_growth(rule_string, self.df_dummy.columns)
        cfg.logger.debug(f"Using the following columns: {dummy_cols_to_use}")

        # Number of columlns playing a role in this rule string
        num_cols = len(rule_string.split(" => ")[0].split(",")) + 1


        mini_ar_finder = AssociationRuleFinder(self.df_dummy[dummy_cols_to_use], 
                                            min_support=1/(self.original_df.shape[0] + 10.0), 
                                            max_len=num_cols, 
                                            min_lift=0.0, min_confidence=0.0)

        value_rules = mini_ar_finder.get_association_rules()

        value_mapping = self.create_mapping(value_rules, rule_string)

        return ColumnRule(rule_string=rule_string, value_mapping=value_mapping, original_df=self.original_df) 



    def get_columns_for_mini_fp_growth(self, rule_string : str, df_column_list : Sequence[str]) -> List[str]:
        """
            Determine the columns to use when one wants to find a complete mapping 
            between the antecedents and the consequents.

            rule_string: string of the form "A,B => C"
            df_column_list: the sequence of columns the dataframe has, these should be column names
            of the form A_a, B_b and so on
        """
        cfg.logger.debug(f"Determining columns to use for '{rule_string}'")
        cols_to_use = []

        antecedents, consequents = (rule_string.split(" => "))
        for attribute in antecedents.split(",") + [consequents]:
            cfg.logger.debug(f"Considering attribute '{attribute}'")
            cols_to_use.extend([col for col in df_column_list if col.split("_")[0] == attribute])

        return cols_to_use


    def create_mapping(self, value_rules: pd.DataFrame, rule_string: str) -> Dict[FrozenSet[str], str]:
        """
        value_rules: dictionary as returned by 'association_rules' method from mlxtend.
            We only consider the 'antecedents', 'consequents' and 'confidence' columns.
        rule_string: string of the form "A,B => C_c"

        Idea: sort the dataframe by confidence, then only look at rows involving the same columns 
        as the rule_string in both antecedent and consequent.

        For each combination of values in the antecedents, pick the consequent value that has 
        the highest confidence. This will lead to the overall rule will the highest confidence.
        """
        value_rules = value_rules.sort_values(by="confidence", ascending=False)

        mapping: Dict[FrozenSet[str], str] = {}

        rs_antecedent_columns = frozenset([col for col in rule_string.split(" => ")[0].split(",")])

        for _, row in value_rules.iterrows():
            #  Moet enkel gekeken worden naar mini_rules die dezelfde antecedenten heeft als de initiële regel
            antecedent_columns = frozenset([a.split('_')[0] for a in list(row["antecedents"])]) 
            if rs_antecedent_columns == antecedent_columns:
                if row["antecedents"] not in mapping:
                    mapping[row["antecedents"]] = list(row["consequents"])[0] 

        return mapping