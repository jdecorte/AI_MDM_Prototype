import streamlit as st
import pandas as pd
from src.frontend.Handler.IHandler import IHandler
from st_aggrid import GridOptionsBuilder, AgGrid
from src.frontend.Cleaner.CleanerFuzzyMatching import FuzzyClusterView
import re
import extra_streamlit_components as stx

from src.frontend.enums.VarEnum import VarEnum


class CleanerInitPage:

    def __init__(self, canvas, handler: IHandler) -> None:
        self.canvas = canvas
        self.handler = handler

    def _show_ag_grid(self):
        # Toon de dataframe -> NIET EDITEERBAAR
        MIN_HEIGHT = 50
        MAX_HEIGHT = 500
        ROW_HEIGHT = 60

        gb = GridOptionsBuilder.from_dataframe(st.session_state[VarEnum.sb_LOADED_DATAFRAME.value])
        gb.configure_side_bar()
        gb.configure_default_column(groupable=True, value=True, enableRowGroup=True, aggFunc="sum", editable=False)
        gridOptions = gb.build()
        _ = AgGrid(st.session_state[VarEnum.sb_LOADED_DATAFRAME.value], gridOptions=gridOptions, enable_enterprise_modules=True, height=min(MIN_HEIGHT + len(st.session_state[VarEnum.sb_LOADED_DATAFRAME.value]) * ROW_HEIGHT, MAX_HEIGHT))

    def _show_unique_values(self, series):
        # find all the unique characters in the values of the column and show the value counts
        unique_characters = set()
        series = series.astype(str)
        series.apply(lambda x: list(map(lambda y: unique_characters.add(y), x)))
        
        value_counts = {}
        series.apply(lambda x: list(map(lambda y: value_counts.update({y: value_counts.get(y, 0) + 1}) if y not in value_counts else None, x)))
        unique_characters_df = pd.DataFrame(value_counts.items(), columns=["character", "value_counts"]).sort_values(by="value_counts", ascending=False)

        # remove all the characters that are in the regex pattern [a-zA-Z0-9]
        regex_pattern_to_remove = '[a-zA-Z0-9]+'
        unique_characters_df = unique_characters_df[~unique_characters_df["character"].str.contains(regex_pattern_to_remove)]

        return unique_characters_df

    # TODO: check that the next two methods can be removed? They are not used anymore.
    def _transform_to_simple_representation(self, series, extra_exceptions="", compress=False):
        #  transform the values to values which follow the regex pattern [a-zA-Z0-9]
        series = series.astype(str)
        regex_pattern_to_remove = '[^a-zA-Z0-9'+ extra_exceptions+']+'
        series = series.apply(lambda x: re.sub(regex_pattern_to_remove, '', x))
        series = series.apply(lambda x: re.sub('[a-zA-Z]', 'X', x))
        series = series.apply(lambda x: re.sub('[0-9]', '9', x))
        if compress:
            series = self._compress_values_of_series(series)
        return series

    def _compress_values_of_series(self, series):
        # If a character is followed by the same character, this character is removed
        # Example: "XX9" -> "X9"
        series = series.apply(lambda x: re.sub(r'([X9])\1+', r'\1', x))
        return series

    def show(self):
        chosen_tab = stx.tab_bar(data=[
            stx.TabBarItemData(id=1, title="Dataset", description=""),
            stx.TabBarItemData(id=2, title="Structure Detection", description=""),
            stx.TabBarItemData(id=3, title="Fuzzy Matching", description=""),
            stx.TabBarItemData(id=4, title="Cleaning Pipelines", description="")
            ], default=1)

        if chosen_tab == "1":
            st.header('Loaded dataset:')
            self._show_ag_grid()

        if chosen_tab == "2":
            self._show_structure_detection_tab()

        if chosen_tab == "3":
            self._show_fuzzy_matching_tab()

        if chosen_tab == "4":
            st.header('Cleaning Operations:')

            colG_1, colG_2, colG_3 = st.columns([1, 1, 1])

            with colG_2:
                cleaning_methods_list = ["fillna", "lowercase", "uppercase",
                                         "remove_digits", "remove_html",
                                         "remove_urls", "remove_punctuation",
                                         "remove_accents", "remove_stopwords",
                                         "remove_whitespace", "remove_bracketed",
                                         "remove_prefixed"]
                special_methods = ["remove_stopwords", "remove_bracketed",
                                   "remove_prefixed"]

                cleaning_method = st.selectbox(
                    "Select the cleaning method", cleaning_methods_list)
                if cleaning_method in special_methods:
                    colH_1, _ = st.columns([1, 1])
                    with colH_1:
                        value = st.text_input(
                            "Enter additional parameters to replace with", "")

            with colG_3:
                st.write("")
                st.write("")
                colG_3_1, colG_3_2, _ = st.columns([1, 1, 1])
                with colG_3_1:
                    if st.button("Add to pipeline"):
                        # check if the pipeline is empty
                        if st.session_state['pipeline'] == {}:
                            st.session_state['pipeline']['text'] = []

                        st.session_state['pipeline']['text'].append(
                            {'operator': cleaning_method}
                            if cleaning_method not in special_methods
                            else {'operator': cleaning_method, 'value': value})
                with colG_3_2:
                    if st.button("Clear pipeline"):
                        st.session_state['pipeline'] = {}

            st.write("")
            st.write("")
            colI_1, colI_3, _ = st.columns([4, 2, 4])

            with colI_1:
                chosen_column = st.selectbox(
                    "Select the column that you want to clean:",
                    st.session_state[VarEnum.sb_LOADED_DATAFRAME.value].columns)

            with colI_3:
                st.write("")
                st.write("")
                if st.button("Apply pipeline to column"):
                    st.session_state['cleaned_column_from_pipeline'] = pd.DataFrame(
                        self.handler.clean_dataframe_dataprep(
                            dataframe_in_json=st.session_state[VarEnum.sb_LOADED_DATAFRAME.value][chosen_column].to_frame().to_json(), 
                            custom_pipeline=st.session_state['pipeline']))
                    # transform the index to int and sort it
                    st.session_state['cleaned_column_from_pipeline'].index = st.session_state['cleaned_column_from_pipeline'].index.astype(int)
            # check if a pandas dataframe is not empty
            if st.session_state['cleaned_column_from_pipeline'] is not None:
                st.subheader("Cleaned Column:")
                st.write(st.session_state['cleaned_column_from_pipeline'])

                if st.button("Save column"):
                    # save the cleaned column to the dataframe
                    st.session_state[VarEnum.sb_LOADED_DATAFRAME.value][chosen_column] = st.session_state['cleaned_column_from_pipeline'][chosen_column]
                    st.write("Column saved")

            with colG_1:
                st.subheader("Current pipeline:")
                st.write(st.session_state['pipeline'])

    def _show_structure_detection_tab(self):
        st.header('Structure Detection:')
        colA_1, colA_2, colA_3 = st.columns([1, 1, 1])
        with colA_1:
            chosen_column = st.selectbox(
                "Select a column to detect the structure of the values",
                st.session_state[VarEnum.sb_LOADED_DATAFRAME.value].columns)
        with colA_2:
            extra_exceptions = "".join(st.multiselect(
                "Select the characters that you want to keep in the pattern",
                self._show_unique_values(
                    st.session_state[VarEnum.sb_LOADED_DATAFRAME.value][chosen_column])["character"].tolist()))
        with colA_3:
            st.write("")
            st.write("")
            compress = st.checkbox("Compress the found patterns")

        simple_repr = pd.Series(
            self.handler.structure_detection(
                st.session_state[VarEnum.sb_LOADED_DATAFRAME.value][chosen_column].to_json(),
                extra_exceptions, compress))

        series_for_aggrid = (simple_repr.value_counts(normalize=True)
                                        .copy(deep=True))
        series_for_aggrid = (series_for_aggrid.rename_axis('pattern')
                                              .reset_index(name='percentage'))
        colB_1, _, colB_3 = st.columns([2, 1, 3])
        with colB_1:
            st.write("The found patterns are:")
            gb = GridOptionsBuilder.from_dataframe(series_for_aggrid)
            gb.configure_side_bar()
            gb.configure_default_column(
                groupable=True, value=True,
                enableRowGroup=True, aggFunc="sum", editable=False)
            gb.configure_selection(
                'single', pre_selected_rows=[], use_checkbox=True,
                groupSelectsChildren=True, groupSelectsFiltered=True)
            response_patterns = AgGrid(
                series_for_aggrid,
                editable=False,
                gridOptions=gb.build(),
                data_return_mode="filtered_and_sorted",
                update_mode="selection_changed",
                fit_columns_on_grid_load=True,
                theme="streamlit",
                enable_enterprise_modules=False,
            )

        with colB_3:
            if response_patterns["selected_rows"]:
                # show the records that match the selected pattern
                selected_pattern = (response_patterns["selected_rows"][0]["pattern"]
                                    if len(response_patterns["selected_rows"]) > 0
                                    else None)
                if selected_pattern is not None:
                    df_for_aggrid2 = st.session_state[VarEnum.sb_LOADED_DATAFRAME.value][simple_repr.values == selected_pattern]

                    if st.session_state["idx_of_structure_df"] is None:
                        st.session_state["idx_of_structure_df"] = list(df_for_aggrid2.index)
                    gb2 = GridOptionsBuilder.from_dataframe(df_for_aggrid2)
                    gb2.configure_side_bar()
                    gb2.configure_default_column(
                        groupable=False, value=True,
                        enableRowGroup=True, aggFunc="sum", editable=True)
                    gridOptions = gb2.build()
                    grid = AgGrid(df_for_aggrid2, gridOptions=gridOptions,
                                  enable_enterprise_modules=False, height=500)
                    
                    st.write("The records that match the selected pattern are:")
                    grid['data'].index = st.session_state["idx_of_structure_df"]

                    if st.button("Save"):
                        # Replace values in the dataframe with the (possibly) new values
                        st.session_state[VarEnum.sb_LOADED_DATAFRAME.value].loc[grid['data'].index] = grid['data']
                        st.experimental_rerun()
            else:
                st.session_state["idx_of_structure_df"] = None

    def _show_fuzzy_matching_tab(self):
        st.header('Fuzzy Matching:')
        colC_1, colC_2, _ = st.columns([1, 1, 1])
        with colC_1:
            chosen_column = st.selectbox(
                "Select the column that you want to cluster:",
                st.session_state[VarEnum.sb_LOADED_DATAFRAME.value].columns)
        with colC_2:
            cluster_method = st.selectbox(
                "Select the cluster method",
                ["fingerprint", "phonetic-fingerprint",
                    "ngram-fingerprint", "levenshtein"])

        colD_1, _ = st.columns([2, 1])

        with colD_1:
            n_gram = 0
            radius = 0
            block_size = 0
            if cluster_method == 'ngram-fingerprint':
                colE_1, _ = st.columns([1, 1])
                with colE_1:
                    n_gram = st.slider(
                        'The Number of N-Grams',
                        min_value=2, max_value=10, value=2)
            if cluster_method == 'levenshtein':
                colF_1, colF_2 = st.columns([1, 1])
                with colF_1:
                    radius = st.slider(
                        'The Radius',
                        min_value=1, max_value=10, value=2)
                with colF_2:
                    block_size = st.slider(
                        'The Block Size',
                        min_value=1, max_value=10, value=6)

        # Iterate over clusters
        st.session_state['list_of_cluster_view'] = []
        list_of_fuzzy_clusters = []

        for cluster_id, list_of_values in self.handler.fuzzy_match_dataprep(
                dataframe_in_json=st.session_state[VarEnum.sb_LOADED_DATAFRAME.value][chosen_column].to_frame().to_json(),
                df_name=st.session_state[VarEnum.sb_LOADED_DATAFRAME_NAME.value],
                col=chosen_column,
                cluster_method=cluster_method,
                ngram=n_gram,
                radius=radius,
                block_size=block_size).items():
            if f'fuzzy_merge_{cluster_id}' not in st.session_state:
                st.session_state[f'fuzzy_merge_{cluster_id}'] = True
            # Create a view for each cluster
            list_of_fuzzy_clusters.append(FuzzyClusterView(
                cluster_id, list_of_values,
                st.session_state[VarEnum.sb_LOADED_DATAFRAME.value][chosen_column]))
        st.session_state["list_of_fuzzy_cluster_view"] = list_of_fuzzy_clusters

        if list_of_fuzzy_clusters != []:
            st.header("Found clusters:")
            st.write("")
            st.write("")
            sub_rows_to_use = self. _create_pagination(
                "page_number_Dedupe",
                st.session_state["list_of_fuzzy_cluster_view"], 5)
            for idx, cv in enumerate(sub_rows_to_use):
                self._create_cluster_card(idx, cv)
            if st.button("Bevestig clusters"):
                self._merge_clusters(st.session_state["list_of_fuzzy_cluster_view"],chosen_column )
        else:
            st.markdown("**No clusters have been found**")

    def _create_pagination(self, key, cols_to_use, N):
        # A variable to keep track of which product we are currently displaying
        if key not in st.session_state:
            st.session_state[key] = 0

        last_page = len(cols_to_use) // N

        # Add a next button and a previous button
        prev, _, tussen, _, next, _ = st.columns([3, 1, 2, 1, 3, 2])

        if next.button("Next results"):
            if st.session_state[key] + 1 > last_page:
                st.session_state[key] = 0
            else:
                st.session_state[key] += 1

        if prev.button("Previous results"):
            if st.session_state[key] - 1 < 0:
                st.session_state[key] = last_page
            else:
                st.session_state[key] -= 1

        with tussen:
            st.write(str(st.session_state[key] + 1) + "/" +
                     str(last_page + 1) + " (" + str(len(cols_to_use)) +
                     " resultaten)")

        # Get start and end indices of the next page of the dataframe
        start_idx = st.session_state[key] * N
        end_idx = (1 + st.session_state[key]) * N

        # Index into the sub dataframe
        return cols_to_use[start_idx:end_idx]

    def _merge_clusters(self, list_of_cluster_view, column_name):
        # Itereer over alle clusterview
        # df_to_use  = st.session_state[VarEnum.sb_LOADED_DATAFRAME.value]
        merged_df = pd.DataFrame(columns=st.session_state[VarEnum.sb_LOADED_DATAFRAME.value].columns)
        for cv in list_of_cluster_view:
            if st.session_state[f'fuzzy_merge_{cv.cluster_id}']:
                for e in list(cv.distinct_values_in_cluster['values']):
                    # Look for value e in the dataframe in column column_name
                    # and replace it with the value in the cluster
                    st.session_state[VarEnum.sb_LOADED_DATAFRAME.value][column_name] = st.session_state[VarEnum.sb_LOADED_DATAFRAME.value][column_name].replace(
                        e, cv.new_cell_value)
            else:
                pass

        st.session_state[VarEnum.gb_CURRENT_STATE.value] = None
        st.experimental_rerun()

    def _create_cluster_card(self, idx, cv):
        MIN_HEIGHT = 50
        MAX_HEIGHT = 500
        ROW_HEIGHT = 35
        
        col0, colA, colB, colC, _ = st.columns([2,4,2,2,4])
        with col0:
            st.subheader(f'Cluster #{cv.cluster_id}')
        with colA:
            # AGGRID die niet editeerbaar is maar wel met select knopjes
            gb1 = GridOptionsBuilder.from_dataframe(cv.distinct_values_in_cluster)
            gb1.configure_side_bar()
            gb1.configure_selection('multiple',use_checkbox=True, groupSelectsChildren=True, groupSelectsFiltered=True, pre_selected_rows= [0,len(cv.distinct_values_in_cluster)-1])
            gb1.configure_default_column(groupable=False, value=True, enableRowGroup=True, aggFunc="sum", editable=False)
            gridOptions = gb1.build()
            _ = AgGrid(cv.distinct_values_in_cluster, gridOptions=gridOptions, enable_enterprise_modules=False, update_mode="VALUE_CHANGED", height=min(MIN_HEIGHT + len(cv.distinct_values_in_cluster) * ROW_HEIGHT, MAX_HEIGHT))
            
        with colB:
            # checkbox om te mergen, default actief
            _ = st.checkbox('Voeg samen',value=True, key=f'fuzzy_merge_{cv.cluster_id}')

        with colC:
            # st.write("Verander naar")
            new_value = st.text_input('New value', value=cv.new_cell_value, key=f'new_value_{cv.cluster_id}')
            cv.set_new_cell_value(new_value)
            