from abc import ABC, abstractmethod

class IDeduper(ABC):

    @abstractmethod
    def next_pair(self):
        raise Exception("Not implemented Exception")

    @abstractmethod
    def mark_pair(self, labeled_pair):
        raise Exception("Not implemented Exception")

    @abstractmethod
    def get_stats(self):
        raise Exception("Not implemented Exception")

    @abstractmethod
    def train(self):
        raise Exception("Not implemented Exception")

    @abstractmethod
    def get_clusters(self):
        raise Exception("Not implemented Exception")