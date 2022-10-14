import json
from typing import List, Dict
from src.shared.Enums.BinningEnum import BinningEnum 

class RuleFindingConfig:
    def __init__(self, rule_length: int, min_support: float, lift: int, confidence: float, filtering_string: str, binning_option: Dict[str, BinningEnum], dropping_options : Dict[str,Dict[str, str]]):
        self.rule_length = rule_length
        self.min_support = min_support
        self.lift = lift
        self.confidence = confidence
        self.filtering_string = filtering_string
        self.binning_option = binning_option
        self.dropping_options = dropping_options

    def to_json(self):
        return json.dumps(self.__dict__)

    @staticmethod
    # def create_from_json(json_string) -> RuleFindingConfig:
    def create_from_json(json_string):
        data = json.loads(json_string)
        return RuleFindingConfig(rule_length=data["rule_length"], min_support=data["min_support"], lift=data["lift"], confidence=data["confidence"], filtering_string=data["filtering_string"], binning_option=data["binning_option"], dropping_options=data["dropping_options"])
