import streamlit as st
import json
import pandas as pd
from streamlit.components.v1 import html
from streamlit.components.v1 import iframe
from src.frontend.Handler.IHandler import IHandler
from st_aggrid import GridOptionsBuilder, AgGrid, GridUpdateMode, DataReturnMode, JsCode, ColumnsAutoSizeMode
from src.frontend.Cleaner.CleanerFuzzyMatching import FuzzyClusterView
import re

import numpy as np


class CleanerInitPage:
    def __init__(self, canvas, handler:IHandler) -> None:
        self.canvas = canvas
        self.handler = handler

    def _show_ag_grid(self):
            # Toon de dataframe -> NIET EDITEERBAAR
            MIN_HEIGHT = 50
            MAX_HEIGHT = 500
            ROW_HEIGHT = 60

            st.markdown(f"<h4>Ingeladen Dataset: </h4>", unsafe_allow_html=True)
            gb = GridOptionsBuilder.from_dataframe(st.session_state["dataframe"])
            gb.configure_side_bar()
            gb.configure_default_column(groupable=True, value=True, enableRowGroup=True, aggFunc="sum", editable=False)
            gridOptions = gb.build()
            grid_response = AgGrid(st.session_state["dataframe"], gridOptions=gridOptions, enable_enterprise_modules=True, height=min(MIN_HEIGHT + len(st.session_state["dataframe"]) * ROW_HEIGHT, MAX_HEIGHT))

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
        st.header('Dataset:')
        self._show_ag_grid()

        st.header('Structure Detection:')
        colA_1, colA_2, colA_3 = st.columns([1,1,1])
        with colA_1:
            chosen_column = st.selectbox("Select a column to detect the structure of the values", st.session_state["dataframe"].columns)
        with colA_2:
            extra_exceptions = "".join(st.multiselect("Select the characters that you want to keep in the pattern", self._show_unique_values(st.session_state["dataframe"][chosen_column])["character"].tolist()))
        with colA_3:
            st.write("")
            st.write("")
            compress = st.checkbox("Compress the found patterns")

        simple_representation = pd.Series(self.handler.structure_detection(st.session_state["dataframe"][chosen_column].to_json(), extra_exceptions, compress))

        series_for_aggrid = simple_representation.value_counts(normalize=True).copy(deep=True)
        series_for_aggrid = series_for_aggrid.rename_axis('pattern').reset_index(name='percentage')
        colB_1, _, colB_3= st.columns([2,1,3])
        with colB_1:
            st.write("The found patterns are:")
            gb = GridOptionsBuilder.from_dataframe(series_for_aggrid)
            gb.configure_side_bar()
            gb.configure_default_column(groupable=True, value=True, enableRowGroup=True, aggFunc="sum", editable=False)
            gb.configure_selection('single', pre_selected_rows=[], use_checkbox=True, groupSelectsChildren=True, groupSelectsFiltered=True)
            response_patterns = AgGrid(
                series_for_aggrid,
                editable=False,
                gridOptions=gb.build(),
                data_return_mode="filtered_and_sorted",
                update_mode="selection_changed",
                fit_columns_on_grid_load=True,
                theme="streamlit",
                enable_enterprise_modules = False,
            )
            
        with colB_3:
            if response_patterns["selected_rows"]:
                # show the records that match the selected pattern
                selected_pattern = response_patterns["selected_rows"][0]["pattern"] if len(response_patterns["selected_rows"]) > 0 else None
                if selected_pattern is not None:
                    df_for_aggrid2 = st.session_state['dataframe'][simple_representation.values == selected_pattern]
                    # df_for_aggrid2 = st.session_state['dataframe'][simple_representation == selected_pattern]
                    gb2 = GridOptionsBuilder.from_dataframe(df_for_aggrid2)
                    gb2.configure_side_bar()
                    gb2.configure_default_column(groupable=False, value=True, enableRowGroup=True, aggFunc="sum", editable=True)
                    gridOptions = gb2.build()
                    grid = AgGrid(df_for_aggrid2, gridOptions=gridOptions, enable_enterprise_modules=False, height=500)
                    if st.button("Save"):
                        pass
                
        st.header('Fuzzy Matching:')
        colC_1, colC_2, _= st.columns([1,1,1])
        with colC_1:
            chosen_column = st.selectbox("Select the column that you want to cluster:", st.session_state["dataframe"].columns)
        with colC_2:
            cluster_method = st.selectbox("Select the cluster method", ["fingerprint", "phonetic-fingerprint", "ngram-fingerprint", "levenshtein"])

        colD_1, _= st.columns([2,1])
        
        with colD_1:
            n_gram = 0
            radius = 0
            block_size = 0
            if cluster_method == 'ngram-fingerprint':  
                colE_1, _= st.columns([1,1])
                with colE_1:
                    n_gram = st.slider('The Number of N-Grams', min_value=2, max_value=10, value=2)
            if cluster_method == 'levenshtein':
                colF_1, colF_2= st.columns([1,1])
                with colF_1:
                    radius = st.slider('The Radius', min_value=1, max_value=10, value=2)
                with colF_2:
                    block_size = st.slider('The Block Size', min_value=1, max_value=10, value=6)
          
        # Iterate over clusters
        st.session_state['list_of_cluster_view'] = []
        list_of_fuzzy_clusters = []
        
        for cluster_id, list_of_values in self.handler.fuzzy_match_dataprep(dataframe_in_json=st.session_state["dataframe"][chosen_column].to_frame().to_json(), df_name=st.session_state["dataframe_name"], col=chosen_column, cluster_method=cluster_method, ngram=n_gram, radius=radius, block_size=block_size).items():
            if f'fuzzy_merge_{cluster_id}' not in st.session_state:
                    st.session_state[f'fuzzy_merge_{cluster_id}'] = True
            # Create a view for each cluster
            list_of_fuzzy_clusters.append(FuzzyClusterView(cluster_id, list_of_values, st.session_state["dataframe"][chosen_column]))
        st.session_state["list_of_fuzzy_cluster_view"] = list_of_fuzzy_clusters
        sub_rowstoUse = self. _createPaginering("page_number_Dedupe", st.session_state["list_of_fuzzy_cluster_view"], 5)
        for idx, cv in enumerate(sub_rowstoUse):
            self._create_cluster_card(idx, cv)


        if st.button("Bevestig clusters"):
            self._merge_clusters(st.session_state["list_of_cluster_view"])

        st.header('Cleaning Operations:')
        # TODO: Add cleaning operations


    def _createPaginering(self, key, colstoUse, N):
        # A variable to keep track of which product we are currently displaying
        if key not in st.session_state:
            st.session_state[key] = 0
        
        last_page = len(colstoUse) // N

        # Add a next button and a previous button
        prev, _, tussen, _ ,next = st.columns([1,5,2,5,1])

        if next.button("Volgende resultaten"):
            if st.session_state[key] + 1 > last_page:
                st.session_state[key] = 0
            else:
                st.session_state[key] += 1

        if prev.button("Vorige resultaten"):
            if st.session_state[key] - 1 < 0:
                st.session_state[key] = last_page
            else:
                st.session_state[key] -= 1
        
        with tussen:
            st.write( str(st.session_state[key] +1) + "/"+ str(last_page +1) +" (" + str(len(colstoUse)) +" resultaten)")

        # Get start and end indices of the next page of the dataframe
        start_idx = st.session_state[key] * N 
        end_idx = (1 + st.session_state[key]) * N 

        # Index into the sub dataframe
        return colstoUse[start_idx:end_idx]

    def _merge_clusters(self, list_of_cluster_view):
        # Itereer over alle clusterview
        # df_to_use  = st.session_state["dataframe"]
        merged_df = pd.DataFrame(columns=st.session_state["dataframe"].columns)
        for cv in list_of_cluster_view:
            if st.session_state[f'merge_{cv.cluster_id}']:
                merged_df = pd.concat([merged_df, cv.new_row], ignore_index=True)
                # merged_df.append(cv.new_row, ignore_index=True)
                # merged_df.loc[len(merged_df)] = cv.new_row
            else:
                for _, row in cv.records_df.iterrows():
                    merged_df = pd.concat([merged_df, row], ignore_index=True)
                    # merged_df.append(row, ignore_index=True)

        st.session_state["currentState"] = None
        st.session_state["dataframe"] = merged_df
        st.experimental_rerun()

    def _create_cluster_card(self, idx, cv):
        MIN_HEIGHT = 50
        MAX_HEIGHT = 500
        ROW_HEIGHT = 35
        st.subheader(f'Cluster #{cv.cluster_id}')
        colA, colB, colC, _ = st.columns([4,1,2,6])
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
            st.write("Verander naar")
            new_value = st.text_input('Nieuwe waarde', value=cv.new_cell_value, key=f'new_value_{cv.cluster_id}')
            cv.set_new_cell_value(new_value)
            