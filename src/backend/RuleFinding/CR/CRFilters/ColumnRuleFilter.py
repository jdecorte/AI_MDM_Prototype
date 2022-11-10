from abc import ABC, abstractmethod

import pandas as pd
import numpy as np
import config as cfg
import math

from typing import Sequence, Dict
from src.backend.RuleFinding.CR.ColumnRule import ColumnRule

class ColumnRuleFilter(ABC):

    @abstractmethod
    def execute(self, rules, rule_confidence_bound, original_df) -> Dict[str, ColumnRule]:
        raise Exception("Not implemented Exception")

class ColumnRuleFilter_Entropy(ColumnRuleFilter):

    def __init__(self) -> None:
        pass

    def _calculate_entropy(self,row, df):
        querystring_list = []
        pre = row[:-1]
        if pre.empty:
            return 0
        post = row[-1:]
        for k,v in pre.items():
            querystring_list.append(f"`{k}` == '{v}'")
        querystring = " and ".join(querystring_list)
        df_new = df.query(querystring)
        total_instances = len(df_new)
        # Zit maar 1 k-v pair in
        for k,v in post.items():
            other_query_string = f"`{k}` == '{v}'"
        correct_instances = len(df_new.query(other_query_string))
        percentage_correct = correct_instances / total_instances
        if math.isclose(1,percentage_correct):
            entropy = 0
        
        else:
            if math.isclose(0,percentage_correct):
                percentage_correct = 0.0001
            entropy = (-1*percentage_correct) * math.log(percentage_correct, 2) + (-1*(1-percentage_correct) * math.log(1-percentage_correct, 2))
        
        return entropy
        
 
    def execute(self, rules, rule_confidence_bound, original_df) -> Dict[str, ColumnRule]:

        interesting_rules: Dict[str, ColumnRule] = {}

        # Bvb: 1 -> ["a->b", "b->c", "X->Y"]
        dict_ante_size_to_list_of_rules = {}

        # Filter rules HARDCODED (Nog te veranderen)
        rules = [r for r in rules.values() if r.confidence >= rule_confidence_bound] 
        dict_entropy = {}

        for _, column_rule in enumerate(sorted(rules, key=lambda r : len(r.antecedent_set))):
            vm = column_rule.mapping_df
            print(column_rule.rule_string)
            dict_entropy[column_rule.rule_string] = np.sum(vm.apply(lambda row : self._calculate_entropy(row, original_df), axis = 1))
            if str(len(column_rule.antecedent_set)) in dict_ante_size_to_list_of_rules:
                new_list = dict_ante_size_to_list_of_rules[str(len(column_rule.antecedent_set))]
                new_list.append(column_rule)
                dict_ante_size_to_list_of_rules[str(len(column_rule.antecedent_set))] = new_list
            else:
                dict_ante_size_to_list_of_rules[str(len(column_rule.antecedent_set))] = [column_rule]

        min_val_in_dictAnteSize = min(list(map(int, dict_ante_size_to_list_of_rules.keys())))

        for anteLength, listOfRules in dict_ante_size_to_list_of_rules.items():
            if int(anteLength) == min_val_in_dictAnteSize:
                for r in listOfRules:
                    print(f"Regel Toegevoegd: {r.rule_string}, met entropy: {dict_entropy[r.rule_string]}")
                    interesting_rules[r.rule_string] = r
                        
            else:
                for r in listOfRules:
                    listOfPrevLengthRules = [i for i in dict_ante_size_to_list_of_rules[str(int(anteLength)-1)] if i.consequent_set == r.consequent_set and i.antecedent_set.issubset(r.antecedent_set)]
                    if len(listOfPrevLengthRules) != 0:
                        if(min([dict_entropy[y.rule_string] for y in listOfPrevLengthRules])> dict_entropy[r.rule_string]):
                            print(f"Regel Toegevoegd: {r.rule_string}, met entropy: {dict_entropy[r.rule_string]}")
                            interesting_rules[r.rule_string] = r
                            print(f"Meer algemene regels zijn verwijderd:")
                            for e in listOfPrevLengthRules:
                                print(e.rule_string)
                                if e.rule_string in interesting_rules:
                                    del interesting_rules[e.rule_string]
                            
                    else:
                        print(f"Regel Toegevoegd: {r.rule_string}, met entropy: {dict_entropy[r.rule_string]}")
                        interesting_rules[r.rule_string] = r

        return interesting_rules


