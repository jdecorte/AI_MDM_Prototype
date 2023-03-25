import math
import config as cfg
from src.backend.RuleFinding.CR.ColumnRule import ColumnRule
from typing import Sequence, Dict


class ColumnRuleFactory:

    def __init__(self, df_dummy, original_df) -> None:
        self.df_dummy = df_dummy
        self.original_df = original_df

    def create_dict_of_dict_of_column_rules_from_list_of_strings(self, cr_rule_strings) -> Dict[str, Sequence[ColumnRule]]:
        rule_list = []

        # For progress bar
        index_mod = len(cr_rule_strings) // 10 + 1

        for index, rule in enumerate(cr_rule_strings):
  
            # Log progress
            if index % index_mod == 0:
                cfg.logger.info(f" {index} / {len(cr_rule_strings)}")

            rule_list.append(self.expand_single_column_rule(rule))

        return self.transform_list_of_column_rules_to_dict_of_column_rules(rule_list)   

    def transform_list_of_column_rules_to_dict_of_column_rules(self, column_rules : Sequence[ColumnRule]) -> Dict[str, Sequence[ColumnRule]]:
        """
        Get all the 'definitions' from the column_rules. These are rules of the form A => B
        and B => A that both have a confidence of one.

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
        # Stijn verwijder oproep naar _get_dict_of_columnrules_with_empty_antecedent
        #result["NoDefinitions"] = {**result["NoDefinitions"], **self._get_dict_of_columnrules_with_empty_antecedent(cols_to_use=self.original_df.columns, df=self.original_df)}
        # result["NoDefinitions"].extend(self._get_list_of_columnrules_with_empty_antecedent(cols_to_use=self.original_df.columns, df=self.original_df)) 
        return result

    def expand_single_column_rule(self, rule_string: str) -> ColumnRule:
        return ColumnRule(rule_string=rule_string,
                          original_df=self.original_df,
                          value_mapping=True)
