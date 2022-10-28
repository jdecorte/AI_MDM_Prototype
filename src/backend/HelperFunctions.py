import pandas as pd
import numpy as np
import itertools
from typing import List, Set, Dict, Iterable, Any
import os
# from python_arptable import get_arp_table

class HelperFunctions:

    # @staticmethod
    # def transform_string_series_to_float_series(self, series: pd.Series) -> pd.Series:
    #     return series.apply(lambda stringValue: self._extract_float_from_string(stringValue))

    # def _extract_float_from_string(s: str) -> float:
    #     lst = re.findall(r"[-+]?\d*\.\d+|\d+", str(s))
    #     if len(lst)> 0:
    #         return max([float(i) for i in lst])
    #     else:
    #         return pd.nan

    # HULPMETHODEN
    @staticmethod
    def findsubsets( fullset : Iterable[Any]) -> List[Set[Any]]:
        """
            fullset: an iterable of items
            returns: a list of all non-empty subsets of the given iterable
            
            Find all subsets consisting of elements from the given iterable.
        """
        listrep = list(fullset)
        n = len(listrep)
        toReturn = [set([listrep[k] for k in range(n) if i&1<<k]) for i in range(2**n)]
        
        return toReturn
    
    @staticmethod
    def subsets_minus_one( s : Set[Any]) -> List[Set[Any]]:
        """
            Return a list of sets. All sets in this list are subsets of s and contain 
            one fewer element.

            s : Set

            returns: list of subsets of s that all have one fewer element
        """
        return list(map(set, itertools.combinations(s, len(s)-1)))

    @staticmethod
    def save_results_to(json_string: str, unique_id: str, md5_hash: str, file_name:str):
        dir_path = f"storage/{unique_id}/{md5_hash}"
        os.makedirs(dir_path, exist_ok=True)

        with open(f"{dir_path}/{file_name}.json", 'w') as outfile:
            outfile.write(json_string)       

    # @staticmethod
    # def mac_from_ip(ip):
    #     arp_table = get_arp_table()
    #     for entry in arp_table:
    #         if entry['IP address'] == ip:
    #             return entry['HW address']
    #     return None