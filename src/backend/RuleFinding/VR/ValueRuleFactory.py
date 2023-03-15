import pandas as pd

from src.backend.RuleFinding.VR.ValueRuleElement import ValueRuleElement
from src.backend.RuleFinding.VR.ValueRule import ValueRule
from typing import Dict, Set, List


class ValueRuleFactory:

    def __init__(self):
        pass

    # Note: this method should be a class method
    def transform_ar_dataframe_to_value_rules_dict(
            self, df: pd.DataFrame) -> Dict[str, Set[ValueRule]]:
        """
        df: a DataFrame returned containing information about value rules.
            It should at least have columns: 'antecedents', 'consequents', 'support',
                                             'confidence' and 'lift'

        returns: a dictionary mapping rule strings to sets of value rules.
                 Each value rule in the set has the same rule string, namely
                 the key in the dictionary.
        """
        value_rules_dict: Dict[str, Set[ValueRule]] = {}
        [self._df_to_dict_of_value_rules(*x, value_rules_dict)
            for x in zip(df[['antecedents', 'consequents',
                             'support', 'confidence', 'lift']].to_numpy())]

        return value_rules_dict

    def _df_to_dict_of_value_rules(
            self,
            row,
            value_rules_dict: Dict[str, Set[ValueRule]]) -> None:
        """
        row: numpy array of five elements: antecedents, consequents, support, confidence 
                and lift of a value rule
        value_rules_dict : dictionary

        This method will add elements to `value_rules_dict`.
        The key will be a string of the form "A,B => C" where A, B and C
        are columns participating in the antecedents (A, B) and consequent C.
        The values will be sets of ValueRule where the columns A, B and C participate.
        """
        ll_elements: List[ValueRuleElement] = []
        rl_element: ValueRuleElement = None

        # Antecedents
        for ll_item in list(row[0]):
            ll = ll_item.split("_")
            ll_elements.append(ValueRuleElement(ll[0], ll[1]))

        # Consequents
        rl = list(row[1])[0].split("_")
        rl_element = ValueRuleElement(rl[0], rl[1])

        r = ValueRule(ll_elements, rl_element, support=row[2],
                      confidence=row[3], lift=row[4])
        rule_string = r.get_column_rule_string()

        # Add this value rule to the map under the appropriate key, i.e. the rule string
        # corresponding to this value rule
        if rule_string in value_rules_dict:
            value_rules_dict[rule_string].add(r)
        else:
            value_rules_dict[rule_string] = set([r])
