from src.frontend.Handler.IHandler import IHandler
import json
import requests

class RemoteHandler(IHandler):

    def __init__(self, connection_string) -> None:
        self.connection_string = connection_string

    def get_column_rules(self, dataframe_in_json, rule_finding_config_in_json) -> json:
        data = {}
        data["dataframe_in_json"] = dataframe_in_json
        data["rule_finding_config_in_json"] = rule_finding_config_in_json
        to_return =  requests.post(f"{self.connection_string}/t", data=json.dumps(data))
        return to_return.json()