from ast import arg
from cgitb import handler
import numpy as np
import pandas as pd
import streamlit as st
from st_aggrid import GridOptionsBuilder, AgGrid, GridUpdateMode, DataReturnMode, JsCode
from streamlit.components.v1 import html
from src.frontend.StateManager import StateManager
from src.frontend.Handler.IHandler import IHandler
import json
import math

class RuleLearnerSummaryRulesPage:
    def __init__(self, canvas, handler: IHandler) -> None:
        self.canvas = canvas
        self.handler = handler

    def _calculate_entropy(self,row, df, len_vm):
        querystring_list = []
        pre = row[:-1]
        post = row[-1:]
        for k,v in pre.items():
            querystring_list.append(f"`{k}` == {v}")
        querystring = " and ".join(querystring_list)
        df_new = df.query(querystring)
        total_instances = len(df_new)
        # Zit maar 1 k-v pair in
        for k,v in post.items():
            other_query_string = f"`{k}` == {v}"
        correct_instances = len(df_new.query(other_query_string))
        percentage_correct = correct_instances / total_instances
        if math.isclose(1,percentage_correct):
            entropy = 0
        else:
            entropy = (-1*percentage_correct) * math.log(percentage_correct, 2) + (-1*(1-percentage_correct) * math.log(1-percentage_correct, 2))
        
        return entropy

    def show(self): 

        with self.canvas.container():
            
            st.title("Rule Learning")
            st.header("Gevonden Regels:")

            col_t1, col_t2 = st.columns([2,3])

            with col_t1:
                # Stukje voor de selectionFinder
                st.subheader("Kies regels om te gebruiken voor suggesties:")
                if "list_of_rule_string" in st.session_state:
                    pre_selected = json.loads(st.session_state["list_of_rule_string"])
                else:
                    pre_selected = []
                df_of_column_rules_for_suggestion_finder = pd.DataFrame({"Regel": st.session_state["gevonden_rules_dict"].keys(), "Confidence":[x.confidence for x in st.session_state["gevonden_rules_dict"].values()]})
                if st.session_state["select_all_rules_btn"] == True:
                    pre_selected = [*range(0,len(df_of_column_rules_for_suggestion_finder))]
                
                gb1 = GridOptionsBuilder.from_dataframe(df_of_column_rules_for_suggestion_finder)
                gb1.configure_grid_options(fit_columns_on_grid_load=True)
                gb1.configure_selection('multiple', pre_selected_rows=pre_selected, use_checkbox=True, groupSelectsChildren=True, groupSelectsFiltered=True)
                response_selection_suggestion_finder = AgGrid(
                    df_of_column_rules_for_suggestion_finder,
                    height= 150,
                    editable=False,
                    gridOptions=gb1.build(),
                    data_return_mode="filtered_and_sorted",
                    update_mode="selection_changed",
                    fit_columns_on_grid_load=True,
                    theme="streamlit",
                    enable_enterprise_modules = False
                )


                colsug1, colsug2,_ = st.columns([1,1,3])
                with colsug1:
                    select_all_rules_btn =  st.button('Selecteer Alle', on_click=StateManager.turn_state_button_true, args=("select_all_rules_btn",))
                    # Verder moet er niks gebeuren
                
                with colsug2:
                    find_suggestions_btn =  st.button('Geef Suggesties')
                    if find_suggestions_btn:
                        st.session_state['suggesties_df'] = self.handler.get_suggestions_given_dataframe_and_column_rules(dataframe_in_json=st.session_state["dataframe"].to_json(),list_of_rule_string_in_json=json.dumps([x['Regel'] for x in response_selection_suggestion_finder['selected_rows']]), seq=st.session_state["current_seq"])
                        st.session_state["currentState"] = "BekijkSuggesties"
                        StateManager.reset_all_buttons()
                        st.experimental_rerun()

            with col_t2:
                st.subheader("Meer info over regel:")
                more_info = st.selectbox('Regel:', st.session_state["gevonden_rules_dict"].keys())

                if more_info:
                    st.write("Gevonden Mapping:")
                    cr = st.session_state["gevonden_rules_dict"][more_info]
                    gb2 = GridOptionsBuilder.from_dataframe(cr.value_mapping)
                    gb2.configure_grid_options(fit_columns_on_grid_load=True)
                    _ = AgGrid(
                        cr.value_mapping,
                        height= 150,
                        editable=False,
                        gridOptions=gb2.build(),
                        data_return_mode="filtered_and_sorted",
                        update_mode="no_update",
                        fit_columns_on_grid_load=True,
                        theme="streamlit",
                        enable_enterprise_modules = False,
                        key="gb2"
                    )

                    st.write("Rijen die niet voldoen aan mapping")
                    gb3 = GridOptionsBuilder.from_dataframe(st.session_state['dataframe'].iloc[cr.idx_to_correct])
                    gb3.configure_grid_options(fit_columns_on_grid_load=True)
                    _ = AgGrid(
                        st.session_state['dataframe'].iloc[cr.idx_to_correct],
                        height= 150,
                        editable=False,
                        gridOptions=gb3.build(),
                        data_return_mode="filtered_and_sorted",
                        update_mode="no_update",
                        fit_columns_on_grid_load=True,
                        theme="streamlit",
                        enable_enterprise_modules = False,
                        key="gb3"
                    )

            st.header("Valideer eigen regel:")

            col_b1, col_b2, col_b3 = st.columns([4,4,1])

            with col_b1:
                ant_set = st.multiselect(
                    'Kies de antecedentenset',
                    st.session_state["dataframe"].columns
                    )

            with col_b2:
                con_set = st.selectbox(
                'Kies de consequent kolom',
                st.session_state["dataframe"].columns)

            with col_b3:
                validate_own_rule_btn = st.button("Valideer eigen regel", on_click=StateManager.turn_state_button_true, args=("validate_own_rule_btn",))

            if st.session_state["validate_own_rule_btn"] == True:
                filtered_cols = ant_set + [con_set]
                rule_string =  ','.join(ant_set) + " => " + con_set
                found_rule = self.handler.get_column_rule_from_string(dataframe_in_json=st.session_state["dataframe"][filtered_cols].to_json(),rule_string=rule_string)

                col_bb1, col_bb2, col_bb3, col_bb4 = st.columns([2,3,3,1])

                with col_bb1:
                    st.write("Confidence:")
                    st.write(found_rule.confidence)
                with col_bb2:
                    st.write("Best mogelijke Mapping:")
                    st.write(found_rule.value_mapping)
                with col_bb3:
                    st.write("Rijen die NIET voldoen aan mapping:")
                    # st.write(found_rule.idx_to_correct)
                    gb4 = GridOptionsBuilder.from_dataframe(st.session_state['dataframe'].iloc[found_rule.idx_to_correct])
                    gb4.configure_grid_options(fit_columns_on_grid_load=True)
                    _ = AgGrid(
                        st.session_state['dataframe'].iloc[found_rule.idx_to_correct],
                        height= 150,
                        editable=False,
                        gridOptions=gb4.build(),
                        data_return_mode="filtered_and_sorted",
                        update_mode="no_update",
                        fit_columns_on_grid_load=True,
                        theme="streamlit",
                        enable_enterprise_modules = False, 
                        key="gb4")



                with col_bb4:
                    add_own_rule_btn = st.button("Voeg eigen regel toe voor suggesties", on_click=StateManager.turn_state_button_true, args=("add_own_rule_btn",))
                    calculate_entropy_btn = st.button("Bereken entropy voor specifieke regel",  on_click=StateManager.turn_state_button_true, args=("calculate_entropy_btn",))


            if st.session_state["add_own_rule_btn"] == True:
                st.session_state["gevonden_rules_dict"][found_rule.rule_string] = found_rule
                StateManager.reset_all_buttons()
                st.experimental_rerun()

            if st.session_state["calculate_entropy_btn"] == True:
                vm = found_rule.value_mapping
                df = st.session_state["dataframe"]
                vm['entropy'] = vm.apply(lambda row : self._calculate_entropy(row, df, len(vm)), axis = 1)
                st.write(vm)
                st.write("SOM:")
                st.write(np.sum(vm['entropy'].values))
                



            
