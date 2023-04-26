import streamlit as st
import pandas as pd
import json
import math

from st_aggrid import GridOptionsBuilder, AgGrid, GridUpdateMode, DataReturnMode, JsCode

class DeDupeRedirectLabelPage:
    def __init__(self, canvas, handler) -> None:
        self.canvas = canvas
        self.handler = handler

    def redirect_get_record_pair(self):
        st.session_state['record_pair'] = self.handler.dedupe_next_pair()
        st.session_state['currentState'] = "LabelRecords"
        st.experimental_rerun()

    def redirect_mark_record_pair(self):
        self.handler.dedupe_mark_pair(st.session_state['marked_record_pair'])
        st.session_state['currentState'] = "LabelRecords_get_record_pair"
        st.experimental_rerun()
        

class DeDupeLabelPage:

    def __init__(self, canvas, handler) -> None:
        self.canvas = canvas
        self.handler = handler

    def streamlit_label(self, ) -> None:  # pragma: no cover
        colBB, colCC, colDD, _, colEE  = st.columns([1,1,1,7,1])
        with colBB:
            duplicate_btn = st.button('Duplicaat')
            if duplicate_btn:
                st.session_state['marked_record_pair'] = (st.session_state['record_pair'], "match")
                st.session_state["currentState"] = "LabelRecords_mark_record_pair"
                st.experimental_rerun()

        with colCC:
            not_duplicate_btn = st.button('Geen duplicaat')
            if not_duplicate_btn:
                st.session_state['marked_record_pair'] = (st.session_state['record_pair'], "distinct")
                st.session_state["currentState"] = "LabelRecords_mark_record_pair"
                st.experimental_rerun()

        with colDD:
            unsure_duplicate_btn = st.button('Onzeker')
            if unsure_duplicate_btn:
                st.session_state['marked_record_pair'] = (st.session_state['record_pair'], "unsure")
                st.session_state["currentState"] = "LabelRecords_mark_record_pair"
                st.experimental_rerun()

        with colEE:
            finish_label_btn = st.button('Ga verder naar clustering')
            if finish_label_btn:
                self.handler.dedupe_train()         
                st.session_state["currentState"] = "ViewClusters_get_clusters" 
                st.experimental_rerun()       

    def show(self): 
        with self.canvas.container(): 
            st.title("DeDupe")
            colA, colB = st.columns([1,5])
            with colA:
                st.write(pd.DataFrame.from_dict(self.handler.dedupe_get_stats(), orient='index'))      
                
            with colB:
                st.markdown("**Hieronder staan ​​twee records die op elkaar lijken en mogelijks duplicaten zijn. Label minimaal 10 records als 'duplicaten' en 10 records als 'niet-duplicaten'**")
                # st.write('See a lot of records that don’t match? You may get better results if select different columns or compare existing columns differently:')
                # st.button('Verander fields')

            fields = st.session_state["dedupe_type_dict"].keys()
            st.table(pd.DataFrame().assign(Field= [f for f in st.session_state['record_pair'][0].keys() if f in fields], Record_1 = [v1 for k1,v1 in st.session_state['record_pair'][0].items() if k1 in fields], Record_2 = [v2 for k2,v2 in st.session_state['record_pair'][1].items() if k2 in fields]))
            self.streamlit_label()

