import pandas as pd
import numpy as np
import math

import config as cfg
from src.backend.RuleFinding.CR.ColumnRule import ColumnRule
from src.backend.RuleFinding.CR.CRFilters.ColumnRuleFilter import ColumnRuleFilter

from typing import Sequence, Dict, Set, List

class ColumnRuleRepo:

    def __init__(self, cr_dict: Dict[str, Dict[str, Sequence[ColumnRule]]]) -> None:
        self.definitions_dict = cr_dict["Definitions"]
        self.noDefinitions_dict= cr_dict["NoDefinitions"]


    def keep_only_interesting_column_rules(self, filterer: ColumnRuleFilter, confidence_bound:float, original_df):
        # Verander noDefinitions_dict
        self.noDefinitions_dict = filterer.execute(rules=self.noDefinitions_dict,rule_confidence_bound = confidence_bound, original_df = original_df )
        self.noDefinitions_dict = self.filter_reverse_rules_with_lower_confidence()


    def filter_reverse_rules_with_lower_confidence(self):
        list_interesting_rules = self._filter_reverse_rules_with_lower_confidence(list(self.noDefinitions_dict.values()))["ToKeep"]
        return {cr.rule_string: cr for cr in list_interesting_rules}


    def _filter_reverse_rules_with_lower_confidence(self, rules: Sequence[ColumnRule]) -> Dict[str, Sequence[ColumnRule]]:
        """
        Reduce the number of rules by applying the following logic: if both "A => B" and "B => A"
        are present, only keep the rule that has the highest confidence of the two. In case of a tie, 
        keep both.

        rules: sequence of rules that need to be filtered
        returns: dictionary with two keys: "ToKeep" and "ToDiscard". Each of these keys point 
        to a list of relevant column rules
        """
        result = {
            "ToKeep" : [],
            "ToDiscard" : []
        }

        # Cache of rules that we have seen so far
        seen: Dict[str, ColumnRule] = {} 

        for column_rule in rules:
            cfg.logger.debug(f"Considering column_rule {column_rule}")

            inverse_rule_string = column_rule.rule_string.split(" => ")[1] + \
                " => " + column_rule.rule_string.split(" => ")[0]
            if inverse_rule_string in seen:
                cfg.logger.debug(f"We have already seen {inverse_rule_string}")
                inverse_rule = seen[inverse_rule_string]
                if math.isclose(inverse_rule.confidence, column_rule.confidence):
                    cfg.logger.debug(f"Both rules have similar confidence. Keeping both")
                    result["ToKeep"].append(column_rule)
                    result["ToKeep"].append(inverse_rule)
                elif inverse_rule.confidence > column_rule.confidence:
                    cfg.logger.debug(f"{inverse_rule_string} has higher confidence then {column_rule.rule_string}. Discarding {column_rule.rule_string}")
                    result["ToKeep"].append(inverse_rule)
                    result["ToDiscard"].append(column_rule)
                else:
                    cfg.logger.debug(f"{inverse_rule_string} has lower confidence then {column_rule.rule_string}. Discarding {inverse_rule_string}")
                    result["ToKeep"].append(column_rule)
                    result["ToDiscard"].append(inverse_rule)

                del seen[inverse_rule_string]
            else:
                seen[column_rule.rule_string] = column_rule

        # Add all rules still in the cache to the ToKeep list
        result["ToKeep"].extend(seen.values())

        return result

    def get_definitions_dict(self):
        return self.definitions_dict

    def get_non_definitions_dict(self):
        return self.noDefinitions_dict

    def get_cr_with_100_confidence_dict(self):
        return {rs: cr for (rs,cr) in self.noDefinitions_dict.items() if math.isclose(cr.confidence,1)}

    def get_cr_without_100_confidence_dict(self):
        return {rs: cr for (rs,cr) in self.noDefinitions_dict.items() if not math.isclose(cr.confidence,1)}


    







    