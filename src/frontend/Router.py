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
from streamlit_pandas_profiling import st_profile_report
from src.frontend.DeDuper.DeDupeInitPage import DeDupeInitPage


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

    # def routeDataCleaning():
    #     st.sidebar.markdown(f"<h3>Data Profiling op één dataset</h3>", unsafe_allow_html=True)
    #     key = "inputOneDataSet"
    #     uploaded_file2 = st.sidebar.file_uploader("Kies een .csv bestand", key=key)
    #     # minimal = st.sidebar.checkbox('Minimal report', value=True)
    #     if uploaded_file2 is not None:
    #         canvas = st.empty()
            
    #         dataframe = Helper.createDataFrameFromDataset(uploaded_file2)
    #         Cleaner.initCleaner(dataframe)


    # def routeDeduplication():
    #     st.sidebar.markdown(f"<h3>De-duplicatie van één dataset</h3>", unsafe_allow_html=True)
        
    #     uploaded_file2 = st.sidebar.file_uploader("Kies een .csv bestand", key="inputOneDataSet")
    #     if uploaded_file2 is not None:
    #         canvas = st.empty()
    #         dataframe = Helper.createDataFrameFromDataset(uploaded_file2)

            

    #         # Afhankelijk van de state, worden we naar een andere pagina geleid
    #         if st.session_state["currentState"] == None:
    #             Deduper.initOneDedup(canvas, dataframe)

            
            
    #         if st.session_state["currentState"] == "iterateDubbels":
    #             # Deduper.iterateDubbels(dataframe, st.session_state["dubbelsDF"],st.session_state["dubbelsCertainty"] ,canvas)
    #             Deduper.iterateDubbels(dataframe, st.session_state["dubbelsDF"],0.9 ,canvas)
            

    #     st.sidebar.markdown(f"<h3>Vergelijking, de-duplicatie & samenvoeging van twee datasets</h3>", unsafe_allow_html=True)
    #     uploaded_file3 = st.sidebar.file_uploader("Kies een eerste .csv bestand", key="inputTwoDataSets1")
    #     if uploaded_file3 is not None:
    #         st.write("Beep")

    #     uploaded_file3 = st.sidebar.file_uploader("Kies een tweede .csv bestand", key="inputTwoDataSets2")
    #     if uploaded_file3 is not None:
    #         st.write("Beep")


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
