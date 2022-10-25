import pandas as pd
import streamlit as st
import json
# KEEP NESTED LAYOUT!
import streamlit_nested_layout
from src.frontend.Handler.LocalHandler import LocalHandler
from src.frontend.Handler.RemoteHandler import RemoteHandler
from src.frontend.Router import Router
from src.frontend.StateManager import StateManager


def main():

    # Pagina Stijl:
    st.set_page_config(page_title="De-duplicatie prototype", layout = "wide") 
    with open("src/frontend/Resources/css/style.css") as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)
    

    # StateManagement init
    StateManager.initStateManagement()

    if st.session_state["currentState"] != None:
        st.sidebar.button("Ga terug naar vorige fase", on_click=StateManager.go_back_to_previous_in_flow, args=(st.session_state["currentState"],))

    # Sidebar vullen met functionaliteit-mogelijkheden
    functionality_selectbox = st.sidebar.selectbox(
        "Functionaliteit:",
        ("Data Profiling","Data Cleaning", "De-duplicatie", "Rule-learning")
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

        # DEBUG
        # st.sidebar.write(st.session_state)

        # Check of het een nieuwe file is op basis van file naam:
        if st.session_state["dataframe_name"] != uploaded_file.name:
            st.session_state["currentState"] = None
            df = pd.read_csv(uploaded_file, delimiter=',')
            st.session_state["dataframe"] = df
            st.session_state["dataframe_name"] = uploaded_file.name

        button_container =  st.sidebar.expander("Voorgaande Resultaten op deze dataset", expanded=False)
        for e in json.loads(handler.get_saved_results(st.session_state["dataframe"].to_json())):
            splitted = e.split("\\")[1]
            if splitted.split("_")[0] == st.session_state["current_functionality"]:
                button_container.button("⏪ "+ splitted, on_click=StateManager.restore_state, kwargs={"handler" : handler, "file_path": e})


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
        # if functionality_selectbox == "De-duplicatie":
        #     router.routeDeduplication()
        if functionality_selectbox == "Rule-learning":
            router.route_rule_learning()

if __name__ == "__main__":
    main()





        
    


