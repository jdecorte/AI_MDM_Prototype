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

class RuleLearnerSuggestionsPage:
    def __init__(self, canvas, handler: IHandler) -> None:
        self.canvas = canvas
        self.handler = handler

    def show(self): 
         with self.canvas.container():
            
            st.title("Rule Learning")
            st.header("Suggesties voor de doorgegeven regels:")

            df_with_predictions = pd.read_json(st.session_state["suggesties_df"])
            pre_selected = [*range(0,len(df_with_predictions))]
                
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

            colb1, colb2, _ = st.columns([1,2,4])
            with colb1:
                st.button("Pas geselecteerde suggesties toe")

            with colb2:
                # Dit gaat niet moeten, moet eigenlijk impliciet gebeuren waneer de gebruiker terug keert naar de vorige fase
                herbereken = st.checkbox("Herbereken regels op basis van de gewijzigde velden")
                if herbereken:
                    rlosp = RuleLearnerOptionsSubPage()
                    rlosp.show()
