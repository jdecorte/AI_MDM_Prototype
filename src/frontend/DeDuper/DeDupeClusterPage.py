import streamlit as st
import pandas as pd
import os
import csv
import re
import logging
import optparse
import pickle


import dedupe


class DeDupeClusterPage:

    def __init__(self, canvas, handler) -> None:
        self.canvas = canvas
        self.handler = handler


    # MOET AANGEPAST WORDEN
    def show(self): 
            with self.canvas.container(): 
                st.title("DeDupe")
                if os.path.exists(self.pickled_file):
                    print('reading from', self.pickled_file)
                    with open(self.pickled_file, 'rb') as f:
                        deduper = pickle.load(f)
                else:
                    deduper = dedupe.Dedupe(self._transform_type_dict_to_correct_format_for_dedupe(st.session_state['dedupe_type_dict']))
                    deduper.prepare_training(st.session_state["dataframe"].to_dict(orient="index"))
                st.write(deduper.training_pairs)
                self.streamlit_label(deduper)