import pandas as pd
import numpy as np
import json

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

    # DATA CLEANING

    def clean_data_frame(self,df, json_string) -> pd.DataFrame:
        return self.data_prepper.clean_data_frame(df, json_string)

    @route('/t', methods=['GET','POST'])
    def create_column_rules_and_return_in_json(self,dataframe_in_json="", rule_finding_config_in_json="") -> json:

        if dataframe_in_json == "" and rule_finding_config_in_json=="":
            data_to_use = json.loads(request.data)
            dataframe_in_json = data_to_use["dataframe_in_json"]
            rule_finding_config_in_json = data_to_use["rule_finding_config_in_json"]

        df = pd.read_json(dataframe_in_json)
        rfc = RuleFindingConfig.create_from_json(rule_finding_config_in_json)

        # gebruik de gegevens uit rfc om mee te geven aan create_column_rules_from_dataframe
        self._create_column_rules_from_dataframe(df=df, binning_option=rfc.binning_option, min_confidence=rfc.confidence, dropping_options=rfc.dropping_options, min_support=rfc.min_support, min_lift=rfc.lift, max_len=rfc.rule_length, filterer_string=rfc.filtering_string )
        
        return json.dumps({
        "def" : [x.parse_self_to_view().to_json() for x in self.get_cr_definitions_dict().values()],
        "always" : [x.parse_self_to_view().to_json() for x in self.get_cr_with_100_confidence_dict().values()],
        "not_always" : [x.parse_self_to_view().to_json() for x in self.get_cr_without_100_confidence_dict().values()]})

    def _create_column_rules_from_dataframe(self, df, min_support : float, max_len : int, 
                          min_lift : float, min_confidence : float, filterer_string : str, binning_option: Dict[str, BinningEnum], dropping_options : Dict[str,Dict[str, str]]) -> None:

        # Dataprepper transfromeert dataframe naar OHE op basis van rule_config object dropping en binning opties
        # df_OHE = self.data_prepper.transform_data_frame_to_OHE(df,dropping_options,binning_option)

        # Hier al string type maken
        df_to_use = df.astype(str)
        df_OHE = self.data_prepper.transform_data_frame_to_OHE(df_to_use, drop_nan=False)
        
        # Voor de RuleMediator wordt aangemaakt, moet de df_OHE reeds voldoen aan de dropping en binning opties
        self.rule_mediator = RuleMediator(original_df=df_to_use, df_OHE=df_OHE)
        self.rule_mediator.create_column_rules_from_clean_dataframe(min_support, max_len, min_lift, min_confidence, filterer_string=filterer_string)


    def get_all_column_rules(self):
        return self.rule_mediator.get_all_column_rules()

    def get_cr_definitions_dict(self):
        return self.rule_mediator.get_cr_definitions_dict()

    def get_non_definition_column_rules_dict(self):
        return self.rule_mediator.get_non_definition_column_rules_dict()

    def get_cr_with_100_confidence_dict(self):
        return self.rule_mediator.get_cr_with_100_confidence_dict()

    def get_cr_without_100_confidence_dict(self):
        return self.rule_mediator.get_cr_without_100_confidence_dict()

    # SUGGESTIONS
    def get_suggestions_given_dataframe_and_column_rules(self, df) -> pd.DataFrame:
        self.suggestion_finder = SuggestionFinder(column_rules=self.get_non_definition_column_rules_dict().values(), original_df=df)
        df_rows_with_errors = self.suggestion_finder.df_errors_.drop(['RULESTRING', 'FOUND_CON', 'SUGGEST_CON'], axis=1).drop_duplicates()
        return self.suggestion_finder.highest_scoring_suggestion(df_rows_with_errors)

    def run_flask(self):
        self.app.run()

DomainController.register(app, route_base="/")