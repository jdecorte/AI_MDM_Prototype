import pandas as pd
import numpy as np

from src.backend.RuleFinding.VR.ValueRuleElement import ValueRuleElement
from src.backend.RuleFinding.VR.ValueRule import ValueRule
from mlxtend.frequent_patterns import fpgrowth
from typing import Dict, Set, List

class ValueRuleFactory:

    def __init__(self) -> None:
        pass

    def transform_ar_dataframe_to_value_rules_dict(self, df : pd.DataFrame) -> Dict[str, Set[ValueRule]]:
        """
            df: a DataFrame returned containing information about value rules. 
                It should at least have columns: 'antecedents', 'consequents', 'support', 'confidence' and 'lift'
            min_support: TODO

            returns: a tuple consisting of two maps, TODO
        """    
        value_rules_dict : Dict[str, Set[ValueRule]] = {}
        [self._df_to_dict_of_value_rules(*x, value_rules_dict) for x in zip(df[['antecedents','consequents', 'support', 'confidence', 'lift']].to_numpy())]  

        return value_rules_dict

    def _df_to_dict_of_value_rules(self,row, value_rules_dict : Dict[str, Set[ValueRule]]) -> None:
        """
            row: numpy array of five elements: antecedents, consequents, support, confidence 
                and lift of a value rule
            mapToFilter : dictionary 

            This method will add elements to `mapToFilter`. The key will be a string of the form
            "A,B => C,D" where A, B, C and D are columns participating in the antecedents (A, B)
            and consequents (C, D).  The values will be sets of ValueRule where the columns 
            A, B, C and D participate.
        """
        ll_elements : List[ValueRuleElement] = []
        rl_element : ValueRuleElement = None

        # Antecedents
        for ll_item in list(row[0]):
            ll = ll_item.split("_")
            ll_elements.append(ValueRuleElement(ll[0], ll[1]))

        # Consequents
        rl = list(row[1])[0].split("_") 
        rl_element = ValueRuleElement(rl[0], rl[1])

        r = ValueRule(ll_elements, rl_element ,support=row[2], confidence=row[3], lift=row[4])
        ruleString = r.get_column_rule_string()

        # Add this value rule to the map under the appropriate key, i.e. the rulestring
        # corresponding to this value rule
        if ruleString in value_rules_dict:
            value_rules_dict[ruleString].add(r)
        else:
            value_rules_dict[ruleString] = set([r])