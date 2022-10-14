from src.frontend.Handler.IHandler import IHandler
from src.backend.DomainController import DomainController
import json
from typing import Dict

class LocalHandler(IHandler):

    def __init__(self) -> None:
        self.dc = DomainController()

    def get_column_rules(self, dataframe_in_json, rule_finding_config_in_json) -> Dict:
        return json.loads(self.dc.create_column_rules_and_return_in_json(dataframe_in_json, rule_finding_config_in_json))