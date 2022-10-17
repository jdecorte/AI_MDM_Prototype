from abc import ABC, abstractmethod
import json

class IHandler(ABC):

    @abstractmethod
    def get_column_rules(self, dataframe_in_json="", rule_finding_config_in_json="") -> json:
        raise Exception("Not implemented Exception")

    @abstractmethod
    def get_column_rule_from_string(self,dataframe_in_json="", rule_string=""):
        raise Exception("Not implemented Exception")