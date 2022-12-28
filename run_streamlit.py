import pandas as pd
import streamlit as st
import json
import os
import uuid
import hashlib
# KEEP NESTED LAYOUT!
import streamlit_nested_layout
from src.frontend.Handler.LocalHandler import LocalHandler
from src.frontend.Handler.RemoteHandler import RemoteHandler
from src.frontend.Router import Router
from src.frontend.StateManager import StateManager
from streamlit.components.v1 import html
from streamlit_javascript import st_javascript


def _get_from_local_storage(k):
    v = st_javascript(
        f"JSON.parse(localStorage.getItem('{k}'));"
    )
    return v

def main():

    # Pagina Stijl:
    st.set_page_config(page_title="De-duplicatie prototype", layout = "wide") 
    with open("src/frontend/Resources/css/style.css") as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

    # StateManagement init
    StateManager.initStateManagement()

    # Cookie Management
    if st.session_state["dataframe"] is not None:
        my_js = """
                if(localStorage.getItem('session_flask') == null){
                    localStorage.setItem('session_flask', JSON.stringify(crypto.randomUUID()))
                };
                """   
        html(f'<script>{my_js}</script>')
        st.session_state["session_flask"] = f"{_get_from_local_storage('session_flask')}-{hashlib.md5(st.session_state['dataframe'].to_json().encode('utf-8')).hexdigest()}"


    if st.session_state["currentState"] != None:
        st.sidebar.button("Ga terug naar vorige fase", on_click=StateManager.go_back_to_previous_in_flow, args=(st.session_state["currentState"],))

    # Sidebar vullen met functionaliteit-mogelijkheden
    functionality_selectbox = st.sidebar.selectbox(
        "Functionaliteit:",
        ("Data Profiling","Data Cleaning", "De-duplicatie", "Rule-learning"), index=3
    )
    st.session_state["current_functionality"] = functionality_selectbox

    # Sidebar vullen met file-upload knop
    st.sidebar.markdown(f"<h3>Remote handling van een dataset</h3>", unsafe_allow_html=True)
    uploaded_file = st.sidebar.file_uploader("Kies een .csv bestand", key="inputOneDataSet")

    # Sidebar vullen met Remote of local functionaliteit
    type_handler_input = st.sidebar.radio(
    "Type Handler:",
    ('Remote', 'Local'), horizontal=True )

    if type_handler_input == 'Remote':
        remote_url = st.sidebar.text_input('Remote Location', '127.0.0.1')
        remote_port = st.sidebar.text_input('Port', '5000')       
        handler = RemoteHandler(f"http://{remote_url}:{remote_port}")
    else:
        handler = LocalHandler()

    if uploaded_file:

        # Check of het een nieuwe file is op basis van file naam:
        if st.session_state["dataframe_name"] != uploaded_file.name:
            # StateManager.clear_session_state()
            st.session_state["currentState"] = None
            df = pd.read_csv(uploaded_file, delimiter=',')
            st.session_state["dataframe"] = df
            st.session_state["dataframe_name"] = uploaded_file.name
            print('NEW SESSION')

            # st.session_state["session_flask"] = f"{_get_from_local_storage('session_flask')}-{hashlib.md5(df.to_json().encode('utf-8')).hexdigest()}"

        # LOAD IN SESSION_MAP
        st.session_state['session_map'] = handler.get_session_map(dataframe_in_json=st.session_state["dataframe"].to_json())

        # CALCULATE CURRENT SEQ IF NOT ALREADY PRESENT
        if "current_seq" not in st.session_state:
            st.session_state["current_seq"] = str(max([int(x) for x in st.session_state['session_map'].keys()], default=0)+1)

        # CREATE BUTTONS FROM SESSION_MAP TODO
        button_container =  st.sidebar.expander("Voorgaande Resultaten op deze dataset", expanded=False)

        for seq,method_dict in st.session_state['session_map'].items():
            button_container.write(seq)
            for method, file_name in method_dict.items():
                button_container.write(method)
                button_container.button("⏪ "+seq+ file_name.split("\\")[1], on_click=StateManager.restore_state, kwargs={"handler" : handler, "file_path": file_name, "chosen_seq": seq})
        
        # Toevoegen van download knop:
        # st.sidebar.button('Download huidige dataset')
        st.sidebar.download_button(
                label="Download huidige dataset",
                data=st.session_state["dataframe"].to_csv().encode('utf-8'),
                file_name= f'new_{st.session_state["dataframe_name"]}',
                mime='text/csv',
            )

        # Aanmaken van Router object:
        router = Router(handler=handler)

        # if functionality_selectbox == "Data Profiling":
        #     router.routeDataProfiling()
        # if functionality_selectbox == "Data Cleaning":
        #     router.routeDataCleaning()
        if functionality_selectbox == "De-duplicatie":
            router.route_dedupe()
        if functionality_selectbox == "Rule-learning":
            router.route_rule_learning()

if __name__ == "__main__":
    main()