class ColumnRuleFilter_ZScore(ColumnRuleFilter):

    def __init__(self) -> None:
        pass
        
 
    def execute(self, rules, rule_confidence_bound, original_df) -> Dict[str, ColumnRule]:
        """
            Only keep 'interesting' rules. An 'interesting' rule r is one whose confidence 
            is such that there is no rule whose antecedent set is a subset of the 
            antecedent set of r and that has a strictly higher confidence and the same consequent.

            XXX: we need to punish 'long rules' so that they become less interesting. 
            XXX: Think about a less crude way to do this

            rules: the column rules that need to be filtered
            returns: Dictionary mapping rule strings to their corresponding interesting
                ColumnRule            
        """

        cfg.logger.info(f"Starting with {len(rules.values())} rules")


        interesting_rules: Dict[str, ColumnRule] = {}

        # Bvb: 1 -> ["a->b", "b->c", "X->Y"]
        dict_ante_size_to_list_of_rules = {}

        # Filter rules HARDCODED (Nog te veranderen)
        rules = [r for r in rules.values() if r.confidence >= rule_confidence_bound]

        # Antecedent van Old Rule is steeds een deelverzameling van de antecente van Rule
        # Increased is de increase in confidence van Rule t.o.v. Old Rule
        lemma_df = pd.DataFrame(columns=["Increased", "Old Rule", "Rule"])


        for _, column_rule in enumerate(sorted(rules, key=lambda r : len(r.antecedent_set))):
            if str(len(column_rule.antecedent_set)) in dict_ante_size_to_list_of_rules:
                new_list = dict_ante_size_to_list_of_rules[str(len(column_rule.antecedent_set))]
                new_list.append(column_rule)
                dict_ante_size_to_list_of_rules[str(len(column_rule.antecedent_set))] = new_list
            else:
                dict_ante_size_to_list_of_rules[str(len(column_rule.antecedent_set))] = [column_rule]


        min_val_in_dictAnteSize = min(list(map(int, dict_ante_size_to_list_of_rules.keys())))
        # TODO sort de keys eerst, anders conflict mogelijk
        for anteLength, listOfRules in dict_ante_size_to_list_of_rules.items():
            if int(anteLength) == min_val_in_dictAnteSize:
                # Lengte 0, Automatisch toevoegen als 'interesting rule', aangezien reeds gefiltered is op confidence
                for r in listOfRules:
                    interesting_rules[r.rule_string] = r
                        
            else:
                # Lengte N:
                # Bekijk elke regel die tot lengte = N behoort, Kijk naar hun consequent en kijk voor welke regels uit (N-1) deze een uitbereiding vormt.
                # Bereken vervolgens de stijging in confidence, sla deze op in dataframe en later standardiseer deze vervolgens naar Z-score
                for r in listOfRules:
                    listOfPrevLengthRules = [i for i in dict_ante_size_to_list_of_rules[str(int(anteLength)-1)] if i.consequent_set == r.consequent_set and i.antecedent_set.issubset(r.antecedent_set)]

                    if len(listOfPrevLengthRules) != 0:
                        # Onderstaand kan vervangen worden door een rij toe te voegen aan een Dataframe
                        l_increased = [(r.confidence - p.confidence) for p in listOfPrevLengthRules]
                        l_old_rule = [p for p in listOfPrevLengthRules]
                        l_rule = [r for _ in listOfPrevLengthRules]

                        lemma_to_append_df = pd.DataFrame({"Increased":l_increased, "Old Rule":l_old_rule, "Rule":l_rule})                    
                        lemma_df = pd.concat([lemma_df, lemma_to_append_df])
                    else:
                        # By definition an interesting rule
                        interesting_rules[r.rule_string] = r


        if len(lemma_df) > 0:

            # TODO isclose() toevoegen voor mogelijks floating point error
            filteredIncreases_df = lemma_df[lemma_df["Increased"] != 0]
            data = np.array(filteredIncreases_df["Increased"])
            filteredIncreases_df['zscores'] = (data - np.mean(data))/np.std(data, ddof=1)

            # Define High/Low Increase
            # TODO Magical constant eruit: ofwel parameter, ofwel Kmeans
            filteredIncreases_df['Type Increase'] = np.where(filteredIncreases_df['zscores'] >= 0.50, 'High', 'Low')

            interesting_rules_set = set()
            interesting_rules_set = interesting_rules_set.union(set(filteredIncreases_df[filteredIncreases_df["Type Increase"] == "Low"]["Old Rule"]))
            interesting_rules_set = interesting_rules_set.union(set(filteredIncreases_df[filteredIncreases_df["Type Increase"] == "High"]["Rule"]))

            for e in interesting_rules_set:
                interesting_rules[e.rule_string] = e

            filteredIncreases_df["RuleString"] = filteredIncreases_df["Rule"].apply(lambda x: x.rule_string)
        
        return interesting_rules