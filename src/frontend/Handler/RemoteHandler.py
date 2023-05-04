from src.frontend.Handler.IHandler import IHandler
import json
from src.shared.Views.ColumnRuleView import ColumnRuleView
from typing import List
import requests
import streamlit as st

from src.frontend.enums.VarEnum import VarEnum

class RemoteHandler(IHandler):

    def __init__(self, connection_string) -> None:
        self.connection_string = connection_string

    def get_column_rules(self, dataframe_in_json, rule_finding_config_in_json, seq) -> List[ColumnRuleView]:
        data = {}
        data["dataframe_in_json"] = dataframe_in_json
        data["rule_finding_config_in_json"] = rule_finding_config_in_json
        data["seq"] = seq

        return {k: ColumnRuleView.parse_from_json(v)
                for (k, v) in requests.post(
                    f"{self.connection_string}/get_all_column_rules_from_df_and_config",
                    cookies={"session_flask": st.session_state[VarEnum.gb_SESSION_ID_WITH_FILE_HASH.value]},
                    data=json.dumps(data)).json().items()}

    def get_column_rule_from_string(self,dataframe_in_json, rule_string):
        data = {}
        data["dataframe_in_json"] = dataframe_in_json
        data["rule_string"] = rule_string
        return ColumnRuleView.parse_from_json(json.dumps(requests.post(f"{self.connection_string}/get_column_rule_from_string", data=json.dumps(data)).json()))

    def get_suggestions_given_dataframe_and_column_rules(self,dataframe_in_json, list_of_rule_string_in_json, seq):
        data = {}
        data["dataframe_in_json"] = dataframe_in_json
        data["list_of_rule_string_in_json"] = list_of_rule_string_in_json
        data["seq"] = seq
        return json.dumps(requests.post(
            f"{self.connection_string}/get_suggestions_given_dataframe_and_column_rules",
            cookies={"session_flask": st.session_state[VarEnum.gb_SESSION_ID_WITH_FILE_HASH.value]},
            data=json.dumps(data)).json())

    def fetch_file_from_filepath(self, filepath:str):
        data = {}
        data["filepath"] = filepath
        return json.dumps(requests.post(f"{self.connection_string}/fetch_file_from_filepath", data=json.dumps(data)).json())

    def get_session_map(self, dataframe_in_json):
        data = {}
        data["dataframe_in_json"] = dataframe_in_json
        return requests.post(
            f"{self.connection_string}/get_session_map",
            cookies={"session_flask": st.session_state[VarEnum.gb_SESSION_ID_WITH_FILE_HASH.value]},
            data=json.dumps(data)).json()

    def recalculate_column_rules(
            self,
            old_df_in_json,
            new_df_in_json,
            rule_finding_config_in_json,
            affected_columns) -> None:
        data = {}
        data["old_dataframe_in_json"] = old_df_in_json
        data["new_dataframe_in_json"] = new_df_in_json
        data["rule_finding_config_in_json"] = rule_finding_config_in_json
        data["affected_columns"] = json.dumps(affected_columns)

        requests.post(
            f"{self.connection_string}/recalculate_column_rules",
            cookies={"session_flask": st.session_state[VarEnum.gb_SESSION_ID_WITH_FILE_HASH.value]},
            data=json.dumps(data))
        

    # DEDUPE
    def create_deduper_object(self, dedupe_type_dict, dedupe_data) -> json:
        data = {}
        data["dedupe_type_dict"] = dedupe_type_dict
        data["dedupe_data"] = dedupe_data
        requests.post(f"{self.connection_string}/create_deduper_object", cookies={"session_flask" : st.session_state[VarEnum.gb_SESSION_ID_WITH_FILE_HASH.value]}, data=json.dumps(data))

    def dedupe_next_pair(self) -> json:
        return requests.get(f"{self.connection_string}/dedupe_next_pair", cookies={"session_flask" : st.session_state[VarEnum.gb_SESSION_ID_WITH_FILE_HASH.value]}).json()
    
    def dedupe_mark_pair(self, labeled_pair) -> json:
        data = {}
        data["labeled_pair"] = labeled_pair
        temp_data = json.dumps(data)
        requests.post(f"{self.connection_string}/dedupe_mark_pair", cookies={"session_flask" : st.session_state[VarEnum.gb_SESSION_ID_WITH_FILE_HASH.value]}, data=temp_data)

    def dedupe_get_stats(self) -> json:
        return requests.get(f"{self.connection_string}/dedupe_get_stats", cookies={"session_flask" : st.session_state[VarEnum.gb_SESSION_ID_WITH_FILE_HASH.value]}).json()

    def dedupe_train(self):
        data = {}
        requests.post(f"{self.connection_string}/dedupe_train", cookies={"session_flask" : st.session_state[VarEnum.gb_SESSION_ID_WITH_FILE_HASH.value]}, data=json.dumps(data))

    def dedupe_get_clusters(self):
        return requests.get(f"{self.connection_string}/dedupe_get_clusters", cookies={"session_flask" : st.session_state[VarEnum.gb_SESSION_ID_WITH_FILE_HASH.value]}).json()
    
    # ZINGG
    def prepare_zingg(self, dedupe_type_dict, dedupe_data) -> json:
        data = {}
        data["dedupe_type_dict"] = dedupe_type_dict
        data["dedupe_data"] = dedupe_data
        return requests.post(f"{self.connection_string}/prepare_zingg", cookies={"session_flask" : st.session_state[VarEnum.gb_SESSION_ID_WITH_FILE_HASH.value]}, data=json.dumps(data))

    def run_zingg_phase(self, phase) -> json:
        data = {}
        data["phase"] = phase
        return requests.post(f"{self.connection_string}/run_zingg_phase", cookies={"session_flask" : st.session_state[VarEnum.gb_SESSION_ID_WITH_FILE_HASH.value]}, data=json.dumps(data))
    
    def zingg_clear(self) -> json:
        return requests.post(f"{self.connection_string}/zingg_clear", cookies={"session_flask" : st.session_state[VarEnum.gb_SESSION_ID_WITH_FILE_HASH.value]})

    def zingg_unmarked_pairs(self) -> json:
        return requests.get(f"{self.connection_string}/zingg_unmarked_pairs", cookies={"session_flask" : st.session_state[VarEnum.gb_SESSION_ID_WITH_FILE_HASH.value]}).json()
    
    def zingg_mark_pairs(self, marked_df) -> json:
        data = {}
        data["marked_df"] = marked_df
        return requests.post(f"{self.connection_string}/zingg_mark_pairs", cookies={"session_flask" : st.session_state[VarEnum.gb_SESSION_ID_WITH_FILE_HASH.value]}, data=json.dumps(data))

    def zingg_get_stats(self) -> json:
        return requests.get(f"{self.connection_string}/zingg_get_stats", cookies={"session_flask" : st.session_state[VarEnum.gb_SESSION_ID_WITH_FILE_HASH.value]}).json()
    
    def zingg_get_clusters(self) -> json:
        return requests.get(f"{self.connection_string}/zingg_get_clusters", cookies={"session_flask" : st.session_state[VarEnum.gb_SESSION_ID_WITH_FILE_HASH.value]}).json()
    
    # DATA CLEANING
    def clean_dataframe_dataprep(self,dataframe_in_json, custom_pipeline) -> json:
        data = {}
        data["dataframe_in_json"] = dataframe_in_json
        data["custom_pipeline"] = custom_pipeline
        return requests.post(f"{self.connection_string}/clean_dataframe_dataprep", data=json.dumps(data)).json()
        
    def fuzzy_match_dataprep(self,dataframe_in_json, col, cluster_method, df_name, ngram, radius, block_size) -> json:
        data = {}
        data["dataframe_in_json"] = dataframe_in_json
        data["col"] = col
        data["cluster_method"] = cluster_method
        data["df_name"] = df_name
        data["ngram"] = ngram
        data["radius"] = radius
        data["block_size"] = block_size
        return requests.post(f"{self.connection_string}/fuzzy_match_dataprep", data=json.dumps(data)).json()
        
    def structure_detection(self,series_in_json, exception_chars, compress) -> json:
        data = {}
        data["series_in_json"] = series_in_json
        data["exception_chars"] = exception_chars
        data["compress"] = compress
        return requests.post(f"{self.connection_string}/structure_detection", data=json.dumps(data)).json()