from abc import ABC, abstractmethod
from sklearn.cluster import KMeans

import pandas as pd
from src.backend.HelperFunctions import HelperFunctions

class BinningCommand(ABC):

    @abstractmethod
    def execute(self, series: pd.Series, numberOfBins: int) -> pd.Series:
        raise Exception("Not implemented Exception")


class BinningCommand_KMeans(BinningCommand):

    def __init__(self, series: pd.Series, number_of_bins) -> None:
        self.series = series
        self.number_of_bins = number_of_bins
        
 
    def execute(self, series: pd.Series, numberOfBins) -> pd.Series:
        float_series = HelperFunctions.transform_string_series_to_float_series(series)

        model = KMeans(n_clusters=numberOfBins)
        cluster_labels = model.fit_predict(float_series.reshape(-1,1))

        cluster_labelsTemp = [int(x) for x in model.cluster_centers_]
        cluster_labelsTemp.sort()
        
        cutOffMap = {}
        cutOffMap[-1] = "Niet ingevuld"

        new_cluster_labelsTemp = []
        for idx, l in enumerate(cluster_labelsTemp):
            if l != cluster_labelsTemp[-1]:
                new_cluster_labelsTemp.append( int((l + cluster_labelsTemp[idx+1]) /2) )



        for idx, label in enumerate(new_cluster_labelsTemp):

            if label == new_cluster_labelsTemp[0]:
                cutOffMap[idx] = "Tot " + str(label) 
                nextLabel = new_cluster_labelsTemp[idx+1]
                cutOffMap[idx+1] = "[ " + str(label) + " - " + str(nextLabel) + " ]" 
            else:
                if label == new_cluster_labelsTemp[-1]:
                    cutOffMap[idx+1] = "Vanaf " + str(label)
                else:
                    nextLabel = new_cluster_labelsTemp[idx+1]
                    cutOffMap[idx+1] = "[ " + str(label) + " - " + str(nextLabel) + " ]"


        
        return pd.Series([cutOffMap[x] for x in cluster_labels])


class BinningCommand_EqualBins(BinningCommand):

    def __init__(self, series: pd.Series, number_of_bins) -> None:
        self.series = series
        self.number_of_bins = number_of_bins
 
    def execute(self) -> pd.Series:
        return pd.cut(HelperFunctions.transform_string_series_to_float_series(self.series), bins=self.number_of_bins)