import streamlit as st
import pandas as pd

from st_aggrid import GridOptionsBuilder, AgGrid, GridUpdateMode, DataReturnMode, JsCode
from src.frontend.DeDuper.DeDupeTypesEnum import DeDupeTypesEnum
from src.frontend.DeDuper.ZinggTypesEnum import ZinggTypesEnum
from src.frontend.Handler.IHandler import IHandler
from src.frontend.DatasetDisplayer.DatasetDisplayerComponent import DatasetDisplayerComponent


class DeDupeInitPage:
    def __init__(self, canvas, handler) -> None:
        self.canvas = canvas
        self.handler = handler

    def show(self):        

        with self.canvas.container(): 
            st.title("De-duplicatie")
            DatasetDisplayerComponent().show(st.session_state["dataframe"])
            
            # Select if you want to use Zingg or Dedupe
            st.subheader("Selecteer de methode die je wilt gebruiken")
            st.session_state['selected_deduplication_method'] = st.selectbox('Methode:', ["Dedupe", "Zingg"])

            st.subheader("Selecteer kolommen om te gebruiken in deduplicatie-proces")

            if st.session_state['selected_deduplication_method'] == "Dedupe":
                selected_col, selected_type = self._show_format_for_dedupe()

            if st.session_state['selected_deduplication_method'] == "Zingg":
                selected_col, selected_type = self._show_format_for_zingg()

            
            # FOR DEBUG ON RESTOS.CSV PRE-DEFINED FIELDS:
            # if st.session_state['dedupe_type_dict'] == {}:
            st.session_state['dedupe_type_dict'] = {k: "String" if st.session_state['selected_deduplication_method'] == "Dedupe" else "FUZZY" for k in st.session_state["dataframe"].columns}


            col_1, col_2, col_3,_ = st.columns([1,1,1,6])
            with col_1:
                add_btn = st.button("Voeg toe")
                if add_btn:
                    st.session_state["dedupe_type_dict"][selected_col] = selected_type
                    
            with col_2:
                remove_btn = st.button("Verwijder")
                if remove_btn:
                    if selected_col in st.session_state["dedupe_type_dict"]:
                        del st.session_state["dedupe_type_dict"][selected_col]
            
            with col_3:
                if len(st.session_state['dedupe_type_dict'].values()) > 0:
                    start_training_btn = st.button("Start training")
                    if start_training_btn:
                        if st.session_state['selected_deduplication_method'] == "Dedupe":
                            self.handler.create_deduper_object(st.session_state["dedupe_type_dict"], st.session_state["dataframe"].to_json())
                            st.session_state["currentState"] = "LabelRecords_get_record_pair" 
                            st.experimental_rerun()    
                        
                        if st.session_state['selected_deduplication_method'] == "Zingg":
                            self.handler.prepare_zingg(st.session_state["dedupe_type_dict"], st.session_state["dataframe"].to_json())
                            # st.session_state["currentState"] = "LabelRecords_get_all_unmarked_pairs" 
                            # st.experimental_rerun()

            st.markdown("**Geselecteerd:**")
            if st.session_state['dedupe_type_dict'] == {}:
                st.write("U heeft nog geen kolommen gekozen")
            else:
                st.write(st.session_state["dedupe_type_dict"])

    def _show_format_for_dedupe(self):
        colA, colB, colC = st.columns([3,3,8])
        with colA:
            selected_col = st.selectbox('Kolom:', st.session_state["dataframe"].columns)

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
            selected_col = st.selectbox('Kolom:', st.session_state["dataframe"].columns)

        with colB:
            selected_type = st.selectbox('Type:', ZinggTypesEnum._member_names_)

        with colC:
            if selected_type:
                st.write("")
                st.write("")
                st.write(eval(f"ZinggTypesEnum.{selected_type}"))

        return selected_col, selected_type