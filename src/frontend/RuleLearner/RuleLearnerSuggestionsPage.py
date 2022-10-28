from ast import arg
from cgitb import handler
import rlcompleter
import numpy as np
import pandas as pd
import streamlit as st
from st_aggrid import GridOptionsBuilder, AgGrid, GridUpdateMode, DataReturnMode, JsCode
from streamlit.components.v1 import html
from src.frontend.RuleLearner.RuleLearnerOptionsSubPage import RuleLearnerOptionsSubPage
from src.frontend.StateManager import StateManager
from src.frontend.Handler.IHandler import IHandler
from src.shared.Configs.RuleFindingConfig import RuleFindingConfig

class RuleLearnerSuggestionsPage:
    def __init__(self, canvas, handler: IHandler) -> None:
        self.canvas = canvas
        self.handler = handler

    def show(self): 
         with self.canvas.container():
            
            st.title("Rule Learning")
            st.header("Suggesties voor de doorgegeven regels:")

            df_with_predictions = pd.read_json(eval(st.session_state["suggesties_df"]))
            # pre_selected = [*range(0,len(df_with_predictions))]
            pre_selected = []
                
            gb1 = GridOptionsBuilder.from_dataframe(df_with_predictions)
            gb1.configure_grid_options(fit_columns_on_grid_load=True)
            gb1.configure_selection('multiple', pre_selected_rows=pre_selected, use_checkbox=True, groupSelectsChildren=True, groupSelectsFiltered=True)
            response_selection_suggestion_finder = AgGrid(
                df_with_predictions,
                height= 150,
                editable=False,
                gridOptions=gb1.build(),
                data_return_mode="filtered_and_sorted",
                update_mode="selection_changed",
                theme="streamlit",
                enable_enterprise_modules = False
            )

            colb0, colb1, colb2, _ = st.columns([1,1,2,4])
           
                
            with colb0:
                apply_suggestions = st.button("Pas geselecteerde suggesties toe")
                if apply_suggestions:
                    
                    rows_selected = response_selection_suggestion_finder['selected_rows']
                    list_of_df_idx = df_with_predictions.index
                    st.write(list_of_df_idx)
                    st.write(rows_selected)
                    set_of_cols = set()
                    for idx, row in enumerate(rows_selected):
                        index_of_to_change = list_of_df_idx[idx]
                        val_to_change = row["__BEST_PREDICTION"]
                        rs = row["__BEST_RULE"]
                        rss = rs.split(" => ")
                        col_to_change = rss[1]
                        set_of_cols.add(col_to_change)
                        for e in rss[0].split(","):
                            set_of_cols.add(e)
                        # Change value in dataframe
                        st.session_state['dataframe'].loc[index_of_to_change, col_to_change] = val_to_change

                    # Toon nog is de dataframe om zeker te zijn
                    st.write(st.session_state['dataframe'])
                    
                    st.write(rows_selected)
                    st.write(list(set_of_cols))
                    st.session_state["columns_affected_by_suggestion_application"] = list(set_of_cols)

                    # Herbereken de CRs van de regels uit st.Session_state[XXXX] en replace deze (gewoon value aanpassen voor zelfde key)
                    for k in st.session_state["gevonden_rules_dict"].keys():
                        ks = k.split(" => ")
                        ksr = ks[1]
                        ksl = ks[0].split(",")
                        kst = ksr + ksl
                        for e in st.session_state["columns_affected_by_suggestion_application"]:
                            if e in kst:
                                st.session_state["gevonden_rules_dict"][k] = self.handler.get_column_rule_from_string(dataframe_in_json=st.session_state['dataframe'], rule_string=e)
                                break



            with colb2:
                # Dit gaat niet moeten, moet eigenlijk impliciet gebeuren waneer de gebruiker terug keert naar de vorige fase
                herbereken = st.checkbox("Herbereken regels op basis van de gewijzigde velden")
                if herbereken:
                    rlosp = RuleLearnerOptionsSubPage()
                    rlosp.show()

            with colb1:
                submitted = st.button("Bereken Regels opnieuw")
                if submitted:
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
                    new_rules = self.handler.get_column_rules(dataframe_in_json=st.session_state["dataframe"].to_json(),rule_finding_config_in_json=json_rule_finding_config)
                    

                    # TODO vervang None
                    st.session_state['gevonden_rules_dict'] = None
                    st.session_state["currentState"] = "BekijkRules"
                    st.experimental_rerun()