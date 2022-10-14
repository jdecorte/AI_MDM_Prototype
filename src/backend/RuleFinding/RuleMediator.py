from ipaddress import collapse_addresses
import pandas as pd
import numpy as np
import config as cfg

from src.backend.RuleFinding.CR.CRFilters.ColumnRuleFilter import ColumnRuleFilter
from src.backend.RuleFinding.VR.ValueRuleFactory import ValueRuleFactory
from src.backend.RuleFinding.VR.ValueRuleRepo import ValueRuleRepo
from src.backend.RuleFinding.CR.ColumnRuleFactory import ColumnRuleFactory
from src.backend.RuleFinding.CR.ColumnRuleRepo import ColumnRuleRepo
from src.backend.RuleFinding.AR.AssociationRuleFinder import AssociationRuleFinder
from src.shared.Enums.FiltererEnum import FiltererEnum
from src.backend.RuleFinding.CR.CRFilters.ColumnRuleFilter import ColumnRuleFilter_ZScore

class RuleMediator:
    def __init__(self, df_OHE, original_df) -> None:
        self.df_OHE = df_OHE
        self.original_df = original_df

        self.association_rule_finder = None
        self.value_rule_repo = None
        self.column_rule_repo = None

        self.value_rule_factory = ValueRuleFactory()
        self.column_rule_factory = ColumnRuleFactory(df_dummy=df_OHE,  original_df=original_df)

    def create_column_rules_from_clean_dataframe(self, min_support : float, max_len : int, 
                          min_lift : float, min_confidence : float, filterer_string : str) -> None:
        ar_dataframe = self._find_association_rules(self.df_OHE, min_support, max_len, min_lift, min_confidence)
        # Maak een dict van ValueRules aan in de VR Factory
        vr_dict = self.value_rule_factory.transform_ar_dataframe_to_value_rules_dict(ar_dataframe)
        # Maak een VR Repo aan door de dict van ValueRules mee te geven
        self.value_rule_repo = ValueRuleRepo(vr_dict)
        # Roep get_filtered methode aan op de Repo
        list_of_strings_that_represent_CR = self.value_rule_repo.filter_out_column_rule_strings_from_dict_of_value_rules(min_support=min_support)
        # De overige ValueRules worden gebruikt om opnieuw een dict aan te maken in de CR Factory
        cr_dict = self.column_rule_factory.create_dict_of_dict_of_column_rules_from_list_of_strings(list_of_strings_that_represent_CR)
        # Maak een CR Repo aan door de dict van ColumnRules mee te geven
        self.column_rule_repo = ColumnRuleRepo(cr_dict)
        # Roep getInteresting Rules methode aan op de Repo -> Verschillende implementaties en RETURN deze.
        self.column_rule_repo.keep_only_interesting_column_rules(filterer=self._parse_filterer_string(filterer_string), confidence_bound=min_confidence)


        

    def get_all_column_rules(self):
        return {**self.get_cr_definitions_dict(),**self.get_cr_with_100_confidence_dict(), **self.get_cr_without_100_confidence_dict()}

    def get_cr_definitions_dict(self):
        return self.column_rule_repo.get_definitions_dict()

    def get_cr_with_100_confidence_dict(self):
        return self.column_rule_repo.get_cr_with_100_confidence_dict()

    def get_cr_without_100_confidence_dict(self):
        return self.column_rule_repo.get_cr_without_100_confidence_dict()

    def get_non_definition_column_rules_dict(self):
        return self.column_rule_repo.get_non_definitions_dict()
        
    def _find_association_rules(self, df_OHE, min_support : float, max_len : int, 
                          min_lift : float, min_confidence : float):
        self.association_rule_finder = AssociationRuleFinder(df_OHE, min_support, max_len, min_lift, min_confidence)
        return self.association_rule_finder.get_association_rules()


    def _parse_filterer_string(self, s:str)-> ColumnRuleFilter:
        filter_to_return = None
        if s == FiltererEnum.Z_SCORE:
            filter_to_return = ColumnRuleFilter_ZScore()
        else:
            raise Exception("Invalid Parsing of Filterer string")
        return filter_to_return


        


        

