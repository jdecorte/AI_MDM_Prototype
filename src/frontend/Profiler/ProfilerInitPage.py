import streamlit as st
from streamlit_pandas_profiling import st_profile_report
from dataprep.eda import create_report
from src.frontend.Handler.IHandler import IHandler
from ydata_profiling import ProfileReport


class ProfilerInitPage:
    def __init__(self, canvas, handler: IHandler) -> None:
        self.canvas = canvas
        self.handler = handler

    def show_pandas_profiling(self):
        st.header('Data Profiling Report is succesvol gegenereerd hieronder')
        pr = ProfileReport(st.session_state["dataframe"])
        st_profile_report(pr)

    def show_dataprep_profiling(self):
        st.header('Data Profiling Report is succesvol gegenereerd in een nieuw tabblad')
        create_report(st.session_state["dataframe"]).show_browser()
