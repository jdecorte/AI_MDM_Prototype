from src.frontend.Handler.IHandler import IHandler
from src.backend.DomainController import DomainController
import json
from src.shared.Views.ColumnRuleView import ColumnRuleView
from typing import List

class LocalHandler(IHandler):

    def __init__(self) -> None:
        self.dc = DomainController()

    def get_column_rules(self, dataframe_in_json, rule_finding_config_in_json) -> List[ColumnRuleView]:
        print("LOCALHANDLER")
        print(json.loads(self.dc.get_all_column_rules_from_df_and_config(dataframe_in_json, rule_finding_config_in_json)))
        to_return =  {k: ColumnRuleView.parse_from_json(v) for (k,v) in json.loads(self.dc.get_all_column_rules_from_df_and_config(dataframe_in_json, rule_finding_config_in_json)).items()}

        
        print(to_return)
        return to_return