import mitosheet
import streamlit as st
import pandas as pd
from streamlit.components.v1 import html
from streamlit.components.v1 import iframe
mitosheet.sheet()


def initCleaner(dataframe):
    st.write("Beep")
    iframe(mitosheet.sheet(analysis_to_replay="id-nfodcrmqft"))