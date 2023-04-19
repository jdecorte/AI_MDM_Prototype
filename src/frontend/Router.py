import streamlit as st
import pandas as pd
from src.frontend.RuleLearner.RuleLearnerSuggestionsPage import RuleLearnerSuggestionsPage

from src.frontend.RuleLearner.RuleLearnerInitPage import RuleLearnerInitPage
from src.frontend.RuleLearner.RuleLearnerSummaryRulesPage import RuleLearnerSummaryRulesPage

# from src.frontend import Profiler
# from src.frontend import Deduper
# from src.frontend import Helper
# from src.frontend import Cleaner
from src.frontend.Handler.IHandler import IHandler
from src.frontend.Cleaner.CleanerInitPage import CleanerInitPage
from streamlit_pandas_profiling import st_profile_report
from src.frontend.DeDuper.DeDupeInitPage import DeDupeInitPage
from src.frontend.DeDuper.DeDupeLabelPage import DeDupeLabelPage, DeDupeRedirectLabelPage
from src.frontend.DeDuper.DeDupeClusterPage import DeDupeClusterPage, DeDupeClusterRedirectPage, ZinggClusterPage
from src.frontend.Profiler.ProfilerInitPage import ProfilerInitPage
from src.frontend.Extractor.DataExtractorInitPage import DataExtractorInitPage
from src.frontend.DeDuper.DeDupeLabelPage import ZinggLabelPage

class Router:
    def __init__(self, handler:IHandler) -> None:
        self.handler = handler

    # def routeDataProfiling():
    #     st.sidebar.markdown(f"<h3>Data Profiling op één dataset</h3>", unsafe_allow_html=True)
    #     key = "inputOneDataSet"
    #     uploaded_file2 = st.sidebar.file_uploader("Kies een .csv bestand", key=key)
        
    #     # Rule Learner\Rule-Learner\data

    #     # minimal = st.sidebar.checkbox('Minimal report', value=True)
    #     minimal = True
    #     if uploaded_file2 is not None:
    #         canvas = st.empty()
            
    #         dataframe = Helper.createDataFrameFromDataset(uploaded_file2)
    #         Profiler.generate_profile_report(dataframe, minimal)
    #         if (uploaded_file2 and st.session_state.profile_report):
    #             pr = st.session_state.profile_report['pr']
    #             st_profile_report(pr)

    def route_data_extraction(self):
        canvas = st.empty()
                
        if st.session_state["currentState"] == None:
            DataExtractorInitPage(canvas=canvas, handler=self.handler).show()

    def route_dataprep_data_profiling(self):
        canvas = st.empty()
        
        if st.session_state["currentState"] == None:
            ProfilerInitPage(canvas=canvas, handler=self.handler).show_dataprep_profiling()

    def route_pandas_data_profiling(self):
        canvas = st.empty()

        if st.session_state["currentState"] == None:
            ProfilerInitPage(canvas=canvas, handler=self.handler).show_pandas_profiling()

    def route_data_cleaning(self):
        canvas = st.empty()

        if st.session_state["currentState"] == None:
            CleanerInitPage(canvas=canvas, handler=self.handler).show()

    def route_rule_learning(self):
        canvas = st.empty()
                
        if st.session_state["currentState"] == None:
            RuleLearnerInitPage(canvas=canvas, handler=self.handler).show()

        if st.session_state["currentState"] == "BekijkRules":
            RuleLearnerSummaryRulesPage(canvas=canvas, handler=self.handler).show()

        if st.session_state["currentState"] == "BekijkSuggesties":
            RuleLearnerSuggestionsPage(canvas=canvas, handler=self.handler).show()

    def route_dedupe(self):
        canvas = st.empty()
                
        if st.session_state["currentState"] == None:
            DeDupeInitPage(canvas=canvas, handler=self.handler).show()
        
        if st.session_state["currentState"] == "LabelRecords":
            DeDupeLabelPage(canvas=canvas, handler=self.handler).show()

        if st.session_state["currentState"] == "LabelRecords_get_record_pair":
            DeDupeRedirectLabelPage(canvas=canvas, handler=self.handler).redirect_get_record_pair()

        if st.session_state["currentState"] == "LabelRecords_get_all_unmarked_pairs":
            ZinggLabelPage(canvas=canvas, handler=self.handler).show()

        if st.session_state["currentState"] == "LabelRecords_mark_record_pair":
            DeDupeRedirectLabelPage(canvas=canvas, handler=self.handler).redirect_mark_record_pair()

        if st.session_state["currentState"] == "ViewClusters_get_clusters":
            DeDupeClusterRedirectPage(canvas=canvas, handler=self.handler).redirect_get_clusters()

        if st.session_state["currentState"] == "Zingg_ViewClusters_get_clusters":
            # Moet een redirect worden
            ZinggClusterPage(canvas=canvas, handler=self.handler).show()

        if st.session_state["currentState"] == "ViewClusters":
            DeDupeClusterPage(canvas=canvas, handler=self.handler).show()
