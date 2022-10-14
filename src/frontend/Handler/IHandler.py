from abc import ABC, abstractmethod
import json

class IHandler(ABC):

    @abstractmethod
    def get_column_rules(self, dataframe_in_json="", rule_finding_config_in_json="") -> json:
        raise Exception("Not implemented Exception")