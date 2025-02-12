import numpy as np
import pandas as pd
import streamlit as st
from st_aggrid import GridOptionsBuilder, AgGrid, ColumnsAutoSizeMode
from src.frontend.StateManager import StateManager
from src.frontend.Handler.IHandler import IHandler
import json
import math

from src.frontend.enums.VarEnum import VarEnum


class RuleLearnerSummaryRulesPage:

    def __init__(self, canvas, handler: IHandler) -> None:
        self.canvas = canvas
        self.handler = handler

    def _calculate_entropy(self, row, df, len_vm):
        querystring_list = []
        pre = row[:-1]
        post = row[-1:]
        for k, v in pre.items():
            querystring_list.append(f"`{k}` == {v}")
        querystring = " and ".join(querystring_list)
        df_new = df.query(querystring)
        total_instances = len(df_new)
        # Zit maar 1 k-v pair in
        for k, v in post.items():
            other_query_string = f"`{k}` == {v}"
        correct_instances = len(df_new.query(other_query_string))
        percentage_correct = correct_instances / total_instances
        if math.isclose(1, percentage_correct):
            entropy = 0
        else:
            entropy = ((-1*percentage_correct) * math.log(percentage_correct, 2) +
                       (-1*(1-percentage_correct) * math.log(1-percentage_correct, 2)))

        return entropy

    def show(self):

        with self.canvas.container():

            st.title("Rule Learning")
            st.header("Found Rules:")

            col_t1, _, col_t2 = st.columns([8, 1, 12])

            with col_t1:
                # Stukje voor de selectionFinder
                st.subheader("Choose rules to give suggestions:")
                if "list_of_rule_string" in st.session_state:
                    pre_selected = json.loads(st.session_state["list_of_rule_string"])
                else:
                    pre_selected = []
                df_of_column_rules_for_suggestion_finder = pd.DataFrame(
                    {"Regel": st.session_state["gevonden_rules_dict"].keys(),
                     "Confidence": [x.confidence for x in st.session_state["gevonden_rules_dict"].values()]})

                if st.session_state["select_all_rules_btn"]:
                    pre_selected = [*range(0, len(df_of_column_rules_for_suggestion_finder))]

                gb1 = GridOptionsBuilder.from_dataframe(df_of_column_rules_for_suggestion_finder)
                gb1.configure_grid_options(fit_columns_on_grid_load=True)
                gb1.configure_selection(
                    'multiple',
                    pre_selected_rows=pre_selected,
                    use_checkbox=True,
                    groupSelectsChildren=True,
                    groupSelectsFiltered=True)
                response_selection_suggestion_finder = AgGrid(
                    df_of_column_rules_for_suggestion_finder,
                    editable=False,
                    gridOptions=gb1.build(),
                    data_return_mode="filtered_and_sorted",
                    update_mode="selection_changed",
                    fit_columns_on_grid_load=True,
                    theme="streamlit",
                    enable_enterprise_modules=False,
                    height=450,
                    columns_auto_size_mode=ColumnsAutoSizeMode.NO_AUTOSIZE
                )

                colsug1, colsug2, _ = st.columns([1, 1, 2])
                with colsug1:
                    select_all_rules_btn = st.button(
                        'Select all rules',
                        on_click=StateManager.turn_state_button_true,
                        args=("select_all_rules_btn",))
                    # Verder moet er niks gebeuren

                with colsug2:
                    find_suggestions_btn = st.button('Give Suggestions')
                    if find_suggestions_btn:
                        st.session_state['suggesties_df'] = \
                            self.handler.get_suggestions_given_dataframe_and_column_rules(
                            dataframe_in_json=st.session_state[VarEnum.sb_LOADED_DATAFRAME.value].to_json(),
                            list_of_rule_string_in_json=json.dumps([x['Regel'] for x in response_selection_suggestion_finder['selected_rows']]),
                            seq=st.session_state[VarEnum.gb_CURRENT_SEQUENCE_NUMBER.value])
                        st.session_state[VarEnum.gb_CURRENT_STATE.value] = "BekijkSuggesties"
                        StateManager.reset_all_buttons()
                        st.experimental_rerun()

            with col_t2:
                st.subheader("More info about the rule:")
                more_info = st.selectbox('Rule:', st.session_state["gevonden_rules_dict"].keys())
                if more_info:
                    st.write("Found Mapping:")
                    cr = st.session_state["gevonden_rules_dict"][more_info]
                    gb2 = GridOptionsBuilder.from_dataframe(cr.value_mapping)
                    _ = AgGrid(
                        cr.value_mapping,
                        height=150,
                        editable=False,
                        gridOptions=gb2.build(),
                        data_return_mode="filtered_and_sorted",
                        update_mode="no_update",
                        fit_columns_on_grid_load=True,
                        theme="streamlit",
                        enable_enterprise_modules=False,
                        columns_auto_size_mode=ColumnsAutoSizeMode.NO_AUTOSIZE
                    )

                    st.markdown("**Rows that do not comply with the found mapping:**")
                    gb3 = GridOptionsBuilder.from_dataframe(st.session_state[VarEnum.sb_LOADED_DATAFRAME.value].iloc[cr.idx_to_correct])
                    _ = AgGrid(
                        st.session_state[VarEnum.sb_LOADED_DATAFRAME.value].iloc[cr.idx_to_correct],
                        height=150,
                        editable=False,
                        gridOptions=gb3.build(),
                        data_return_mode="filtered_and_sorted",
                        update_mode="no_update",
                        fit_columns_on_grid_load=False,
                        theme="streamlit",
                        enable_enterprise_modules=False,
                        columns_auto_size_mode=ColumnsAutoSizeMode.NO_AUTOSIZE
                    )

            st.header("Validate own rule:")

            col_b1, col_b2, col_b3 = st.columns([4, 4, 1])

            with col_b1:
                ant_set = st.multiselect(
                    'Choose the antecedent set',
                    st.session_state[VarEnum.sb_LOADED_DATAFRAME.value].columns
                    )

            with col_b2:
                con_set = st.selectbox(
                    'Choose the consequent column',
                    st.session_state[VarEnum.sb_LOADED_DATAFRAME.value].columns)

            with col_b3:
                st.write(" ")
                st.write(" ")
                validate_own_rule_btn = st.button(
                    "Valiate own rule",
                    on_click=StateManager.turn_state_button_true,
                    args=("validate_own_rule_btn",))

            if st.session_state["validate_own_rule_btn"]:
                filtered_cols = ant_set + [con_set]
                rule_string = ','.join(ant_set) + " => " + con_set
                found_rule = self.handler.get_column_rule_from_string(
                    dataframe_in_json=st.session_state[VarEnum.sb_LOADED_DATAFRAME.value][filtered_cols].to_json(),
                    rule_string=rule_string)

                col_bb1, col_bb2, col_bb3, col_bb4 = st.columns([2, 2, 3, 1])

                with col_bb1:
                    st.write("Confidence:")
                    st.write(found_rule.confidence)
                with col_bb2:
                    st.write("Most likely mapping:")
                    st.write(found_rule.value_mapping)
                with col_bb3:
                    st.markdown("**Rows that do not comply with the found mapping:**")
                    # st.write(found_rule.idx_to_correct)
                    gb4 = GridOptionsBuilder.from_dataframe(
                        st.session_state[VarEnum.sb_LOADED_DATAFRAME.value].iloc[found_rule.idx_to_correct])
                    gb4.configure_grid_options(fit_columns_on_grid_load=True)
                    _ = AgGrid(
                        st.session_state[VarEnum.sb_LOADED_DATAFRAME.value].iloc[found_rule.idx_to_correct],
                        height=150,
                        editable=False,
                        gridOptions=gb4.build(),
                        data_return_mode="filtered_and_sorted",
                        update_mode="no_update",
                        fit_columns_on_grid_load=False,
                        theme="streamlit",
                        enable_enterprise_modules=False,
                        columns_auto_size_mode=ColumnsAutoSizeMode.NO_AUTOSIZE
                        )

                with col_bb4:
                    add_own_rule_btn = st.button(
                        "Add own rule for suggestions",
                        on_click=StateManager.turn_state_button_true,
                        args=("add_own_rule_btn",))
                    calculate_entropy_btn = st.button(
                        "Calculate entropy for specific rule",
                        on_click=StateManager.turn_state_button_true,
                        args=("calculate_entropy_btn",))

            if st.session_state["add_own_rule_btn"]:
                st.session_state["gevonden_rules_dict"][found_rule.rule_string] = found_rule
                StateManager.reset_all_buttons()
                st.experimental_rerun()

            if st.session_state["calculate_entropy_btn"]:
                vm = found_rule.value_mapping
                df = st.session_state[VarEnum.sb_LOADED_DATAFRAME.value]
                vm['entropy'] = vm.apply(
                    lambda row: self._calculate_entropy(row, df, len(vm)), axis=1)
                st.write(vm)
                st.write("SOM:")
                st.write(np.sum(vm['entropy'].values))