class ZinggLabelPage:
    def __init__(self, canvas, handler) -> None:
        self.canvas = canvas
        self.handler = handler

    def show(self):
        st.header('Zingg Deduplication:')
        stats = st.container()
        if "zingg_current_label_round" not in st.session_state:
            st.session_state["zingg_current_label_round"] = pd.DataFrame(self.handler.zingg_unmarked_pairs())
        if "zingg_stats" not in st.session_state:
            st.session_state["zingg_stats"] = self.handler.zingg_get_stats()

        reponse_error_container = st.empty()

        st.subheader("Pairs to mark:")
        # group by z_cluster and create a new zingg_label_card for each cluster
        container_for_cards = st.container()
        with container_for_cards:
            self._give_custom_css_to_container()
            counter = 0
            for z_cluster_id, z_cluster_df in st.session_state["zingg_current_label_round"].groupby('z_cluster'):
                counter += 1
                self._create_zingg_label_card(z_cluster_df, z_cluster_id, counter)
                st.write("")
                st.write("")

        with stats:
            colB_1, colB_2 = st.columns([1,1])
            with colB_1:
                sum_stats = sum(st.session_state['zingg_stats'].values())
                st.write(f"Previous Round(s): {st.session_state['zingg_stats']['match_files']}/{sum_stats} MATCHES, {st.session_state['zingg_stats']['no_match_files']}/{sum_stats} NON-MATCHES, {st.session_state['zingg_stats']['unsure_files']}/{sum_stats} UNSURE")
                # st.write("Previous Round(s): " + self.handler.zingg_get_stats())
                st.write("Current labeling round: {}/{} MATCHES, {}/{} NON-MATCHES, {}/{} UNSURE".format(
                    len(st.session_state["zingg_current_label_round"][st.session_state["zingg_current_label_round"].z_isMatch == 1])//2,
                    len(st.session_state["zingg_current_label_round"])//2,
                    len(st.session_state["zingg_current_label_round"][st.session_state["zingg_current_label_round"].z_isMatch == 0])//2,
                    len(st.session_state["zingg_current_label_round"])//2,
                    len(st.session_state["zingg_current_label_round"][st.session_state["zingg_current_label_round"].z_isMatch == 2])//2,
                    len(st.session_state["zingg_current_label_round"])//2
                    ))
            with colB_2:
                colB_2_1, colB_2_2, colB_2_3 =st.columns([1,1,1])
                with colB_2_1:
                    st.write("")
                    next = st.button("Update and give new pairs")
                with colB_2_2:
                    st.write("")
                    clear = st.button("Clear all previous labels (Rerun)")
                with colB_2_3:
                    st.write("")
                    finish = st.button("Finish labeling, go to clustering")

        if next:
            _ = self.handler.zingg_mark_pairs(st.session_state["zingg_current_label_round"].to_json())
            _ = self.handler.run_zingg_phase("findTrainingData")
            st.session_state["zingg_current_label_round"] = pd.DataFrame(self.handler.zingg_unmarked_pairs())
            st.session_state['zingg_stats'] = self.handler.zingg_get_stats()
            st.experimental_rerun()

        if clear:
            _ = self.handler.zingg_clear()
            _ = self.handler.run_zingg_phase("findTrainingData")
            st.session_state["zingg_current_label_round"] = pd.DataFrame(self.handler.zingg_unmarked_pairs())
            st.session_state['zingg_stats'] = self.handler.zingg_get_stats()
            st.experimental_rerun()

        if finish:
            # Moet nog een nagegaan worden of model gemaakt is, of er een error is opgetreden door te weinig gelaabelde data => check op bestaan van folder 'model'
            # _ = self.handler.zingg_mark_pairs(st.session_state["zingg_current_label_round"].to_json())
            response = self.handler.run_zingg_phase("train").json()
        
            if response == "200":
                st.session_state["currentState"] = "Zingg_ViewClusters_get_clusters"
                st.experimental_rerun()
            else:
                with reponse_error_container:
                    st.error("The model could not be created. Please label more data and try again.")

        self._clear_js_containers()
        

    def _create_zingg_label_card(self, grouped_df, z_cluster_id, idx):

        MIN_HEIGHT = 40
        MAX_HEIGHT = 500
        ROW_HEIGHT = 40
        
        fields = st.session_state["dedupe_type_dict"].keys()

        cont_card = st.container()
        with cont_card:
            colLeft, colRight = st.columns([3,1])
            with colLeft:
                st.write("#"+str(idx))
                gb1 = GridOptionsBuilder.from_dataframe(grouped_df[[c for c in grouped_df.columns if c in fields]])
                gb1.configure_default_column(groupable=False, value=True, enableRowGroup=True, aggFunc="sum", editable=False)
                gridOptions = gb1.build()
                _ = AgGrid(grouped_df[[c for c in grouped_df.columns if c in fields]], gridOptions=gridOptions, enable_enterprise_modules=False, height=min(MIN_HEIGHT + len(grouped_df[[c for c in grouped_df.columns if c in fields]]) * ROW_HEIGHT, MAX_HEIGHT))

            with colRight: 
                if grouped_df['z_prediction'].mean() > 0:
                    colAA, colBB = st.columns([1,1])
                    with colAA:
                        st.write("Prediction score:", str(format(grouped_df['z_score'].mean() * 100, '.2f') )+ '%')
                    with colBB:
                        st.write(f"Prediction: {'is a match' if (grouped_df['z_prediction'].mean() > 0) else 'is not a match'}")
                else:
                    st.write('')
                    st.write('')
                    st.write('')

                choice = st.selectbox('Choice', ['is a match', 'is not a match', 'unsure'], index=2, key="selectbox_"+z_cluster_id)
                if choice == 'is a match':
                    st.session_state["zingg_current_label_round"].loc[st.session_state["zingg_current_label_round"]['z_cluster'] == z_cluster_id, 'z_isMatch'] = 1
                if choice == 'is not a match':
                    st.session_state["zingg_current_label_round"].loc[st.session_state["zingg_current_label_round"]['z_cluster'] == z_cluster_id, 'z_isMatch'] = 0
                if choice == 'unsure':
                    st.session_state["zingg_current_label_round"].loc[st.session_state["zingg_current_label_round"]['z_cluster'] == z_cluster_id, 'z_isMatch'] = 2

            customSpan = rf"""
                <span id="duplicateCardsFinder{z_cluster_id}">
                </span>
                """
            st.markdown(customSpan,unsafe_allow_html=True)
            js = f'''<script>
            containerElement = window.parent.document.getElementById("duplicateCardsFinder{z_cluster_id}").parentElement.parentElement.parentElement.parentElement.parentElement
            containerElement.setAttribute('class', 'materialcard')
            </script>
            '''
            st.components.v1.html(js)


    def _clear_js_containers(self):
        js = f'''<script>
            iframes = window.parent.document.getElementsByTagName("iframe")
            for (var i=0, max=iframes.length; i < max; i++)
                iframes[i].title == "st.iframe" ? iframes[i].style.display = "none" : iframes[i].style.display = "block";
            </script>
            '''
        st.components.v1.html(js)
    

    def _give_custom_css_to_container(self):
        customSpan = rf"""
        <span id="containerDuplicateCardsFinder">
        </span>
        """
        st.markdown(customSpan,unsafe_allow_html=True)
        js = '''<script>
        containerElement = window.parent.document.getElementById("containerDuplicateCardsFinder").parentElement.parentElement.parentElement.parentElement.parentElement
        containerElement.setAttribute('id', 'containerDuplicateCards')
        </script>
        '''
        st.components.v1.html(js)