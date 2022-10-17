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