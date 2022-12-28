import streamlit as st
import pandas as pd
import os
import csv
import re
import logging
import optparse
import io
import json
import pickle
import traceback

import dedupe
import dedupe.blocking as blocking
import dedupe.datamodel as datamodel
import dedupe.labeler as labeler
import dedupe.predicates

from st_aggrid import GridOptionsBuilder, AgGrid, GridUpdateMode, DataReturnMode, JsCode
from src.frontend.RuleLearner.RuleLearnerOptionsSubPage import RuleLearnerOptionsSubPage
from src.frontend.Handler.IHandler import IHandler

class DeDupeRedirectLabelPage:
    def __init__(self, canvas, handler) -> None:
        self.canvas = canvas
        self.handler = handler

    def redirect_get_record_pair(self):
        st.session_state['record_pair'] = self.handler.dedupe_next_pair()
        st.session_state['currentState'] = "LabelRecords"
        st.experimental_rerun()

    def redirect_mark_record_pair(self):
        self.handler.dedupe_mark_pair(st.session_state['marked_record_pair'])
        st.session_state['currentState'] = "LabelRecords_get_record_pair"
        st.experimental_rerun()
        

class DeDupeLabelPage:

    def __init__(self, canvas, handler) -> None:
        self.canvas = canvas
        self.handler = handler

    def streamlit_label(self, ) -> None:  # pragma: no cover
        colBB, colCC, colDD, colEE  = st.columns([1,1,1,1])
        with colBB:
            duplicate_btn = st.button('Duplicaat')
            if duplicate_btn:
                st.session_state['marked_record_pair'] = (st.session_state['record_pair'], "match")
                st.session_state["currentState"] = "LabelRecords_mark_record_pair"
                st.experimental_rerun()

        with colCC:
            not_duplicate_btn = st.button('Geen duplicaat')
            if not_duplicate_btn:
                st.session_state['marked_record_pair'] = (st.session_state['record_pair'], "distinct")
                st.session_state["currentState"] = "LabelRecords_mark_record_pair"
                st.experimental_rerun()

        with colDD:
            unsure_duplicate_btn = st.button('Onzeker')
            if unsure_duplicate_btn:
                st.session_state['marked_record_pair'] = (st.session_state['record_pair'], "unsure")
                st.session_state["currentState"] = "LabelRecords_mark_record_pair"
                st.experimental_rerun()

        with colEE:
            finish_label_btn = st.button('Finish')
            if finish_label_btn:
                self.handler.dedupe_train()         
                st.session_state["currentState"] = "ViewClusters_get_clusters" 
                st.experimental_rerun()       

    def show(self): 
        with self.canvas.container(): 
            st.title("DeDupe")
            colA, colB = st.columns([1,5])
            with colA:
                st.write(pd.DataFrame.from_dict(self.handler.dedupe_get_stats(), orient='index'))      
                
            with colB:
                st.write("Below are two records that look similar and might be duplicate records. Label at least 10 records as ‘duplicates’ and 10 records as ‘non-duplicates’")
                # st.write('See a lot of records that don’t match? You may get better results if select different columns or compare existing columns differently:')
                # st.button('Verander fields')

            fields = st.session_state["dedupe_type_dict"].keys()
            st.table(pd.DataFrame().assign(Field= [f for f in st.session_state['record_pair'][0].keys() if f in fields], Record_1 = [v1 for k1,v1 in st.session_state['record_pair'][0].items() if k1 in fields], Record_2 = [v2 for k2,v2 in st.session_state['record_pair'][1].items() if k2 in fields]))
            self.streamlit_label()