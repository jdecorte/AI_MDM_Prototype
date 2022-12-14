import streamlit as st
import pandas as pd
import os
import csv
import re
import logging
import optparse


import dedupe

from st_aggrid import GridOptionsBuilder, AgGrid, GridUpdateMode, DataReturnMode, JsCode
from src.frontend.RuleLearner.RuleLearnerOptionsSubPage import RuleLearnerOptionsSubPage
from src.frontend.Handler.IHandler import IHandler
from src.frontend.DeDuper.DeDupeTypesEnum import DeDupeTypesEnum


class DeDupeInitPage:
    def __init__(self, canvas, handler) -> None:
        self.canvas = canvas
        self.handler = handler

    # def _transform_type_dict_to_correct_format_for_dedupe(self, dict_of_types):
    #     return [{'field':k, 'type':v} for k,v in dict_of_types.items()]


    def show(self): 

        # FOR DEBUG ON RESTOS.CSV PRE-DEFINED FIELDS:
        st.session_state['dedupe_type_dict'] = {
            # "id" : "String",
            "name":"String",
            "addr":"String",
            "city":"String",
            "type":"String",
            "class": "String"
        }

        with self.canvas.container(): 
            st.title("DeDupe")
            st.markdown(f"<h4>Ingeladen Dataset: </h4>", unsafe_allow_html=True)

            # Toon de dataframe -> NIET EDITEERBAAR
            MIN_HEIGHT = 50
            MAX_HEIGHT = 500
            ROW_HEIGHT = 60

            gb = GridOptionsBuilder.from_dataframe(st.session_state["dataframe"])
            gb.configure_side_bar()
            gb.configure_default_column(groupable=True, value=True, enableRowGroup=True, aggFunc="sum", editable=False)
            gridOptions = gb.build()
            grid_response = AgGrid(st.session_state["dataframe"], gridOptions=gridOptions, enable_enterprise_modules=True, height=min(MIN_HEIGHT + len(st.session_state["dataframe"]) * ROW_HEIGHT, MAX_HEIGHT))

            st.subheader("Selecteer kolommen om te gebruiken in deduplicatie-proces")

            colA, colB, colC = st.columns([3,3,8])
            with colA:
                selected_col = st.selectbox('Kolom:', st.session_state["dataframe"].columns)

            with colB:
                selected_type = st.selectbox('Type:', DeDupeTypesEnum._member_names_)

            with colC:
                if selected_type:
                    st.write(eval(f"DeDupeTypesEnum.{selected_type}"))


            col_1, col_2, col_3,_ = st.columns([1,1,1,6])
            with col_1:
                add_btn = st.button("Add")
                if add_btn:
                    st.session_state["dedupe_type_dict"][selected_col] = selected_type
                    
            with col_2:
                remove_btn = st.button("Remove")
                if remove_btn:
                    if selected_col in st.session_state["dedupe_type_dict"]:
                        del st.session_state["dedupe_type_dict"][selected_col]
            
            with col_3:
                if len(st.session_state['dedupe_type_dict'].values()) > 0:
                    start_training_btn = st.button("Start training")
                    if start_training_btn:
                        self.handler.create_deduper_object(st.session_state["dedupe_type_dict"], st.session_state["dataframe"].to_json())
                        st.session_state["currentState"] = "LabelRecords_get_record_pair" 
                        st.experimental_rerun()

            st.write("Actieve selectie:")
            if st.session_state['dedupe_type_dict'] == {}:
                st.write("U heeft nog geen kolommen gekozen")
            else:
                st.write(st.session_state["dedupe_type_dict"])