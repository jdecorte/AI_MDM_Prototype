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
    def __init__(self, canvas, handler: IHandler) -> None:
        self.canvas = canvas
        self.handler = handler

    def _mark_pair(deduper: dedupe.api.ActiveMatching, labeled_pair) -> None:
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
        LabeledPair = Tuple[RecordDictPair, Literal["match", "distinct", "unsure"]]
        finished = False
        use_previous = False
        fields = unique(var.field for var in deduper.data_model.primary_variables)

        buffer_len = 1  # Max number of previous operations
        unlabeled: list[RecordDictPair] = []
        labeled: list[LabeledPair] = []

        n_match = len(deduper.training_pairs["match"])
        n_distinct = len(deduper.training_pairs["match"])

        while not finished:
            if use_previous:
                record_pair, label = labeled.pop(0)
                if label == "match":
                    n_match -= 1
                elif label == "distinct":
                    n_distinct -= 1
                use_previous = False
            else:
                try:
                    if not unlabeled:
                        unlabeled = deduper.uncertain_pairs()

                    record_pair = unlabeled.pop()
                except IndexError:
                    break

            for record in record_pair:
                for field in fields:
                    line = "%s : %s" % (field, record[field])
                    st.write(line)
                st.write()
            st.write(f"{n_match}/10 positive, {n_distinct}/10 negative")
            st.write("Do these records refer to the same thing?")

            valid_response = False
            user_input = ""
            while not valid_response:
                if labeled:
                    st.write("(y)es / (n)o / (u)nsure / (f)inished / (p)revious")
                    valid_responses = {"y", "n", "u", "f", "p"}
                else:
                    st.write("(y)es / (n)o / (u)nsure / (f)inished")
                    valid_responses = {"y", "n", "u", "f"}
                user_input = input()
                if user_input in valid_responses:
                    valid_response = True

            if user_input == "y":
                labeled.insert(0, (record_pair, "match"))
                n_match += 1
            elif user_input == "n":
                labeled.insert(0, (record_pair, "distinct"))
                n_distinct += 1
            elif user_input == "u":
                labeled.insert(0, (record_pair, "unsure"))
            elif user_input == "f":
                st.write("Finished labeling")
                finished = True
            elif user_input == "p":
                use_previous = True
                unlabeled.append(record_pair)

            while len(labeled) > buffer_len:
                self._mark_pair(deduper, labeled.pop())

        for labeled_pair in labeled:
            self._mark_pair(deduper, labeled_pair)

    def show(self): 
        with self.canvas.container(): 
            st.title("DeDupe")

            fields = [
            {'field': 'name', 'type': 'String'},
            {'field': 'addr', 'type': 'String'},
            {'field': 'city', 'type': 'String'},
            {'field': 'type', 'type': 'String'},
            ]
            st.session_state["deduper"] = dedupe.Dedupe(fields)
            st.session_state["deduper_data"] = st.session_state["dataframe"].to_dict(orient="index")
            st.session_state["deduper"].prepare_training(st.session_state["deduper_data"])

            st.write('starting active labeling...')
            self.streamlit_label(st.session_state["deduper"])