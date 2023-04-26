import pandas as pd
import streamlit as st
import uuid
import hashlib
import uuid
# KEEP NESTED LAYOUT!
import streamlit_nested_layout
from src.frontend.Handler.LocalHandler import LocalHandler
from src.frontend.Handler.RemoteHandler import RemoteHandler
from src.frontend.Router import Router
from src.frontend.StateManager import StateManager
from streamlit.components.v1 import html
from streamlit_javascript import st_javascript
from streamlit_ws_localstorage import injectWebsocketCode, getOrCreateUID
import json
import config as cfg



def _reload_dataframe(uploaded_file):
    t2 = st.session_state["dataframe"]
    t3 = st.session_state["dataframe_name"]
    t4 = st.session_state["session_flask"]
    t5 = st.session_state["session_flask_local_id"]
    seperator_input = st.session_state["seperator_input"]
    t8 = st.session_state["session_map"]
    t9 = st.session_state["type_handler_input"]
    t10 = st.session_state["current_functionality"]
    t11 = st.session_state["current_profiling"]

    st.session_state = {}

    st.session_state["currentState"] = None
    st.session_state["dataframe"] = pd.read_csv(uploaded_file, delimiter= seperator_input if seperator_input else ',')
    st.session_state["dataframe_name"] = uploaded_file.name
    st.session_state["session_flask_local_id"] = t5
    st.session_state["session_flask"] = f"{st.session_state['session_flask_local_id']}-{hashlib.md5(st.session_state['dataframe'].to_json().encode('utf-8')).hexdigest()}"
    st.session_state["seperator_input"] = seperator_input

    st.session_state["session_map"] = t8
    st.session_state["type_handler_input"] = t9
    st.session_state["current_functionality"] = t10
    st.session_state["current_profiling"] = t11

    st.experimental_rerun()

def get_from_local_storage(k):
    v = st_javascript(
        f"JSON.parse(localStorage.getItem('{k}'));"
    )
    return v or {}

def set_to_local_storage(k, v):
    jdata = json.dumps(v)
    st_javascript(
        f"localStorage.setItem('{k}', JSON.stringify({jdata}));"
    )

def main():

    # Pagina Stijl:
    st.set_page_config(page_title="AI MDM Tool", layout = "wide") 
    with open("src/frontend/Resources/css/style.css") as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

    # StateManagement init
    StateManager.initStateManagement()
    # Cookie Management
    if st.session_state["dataframe"] is None and (st.session_state["session_flask"] is None) and(st.session_state["session_flask_local_id"] is None):
        ret=get_from_local_storage('session_flask')
        if ret == {}:
            temp_id = uuid.uuid4()
            _ = set_to_local_storage('session_flask', str(temp_id))
            st.session_state["session_flask_local_id"] = temp_id
        else:
            st.session_state["session_flask_local_id"] = ret
    if st.session_state["dataframe"] is not None:
        st.session_state["session_flask"] = f"{st.session_state['session_flask_local_id']}-{hashlib.md5(st.session_state['dataframe'].to_json().encode('utf-8')).hexdigest()}"

    if st.session_state["currentState"] != None:
        st.sidebar.button("Go back to previous phase", on_click=StateManager.go_back_to_previous_in_flow, args=(st.session_state["currentState"],))

    # Sidebar vullen met functionaliteit-mogelijkheden
    st.session_state["current_functionality"] = st.sidebar.selectbox(
        "Functionality:",
        ("Data Profiling","Data Extraction","Data Cleaning", "Deduplication", "Rule-learning"), index=3
    )

    # Extra opties voor data profiling
    if st.session_state["current_functionality"] == "Data Profiling":
        profiling_radio = st.sidebar.radio(
            "Data Profiling:",
            ("Pandas Profiling", "Dataprep Profiling"), index=0, horizontal=True
        )
        st.session_state["current_profiling"] = profiling_radio

    # Sidebar vullen met file-upload knop
    # st.sidebar.markdown(f"<h3>Remote handling van een dataset</h3>", unsafe_allow_html=True)
    uploaded_file = st.sidebar.file_uploader("Choose a .csv file", key="inputOneDataSet")

    # Sidebar vullen met optionele seperator
    if uploaded_file:
        with st.sidebar.expander("Optional seperator", expanded=False):
            st.write("Aan te passen wanneer de seperator niet een ',' is.")
            col_sep_left, col_sep_right = st.columns([1,1])
            with col_sep_left:
                st.session_state["seperator_input"] = st.text_input("Seperator", value=',')
            with col_sep_right:
                st.write("")
                st.write("")
                flag_reload = st.button("Reload", key="reload_button")
                if flag_reload:
                    _reload_dataframe(uploaded_file)

    # Sidebar vullen met Remote of local functionaliteit
    # type_handler_input = st.sidebar.radio(
    # "Type Handler:",
    # ('Remote', 'Local'), horizontal=True, key="type_handler_input" )

    if st.session_state['type_handler_input'] == 'Remote':
        pass
        # remote_url = st.sidebar.text_input('Remote Location', '127.0.0.1')
        # remote_port = st.sidebar.text_input('Port', '5000')       
        # handler = RemoteHandler(f"http://{remote_url}:{remote_port}")
        handler = RemoteHandler(f"http://{cfg.configuration['remote_url']}:{cfg.configuration['remote_port']}")
    else:
        handler = LocalHandler()
    # handler = RemoteHandler(f"http://127.0.0.1:5000")

    if uploaded_file:
        if st.session_state["dataframe_name"] != uploaded_file.name:
            _reload_dataframe(uploaded_file)

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
                button_container.button("⏪ " + seq + file_name.split("/")[-1],  # file_name.split("\\")[1], 
                                        on_click=StateManager.restore_state,
                                        kwargs={"handler": handler,
                                                "file_path": file_name,
                                                "chosen_seq": seq})
        
        # Toevoegen van download knop:
        # st.sidebar.button('Download huidige dataset')
        st.sidebar.download_button(
                label="Download currently loaded dataset",
                data=st.session_state["dataframe"].to_csv(index=False).encode('utf-8'),
                file_name= f'new_{st.session_state["dataframe_name"]}',
                mime='text/csv',
            )
        
        st.sidebar.button('Panic Button', on_click=_reload_dataframe, kwargs=({"uploaded_file": uploaded_file}))

        # Aanmaken van Router object:
        router = Router(handler=handler)
        if st.session_state["current_functionality"] == "Data Profiling":
            if profiling_radio == "Pandas Profiling":
                router.route_pandas_data_profiling()
            if profiling_radio == "Dataprep Profiling":
                router.route_dataprep_data_profiling()
        if st.session_state["current_functionality"] == "Data Cleaning":
            router.route_data_cleaning()
        if st.session_state["current_functionality"] == "Deduplication":
            router.route_dedupe()
        if st.session_state["current_functionality"] == "Rule-learning":
            router.route_rule_learning()
        if st.session_state["current_functionality"] == "Data Extraction":
            router.route_data_extraction()

if __name__ == "__main__":
        print("Starting Streamlit")
        main()