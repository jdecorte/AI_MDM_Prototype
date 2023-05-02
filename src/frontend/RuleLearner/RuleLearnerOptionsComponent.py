import streamlit as st
import extra_streamlit_components as stx

from src.shared.Enums.FiltererEnum import FiltererEnum
from src.shared.Enums.BinningEnum import BinningEnum
from src.shared.Enums.DroppingEnum import DroppingEnum

from src.frontend.enums.DialogEnum import DialogEnum
from src.frontend.enums.VarEnum import VarEnum


class RuleLearnerOptionsComponent:

    def __init__(self) -> None:
        pass

    def _create_total_binning_dict(_self, dict_to_show):
        st.session_state["binning_option"] = dict_to_show
        return st.session_state["binning_option"]

    def _create_total_dropping_dict(_self, dict_to_show):
        st.session_state["dropping_options"] = dict_to_show
        return st.session_state["dropping_options"]

    @st.cache_data
    def _create_default_dropping_dict(_self, d):
        return d

    def show(self):
        # # Default values:
        default_rule_length = 3
        default_min_support = 0.0001
        default_lift = 1.0
        default_confidence = 0.95
        default_filtering_string = FiltererEnum.Z_SCORE
        default_binning_option = {}
        default_dropping_options = {}

        preview_default_to_show = self._create_default_dropping_dict(default_dropping_options)
        if "dropping_options" in st.session_state:
            preview_total_to_show = self._create_total_dropping_dict(
                st.session_state["dropping_options"])
        else:
            preview_total_to_show = self._create_total_dropping_dict({})
        if "binning_option" in st.session_state:
            preview_total_to_show_binning = self._create_total_binning_dict(
                st.session_state["binning_option"])
        else:
            preview_total_to_show_binning = self._create_total_binning_dict({})
        # # END DEFAULTS

        st.write("")
        chosen_tab = stx.tab_bar(data=[
            stx.TabBarItemData(id=1, title="Algoritme", description=""),
            stx.TabBarItemData(id=2, title="Dropping", description=""),
            stx.TabBarItemData(id=3, title="Binning", description=""),
            ], default=1)

        # Algoritme
        if chosen_tab == "1":
            st.session_state["rule_length"] = st.number_input(
                'Rule length:',
                value=default_rule_length,
                format="%d",
                key="rule_length")
            st.session_state["min_support"] = st.slider(
                'Minimum support',
                min_value=0.0,
                max_value=1.0,
                step=0.0001,
                value=default_min_support,
                key="min_support")
            st.session_state["lift"] = st.slider(
                'Minimum lift',
                min_value=0.0,
                max_value=10.0,
                value=default_lift,
                key="lift")
            st.session_state["confidence"] = st.slider(
                'Minimum confidence',
                min_value=0.0,
                max_value=1.0,
                value=default_confidence,
                key="confidence")
            st.session_state["filtering_string"] = st.selectbox(
                'Filtering Type:',
                [e.value for e in FiltererEnum],
                index=[e.value for e in FiltererEnum].index(default_filtering_string),
                key="filtering_string")

        # Dropping
        if chosen_tab == "2":
            colA, colB, _, colC = st.columns([3, 4, 1, 8])
            with colB:
                v = st.selectbox('Default condition', [e.value for e in DroppingEnum])
                w = st.text_input("Value")

                colA_1, colB_1 = st.columns(2)
                with colA_1:
                    button = st.button("Add/Change default condition")
                    if button:
                        if v and w:
                            preview_default_to_show[v] = w
                with colB_1:
                    button2 = st.button("Remove default condition")
                    if button2:
                        if v:
                            del preview_default_to_show[v]

            with colC:
                st.subheader("Column-specific Dropping Options:")

                kolom_specific = None
                col1, col2, col3 = st.columns(3)
                with col1:
                    kolom_specific = st.selectbox(
                        'Column:',
                        [e for e in st.session_state[VarEnum.sb_LOADED_DATAFRAME.value].columns])
                with col2:
                    vw_specific = st.selectbox(
                        'Condition:',
                        [e.value for e in DroppingEnum])
                with col3:
                    value_specific = st.text_input("Value")

                colC_1, colC_2, _ = st.columns([4, 4, 14])
                with colC_1:
                    buttonC_1 = st.button("Add condition")
                    if buttonC_1:
                        if kolom_specific and vw_specific and value_specific:
                            if kolom_specific not in preview_total_to_show:
                                preview_total_to_show[kolom_specific] = {}
                            preview_total_to_show[kolom_specific][vw_specific] = value_specific
                with colC_2:
                    buttonC_2 = st.button("Remove Condition")
                    if buttonC_2:
                        if vw_specific and kolom_specific:
                            del preview_total_to_show[kolom_specific][vw_specific]

            with colA:
                st.subheader("Default Dropping Options:")
                st.write(preview_default_to_show)

                use_default = st.checkbox(
                    'Use the default dropping options',
                    value=True)
                temp_dict = {key: preview_default_to_show.copy()
                             for key in st.session_state[VarEnum.sb_LOADED_DATAFRAME.value].columns}
                if use_default:
                    if preview_total_to_show is None:
                        preview_total_to_show = self._create_total_dropping_dict({})

                    for k, v in temp_dict.items():
                        for v1, v2 in v.items():
                            if k not in preview_total_to_show:
                                preview_total_to_show[k] = {}
                            if v1 not in preview_total_to_show:
                                preview_total_to_show[k][v1] = {}
                            preview_total_to_show[k][v1] = v2

                else:
                    # Nu opnieuw de values uit temp_dict eruit gooien
                    for k, v in temp_dict.items():
                        for v1, v2 in v.items():
                            if k not in preview_total_to_show:
                                preview_total_to_show[k] = {}
                            preview_total_to_show[k].pop(v1, None)

            st.subheader("Options that will be applied:")
            st.write(preview_total_to_show)

        if chosen_tab == "3":

            colA_binning, colB_binning = st.columns(2)
            with colA_binning:
                st.subheader("Default Binning Option:")

                default_binning_option = st.selectbox(
                    'Binning methode:',
                    [e.value for e in BinningEnum], key="kolom_default_binning")                    
                use_default_binning = st.checkbox(
                    'Use the default binning options',
                    value=False,
                    key="checkbox_default_binning")
                temp_dict_binning = {key: default_binning_option
                                     for key in st.session_state[VarEnum.sb_LOADED_DATAFRAME.value].columns}

                if use_default_binning:
                    for k, v in temp_dict_binning.items():
                        preview_total_to_show_binning[k] = v
                else:
                    for k, v in temp_dict_binning.items():
                        if k in preview_total_to_show_binning:
                            del preview_total_to_show_binning[k]

            with colB_binning:
                st.subheader("Column-specific Binning Options:")
                kolom_specific_binnig = None
                col1, col2, col3 = st.columns(3)
                with col1:
                    kolom_specific_binnig = st.selectbox(
                        'Column:',
                        [e for e in st.session_state[VarEnum.sb_LOADED_DATAFRAME.value].columns],
                        key="Kolom_Binning")
                with col2:
                    specific_binnig = st.selectbox(
                        'Binning methode:',
                        [e.value for e in BinningEnum])

                colC_1_binning, colC_2_binning, _ = st.columns([4, 4, 14])
                with colC_1_binning:
                    buttonC_1_binning = st.button("Add Binning")
                    if buttonC_1_binning:
                        preview_total_to_show_binning[kolom_specific_binnig] = specific_binnig
                with colC_2_binning:
                    buttonC_2_binning = st.button("Remove Binning")
                    if buttonC_2_binning:
                        if k in preview_total_to_show_binning:
                            del preview_total_to_show_binning[kolom_specific_binnig]

            st.subheader("Options that will be applied:")
            st.write(preview_total_to_show_binning)
