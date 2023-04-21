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

        cluster_view_dict = {}
        for k,v in st.session_state['clusters'].items():
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
                
                records = st.session_state["dataframe"].iloc[tmpList]
                list_of_cluster_view.append(DedupeClusterView(k,accumulated_confidence/len(v),records, records.head(1)))
        
        st.session_state['list_of_cluster_view'] = list_of_cluster_view

        st.session_state['currentState'] = "ViewClusters"
        st.experimental_rerun()


class ZinggClusterRedirectPage:
    def __init__(self, canvas, handler) -> None:
        self.canvas = canvas
        self.handler = handler

    def redirect_get_clusters(self):
        st.session_state['zingg_clusters_df'] = pd.DataFrame(self.handler.zingg_get_clusters())
        tmp = st.session_state['zingg_clusters_df']
        # value_counts of values in cluster_id kolom and keep the cluster°id where there are more than 2 records
        cluster_ids = st.session_state['zingg_clusters_df']['z_cluster'].value_counts()[st.session_state['zingg_clusters_df']['z_cluster'].value_counts() >= 2].index.tolist()

        # for each cluster_id, get the records and create a ClusterView
        list_of_cluster_view = []
        for cluster_id in cluster_ids:
            records_df = st.session_state['zingg_clusters_df'][st.session_state['zingg_clusters_df']['z_cluster'] == cluster_id]

            cluster_low = records_df['z_minScore'].min()
            cluster_high = records_df['z_maxScore'].max()

            # cluster confidence is the average of the z_lower and z_higher values in the column
            cluster_confidence  = (records_df['z_minScore'].mean() + records_df['z_maxScore'].mean()) / 2

            # new_row is the row that with the highest 'cluster_high' value
            new_row = records_df[records_df['z_minScore'] == records_df['z_minScore'].max()][:1]
            
            list_of_cluster_view.append(ZinggClusterView(cluster_id, cluster_confidence, records_df.drop(['z_minScore', 'z_maxScore', 'z_cluster'], axis=1), new_row, cluster_low, cluster_high))

        st.session_state['list_of_cluster_view'] = list_of_cluster_view

        st.session_state['currentState'] = "Zingg_ViewClusters"
        st.experimental_rerun()

