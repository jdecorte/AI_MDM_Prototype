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


    def keep_only_interesting_column_rules(self, filterer: ColumnRuleFilter, confidence_bound:float):
        self.noDefinitions_dict = filterer.filter_based_on_confidence_bound(rules = self.noDefinitions_dict, rule_confidence_bound=confidence_bound)
        self.noDefinitions_dict = filterer.execute(rules=self.noDefinitions_dict)
        self.noDefinitions_dict = filterer.filter_reverse_rules_with_lower_confidence(self.noDefinitions_dict)

    def get_definitions_dict(self):
        return self.definitions_dict

    def get_non_definitions_dict(self):
        return self.noDefinitions_dict

    def get_cr_with_100_confidence_dict(self):
        return {rs: cr for (rs,cr) in self.noDefinitions_dict.items() if math.isclose(cr.confidence,1)}

    def get_cr_without_100_confidence_dict(self):
        return {rs: cr for (rs,cr) in self.noDefinitions_dict.items() if not math.isclose(cr.confidence,1)}


    







    