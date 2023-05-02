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
from src.frontend.Deduplication.InitPage import InitPage
from src.frontend.Deduplication.LabelPage import DeDupeLabelPage, DeDupeRedirectLabelPage
from src.frontend.Deduplication.ClusterPage import ClusterPage, DeDupeClusterRedirectPage, ZinggClusterRedirectPage, ZinggClusterPage
from src.frontend.Profiler.ProfilerInitPage import ProfilerInitPage
from src.frontend.Extractor.DataExtractorInitPage import DataExtractorInitPage
from src.frontend.Deduplication.LabelPage import ZinggLabelPage

from src.frontend.enums.DialogEnum import DialogEnum
from src.frontend.enums.VarEnum import VarEnum

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
                
        if st.session_state[VarEnum.gb_CURRENT_STATE.value] == None:
            DataExtractorInitPage(canvas=canvas, handler=self.handler).show()

    def route_dataprep_data_profiling(self):
        canvas = st.empty()
        
        if st.session_state[VarEnum.gb_CURRENT_STATE.value] == None:
            ProfilerInitPage(canvas=canvas, handler=self.handler).show_dataprep_profiling()

    def route_pandas_data_profiling(self):
        canvas = st.empty()

        if st.session_state[VarEnum.gb_CURRENT_STATE.value] == None:
            ProfilerInitPage(canvas=canvas, handler=self.handler).show_pandas_profiling()

    def route_data_cleaning(self):
        canvas = st.empty()

        if st.session_state[VarEnum.gb_CURRENT_STATE.value] == None:
            CleanerInitPage(canvas=canvas, handler=self.handler).show()

    def route_rule_learning(self):
        canvas = st.empty()
                
        if st.session_state[VarEnum.gb_CURRENT_STATE.value] == None:
            RuleLearnerInitPage(canvas=canvas, handler=self.handler).show()

        if st.session_state[VarEnum.gb_CURRENT_STATE.value] == "BekijkRules":
            RuleLearnerSummaryRulesPage(canvas=canvas, handler=self.handler).show()

        if st.session_state[VarEnum.gb_CURRENT_STATE.value] == "BekijkSuggesties":
            RuleLearnerSuggestionsPage(canvas=canvas, handler=self.handler).show()

    def route_dedupe(self):
        canvas = st.empty()
                
        if st.session_state[VarEnum.gb_CURRENT_STATE.value] == None:
            InitPage(canvas=canvas, handler=self.handler).show()
        
        if st.session_state[VarEnum.gb_CURRENT_STATE.value] == "LabelRecords":
            DeDupeLabelPage(canvas=canvas, handler=self.handler).show()

        if st.session_state[VarEnum.gb_CURRENT_STATE.value] == "LabelRecords_get_record_pair":
            DeDupeRedirectLabelPage(canvas=canvas, handler=self.handler).redirect_get_record_pair()

        if st.session_state[VarEnum.gb_CURRENT_STATE.value] == "LabelRecords_get_all_unmarked_pairs":
            ZinggLabelPage(canvas=canvas, handler=self.handler).show()

        if st.session_state[VarEnum.gb_CURRENT_STATE.value] == "LabelRecords_mark_record_pair":
            DeDupeRedirectLabelPage(canvas=canvas, handler=self.handler).redirect_mark_record_pair()

        if st.session_state[VarEnum.gb_CURRENT_STATE.value] == "ViewClusters_get_clusters":
            DeDupeClusterRedirectPage(canvas=canvas, handler=self.handler).redirect_get_clusters()

        if st.session_state[VarEnum.gb_CURRENT_STATE.value] == "Zingg_ViewClusters_get_clusters":
            ZinggClusterRedirectPage(canvas=canvas, handler=self.handler).redirect_get_clusters()

        if st.session_state[VarEnum.gb_CURRENT_STATE.value] == "ViewClusters":
            ClusterPage(canvas=canvas, handler=self.handler).show()

        if st.session_state[VarEnum.gb_CURRENT_STATE.value] == "Zingg_ViewClusters":
            ZinggClusterPage(canvas=canvas, handler=self.handler).show()
