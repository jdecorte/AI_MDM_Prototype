import pandas as pd
import streamlit as st
from st_aggrid import GridOptionsBuilder, AgGrid
from src.frontend.StateManager import StateManager
from src.frontend.Handler.IHandler import IHandler
import config as cfg
import hashlib

from src.frontend.enums.VarEnum import VarEnum


class RuleLearnerSuggestionsPage:

    def __init__(self, canvas, handler: IHandler) -> None:
        self.canvas = canvas
        self.handler = handler

    def show(self):
        with self.canvas.container():
            st.title("Rule Learning")
            df_with_predictions = pd.read_json(eval(st.session_state["suggesties_df"]))

            # Controleer of er wel suggesties gevonden zijn
            if df_with_predictions.shape[0] == 0:
                st.markdown("**There are no more suggestions**")
                return

            st.header("Suggestions for the selected rules:")     
            df_with_predictions = df_with_predictions[
                df_with_predictions.columns.drop(
                    list(df_with_predictions.filter(
                        regex='(__SCORE.*|__PREDICTION.*|__BEST_SCORE)')))]

            # Order columns: __BEST_RULE and __BEST_PREDICTION at the front
            # TODO: this seems brittle, relies on the order of the columns in dataframe
            cols = df_with_predictions.columns.tolist()
            cols = cols[-2:] + cols[:-2]
            df_with_predictions = df_with_predictions[cols]

            suggestions_rows_selected = []
            list_of_df_idx = []
            if st.session_state["select_all_suggestions_btn"]:
                pre_selected = [*range(0, len(df_with_predictions))]
            else:
                pre_selected = []

            gb1 = GridOptionsBuilder.from_dataframe(df_with_predictions)
            gb1.configure_grid_options(fit_columns_on_grid_load=True)
            gb1.configure_selection(
                'multiple',
                pre_selected_rows=pre_selected,
                use_checkbox=True,
                groupSelectsChildren=True,
                groupSelectsFiltered=True)
            response_selection_suggestion_finder = AgGrid(
                df_with_predictions,
                height=350,
                editable=False,
                gridOptions=gb1.build(),
                data_return_mode="filtered_and_sorted",
                update_mode="selection_changed",
                theme="streamlit",
                enable_enterprise_modules=False
            )

            colb3, colb0, colb1, colb2,  = st.columns([1, 2, 1, 4])

            aangepaste_dataset = st.container()

            with colb0:
                apply_suggestions = st.button(
                    "Apply the selected suggestions", key="apply_suggestions")
                # Maak tijdelijke dataframe aan, zodat wijzigingen niet meteen
                # de sidebar gaan beginnen aanpassen

                if apply_suggestions:
                    st.session_state['temp_dataframe'] = st.session_state[VarEnum.sb_LOADED_DATAFRAME.value].copy()
                    suggestions_rows_selected = response_selection_suggestion_finder['selected_rows']
                    list_of_df_idx = df_with_predictions.index
                    set_of_cols = set()
                    for idx, row in enumerate(suggestions_rows_selected):
                        index_of_to_change = list_of_df_idx[idx]
                        val_to_change = row["__BEST_PREDICTION"]
                        rs = row["__BEST_RULE"]
                        rss = rs.split(" => ")
                        col_to_change = rss[1]
                        set_of_cols.add(col_to_change)
                        for e in rss[0].split(","):
                            set_of_cols.add(e)
                        # Change value in temp_dataframe
                        st.session_state['temp_dataframe'].loc[index_of_to_change, col_to_change] = val_to_change

                    st.session_state["columns_affected_by_suggestion_application"] = list(set_of_cols)

                    with aangepaste_dataset:
                        st.info('Changes have been applied to the dataset! Press the "Recalculate rules" button to see what impact your changes have on the rules.')
                        st.header("Modified dataset:")
                        rows_selected = []

                        for idx, row in enumerate(suggestions_rows_selected):
                            rows_selected.append(int(list_of_df_idx[idx]))

                        gb22 = GridOptionsBuilder.from_dataframe(st.session_state["temp_dataframe"])
                        gb22.configure_side_bar()
                        # gb22.configure_selection('multiple', pre_selected_rows=rows_selected)
                        # gb22.configure_default_column(
                        #     groupable=True,
                        #     value=True,
                        #     enableRowGroup=True,
                        #     aggFunc="sum",
                        #     editable=False)
                        gridOptions = gb22.build()
                        _ = AgGrid(
                                st.session_state["temp_dataframe"],
                                gridOptions=gridOptions,
                                enable_enterprise_modules=True, height=350, key="aangepaste_dataset")


            with colb1:
                submitted = st.button("Recalculate rules")                
                if submitted:
                    # Get the rule_finding_config from the session_state
                    rule_finding_config = st.session_state["rule_finding_config"]

                    json_rule_finding_config = rule_finding_config.to_json()

                    # recalculate unique storage id
                    st.session_state[VarEnum.gb_SESSION_ID_WITH_FILE_HASH.value] = f"{st.session_state[VarEnum.gb_SESSION_ID.value]}-{hashlib.md5(st.session_state['temp_dataframe'].to_json().encode('utf-8')).hexdigest()}"

                    self.handler.recalculate_column_rules(
                        old_df_in_json=st.session_state[VarEnum.sb_LOADED_DATAFRAME.value].to_json(),
                        new_df_in_json=st.session_state["temp_dataframe"].to_json(),
                        rule_finding_config_in_json=json_rule_finding_config,
                        affected_columns=st.session_state["columns_affected_by_suggestion_application"])                  
                    # Reset columns_affected_by_suggestion_application
                    del st.session_state["columns_affected_by_suggestion_application"]

                    cfg.logger.debug("Recalculate rules done")

                    # Restore state van de aangemaakte file in de session_map
                    st.session_state[VarEnum.gb_SESSION_MAP.value] = self.handler.get_session_map(
                        st.session_state['temp_dataframe'].to_json())
                    StateManager.restore_state(
                        **{"handler": self.handler,
                           "file_path": st.session_state[VarEnum.gb_SESSION_MAP.value]["1"]["rules"],
                           "chosen_seq": "1"})
                    
                    # Nieuwe dataframe, betekent sowieso dat current_session gelijk zal zijn aan 1:
                    st.session_state[VarEnum.sb_LOADED_DATAFRAME.value] = st.session_state['temp_dataframe'].copy()
                    st.session_state[VarEnum.gb_CURRENT_SEQUENCE_NUMBER.value] = 1

                    st.experimental_rerun()

            with colb2:
                # Download de temp_dataframe
                if "columns_affected_by_suggestion_application" in st.session_state:
                    st.download_button(
                        label="Download modified dataset",
                        data=st.session_state["temp_dataframe"].to_csv(index=False).encode('utf-8'),
                        file_name=f'new_{st.session_state[VarEnum.sb_LOADED_DATAFRAME_NAME.value]}',
                        mime='text/csv',
                    )

            with colb3:
                # Select all button
                select_all_rules_btn = st.button(
                    'Select all',
                    on_click=StateManager.turn_state_button_true,
                    args=("select_all_suggestions_btn",))

            # if apply_suggestions:
            #     st.header("Modified dataset:")
            #     rows_selected = []

            #     for idx, row in enumerate(suggestions_rows_selected):
            #         rows_selected.append(int(list_of_df_idx[idx]))

            #     gb = GridOptionsBuilder.from_dataframe(st.session_state["temp_dataframe"])
            #     gb.configure_side_bar()
            #     gb.configure_selection('multiple', pre_selected_rows=rows_selected)
            #     gb.configure_default_column(
            #         groupable=True,
            #         value=True,
            #         enableRowGroup=True,
            #         aggFunc="sum",
            #         editable=False)
            #     gridOptions = gb.build()
            #     _ = AgGrid(
            #             st.session_state["temp_dataframe"],
            #             gridOptions=gridOptions,
            #             enable_enterprise_modules=True)
