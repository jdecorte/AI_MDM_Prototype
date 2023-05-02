import streamlit as st
import pandas as pd

from st_aggrid import GridOptionsBuilder, AgGrid, GridUpdateMode, DataReturnMode, JsCode
from src.frontend.Deduplication.Enums.DeDupeTypesEnum import DeDupeTypesEnum
from src.frontend.Deduplication.Enums.ZinggTypesEnum import ZinggTypesEnum
from src.frontend.Handler.IHandler import IHandler
from src.frontend.DatasetDisplayer.DatasetDisplayerComponent import DatasetDisplayerComponent

from src.frontend.enums.DialogEnum import DialogEnum
from src.frontend.enums.VarEnum import VarEnum

class InitPage:
    def __init__(self, canvas, handler) -> None:
        self.canvas = canvas
        self.handler = handler

    def show(self):        

        with self.canvas.container(): 
            st.title("Deduplication")
            DatasetDisplayerComponent().show(st.session_state[VarEnum.sb_LOADED_DATAFRAME.value])
            
            # Select if you want to use Zingg or Dedupe
            # st.subheader("Select an algorithm to use for deduplication")
            # st.session_state['selected_deduplication_method'] = st.selectbox('Methode:', ["Dedupe", "Zingg"], index=1)
            st.session_state['selected_deduplication_method'] = "Zingg"

            st.subheader("Select which columns to use in the deduplication-proces")

            if st.session_state['selected_deduplication_method'] == "Dedupe":
                selected_col, selected_type = self._show_format_for_dedupe()

            if st.session_state['selected_deduplication_method'] == "Zingg":
                selected_col, selected_type = self._show_format_for_zingg()

            
            # FOR DEBUG ON RESTOS.CSV PRE-DEFINED FIELDS:
            if st.session_state['dedupe_type_dict'] == {}:
                st.session_state['dedupe_type_dict'] = {k: "String" if st.session_state['selected_deduplication_method'] == "Dedupe" else "FUZZY" for k in st.session_state[VarEnum.sb_LOADED_DATAFRAME.value].columns}


            col_1, col_3,_ = st.columns([1,2,8])
            with col_1:
                add_btn = st.button("Change type")
                if add_btn:
                    st.session_state["dedupe_type_dict"][selected_col] = selected_type
                    
            # with col_2:
            #     remove_btn = st.button("Verwijder")
            #     if remove_btn:
            #         if selected_col in st.session_state["dedupe_type_dict"]:
            #             del st.session_state["dedupe_type_dict"][selected_col]
            
            with col_3:
                if len(st.session_state['dedupe_type_dict'].values()) > 0:
                    start_training_btn = st.button("Start training")
                    if start_training_btn:
                        if st.session_state['selected_deduplication_method'] == "Dedupe":
                            self.handler.create_deduper_object(st.session_state["dedupe_type_dict"], st.session_state[VarEnum.sb_LOADED_DATAFRAME.value].to_json())
                            st.session_state[VarEnum.gb_CURRENT_STATE.value] = "LabelRecords_get_record_pair" 
                            st.experimental_rerun()    
                        
                        if st.session_state['selected_deduplication_method'] == "Zingg":
                            self.handler.prepare_zingg(st.session_state["dedupe_type_dict"], st.session_state[VarEnum.sb_LOADED_DATAFRAME.value].to_json())
                            st.session_state[VarEnum.gb_CURRENT_STATE.value] = "LabelRecords_get_all_unmarked_pairs" 
                            st.experimental_rerun()

            st.markdown("**Selected:**")
            if st.session_state['dedupe_type_dict'] == {}:
                st.write("You haven't chosen any columns yet")
            else:
                st.write(st.session_state["dedupe_type_dict"])

    def _show_format_for_dedupe(self):
        colA, colB, colC = st.columns([3,3,8])
        with colA:
            selected_col = st.selectbox('Column:', st.session_state[VarEnum.sb_LOADED_DATAFRAME.value].columns)

        with colB:
            selected_type = st.selectbox('Type:', DeDupeTypesEnum._member_names_)

        with colC:
            if selected_type:
                st.write("")
                st.write("")
                st.write(eval(f"DeDupeTypesEnum.{selected_type}"))
        return selected_col, selected_type
    
    def _show_format_for_zingg(self):
        colA, colB, colC = st.columns([3,3,8])
        with colA:
            selected_col = st.selectbox('Column:', st.session_state[VarEnum.sb_LOADED_DATAFRAME.value].columns)

        with colB:
            selected_type = st.selectbox('Type:', ZinggTypesEnum._member_names_)

        with colC:
            if selected_type:
                st.write("")
                st.write("")
                st.write(eval(f"ZinggTypesEnum.{selected_type}"))

        return selected_col, selected_type