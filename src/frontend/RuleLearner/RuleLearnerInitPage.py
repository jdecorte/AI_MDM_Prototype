import streamlit as st
import pandas as pd
from st_aggrid import GridOptionsBuilder, AgGrid, GridUpdateMode, DataReturnMode, JsCode
from src.frontend.Handler.IHandler import IHandler

from src.shared.Enums.FiltererEnum import FiltererEnum
from src.shared.Enums.BinningEnum import BinningEnum
from src.shared.Enums.DroppingEnum import DroppingEnum

from src.shared.Configs.RuleFindingConfig import RuleFindingConfig
from src.shared.Views.ColumnRuleView import ColumnRuleView

class RuleLearnerInitPage:
    def __init__(self, canvas, handler: IHandler) -> None:
        self.canvas = canvas
        self.handler = handler

    @st.experimental_singleton()
    def _create_total_binning_dict(_self, dict_to_show):
        return dict_to_show

    @st.experimental_singleton()
    def _create_total_dropping_dict(_self, dict_to_show):
        return dict_to_show

    @st.experimental_singleton()
    def _create_default_dropping_dict(_self, d):
        return d

    def show(self): 
        with self.canvas.container(): 
            st.title("Rule Learning")
            st.markdown(f"<h4>Ingeladen Dataset: </h4>", unsafe_allow_html=True)

            # Toon de dataframe -> NIET EDITEERBAAR
            gb = GridOptionsBuilder.from_dataframe(st.session_state["dataframe"])
            gb.configure_side_bar()
            gb.configure_default_column(groupable=True, value=True, enableRowGroup=True, aggFunc="sum", editable=False)
            gridOptions = gb.build()
            grid_response = AgGrid(st.session_state["dataframe"], gridOptions=gridOptions, enable_enterprise_modules=True)


            # Toon de form om de RuleFindingConfig file te gebruiken
                
            # Default values:
            default_rule_length = 3
            default_min_support = 0.0001
            default_lift = 1.0
            default_confidence = 0.95
            default_filtering_string = FiltererEnum.Z_SCORE
            default_binning_option = BinningEnum.K_MEANS
            # default_dropping_options = {DroppingEnum.DROP_NAN: str(False), DroppingEnum.DROP_WITH_UPPER_BOUND:str(50)}
            default_dropping_options = {}


            st.header("Opties:")
            tab1, tab2, tab3 = st.tabs(["Algoritme", "Dropping", "Binning"])
            # Algoritme
            with tab1:
                form_rule_length = st.number_input('Rule length:', value=default_rule_length, format="%d")
                form_min_support = st.slider('Minimum support', min_value=0.0, max_value=1.0, step=0.0001, value=default_min_support )
                form_lift = st.slider('Minimum lift', 0.0, 10.0, default_lift)
                form_confidence = st.slider('Minimum confidence', 0.0, 1.0, default_confidence)
                form_filtering_string = st.selectbox('Filtering Type:', [e.value for e in FiltererEnum] , index=[e.value for e in FiltererEnum].index(default_filtering_string))

            # Dropping
            with tab2:
                colA, colB,_, colC = st.columns([3,4,1,8])

                preview_default_to_show = self._create_default_dropping_dict(default_dropping_options)
                preview_total_to_show = self._create_total_dropping_dict({})
                
            
                with colB:
                    v = st.selectbox('Default Voorwaarde:', [e.value for e in DroppingEnum] )
                    w = st.text_input("Waarde") 

                    colA_1, colB_1 = st.columns(2)
                    with colA_1:
                        button = st.button("Add/Change Default Voorwaarde")
                        if button:
                            if v and w:
                                preview_default_to_show[v] = w
                    with colB_1:
                        button2 = st.button("Remove Default Voorwaarde")
                        if button2:
                            if v:
                                del preview_default_to_show[v]

                with colC:
                    st.subheader("Kolomspecifieke Dropping Options:")
                    
                    kolom_specific= None
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        kolom_specific = st.selectbox('Kolom:', [e for e in st.session_state["dataframe"].columns] )
                    with col2:
                        vw_specific = st.selectbox('Voorwaarde:', [e.value for e in DroppingEnum] )
                    with col3:
                        value_specific = st.text_input("Value")


                    colC_1, colC_2,_ = st.columns([4,4,14])
                    with colC_1:
                        buttonC_1 = st.button("Add Voorwaarde")
                        if buttonC_1:
                            if kolom_specific and vw_specific and value_specific:
                                if kolom_specific not in preview_total_to_show:
                                    preview_total_to_show[kolom_specific] = {}
                                preview_total_to_show[kolom_specific][vw_specific] = value_specific
                    with colC_2:
                        buttonC_2 = st.button("Remove Voorwaarde")
                        if buttonC_2:
                            if vw_specific and kolom_specific:
                                del preview_total_to_show[kolom_specific][vw_specific]    

                with colA:
                    st.subheader("Default Dropping Options:")                    
                    st.write(preview_default_to_show)

                    use_default = st.checkbox('Maak gebruik van default voorwaarden', value=True)
                    temp_dict = {key: preview_default_to_show.copy() for key in st.session_state["dataframe"].columns}
                    if use_default:
                        if preview_total_to_show is None:
                            preview_total_to_show = self._create_total_dropping_dict({})
                        
                        
                        for k,v in temp_dict.items():
                            for v1, v2 in v.items():
                                if k not in preview_total_to_show:
                                    preview_total_to_show[k] = {}
                                if v1 not in preview_total_to_show:
                                    preview_total_to_show[k][v1] = {}
                                preview_total_to_show[k][v1] = v2
                        
                    else:
                        # Nu opnieuw de values uit temp_dict eruit gooien
                        for k,v in temp_dict.items():
                            for v1,v2 in v.items():
                                if k not in preview_total_to_show:
                                    preview_total_to_show[k] = {}
                                preview_total_to_show[k].pop(v1, None)                        

                st.subheader("Opties die zullen worden toegepast:")
                st.write(preview_total_to_show)

            # Binning TODO
            with tab3:

                colA_binning, colB_binning = st.columns(2)
                preview_total_to_show_binning = self._create_total_binning_dict({})

                with colA_binning:
                    st.subheader("Default Binning Option:")
                    
                    default_binning_option = st.selectbox('Binning methode:', [e.value for e in BinningEnum], key="kolom_default_binning")                    
                    use_default_binning = st.checkbox('Maak gebruik van default voorwaarden', value=False, key="checkbox_default_binning")
                    temp_dict_binning = {key: default_binning_option for key in st.session_state["dataframe"].columns}


                    if use_default_binning:
                        for k,v in temp_dict_binning.items():
                            preview_total_to_show_binning[k] = v
                        
                    else:
                        for k,v in temp_dict_binning.items():
                            if k in preview_total_to_show_binning:
                                del preview_total_to_show_binning[k]

                with colB_binning:
                    st.subheader("Kolomspecifieke Binning Options:")
                    kolom_specific_binnig= None
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        kolom_specific_binnig = st.selectbox('Kolom:', [e for e in st.session_state["dataframe"].columns], key="Kolom_Binning")
                    with col2:
                        specific_binnig = st.selectbox('Binning methode:', [e.value for e in BinningEnum] )
                    
                    colC_1_binning, colC_2_binning,_ = st.columns([4,4,14])
                    with colC_1_binning:
                        buttonC_1_binning = st.button("Add Binning")
                        if buttonC_1_binning:
                            preview_total_to_show_binning[kolom_specific_binnig] = specific_binnig
                    with colC_2_binning:
                        buttonC_2_binning = st.button("Remove Binning")
                        if buttonC_2_binning:
                            if k in preview_total_to_show_binning:
                                del preview_total_to_show_binning[kolom_specific_binnig]

                st.subheader("Opties die zullen worden toegepast:")
                st.write(preview_total_to_show_binning)
                        
        submitted = st.button("Analyseer Data")
        if submitted:
            # Maak RuleFindingConfig aan om die dan om te vormen tot JSON en door te geven aan de (Remote)Handler.
            # Plaat vervolgens de status naar 'BekijkRegels' in de session_state

            binning_dict = {key:default_binning_option for key in st.session_state["dataframe"].columns}
            rule_finding_config = RuleFindingConfig(
                rule_length=form_rule_length, 
                min_support=form_min_support,
                lift=form_lift, 
                confidence=form_confidence,
                filtering_string=form_filtering_string,
                dropping_options=preview_total_to_show,
                binning_option=binning_dict
                )

            json_rule_finding_config = rule_finding_config.to_json()
            found_rules = self.handler.get_column_rules(dataframe_in_json=st.session_state["dataframe"].to_json(),rule_finding_config_in_json=json_rule_finding_config)
            st.session_state['gevonden_rules_dict'] = found_rules
            st.session_state["currentState"] = "BekijkRules"
            st.experimental_rerun()

