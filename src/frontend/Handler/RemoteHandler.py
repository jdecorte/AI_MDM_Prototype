from src.frontend.Handler.IHandler import IHandler
import json
from src.shared.Views.ColumnRuleView import ColumnRuleView
from typing import List
import requests

class RemoteHandler(IHandler):

    def __init__(self, connection_string) -> None:
        self.connection_string = connection_string

    def get_column_rules(self, dataframe_in_json, rule_finding_config_in_json) -> List[ColumnRuleView]:
        data = {}
        data["dataframe_in_json"] = dataframe_in_json
        data["rule_finding_config_in_json"] = rule_finding_config_in_json
        return  {k: ColumnRuleView.parse_from_json(v) for (k,v) in requests.post(f"{self.connection_string}/get_all_column_rules_from_df_and_config", data=json.dumps(data)).json().items()}

    def get_column_rule_from_string(self,dataframe_in_json, rule_string):
        data = {}
        data["dataframe_in_json"] = dataframe_in_json
        data["rule_string"] = rule_string
        return ColumnRuleView.parse_from_json(json.dumps(requests.post(f"{self.connection_string}/get_column_rule_from_string", data=json.dumps(data)).json()))

    def get_suggestions_given_dataframe_and_column_rules(self,dataframe_in_json, list_of_rule_string_in_json):
        data = {}
        data["dataframe_in_json"] = dataframe_in_json
        data["list_of_rule_string_in_json"] = list_of_rule_string_in_json
        return json.dumps(requests.post(f"{self.connection_string}/get_suggestions_given_dataframe_and_column_rules", data=json.dumps(data)).json())

    def get_saved_results(self,dataframe_in_json):
        data = {}
        data["dataframe_in_json"] = dataframe_in_json
        return json.dumps(requests.post(f"{self.connection_string}/get_saved_results", data=json.dumps(data)).json())

    def get_saved_params(self,dataframe_in_json):
        data = {}
        data["dataframe_in_json"] = dataframe_in_json
        return json.dumps(requests.post(f"{self.connection_string}/get_saved_params", data=json.dumps(data)).json())

    def fetch_file_from_filepath(self, filepath:str):
        data = {}
        data["filepath"] = filepath
        return json.dumps(requests.post(f"{self.connection_string}/fetch_file_from_filepath", data=json.dumps(data)).json())