class ZinggClusterPage:
    def __init__(self, canvas, handler) -> None:
        self.canvas = canvas
        self.handler = handler
        
    def _createPaginering(self, key, colstoUse, N):
        # A variable to keep track of which product we are currently displaying
        if key not in st.session_state:
            st.session_state[key] = 0
        
        last_page = len(colstoUse) // N

        # Add a next button and a previous button
        prev, _, tussen, _ ,next = st.columns([2,1,2,1,2])

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

    def show(self): 
        with self.canvas.container(): 
            st.title("Gevonden Clusters")
            col0, col1 = st.columns([6,2])
            with col0:
                sort_clusters = st.selectbox(
                'Sorteer clusters op:',
                ('Aantal records in cluster', 'Cluster confidence score', 'Lowest cluster Similairty', 'Highest cluster Similairty'))
                if sort_clusters == 'Cluster confidence score':
                    st.session_state["list_of_cluster_view"] = sorted(st.session_state["list_of_cluster_view"], key=lambda x: x.cluster_confidence, reverse=True)
                if sort_clusters == 'Aantal records in cluster':
                    st.session_state["list_of_cluster_view"] = sorted(st.session_state["list_of_cluster_view"], key=lambda x: len(x.records_df), reverse=True)
                if sort_clusters == 'Lowest cluster Similairty':
                    st.session_state["list_of_cluster_view"] = sorted(st.session_state["list_of_cluster_view"], key=lambda x: x.cluster_low, reverse=False)
                if sort_clusters == 'Highest cluster Similairty':
                    st.session_state["list_of_cluster_view"] = sorted(st.session_state["list_of_cluster_view"], key=lambda x: x.cluster_high, reverse=True)

            for cv in st.session_state["list_of_cluster_view"]:
                if f'merge_{cv.cluster_id}' not in st.session_state:
                    st.session_state[f'merge_{cv.cluster_id}'] = True
                if f'dedup_{cv.cluster_id}' not in st.session_state:
                    st.session_state[f'dedup_{cv.cluster_id}'] = False

            with col1:
                st.write("")
                st.write("")
                confirm_cluster = st.button("Bevestig clusters")

            # Als test toon de eerste 5 elementen
            sub_rowstoUse = self. _createPaginering("page_number_Dedupe", st.session_state["list_of_cluster_view"], 5)

            # give css to div where all cluster cards are located
            container_for_cards = st.container()
            with container_for_cards:
                self._give_custom_css_to_container()
                for idx, cv in enumerate(sub_rowstoUse):
                    self._create_cluster_card(idx, cv)

            if confirm_cluster:
                self._merge_clusters(st.session_state["list_of_cluster_view"])
        self._clear_js_containers()
                
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
        
        cont_card = st.container()
        with cont_card:
            _ = st.checkbox('Pas deze wijzingen toe!',value=True, key=f'merge_{cv.cluster_id}')
            col0, col1, col2 = st.columns([1,1,1])
            with col0:
                st.write(f"Confidence van deze cluster: {cv.cluster_confidence}")
            with col1:
                st.write(f"Laagste similarity in deze cluster: {cv.cluster_low}")
            
            with col2:
                st.write(f"Hoogste similarity in deze cluster: {cv.cluster_high}")
                 
            gb1 = GridOptionsBuilder.from_dataframe(cv.records_df)
            gb1.configure_side_bar()
                    # gb1.configure_selection('multiple',use_checkbox=True, groupSelectsChildren=True, groupSelectsFiltered=True, pre_selected_rows= list(range(0,len(cv.records_df))))
            gb1.configure_selection('multiple',use_checkbox=True, groupSelectsChildren=True, groupSelectsFiltered=True, pre_selected_rows= [0,1])
            gb1.configure_default_column(groupable=False, value=True, enableRowGroup=True, aggFunc="sum", editable=False)
            gridOptions = gb1.build()
            _ = AgGrid(cv.records_df, gridOptions=gridOptions, enable_enterprise_modules=False, update_mode="VALUE_CHANGED", height=min(MIN_HEIGHT + len(cv.records_df) * ROW_HEIGHT, MAX_HEIGHT))
            
            dedupe_rows = st.radio('Geselecteerde records worden... ',('behouden maar aangepast naar de volgende waarden:', 'verwijderd en vervangen door één record:'), key=f'dedup_{cv.cluster_id}', horizontal = True)

            # AGGRID die wel editeerbaar is, met als suggestie de eerste van de selected_rows van hierboven
            gb2 = GridOptionsBuilder.from_dataframe(cv.records_df.head(1))
            gb2.configure_side_bar()
            gb2.configure_default_column(groupable=False, value=True, enableRowGroup=True, aggFunc="sum", editable=True)
            gridOptions = gb2.build()
            grid = AgGrid(cv.new_row, gridOptions=gridOptions, enable_enterprise_modules=False, height=min(MIN_HEIGHT + ROW_HEIGHT, MAX_HEIGHT))
            cv.set_new_row(grid["data"])

            customSpan = rf"""
            <span id="duplicateCardsFinder{idx}">
            </span>
            """
            st.markdown(customSpan,unsafe_allow_html=True)
            js = f'''<script>
            containerElement = window.parent.document.getElementById("duplicateCardsFinder{idx}").parentElement.parentElement.parentElement.parentElement.parentElement
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

class ClusterPage:

    def __init__(self, canvas, handler) -> None:
        self.canvas = canvas
        self.handler = handler
        
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

    def show(self): 
        with self.canvas.container(): 
            st.title("Gevonden Clusters")

            sort_clusters = st.selectbox(
            'Sorteer clusters op:',
            ('Aantal records in cluster', 'Cluster confidence score'))
            if sort_clusters == 'Cluster confidence score':
                st.session_state["list_of_cluster_view"] = sorted(st.session_state["list_of_cluster_view"], key=lambda x: x.cluster_confidence, reverse=True)
            if sort_clusters == 'Aantal records in cluster':
                st.session_state["list_of_cluster_view"] = sorted(st.session_state["list_of_cluster_view"], key=lambda x: len(x.records_df), reverse=True)

            for cv in st.session_state["list_of_cluster_view"]:
                if f'merge_{cv.cluster_id}' not in st.session_state:
                    st.session_state[f'merge_{cv.cluster_id}'] = True

            # Als test toon de eerste 5 elementen
            sub_rowstoUse = self. _createPaginering("page_number_Dedupe", st.session_state["list_of_cluster_view"], 5)
            for idx, cv in enumerate(sub_rowstoUse):
                self._create_cluster_card(idx, cv)

            if st.button("Bevestig clusters"):
                self._merge_clusters(st.session_state["list_of_cluster_view"])
                
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
        st.write(f"Met een confidence van: {cv.cluster_confidence}")
                # AGGRID die niet editeerbaar is maar wel met select knopjes
        gb1 = GridOptionsBuilder.from_dataframe(cv.records_df)
        gb1.configure_side_bar()
                # gb1.configure_selection('multiple',use_checkbox=True, groupSelectsChildren=True, groupSelectsFiltered=True, pre_selected_rows= list(range(0,len(cv.records_df))))
        gb1.configure_selection('multiple',use_checkbox=True, groupSelectsChildren=True, groupSelectsFiltered=True, pre_selected_rows= [0,1])
        gb1.configure_default_column(groupable=False, value=True, enableRowGroup=True, aggFunc="sum", editable=False)
        gridOptions = gb1.build()
        _ = AgGrid(cv.records_df, gridOptions=gridOptions, enable_enterprise_modules=False, update_mode="VALUE_CHANGED", height=min(MIN_HEIGHT + len(cv.records_df) * ROW_HEIGHT, MAX_HEIGHT))
        
        st.write("Verander naar")

        colA, colB = st.columns([5,1])
        with colA:
            # AGGRID die wel editeerbaar is, met als suggestie de eerste van de selected_rows van hierboven
            gb2 = GridOptionsBuilder.from_dataframe(cv.records_df.head(1))
            gb2.configure_side_bar()
            gb2.configure_default_column(groupable=False, value=True, enableRowGroup=True, aggFunc="sum", editable=True)
            gridOptions = gb2.build()
            grid = AgGrid(cv.new_row, gridOptions=gridOptions, enable_enterprise_modules=False, height=min(MIN_HEIGHT + ROW_HEIGHT, MAX_HEIGHT))
            cv.set_new_row(grid["data"])

        with colB:
            # checkbox om te mergen, default actief
            _ = st.checkbox('Voeg samen',value=True, key=f'merge_{cv.cluster_id}')
                    
class DedupeClusterView:
    def __init__(self, cluster_id, cluster_confidence, records_df, new_row) -> None:
        self.cluster_id = cluster_id
        self.cluster_confidence = cluster_confidence
        self.records_df = records_df
        self.set_new_row(new_row)

    def set_new_row(self, new_row):
        self.new_row = new_row


class ZinggClusterView:
    def __init__(self, cluster_id, cluster_confidence, records_df, new_row, cluster_low, cluster_high) -> None:
        self.cluster_id = cluster_id
        self.cluster_confidence = round(cluster_confidence, 4)
        self.records_df = records_df
        self.cluster_low = round(cluster_low, 4)
        self.cluster_high = round(cluster_high, 4)
        self.set_new_row(new_row)

    def set_new_row(self, new_row):
        self.new_row = new_row
        
