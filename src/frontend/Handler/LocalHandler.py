from src.frontend.Handler.IHandler import IHandler
from src.backend.DomainController import DomainController
import json
from src.shared.Views.ColumnRuleView import ColumnRuleView
from typing import List

class LocalHandler(IHandler):

    def __init__(self) -> None:
        self.dc = DomainController()

    def get_column_rules(self, dataframe_in_json, rule_finding_config_in_json) -> List[ColumnRuleView]:
        return {k: ColumnRuleView.parse_from_json(v) for (k,v) in json.loads(self.dc.get_all_column_rules_from_df_and_config(dataframe_in_json, rule_finding_config_in_json)).items()}

    def get_column_rule_from_string(self,dataframe_in_json, rule_string):
        return ColumnRuleView.parse_from_json(self.dc.get_column_rule_from_string(dataframe_in_json=dataframe_in_json, rule_string=rule_string))

    def get_suggestions_given_dataframe_and_column_rules(self,dataframe_in_json, list_of_rule_string_in_json):
        return self.dc.get_suggestions_given_dataframe_and_column_rules(dataframe_in_json=dataframe_in_json, list_of_rule_string_in_json=list_of_rule_string_in_json)

    def get_saved_results(self,dataframe_in_json):
        return self.dc.get_saved_results(dataframe_in_json=dataframe_in_json)

    def get_saved_params(self,dataframe_in_json):
        return self.dc.get_saved_params(dataframe_in_json=dataframe_in_json)

    def fetch_file_from_filepath(self, filepath:str):
        return self.dc.fetch_file_from_filepath(filepath=filepath)


