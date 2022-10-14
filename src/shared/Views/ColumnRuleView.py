from typing import List, Dict
import json

class ColumnRuleView:
    def __init__(self, rule_string : str, value_mapping, confidence, idx_to_correct: List[int] ):
        self.value_mapping = value_mapping
        self.rule_string = rule_string
        self.idx_to_correct = idx_to_correct
        self.confidence = confidence

    def to_json(self):
        return json.dumps(self, default=lambda o: o.__dict__)
    
    @staticmethod
    def parse_from_json(json_string):
        data = json.loads(json_string)
        return ColumnRuleView(rule_string=data["rule_string"], value_mapping= json.loads(data["value_mapping"]), idx_to_correct=json.loads(data["idx_to_correct"]), confidence = data["confidence"])