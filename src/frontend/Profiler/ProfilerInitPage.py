import streamlit as st
from streamlit_pandas_profiling import st_profile_report
from dataprep.eda import create_report
from src.frontend.Handler.IHandler import IHandler
from ydata_profiling import ProfileReport
import hashlib
import os
import config as cfg

from src.frontend.enums.VarEnum import VarEnum


class ProfilerInitPage:

    def __init__(self, canvas, handler: IHandler) -> None:
        self.canvas = canvas
        self.handler = handler

    def show_pandas_profiling(self):
        st.header('The Data Profiling report is getting generated. Please wait...')
        pr = ProfileReport(st.session_state[VarEnum.sb_LOADED_DATAFRAME.value])
        st_profile_report(pr)

    def show_dataprep_profiling(self):

        # Create MD5 of the dataframe to use as a filename
        df = st.session_state[VarEnum.sb_LOADED_DATAFRAME.value]
        md5_hash = hashlib.md5(df.to_string().encode("utf-8")).hexdigest()

        # Make path to directory to store the reports.
        # We assume that this directory already exists.
        directory = os.path.join(cfg.configuration["WWW_ROOT"], "reports")

        # Create and save the report
        path = os.path.join(directory, f"{md5_hash}.html")
        report = create_report(df)
        report.save(path)

        # Show a link to the report
        text = "Link to the report"
        st.header('The Data Profiling report is getting generated. ' +
                  'Click on the link below to view it')
        # The url starts from WWW_ROOT, so we need to go up one level
        # in order to get rid of "aimdmtool" in the url
        url = os.path.join("..", "reports", f"{md5_hash}.html")
        st.markdown(f'<a href="{url}">{text}</a>', unsafe_allow_html=True)
