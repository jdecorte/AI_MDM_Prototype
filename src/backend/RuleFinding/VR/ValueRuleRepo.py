import numpy as np
import config as cfg

from typing import Dict, Set, List, FrozenSet

from src.backend.RuleFinding.VR.ValueRule import ValueRule
from src.backend.RuleFinding.CR.ColumnRule import ColumnRule
from src.backend.HelperFunctions import HelperFunctions


class ValueRuleRepo:

    def __init__(self, value_rules_dict: Dict[str, Set[ValueRule]]):
        self.value_rules_dict = value_rules_dict

    def filter_out_column_rule_strings_from_dict_of_value_rules(self, min_support:float) -> List[str]:
        """
        TODO!!
        """
        self.value_rules_dict = self._filter_low_support_rules(min_support)

        potential_conf_dict = self._create_potential_conf_dict_from_value_rules()
        cfg.logger.debug('potential_conf_dict' + str(potential_conf_dict))
        
        dict_of_antecedents_to_list_of_column_rules = self._create_dict_of_column_rules_with_potential_confidence_from_value_rules(potential_conf_dict)

        list_of_kept_rules_after_potential_conf_filter = self._filter_on_potential_conf_of_rules(potential_conf_dict,dict_of_antecedents_to_list_of_column_rules,self.value_rules_dict)

        return list_of_kept_rules_after_potential_conf_filter
        


    def _filter_on_potential_conf_of_rules(self,potential_conf_dict, dict_of_antecedents_to_list_of_column_rules, dict_of_kept_rules_to_be_filtered  ):

        counter = 0
        for rs, max_confidence in potential_conf_dict.items():

            # Log progress
            counter += 1
            if (counter % int(1 + (len(potential_conf_dict) / 10))) == 0:
                cfg.logger.info(f"Progressie LemmaRule Maken en Filteren:  {counter}/{len(potential_conf_dict)}")

            cr = ColumnRule(rs, confidence = max_confidence)
            if len(cr.antecedent_set) > 1:           
                for s in [frozenset(_) for _ in HelperFunctions.subsets_minus_one(cr.antecedent_set)]:
                    if s in dict_of_antecedents_to_list_of_column_rules:
                        innerListToCheck : List[ColumnRule]= dict_of_antecedents_to_list_of_column_rules[s] # consequents of this rule
                        for e in innerListToCheck:
                            # When a 'smaller' rule exists that has the same consequent, but a smaller antecedent 
                            # and the smaller rule has a higher confidence then we drop the larger rule

                            # TODO: maybe change >= into > or math.isclose()
                            if (e.consequent_set == cr.consequent_set) and (e.confidence >= cr.confidence):
                                if rs in dict_of_kept_rules_to_be_filtered:
                                    # TODO: should we also keep these rules for later reference
                                    cfg.logger.debug(f"Remove column rule {rs}, because of {e}")
                                    print(f"Remove column rule {rs}, because of {e}")
                                    del dict_of_kept_rules_to_be_filtered[rs]


        cfg.logger.debug(f"Kept rules = {dict_of_kept_rules_to_be_filtered}")

        return dict_of_kept_rules_to_be_filtered.keys()

    def _create_potential_conf_dict_from_value_rules(self):
        potential_conf_dict: Dict[str, float] = \
            {rs: self._calculate_max_confidence(vrs)
                for rs, vrs in self.value_rules_dict.items()}
        return potential_conf_dict

    def _create_dict_of_column_rules_with_potential_confidence_from_value_rules(self, potential_conf_dict):
        dict_of_antecedents_to_list_of_column_rules : Dict[FrozenSet[str], List[ColumnRule]]= {}
        for rs, max_confidence in potential_conf_dict.items():
            cr = ColumnRule(rs, confidence=max_confidence)
            key_lr = cr.antecedent_set
            if key_lr in dict_of_antecedents_to_list_of_column_rules:
                dict_of_antecedents_to_list_of_column_rules[key_lr].append(cr)
            else:
                dict_of_antecedents_to_list_of_column_rules[key_lr] = [cr]

        return dict_of_antecedents_to_list_of_column_rules
        

    def _filter_low_support_rules(self, min_support) -> Dict[str, Set[ValueRule]]:
        """ Remove all entries from the dictionary `self.value_rules_dict` whose total 
            support is currently not greater or equal than `min_support`.

            self.value_rules_dict: dictionary mapping rule strings, i.e. strings of the form (A,B => C,D)
            to a set of value rules involving those columns.
            min_support: a float (0.0 <= min_support <= 1.0) 

            returns: a dictionary of kept entries
        """
        cfg.logger.info(f"Trying to remove rule_strings for which total support is less than {min_support}")
        removed_rs : Dict[str, Set[ValueRule]] = {}
        kept_rs : Dict[str, Set[ValueRule]] = {}
        for rs, value_rules in self.value_rules_dict.items():
            support = np.sum([vr.support for vr in value_rules])
            # cfg.logger.debug(f"Total support for {rs} is {support}")
            # cfg.logger.debug(f"Individual value rules have support {[(str(vr), vr.support) for vr in value_rules]}")

            if support < min_support: # remove this one
                removed_rs[rs] = self.value_rules_dict[rs]
            else:
                kept_rs[rs] = self.value_rules_dict[rs]

        cfg.logger.info(f"Removed {len(removed_rs)} rule strings because of low support, kept {len(kept_rs)}.")

        return kept_rs

    def _calculate_max_confidence(self, value_rules: Set[ValueRule]) -> float:
        """
        Calculate the maximum confidence that a column rule might obtain based
        on the confidences and supports of the current value rules for that potential
        column rule.
        Do this by assuming that all values that are currently not mapped are correct.

        value_rules: a set of value rules. These should all pertain to the same columns

        returns: a float that represents the maximum confidence level that
        this rule can ever achieve
        """
        cfg.logger.debug(
            f"Calculating max confidence for {';'.join(str(_) for _ in value_rules)}")
        support = np.sum([vr.support for vr in value_rules])
        cfg.logger.debug(f"The value rules together have support {support}")

        weighted_confidence = np.sum([vr.support * vr.confidence for vr in value_rules])

        cfg.logger.debug(f"Weighted confidence: {weighted_confidence}")

        return weighted_confidence + (1 - support) * 1.0
