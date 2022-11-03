from abc import ABC, abstractmethod
import json

class IHandler(ABC):

    @abstractmethod
    def get_column_rules(self, dataframe_in_json, rule_finding_config_in_json, seq) -> json:
        raise Exception("Not implemented Exception")

    @abstractmethod
    def get_column_rule_from_string(self,dataframe_in_json, rule_string):
        raise Exception("Not implemented Exception")

    @abstractmethod
    def get_suggestions_given_dataframe_and_column_rules(self,dataframe_in_json, list_of_rule_string_in_json, seq):
        raise Exception("Not implemented Exception")

    @abstractmethod
    def fetch_file_from_filepath(self, filepath:str):
        raise Exception("Not implemented Exception")

    @abstractmethod
    def get_session_map(self, dataframe_in_json):
        raise Exception("Not implemented Exception")

    @abstractmethod
    def recalculate_column_rules(self, old_dataframe_in_json, new_dataframe_in_json, rule_finding_config_in_json, affected_columns):
        raise Exception("Not implemented Exception")