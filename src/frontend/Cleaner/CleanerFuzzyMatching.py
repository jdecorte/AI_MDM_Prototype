import streamlit as st
import config as cfg


class CleanerFuzzyMatchingRedirectPage:

    def __init__(self, canvas, handler) -> None:
        self.canvas = canvas
        self.handler = handler

    def redirect_get_clusters(self):
        st.session_state['fuzzy_clusters'] = self.handler.dedupe_get_clusters()

        if st.session_state['fuzzy_clusters'] == {}:
            st.error('There are no values to be found that are similar to each other', icon="🚨")

        cluster_view_dict = {}
        for k, v in st.session_state['fuzzy_clusters'].items():
            if not v["Cluster ID"] in cluster_view_dict:
                cluster_view_dict[v["Cluster ID"]] = []
            cluster_view_dict[v["Cluster ID"]] = (cluster_view_dict[v["Cluster ID"]] +
                                                  [{"record_id": k,
                                                    "record_confidence": v["confidence_score"]}])

        list_of_cluster_view = []
        for k, v in cluster_view_dict.items():
            if len(v) > 1:
                tmpList = []
                accumulated_confidence = 0
                for e in v:
                    tmpList.append(e["record_id"])
                    accumulated_confidence += float(e["record_confidence"])

                records = st.session_state["dataframe"].iloc[tmpList]
                list_of_cluster_view.append(
                    FuzzyClusterView(k, accumulated_confidence/len(v),
                                     records, records.head(1)))

        st.session_state['list_of_cluster_view'] = list_of_cluster_view

        st.session_state['currentState'] = "ViewClusters"
        st.experimental_rerun()


class FuzzyClusterView:

    def __init__(self, cluster_id, list_of_values, column_as_series) -> None:
        cfg.logger.debug(f"FuzzyClusterView: __init__: cluster_id = {cluster_id}," +
                         f"list_of_values = {list_of_values}, " +
                         f"column_as_series = {column_as_series}")
        self.cluster_id = cluster_id
        # check how many values in column_as_series are in list_of_values
        # transform list_of_values to dataframe with index as separate column
        self.distinct_values_in_cluster = column_as_series[
            column_as_series.isin(list_of_values)].value_counts().\
            reset_index(name='count').rename(columns={'index': 'values'})
        self.merge = False
        # take max value of distinct_values_in_cluster
        self.new_cell_value = self.distinct_values_in_cluster.values[0][0]

    def set_new_cell_value(self, new_cell_value):
        self.new_cell_value = new_cell_value
