from abc import ABC, abstractmethod
import json

class IDeduper(ABC):

    # RULE LEARNING
    @abstractmethod
    def next_pair(self):
        raise Exception("Not implemented Exception")