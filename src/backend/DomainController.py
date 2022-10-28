import pandas as pd
import numpy as np
import json
import hashlib
import glob
import os
from src.backend.HelperFunctions import HelperFunctions
from datetime import datetime

from src.backend.RuleFinding.RuleMediator import RuleMediator
from src.backend.Suggestions.SuggestionFinder import SuggestionFinder
from src.backend.DataPreperation.DataPrepper import DataPrepper
from src.shared.Configs.RuleFindingConfig import RuleFindingConfig
from src.shared.Enums.BinningEnum import BinningEnum
from typing import Dict
from flask import request
from flask import Flask, json
from flask_classful import FlaskView, route

app = Flask(__name__)

class DomainController(FlaskView):
    
    def __init__(self) -> None:
        self.app = app
        self.data_prepper = DataPrepper()
        self.rule_mediator = None
        self.suggestion_finder = None


    # FETCHING OF FILES FOR GUI STATE:
    @route('/fetch_file_from_filepath', methods=['GET','POST'])
    def fetch_file_from_filepath(self, filepath:str=""):
        if filepath == "":
            data_to_use = json.loads(request.data)
            filepath = data_to_use["filepath"]
        with open(filepath, "r") as json_file:
            content = json_file.read()
        return content



    # VERIFICATION IN LOCAL STORAGE
    def _verify_in_local_storage(self,md5_to_check:str,unique_storage_id,md5_of_dataframe, seq) -> json:
        # If method returns None -> Was not in storage with specific settings
        list_of_globs = glob.glob(f"storage/{unique_storage_id}/{md5_of_dataframe}/*.json")
        for gl in list_of_globs:
            found_md5 = (gl.split("_")[-1]).split(".")[0]
            if md5_to_check == found_md5:
                with open(gl, "r") as json_file:
                    to_return = json.loads(json_file.read())
                self._write_to_session_map(unique_storage_id,md5_of_dataframe,gl.split("/")[-1].split("_")[1],seq,gl)
                return to_return["result"]
        return None
        
    
    # METHODS FOR SESSION_MAP
    @route('/get_session_map', methods=['GET','POST'])
    def get_session_map(self,dataframe_in_json=""):
        unique_storage_id = "Local"
        if dataframe_in_json == "":
            data_to_use = json.loads(request.data)
            unique_storage_id = request.remote_addr
            dataframe_in_json = data_to_use["dataframe_in_json"]

        path = f"storage/{unique_storage_id}/{hashlib.md5(dataframe_in_json.encode('utf-8')).hexdigest()}"
        path_with_file = f"{path}/session_map.json"
        if not os.path.exists(path):
            os.makedirs(path)
            with open(path_with_file,"w+") as f:
                f.write(json.dumps({}))
            return {}
        else:
            with open(path_with_file, "r") as json_file:
                content = json.loads(json_file.read())
                return content

    def _write_to_session_map(self,unique_storage_id,md5_of_dataframe, method_name:str, session_id:str, file_name_of_results:str):
        path = f"storage/{unique_storage_id}/{md5_of_dataframe}/session_map.json"
        with open(path, "r") as json_file:
            content = json.loads(json_file.read())
        if session_id in content:
            content[session_id][method_name] = file_name_of_results
        else:
             content[session_id] = {method_name:file_name_of_results}
        with open(path, "w+") as json_file:
            json_file.write(json.dumps(content))
        
            
    # DATA CLEANING
    @route('/clean_dataframe', methods=['GET','POST'])
    def clean_dataframe(self,df, json_string) -> pd.DataFrame:
        return self.data_prepper.clean_data_frame(df, json_string)

    # RULE LEARNING
    @route('/get_all_column_rules_from_df_and_config', methods=['GET','POST'])
    def get_all_column_rules_from_df_and_config(self,dataframe_in_json="", rule_finding_config_in_json="", seq="") -> json:

        # LOAD PARAMS
        unique_storage_id = "Local"
        if dataframe_in_json == "" and rule_finding_config_in_json=="" and seq=="":
            data_to_use = json.loads(request.data)
            unique_storage_id = request.remote_addr
            dataframe_in_json = data_to_use["dataframe_in_json"]
            rule_finding_config_in_json = data_to_use["rule_finding_config_in_json"]
            if "seq" not in data_to_use:
                seq = ""
            else:
                seq = data_to_use["seq"]

        # VERIFY IF IN LOCAL STORAGE:
        md5_of_dataframe = hashlib.md5(dataframe_in_json.encode('utf-8')).hexdigest()
        result_in_local_storage = self._verify_in_local_storage(hashlib.md5(rule_finding_config_in_json.encode('utf-8')).hexdigest(),unique_storage_id,md5_of_dataframe, seq)
        if result_in_local_storage != None:
            return json.dumps(result_in_local_storage)
           

        # COMPUTE RESULTS
        rfc = RuleFindingConfig.create_from_json(rule_finding_config_in_json)
        df = pd.read_json(dataframe_in_json)
        df_to_use = df.astype(str)
        df_OHE = self.data_prepper.transform_data_frame_to_OHE(df_to_use, drop_nan=False)
        self.rule_mediator = RuleMediator(original_df=df_to_use, df_OHE=df_OHE)
        self.rule_mediator.create_column_rules_from_clean_dataframe(rfc.min_support, rfc.rule_length, rfc.lift, rfc.confidence, filterer_string=rfc.filtering_string)
        result = {k: v.parse_self_to_view().to_json() for (k,v) in self.rule_mediator.get_all_column_rules().items()}
        save_dump = json.dumps({"result": result, "params": {"rule_finding_config_in_json" : rule_finding_config_in_json}})

        # SAVE RESULTS
        parsed_date_time = datetime.now().strftime("%m_%d_%H_%M_%S")
        file_name = f"Rule-learning_rules_{parsed_date_time}_{hashlib.md5(rule_finding_config_in_json.encode('utf-8')).hexdigest()}"
        file_path = f"storage/{unique_storage_id}/{md5_of_dataframe}\\{file_name}.json"
        HelperFunctions.save_results_to(unique_id=unique_storage_id, md5_hash= hashlib.md5(dataframe_in_json.encode('utf-8')).hexdigest()
                                        ,json_string=save_dump, file_name=file_name)
        self._write_to_session_map(unique_storage_id,md5_of_dataframe,"rules",seq,file_path)
        # RETURN RESULTS
        return json.dumps(result)

    @route('/get_column_rule_from_string', methods=['GET','POST'])
    def get_column_rule_from_string(self,dataframe_in_json="", rule_string=""):
        if dataframe_in_json == "" and rule_string=="":
            data_to_use = json.loads(request.data)
            dataframe_in_json = data_to_use["dataframe_in_json"]
            rule_string = data_to_use["rule_string"]

        df = pd.read_json(dataframe_in_json)
        df_to_use = df.astype(str)
        df_OHE = self.data_prepper.transform_data_frame_to_OHE(df_to_use, drop_nan=False)
        
        self.rule_mediator = RuleMediator(original_df=df_to_use, df_OHE=df_OHE)
        return self.rule_mediator.get_column_rule_from_string(rule_string=rule_string).parse_self_to_view().to_json()


    @route('/get_saved_results', methods=['GET','POST'])
    def get_saved_results(self,dataframe_in_json=""):
        unique_storage_id = "Local"
        if dataframe_in_json == "":
            data_to_use = json.loads(request.data)
            dataframe_in_json = data_to_use["dataframe_in_json"]
            unique_storage_id = request.remote_addr
        return json.dumps(self._get_all_json_for_dataframe(unique_storage_id,hashlib.md5(dataframe_in_json.encode('utf-8')).hexdigest()))


    # SUGGESTIONS
    @route('/get_suggestions_given_dataframe_and_column_rules', methods=['POST'])
    def get_suggestions_given_dataframe_and_column_rules(self, dataframe_in_json="", list_of_rule_string_in_json="", seq="") -> json:
        
        # LOAD PARAMS
        unique_storage_id = "Local"
        if dataframe_in_json == "" and list_of_rule_string_in_json=="":
            data_to_use = json.loads(request.data)
            unique_storage_id = request.remote_addr
            dataframe_in_json = data_to_use["dataframe_in_json"]
            list_of_rule_string_in_json = data_to_use["list_of_rule_string_in_json"]
            if "seq" not in data_to_use:
                seq = ""
            else:
                seq = data_to_use["seq"]

        # VERIFY IF IN LOCAL STORAGE:
        md5_of_dataframe = hashlib.md5(dataframe_in_json.encode('utf-8')).hexdigest()
        result_in_local_storage = self._verify_in_local_storage(hashlib.md5(list_of_rule_string_in_json.encode('utf-8')).hexdigest(),unique_storage_id,md5_of_dataframe, seq)
        if result_in_local_storage != None:
            return json.dumps(result_in_local_storage)


        # COMPUTE RESULTS
        list_of_rule_string = json.loads(list_of_rule_string_in_json)
        df = pd.read_json(dataframe_in_json)
        df_to_use = df.astype(str)
        df_OHE = self.data_prepper.transform_data_frame_to_OHE(df_to_use, drop_nan=False)
        self.rule_mediator = RuleMediator(original_df=df_to_use, df_OHE=df_OHE)

        column_rules = []
        for rs in list_of_rule_string:
            column_rules.append(self.rule_mediator.get_column_rule_from_string(rule_string=rs))
        self.suggestion_finder = SuggestionFinder(column_rules=column_rules, original_df=df_to_use)
        df_rows_with_errors = self.suggestion_finder.df_errors_.drop(['RULESTRING', 'FOUND_CON', 'SUGGEST_CON'], axis=1).drop_duplicates()
        result = self.suggestion_finder.highest_scoring_suggestion(df_rows_with_errors).to_json()
        save_dump = json.dumps({"result": result, "params": {"list_of_rule_string_in_json":list_of_rule_string_in_json}, "seq":seq})

        # SAVE RESULTS
        parsed_date_time = datetime.now().strftime("%m_%d_%H_%M_%S")
        file_name= f"Rule-learning_suggestions_{parsed_date_time}_{hashlib.md5(list_of_rule_string_in_json.encode('utf-8')).hexdigest()}"
        file_path = f"storage/{unique_storage_id}/{md5_of_dataframe}\\{file_name}.json"
        HelperFunctions.save_results_to(unique_id=unique_storage_id, md5_hash= hashlib.md5(dataframe_in_json.encode('utf-8')).hexdigest()
                                        ,json_string=save_dump, file_name=file_name)
        self._write_to_session_map(unique_storage_id,md5_of_dataframe,"suggestions",seq,file_path)                                

        # RETURN RESULTS
        return json.dumps(result)

    def run_flask(self):
        self.app.run()

DomainController.register(app, route_base="/")