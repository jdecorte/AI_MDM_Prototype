import streamlit as st
import pandas as pd
from st_aggrid import GridOptionsBuilder, AgGrid, GridUpdateMode, DataReturnMode, JsCode

class DeDupeClusterRedirectPage:
    def __init__(self, canvas, handler) -> None:
        self.canvas = canvas
        self.handler = handler

    def redirect_get_clusters(self):
        st.session_state['clusters'] = self.handler.dedupe_get_clusters()

        if st.session_state['clusters'] == {}:
            st.error('Er konden geen clusters worden gevormd op basis van de meegegeven labels', icon="🚨")

        st.session_state['currentState'] = "ViewClusters"
        st.experimental_rerun()



class DeDupeClusterPage:

    def __init__(self, canvas, handler) -> None:
        self.canvas = canvas
        self.handler = handler

    def show(self): 
        MIN_HEIGHT = 50
        MAX_HEIGHT = 500
        ROW_HEIGHT = 35
        with self.canvas.container(): 
            st.title("DeDupe")
            tmp = 
            cluster_view_dict = {}
            for k,v in tmp.items():
                if not v["Cluster ID"] in cluster_view_dict:
                        cluster_view_dict[v["Cluster ID"]] = []
                cluster_view_dict[v["Cluster ID"]] = cluster_view_dict[v["Cluster ID"]] + [{"record_id": k, "record_confidence" : v["confidence_score"]}]


            list_of_cluster_view = []
            for k,v in cluster_view_dict.items():
                if len(v) > 1:
                    tmpList = []
                    accumulated_confidence = 0
                    for e in v:
                        tmpList.append(e["record_id"])
                        accumulated_confidence = accumulated_confidence + float(e["record_confidence"])
                    
                    list_of_cluster_view.append(ClusterView(k,accumulated_confidence/len(v),st.session_state["dataframe"].iloc[tmpList]))


            sort_clusters = st.selectbox(
                'Sorteer clusters op:',
                ('Aantal records in cluster', 'Cluster confidence score'))

            if sort_clusters == 'Cluster confidence score':
            # Sort list op confidence
            # list_of_cluster_view = sorted(list_of_cluster_view, key=lambda x: x.cluster_confidence, reverse=True)
                list_of_cluster_view = sorted(list_of_cluster_view, key=lambda x: x.cluster_confidence, reverse=True)

            # Als test toon de eerste 5 elementen
            for idx, cv in enumerate(list_of_cluster_view[0:4]):
                st.subheader(f'Cluster #{cv.cluster_id}')
                st.write(f"Met een confidence van: {cv.cluster_confidence}")
                # AGGRID die niet editeerbaar is maar wel met select knopjes
                gb1 = GridOptionsBuilder.from_dataframe(cv.records_df)
                gb1.configure_side_bar()
                # gb1.configure_selection('multiple',use_checkbox=True, groupSelectsChildren=True, groupSelectsFiltered=True, pre_selected_rows= list(range(0,len(cv.records_df))))
                gb1.configure_selection('multiple',use_checkbox=True, groupSelectsChildren=True, groupSelectsFiltered=True, pre_selected_rows= [0,1])
                gb1.configure_default_column(groupable=False, value=True, enableRowGroup=True, aggFunc="sum", editable=False)
                gridOptions = gb1.build()
                _ = AgGrid(cv.records_df, gridOptions=gridOptions, enable_enterprise_modules=False, update_mode="selection_changed", height=min(MIN_HEIGHT + len(cv.records_df) * ROW_HEIGHT, MAX_HEIGHT))

                st.write("Verander naar")

                colA, colB = st.columns([5,1])
                with colA:
                    # AGGRID die wel editeerbaar is, met als suggestie de eerste van de selected_rows van hierboven
                    gb2 = GridOptionsBuilder.from_dataframe(cv.records_df.head(1))
                    gb2.configure_side_bar()
                    gb2.configure_default_column(groupable=False, value=True, enableRowGroup=True, aggFunc="sum", editable=True)
                    gridOptions = gb2.build()
                    _ = AgGrid(cv.records_df.head(1), gridOptions=gridOptions, enable_enterprise_modules=False, height=min(MIN_HEIGHT + ROW_HEIGHT, MAX_HEIGHT))

                with colB:
                    # checkbox om te mergen, default actief
                    _ = st.checkbox('Voeg samen',value=True, key=f'merge_{idx}')
                    


class ClusterView:
    def __init__(self, cluster_id, cluster_confidence, records_df) -> None:
        self.cluster_id = cluster_id
        self.cluster_confidence = cluster_confidence
        self.records_df = records_df
