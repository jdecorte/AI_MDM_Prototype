import streamlit as st
import pandas as pd
import os
import csv
import re
import logging
import optparse
import io
import json
import pickle
import traceback

import dedupe
import dedupe.blocking as blocking
import dedupe.datamodel as datamodel
import dedupe.labeler as labeler
import dedupe.predicates

from st_aggrid import GridOptionsBuilder, AgGrid, GridUpdateMode, DataReturnMode, JsCode
from src.frontend.RuleLearner.RuleLearnerOptionsSubPage import RuleLearnerOptionsSubPage
from src.frontend.Handler.IHandler import IHandler
from dedupe.canonical import getCanonicalRep
from dedupe.core import unique
from dedupe._typing import (
    Data,
    Literal,
    RecordDict,
    RecordDictPair,
    RecordID,
    TrainingData,
    Tuple, 
)


class DeDupeLabelPage:

    # settings_file = 'csv_example_learned_settings.bin'
    # trainings_file = 'csv_example_learned_training.bin'
    # labelings_file = 'csv_example_given_labeling.json'
    # pickled_file = 'deduper_object.bin'

    def __init__(self, canvas, handler) -> None:
        self.canvas = canvas
        self.handler = handler

    # def _pickle_deduper(self, deduper):
    #     with open(self.pickled_file, 'wb') as f:
    #         pickle.dump(deduper,f)

    def _mark_pair(self,deduper: dedupe.api.ActiveMatching, labeled_pair) -> None:
        print("_mark_pair was called with: " + str(labeled_pair[0]))
        record_pair, label = labeled_pair
        examples: TrainingData = {"distinct": [], "match": []}
        if label == "unsure":
            # See https://github.com/dedupeio/dedupe/issues/984 for reasoning
            examples["match"].append(record_pair)
            examples["distinct"].append(record_pair)
        else:
            # label is either "match" or "distinct"
            examples[label].append(record_pair)
        try:
            deduper.mark_pairs(examples)
        except:
            traceback.print_exc()
        self._pickle_deduper(deduper)

    def _show_labeling_stats(self, deduper):
        n_match = len(deduper.training_pairs["match"]) - st.session_state['number_of_unsure']
        n_distinct = len(deduper.training_pairs["distinct"]) - st.session_state['number_of_unsure']
        n_unsure = st.session_state['number_of_unsure']
        st.write(pd.DataFrame.from_dict({"Yes":f"{n_match}/10", "No":f"{n_distinct}/10", "Unsure":f"{n_unsure}"}, orient='index'))



    def streamlit_label(self, deduper: dedupe.api.ActiveMatching) -> None:  # pragma: no cover
        """
        Train a matcher instance (Dedupe, RecordLink, or Gazetteer) from the command line.
        Example

        .. code:: python

        > deduper = dedupe.Dedupe(variables)
        > deduper.prepare_training(data)
        > dedupe.streamlit_label(deduper)
        """
        
        
        
        st.write(len(st.session_state["deduper_data"]))
        fields = unique(var.field for var in deduper.data_model.primary_variables)
        
        if st.session_state["record_pair"] is None:
            record_pair = deduper.uncertain_pairs().pop()  
            print('Popped uncertain pair: ' + str(record_pair))
        st.write(record_pair)         
        colA, colB = st.columns([5,3])
        with colA:
            st.write("Below are two records that look similar and might be duplicate records. Label at least 10 records as ‘duplicates’ and 10 records as ‘non-duplicates’")
            self._show_labeling_stats(deduper=deduper)
            
        with colB:
            st.write('See a lot of records that don’t match? You may get better results if select different columns or compare existing columns differently:')
            st.button('Verander fields')

        st.table(pd.DataFrame().assign(Field= fields, Record_1 = [v1 for k1,v1 in record_pair[0].items() if k1 in fields], Record_2 = [v2 for k2,v2 in record_pair[1].items() if k2 in fields]))

        colBB, colCC, colDD, colEE  = st.columns([1,1,1,1])
        with colBB:
            duplicate_btn = st.button('Duplicaat')
            if duplicate_btn:
                st.session_state["stashed_label_pair"] = (record_pair, "match")
                st.experimental_rerun()

        with colCC:
            not_duplicate_btn = st.button('Geen duplicaat')
            if not_duplicate_btn:
                st.session_state["stashed_label_pair"] = (record_pair, "distinct")
                st.experimental_rerun()

        with colDD:
            unsure_duplicate_btn = st.button('Onzeker')
            if unsure_duplicate_btn:
                st.session_state['number_of_unsure'] = st.session_state['number_of_unsure'] + 1
                st.session_state["stashed_label_pair"] = (record_pair, "unsure")
                st.experimental_rerun()

                

        with colEE:
            finish_label_btn = st.button('Finish')
            if finish_label_btn:
                # deduper.train()
                deduper.train(index_predicates=False)
                # st.session_state['currentState'] = "LabelClusters"
                clustered_dupes = self._partition(deduper, st.session_state["deduper_data"], 0.5)
                cluster_membership = {}
                for cluster_id, (records, scores) in enumerate(clustered_dupes):
                    for record_id, score in zip(records, scores):
                        cluster_membership[record_id] = {
                            "Cluster ID": cluster_id,
                            "confidence_score": score
                        }
                st.write(cluster_membership)
                

    def _partition(
        self, deduper,  data: Data, threshold: float = 0.5
    ):  # pragma: no cover
        """
        Identifies records that all refer to the same entity, returns
        tuples containing a sequence of record ids and corresponding
        sequence of confidence score as a float between 0 and 1. The
        record_ids within each set should refer to the same entity and the
        confidence score is a measure of our confidence a particular entity
        belongs in the cluster.
        For details on the confidence score, see :func:`dedupe.Dedupe.cluster`.
        This method should only used for small to moderately sized
        datasets for larger data, you need may need to generate your
        own pairs of records and feed them to :func:`~score`.
        Args:
            data: Dictionary of records, where the keys are record_ids
                  and the values are dictionaries with the keys being
                  field names
            threshold: Number between 0 and 1.  We
                       will only consider put together records into
                       clusters if the `cophenetic similarity
                       <https://en.wikipedia.org/wiki/Cophenetic>`_ of
                       the cluster is greater than the threshold.
                       Lowering the number will increase recall,
                       raising it will increase precision
        Examples:
            >>> duplicates = matcher.partition(data, threshold=0.5)
            >>> duplicates
            [
                ((1, 2, 3), (0.790, 0.860, 0.790)),
                ((4, 5), (0.720, 0.720)),
                ((10, 11), (0.899, 0.899)),
            ]
        """
        pairs = deduper.pairs(data)
        pair_scores = deduper.score(pairs)
        clusters = deduper.cluster(pair_scores, threshold)
        clusters = deduper._add_singletons(data.keys(), clusters)
        clusters = list(clusters)
        # _cleanup_scores(pair_scores)
        return clusters



    def _transform_type_dict_to_correct_format_for_dedupe(self, dict_of_types):
        return [{'field':k, 'type':v} for k,v in dict_of_types.items()]     


    def _get_dedupe_object(self):
        if os.path.exists(self.pickled_file):
                print('reading from', self.pickled_file)
                with open(self.pickled_file, 'rb') as f:
                    deduper = pickle.load(f)
        else:
            deduper = dedupe.Dedupe(self._transform_type_dict_to_correct_format_for_dedupe(st.session_state['dedupe_type_dict'])) 
        return deduper 

    def show(self): 
        print('DeDupeLabelPage show() called')
        with self.canvas.container(): 
            # st.title("DeDupe")
            # deduper = self._get_dedupe_object()

            # if st.session_state["stashed_label_pair"] is not None:
            #     deduper = self._get_dedupe_object()
            #     self._mark_pair(deduper, st.session_state["stashed_label_pair"])
            #     st.session_state["stashed_label_pair"] = None
            #     st.session_state["record_pair"] = None
            #     st.experimental_rerun()
            # else:
            #     st.session_state["deduper_data"] = st.session_state["dataframe"].to_dict(orient="index")
            #     deduper.prepare_training(st.session_state["deduper_data"])
            #     self.streamlit_label(deduper)

            if st.session_state["dedupe_type_dict"] is not {}:
                self.handler.create_deduper_object(st.session_state["dedupe_type_dict"])
                st.session_state["dedupe_type_dict"] = {}
            
            st.write(self.handler.dedupe_next_pair())

            
