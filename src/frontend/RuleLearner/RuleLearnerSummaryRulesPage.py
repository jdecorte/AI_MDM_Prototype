from cgitb import handler
import numpy as np
import pandas as pd
import streamlit as st
from st_aggrid import GridOptionsBuilder, AgGrid, GridUpdateMode, DataReturnMode, JsCode
from streamlit.components.v1 import html
from src.frontend.Handler.IHandler import IHandler

class RuleLearnerSummaryRulesPage:
    def __init__(self, canvas, handler: IHandler) -> None:
        self.canvas = canvas
        self.handler = handler

    def show(self): 

        with self.canvas.container():

            st.write(st.session_state["gevonden_rules_dict"])
            
            st.title("Rule Learning")
            st.header("Gevonden Regels:")

            col_t1, col_t2 = st.columns([2,3])

            with col_t1:
                # Stukje voor de selectionFinder
                st.subheader("Kies regels om te gebruiken voor suggesties:")
                pre_selected = []
                df_of_column_rules_for_suggestion_finder = pd.DataFrame({"Regel": st.session_state["gevonden_rules_dict"].keys(), "Confidence":[x.confidence for x in st.session_state["gevonden_rules_dict"].values()]})

                gb1 = GridOptionsBuilder.from_dataframe(df_of_column_rules_for_suggestion_finder)
                gb1.configure_grid_options(fit_columns_on_grid_load=True)
                gb1.configure_selection('multiple', pre_selected_rows=pre_selected, use_checkbox=True, groupSelectsChildren=True, groupSelectsFiltered=True)
                response_selection_suggestion_finder = AgGrid(
                    df_of_column_rules_for_suggestion_finder,
                    height= 150,
                    editable=False,
                    gridOptions=gb1.build(),
                    data_return_mode="filtered_and_sorted",
                    update_mode="no_update",
                    fit_columns_on_grid_load=True,
                    theme="streamlit",
                    enable_enterprise_modules = False
                )
                # st.write(response_selection_suggestion_finder)


                find_suggestions_btn =  st.button('Geef Suggesties')
                if find_suggestions_btn:
                    st.write('Why hello there')


                st.subheader("Download de gevonden regels:")
                st.download_button(
                    label="Sla Regels op",
                    data=st.session_state["dataframe"].to_csv(index=False),
                    file_name='Rule_Learned_Dataset.csv',
                    mime='text/csv',
                )

            with col_t2:
                st.subheader("Meer info over regel:")
                more_info = st.selectbox('Regel:', st.session_state["gevonden_rules_dict"].keys())

                if more_info:
                    st.write("Gevonden Mapping:")
                    cr = st.session_state["gevonden_rules_dict"][more_info]
                    gb2 = GridOptionsBuilder.from_dataframe(cr.value_mapping)
                    gb2.configure_grid_options(fit_columns_on_grid_load=True)
                    more_info_mapping = AgGrid(
                        cr.value_mapping,
                        height= 150,
                        editable=False,
                        gridOptions=gb2.build(),
                        data_return_mode="filtered_and_sorted",
                        update_mode="no_update",
                        fit_columns_on_grid_load=True,
                        theme="streamlit",
                        enable_enterprise_modules = False
                    )

                    st.write("Rijen die niet voldoen aan mapping")
                    gb3 = GridOptionsBuilder.from_dataframe(st.session_state['dataframe'].iloc[cr.idx_to_correct])
                    gb3.configure_grid_options(fit_columns_on_grid_load=True)
                    more_info_mapping = AgGrid(
                        st.session_state['dataframe'].iloc[cr.idx_to_correct],
                        height= 150,
                        editable=False,
                        gridOptions=gb3.build(),
                        data_return_mode="filtered_and_sorted",
                        update_mode="no_update",
                        fit_columns_on_grid_load=True,
                        theme="streamlit",
                        enable_enterprise_modules = False
                    )

            st.header("Kies regels om te gebruiken voor suggesties:")

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
                validate_own_rule = st.button("Valideer eigen regel")

            if validate_own_rule:
                st.session_state["validate_own_rule"] = True
                filtered_cols = ant_set + [con_set]
                rule_string =  ','.join(ant_set) + " => " + con_set
                found_rule = self.handler.get_column_rule_from_string(dataframe_in_json=st.session_state["dataframe"][filtered_cols].to_json(),rule_string=rule_string)

                col_bb1, col_bb2, col_bb3, col_bb4 = st.columns([2,4,2,1])

                with col_bb1:
                    st.write(found_rule.confidence)
                with col_bb2:
                    st.write(found_rule.value_mapping)
                with col_bb3:
                    st.write(found_rule.idx_to_correct)
                with col_bb4:
                    add_own_rule = st.button("Voeg eigen regel toe voor suggesties")
                    st.write(st.session_state["gevonden_rules_dict"])

                if add_own_rule and st.session_state["validate_own_rule"]:
                    st.session_state["validate_own_rule"] = False
                    st.session_state["add_own_rule"] = True
            
            if "add_own_rule" in st.session_state and st.session_state["add_own_rule"]:
                st.session_state["gevonden_rules_dict"][found_rule.rule_string] = found_rule
                    
                

            # st.title("Gevonden Regels:")
            # trgNaarDataset = st.button("<- Terug naar Dataset")
            # if trgNaarDataset:
            #     st.session_state["currentState"] = None
            #     st.experimental_rerun()
            
            # st.write("Filter de regels:")
            # col_t1, col_t2, col_t3, col_t4, col_t5 = st.columns([3,1,2,2,2])

            # with col_t1:
            #     ant_set = st.multiselect(
            #         'Kies de antecedentenset',
            #         st.session_state["dataframe"].columns)

            # with col_t2:
            #     st.subheader(" => ")

            # with col_t3:
            #     con_set = st.selectbox(
            #         'Kies de consequent kolom',
            #         st.session_state["dataframe"].columns)

            # with col_t4:
            #     st.download_button(
            #             label="Sla geselecteerde regels op",
            #             data=st.session_state["dataframe"].to_csv(index=False),
            #             file_name='Rule_Learned_Dataset.csv',
            #             mime='text/csv',
            #         )
            
            # with col_t5:
            #     give_suggestions = st.button("Geef beste suggesties o.b.v. selectie")
            #     if give_suggestions:
            #         st.write("DOE CALL NAAR API, SLA RESPONS OP IN SESSION_STATE EN VERANDER VAN PAGINA")

            
            # st.write(st.session_state["gevonden_rules_dataframe"])



            # --------------
            

            # Tabbladen met de verschillende types van gevonden regels
            # tab1, tab2, tab3 = st.tabs(["Definities", "Volledige Mappings", "Onvolledige Mappings"])
            # with tab1:
            #     st.header("Definities")

            #     if st.session_state['gevonden_rules_dict']["def"]:
            #         for idx, cr in enumerate(st.session_state['gevonden_rules_dict']["def"]):
            #             value_mapping_df = pd.DataFrame(cr.value_mapping)
            #             steedsKloppenRegelsContainer = st.expander(label = cr.rule_string, expanded=False)
            #             with steedsKloppenRegelsContainer:
                            
            #                 col1_1, _, col1_2 = steedsKloppenRegelsContainer.columns([2,1,4])
            #                 col2_1,_,  col2_2 = steedsKloppenRegelsContainer.columns([2,1,4])
            #                 with col1_1:
            #                     st.subheader("Gevonden mapping:")
                            
            #                 with col1_2:
            #                     st.subheader("Rijen waar fouten inzitten:")
            #                 with col2_1:
            #                     gb = GridOptionsBuilder.from_dataframe(value_mapping_df)
            #                     gb.configure_default_column(groupable=True, value=True, enableRowGroup=True, aggFunc="sum", editable=True, key="nietIngevuld")
            #                     gridOptions = gb.build()
            #                     grid_response = AgGrid(value_mapping_df,height= 250, gridOptions=gridOptions,fit_columns_on_grid_load = True, enable_enterprise_modules = False)
            #                     temp = grid_response['data']
            #                 with col2_2:
            #                     st.write("Geen foutieve rijen gevonden")
            #     else:
            #         st.subheader("Er werden geen definities in de dataset teruggevonden.")


            
            # with tab2:
            #     st.header("Regels die voor alle records gelden")
            #     for idx, cr in enumerate(st.session_state['gevonden_rules_dict']["always"]):
            #         value_mapping_df = pd.DataFrame(cr.value_mapping)
            #         steedsKloppenRegelsContainer = st.expander(label = cr.rule_string, expanded=False)
            #         with steedsKloppenRegelsContainer:
                        
            #             col1_1, _, col1_2 = steedsKloppenRegelsContainer.columns([2,1,4])
            #             col2_1,_,  col2_2 = steedsKloppenRegelsContainer.columns([2,1,4])
            #             with col1_1:
            #                 st.subheader("Gevonden mapping:")
                        
            #             with col1_2:
            #                 st.subheader("Rijen waar fouten inzitten:")
            #             with col2_1:
            #                 gb = GridOptionsBuilder.from_dataframe(value_mapping_df)
            #                 gb.configure_grid_options(fit_columns_on_grid_load=True)
            #                 gb.configure_default_column(groupable=True, value=True, enableRowGroup=True, aggFunc="sum", editable=True, key="nietIngevuld")
            #                 gridOptions = gb.build()
            #                 grid_response = AgGrid(value_mapping_df,height= 250, gridOptions=gridOptions,fit_columns_on_grid_load = True, enable_enterprise_modules = False)
            #                 temp = grid_response['data']
            #             with col2_2:
            #                 st.write("Geen foutieve rijen gevonden")


            # with tab3:
            #     st.header("Regels die in meer dan 95% van alle records gelden")
            #     for idx, cr in enumerate(st.session_state['gevonden_rules_dict']["not_always"]):
            #         value_mapping_df = pd.DataFrame(cr.value_mapping)
            #         # Opnieuw maken van df_to_correct op basis van ingeladen dataframe
            #         df_to_correct = st.session_state['dataframe'].iloc[cr.idx_to_correct]
            #         steedsKloppenRegelsContainer = st.expander(label = cr.rule_string, expanded=False)
            #         with steedsKloppenRegelsContainer:
                        
            #             col1_1, _, col1_2 = steedsKloppenRegelsContainer.columns([2,1,4])
            #             col2_1,_,  col2_2 = steedsKloppenRegelsContainer.columns([2,1,4])
            #             with col1_1:
            #                 st.subheader("Gevonden mapping:")
            #                 st.write(f"Geldig voor {float(cr.confidence) * 100 }% van de {len(st.session_state['dataframe'])} records")
                        
            #             with col1_2:
            #                 st.subheader("Rijen waar fouten inzitten:")
            #             with col2_1:
            #                 gb = GridOptionsBuilder.from_dataframe(value_mapping_df)
            #                 gb.configure_grid_options(fit_columns_on_grid_load=True)
            #                 gridOptions = gb.build()
            #                 grid_response = AgGrid(value_mapping_df,height= 250, gridOptions=gridOptions,fit_columns_on_grid_load = True, enable_enterprise_modules = False, key="not_always_vm" + str(idx))
            #                 temp = grid_response['data']
            #             with col2_2:
            #                 gb = GridOptionsBuilder.from_dataframe(df_to_correct)
            #                 gb.configure_grid_options(fit_columns_on_grid_load=True)
            #                 gridOptions = gb.build()
            #                 grid_response = AgGrid(df_to_correct,height= 250, gridOptions=gridOptions,fit_columns_on_grid_load = False, enable_enterprise_modules = False, key="not_always_tc" + str(idx))
            #                 temp = grid_response['data']

           
            
            # st.download_button(
            #     label="Sla Regels op",
            #     data=st.session_state["dataframe"].to_csv(index=False),
            #     file_name='Rule_Learned_Dataset.csv',
            #     mime='text/csv',
            # )


