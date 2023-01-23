import config as cfg
import dedupe
import pandas as pd
from dedupe._typing import (
    Data,
    Literal,
    RecordDict,
    RecordDictPair,
    RecordID,
    TrainingData,
    Tuple, 
)

class DeDupeIO():
    
    def __init__(self, dedupe_type_dict, dedupe_data) -> None:
        cfg.logger.debug("Calling DeDupeIO ..... ")
        self.number_of_unsure_labels = 0
        self.dedupe_data = pd.read_json(dedupe_data).astype(str).to_dict(orient="index")
        self.deduper_object = dedupe.Dedupe(self._transform_type_dict_to_correct_format_for_dedupe(dedupe_type_dict))
        cfg.logger.debug("About to call prepare_training on deduper object")
        self.deduper_object.prepare_training(self.dedupe_data)
        cfg.logger.debug("prepare_training done")
        
    def _transform_type_dict_to_correct_format_for_dedupe(self, dict_of_types):
        return [{"field":k, "type":v} for k,v in dict_of_types.items()]   

    def next_pair(self):
        return self.deduper_object.uncertain_pairs().pop() 

    def mark_pair(self,labeled_pair):
        record_pair, label = labeled_pair
        examples: TrainingData = {"distinct": [], "match": []}
        if label == "unsure":
            # See https://github.com/dedupeio/dedupe/issues/984 for reasoning
            examples["match"].append(record_pair)
            examples["distinct"].append(record_pair)
            self.number_of_unsure_labels = self.number_of_unsure_labels + 1
        else:
            # label is either "match" or "distinct"
            examples[label].append(record_pair)
        self.deduper_object.mark_pairs(examples)

    def get_stats(self):
        n_match = len(self.deduper_object.training_pairs["match"]) - self.number_of_unsure_labels
        n_distinct = len(self.deduper_object.training_pairs["distinct"]) - self.number_of_unsure_labels
        n_unsure = self.number_of_unsure_labels
        return {"Yes":f"{n_match}/10", "No":f"{n_distinct}/10", "Unsure":f"{n_unsure}"}

    def train(self):
        try:
            self.deduper_object.train(index_predicates=False)
        except Exception as e:
            print(e)
            print(e.__traceback__)
    
    def get_clusters(self):
        try:
            threshold = 0.5
            pairs = self.deduper_object.pairs(self.dedupe_data)
            pair_scores = self.deduper_object.score(pairs)
            clusters = self.deduper_object.cluster(pair_scores, threshold)
            clusters = self.deduper_object._add_singletons(self.dedupe_data.keys(), clusters)
            clusters = list(clusters) 
            cluster_membership = {}
            for cluster_id, (records, scores) in enumerate(clusters):
                for record_id, score in zip(records, scores):
                    cluster_membership[str(record_id)] = {
                        "Cluster ID": str(cluster_id),
                        "confidence_score": str(score)
                    }
            return cluster_membership   
        except Exception as e:
            print(e) 
            print(e.with_traceback) 
            return {}