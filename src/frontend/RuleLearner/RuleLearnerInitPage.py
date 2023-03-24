import streamlit as st
import pandas as pd
from st_aggrid import GridOptionsBuilder, AgGrid, GridUpdateMode, DataReturnMode, JsCode
from src.frontend.RuleLearner.RuleLearnerOptionsComponent import RuleLearnerOptionsComponent
from src.frontend.Handler.IHandler import IHandler

from src.shared.Enums.FiltererEnum import FiltererEnum
from src.shared.Enums.BinningEnum import BinningEnum
from src.shared.Enums.DroppingEnum import DroppingEnum

from src.shared.Configs.RuleFindingConfig import RuleFindingConfig
from src.shared.Views.ColumnRuleView import ColumnRuleView

from src.frontend.DatasetDisplayer.DatasetDisplayerComponent import DatasetDisplayerComponent

class RuleLearnerInitPage:
    def __init__(self, canvas, handler: IHandler) -> None:
        self.canvas = canvas
        self.handler = handler

    def _create_total_binning_dict(_self, dict_to_show):
        st.session_state["binning_option"] = dict_to_show
        return st.session_state["binning_option"]

    def _create_total_dropping_dict(_self, dict_to_show):
        st.session_state["dropping_options"] = dict_to_show
        return st.session_state["dropping_options"]

    @st.cache_resource
    def _create_default_dropping_dict(_self, d):
        return d

    def _show_ag_grid(self):
            # Toon de dataframe -> NIET EDITEERBAAR
            MIN_HEIGHT = 50
            MAX_HEIGHT = 500
            ROW_HEIGHT = 60

            st.markdown(f"<h4>Ingeladen Dataset: </h4>", unsafe_allow_html=True)
            gb = GridOptionsBuilder.from_dataframe(st.session_state["dataframe"])
            gb.configure_side_bar()
            gb.configure_default_column(groupable=True, value=True, enableRowGroup=True, aggFunc="sum", editable=False)
            gridOptions = gb.build()
            grid_response = AgGrid(st.session_state["dataframe"], gridOptions=gridOptions, enable_enterprise_modules=True, height=min(MIN_HEIGHT + len(st.session_state["dataframe"]) * ROW_HEIGHT, MAX_HEIGHT))

    def show(self): 
        with self.canvas.container(): 

            st.title("Rule Learning")
            DatasetDisplayerComponent().show(st.session_state["dataframe"])
            RuleLearnerOptionsComponent().show()

            if st.button("Analyseer Data"):
                rule_finding_config = RuleFindingConfig(
                    rule_length=st.session_state["rule_length"], 
                    min_support=st.session_state["min_support"],
                    lift=st.session_state["lift"], 
                    confidence=st.session_state["confidence"],
                    filtering_string=st.session_state["filtering_string"],
                    dropping_options=st.session_state["dropping_options"],
                    binning_option=st.session_state["binning_option"]
                    )
                json_rule_finding_config = rule_finding_config.to_json()

                # Set session_state attributes
                st.session_state['gevonden_rules_dict'] = self.handler.get_column_rules(dataframe_in_json=st.session_state["dataframe"].to_json(),rule_finding_config_in_json=json_rule_finding_config, seq=st.session_state["current_seq"])
                st.session_state["currentState"] = "BekijkRules"
                st.experimental_rerun()