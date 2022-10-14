import pandas as pd
import streamlit as st
# KEEP NESTED LAYOUT!
import streamlit_nested_layout
from src.frontend.Handler.LocalHandler import LocalHandler
from src.frontend.Handler.RemoteHandler import RemoteHandler
from src.frontend.Router import Router


def initStateManagement():
    if 'profile_report' not in st.session_state:
        st.session_state['profile_report'] = None
        
    if 'currentState' not in st.session_state:
        st.session_state['currentState'] = None

    if 'currentRegel_LL' not in st.session_state:
        st.session_state['currentRegel_LL'] = None

    if 'currentRegel_RL' not in st.session_state:
        st.session_state['currentRegel_RL'] = None

    if 'ruleEdit' not in st.session_state:
        st.session_state["ruleEdit"] = {}

    if "ListActiveMergeDuplicates" not in  st.session_state:
        st.session_state["ListActiveMergeDuplicates"] = {}

    if "ListEditDuplicates" not in  st.session_state:
        st.session_state["ListEditDuplicates"] = {}

    if "AdviseerOpslaan" not in st.session_state:
        st.session_state["AdviseerOpslaan"] = False

    # if "EDITINIT" not in  st.session_state:
    #     st.session_state["EDITINIT"] = False

    if "dataframe" not in st.session_state:
        # Clearen van caches
        st.experimental_singleton.clear()
        st.session_state["dataframe"] = None

    if "dataframe_name" not in st.session_state:
        st.session_state["dataframe_name"] = None


def main():

    # Pagina Stijl:
    st.set_page_config(page_title="De-duplicatie prototype", layout = "wide") 
    with open("src/frontend/Resources/css/style.css") as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

    # StateManagement init
    initStateManagement()

    # Sidebar vullen met functionaliteit-mogelijkheden
    functionality_selectbox = st.sidebar.selectbox(
        "Functionaliteit:",
        ("Data Profiling","Data Cleaning", "De-duplicatie", "Rule learning")
    )

    # Sidebar vullen met file-upload knop
    st.sidebar.markdown(f"<h3>Remote handling van een dataset</h3>", unsafe_allow_html=True)
    uploaded_file = st.sidebar.file_uploader("Kies een .csv bestand", key="inputOneDataSet")

    # Sidebar vullen met Remote of local functionaliteit
    type_handler_input = st.sidebar.radio(
    "Type Handler:",
    ('Remote', 'Local'), horizontal=True )
    # handler = LocalHandler()

    if type_handler_input == 'Remote':
        remote_url = st.sidebar.text_input('Remote Location', '127.0.0.1')
        remote_port = st.sidebar.text_input('Port', '5000')       
        handler = RemoteHandler(f"http://{remote_url}:{remote_port}")
    else:
        handler = LocalHandler()
    

    if uploaded_file:

        # Check of het een nieuwe file is op basis van file naam:
        if st.session_state["dataframe_name"] != uploaded_file.name:
            df = pd.read_csv(uploaded_file, delimiter=',')
            st.session_state["dataframe"] = df
            st.session_state["dataframe_name"] = uploaded_file.name

        # Aanmaken van Router object:
        router = Router(handler=handler)

        if functionality_selectbox == "Data Profiling":
            router.routeDataProfiling()
        if functionality_selectbox == "Data Cleaning":
            router.routeDataCleaning()
        if functionality_selectbox == "De-duplicatie":
            router.routeDeduplication()
        if functionality_selectbox == "Rule learning":
            router.route_rule_learning()

if __name__ == "__main__":
    main()





        
    


