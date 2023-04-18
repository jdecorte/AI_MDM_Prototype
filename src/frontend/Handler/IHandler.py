from abc import ABC, abstractmethod
import json

class IHandler(ABC):

    # RULE LEARNING
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
    def recalculate_column_rules(self, old_df_in_json, new_df_in_json, rule_finding_config_in_json, affected_columns):
        raise Exception("Not implemented Exception")


    # DEDUPE
    @abstractmethod
    def create_deduper_object(self, dedupe_type_dict, dedupe_data) -> json:
        raise Exception("Not implemented Exception")

    @abstractmethod
    def dedupe_next_pair(self) -> json:
        raise Exception("Not implemented Exception")
    
    @abstractmethod
    def dedupe_mark_pair(self, labeled_pair) -> json:
        raise Exception("Not implemented Exception")

    @abstractmethod
    def dedupe_get_stats(self) -> json:
        raise Exception("Not implemented Exception")

    @abstractmethod
    def dedupe_train(self) -> json:
        raise Exception("Not implemented Exception")

    @abstractmethod
    def dedupe_get_clusters(self) -> json:
        raise Exception("Not implemented Exception")
    
    @abstractmethod
    def prepare_zingg(self, dedupe_type_dict, dedupe_data) -> json:
        raise Exception("Not implemented Exception")
    
    @abstractmethod
    def zingg_unmarked_pairs(self) -> json:
        raise Exception("Not implemented Exception")
    
    @abstractmethod
    def zingg_mark_pairs(self, marked_df) -> json:
        raise Exception("Not implemented Exception")
    
    @abstractmethod
    def zingg_get_stats(self) -> json:
        raise Exception("Not implemented Exception")
    

    

    
    # DATA CLEANING
    @abstractmethod
    def clean_dataframe_dataprep(self,dataframe_in_json, custom_pipeline) -> json:
        raise Exception("Not implemented Exception")
        
    @abstractmethod
    def fuzzy_match_dataprep(self,dataframe_in_json, col, cluster_method, df_name, ngram, radius, block_size) -> json:
        raise Exception("Not implemented Exception")
        
    @abstractmethod
    def structure_detection(self,series_in_json, exception_chars, compress) -> json:
        raise Exception("Not implemented Exception")