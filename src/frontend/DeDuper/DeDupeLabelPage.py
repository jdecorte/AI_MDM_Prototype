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
from dedupe.canonical import getCanonicalRep
from dedupe.core import unique
from dedupe._typing import (
    Data,
    Literal,
    RecordDict,
    RecordDictPair,
    RecordID,
    TrainingData,
    Tuple
)


class DeDupeLabelPage:
    def __init__(self, canvas) -> None:
        self.canvas = canvas

    def _mark_pair(self,deduper: dedupe.api.ActiveMatching, labeled_pair) -> None:
        record_pair, label = labeled_pair
        examples: TrainingData = {"distinct": [], "match": []}
        if label == "unsure":
            # See https://github.com/dedupeio/dedupe/issues/984 for reasoning
            examples["match"].append(record_pair)
            examples["distinct"].append(record_pair)
        else:
            # label is either "match" or "distinct"
            examples[label].append(record_pair)
        deduper.mark_pairs(examples)

    def streamlit_label(self, deduper: dedupe.api.ActiveMatching) -> None:  # pragma: no cover
        """
        Train a matcher instance (Dedupe, RecordLink, or Gazetteer) from the command line.
        Example

        .. code:: python

        > deduper = dedupe.Dedupe(variables)
        > deduper.prepare_training(data)
        > dedupe.streamlit_label(deduper)
        """
        fields = unique(var.field for var in deduper.data_model.primary_variables)
        n_match = len(st.session_state["deduper"].training_pairs["match"]) - st.session_state['number_of_unsure']
        n_distinct = len(deduper.training_pairs["distinct"]) - st.session_state['number_of_unsure']
        n_unsure = st.session_state['number_of_unsure']

        record_pair = deduper.uncertain_pairs().pop()           
        colA, colB = st.columns([5,3])
        with colA:
            st.write("Below are two records that look similar and might be duplicate records. Label at least 10 records as ‘duplicates’ and 10 records as ‘non-duplicates’")
            temp_df = pd.DataFrame.from_dict({"Yes":f"{n_match}/10", "No":f"{n_distinct}/10", "Unsure":f"{n_unsure}"}, orient='index')
            st.dataframe(temp_df)
            
        with colB:
            st.write('See a lot of records that don’t match? You may get better results if select different columns or compare existing columns differently')

        st.table(pd.DataFrame().assign(Field= fields, Record_1 = [v1 for k1,v1 in record_pair[0].items() if k1 in fields], Record_2 = [v2 for k2,v2 in record_pair[1].items() if k2 in fields]))

        colBB, colCC, colDD, colEE  = st.columns([1,1,1,1])
        with colBB:
            duplicate_btn = st.button('Duplicaat')
            if duplicate_btn:
                self._mark_pair(deduper, (record_pair, "match"))

        with colCC:
            not_duplicate_btn = st.button('Geen duplicaat')
            if not_duplicate_btn:
                self._mark_pair(deduper, (record_pair, "distinct"))

        with colDD:
            unsure_duplicate_btn = st.button('Onzeker')
            if unsure_duplicate_btn:
                self._mark_pair(deduper, (record_pair, "unsure"))
                st.session_state['number_of_unsure'] = st.session_state['number_of_unsure'] + 1

        with colEE:
            finish_label_btn = st.button('Finish')
            if finish_label_btn:
                pass
        

    def show(self): 
        with self.canvas.container(): 
            st.title("DeDupe")
            self.streamlit_label(st.session_state["deduper"])
