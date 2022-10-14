import pandas as pd
import numpy as np

import config as cfg
from mlxtend.frequent_patterns import fpgrowth

class AssociationRuleFinder:

    def __init__(self, df_dummy, min_support : float, max_len : int, 
                          min_lift : float, min_confidence : float) -> None:

        self.df_dummy = df_dummy
        self.min_support = min_support
        self.max_len = max_len
        self.min_lift = min_lift
        self.min_confidence = min_confidence


    def get_association_rules(self) -> pd.DataFrame:
        """
            df_dummy   : DataFrame consisting of one-hot-encoded-columns
            min_support: minimum_support for rule to be included
            max_len    : maximum length of item sets found by FP-growth

            returns: pandas DataFrame with columns "antecedents" and "consequents" that
            store itemsets, plus the scoring metric columns: "antecedent support", 
            "consequent support", "support", "confidence", "lift", "leverage", 
            "conviction" of all rules for which 
            lift(rule) >= min_lift and  confidence(rule) >= min_confidence.
        """
        cfg.logger.debug(f"Shape of df in get_association_rules: {self.df_dummy.shape}")
        frequent_itemsets = fpgrowth(self.df_dummy, min_support=self.min_support, 
                                    use_colnames=True, max_len=self.max_len)
        cfg.logger.debug(f"Shape of frequent_itemsets: {frequent_itemsets.shape}")
        cfg.logger.debug(f"{str(frequent_itemsets)}")

        """ Oude code met lift.
        ar = association_rules(frequent_itemsets, metric = 'lift', min_threshold=min_lift)
        # Filter out low confidence rules
        return ar[ar['confidence'] > min_confidence]
        """

        # Remove association rules with multiple consequents. 
        # First use confidence, later filter on lift. 
        # Reason to use confidence is that when a => b, c is present then also
        # a => b and a => c will be present
        ar = self.association_rules(frequent_itemsets, 'confidence', self.min_confidence)

        cfg.logger.debug("Association rules before pruning")
        cfg.logger.debug(f"{str(ar)}")

        return ar[ar['lift'] > self.min_lift] 

    # Code origineel van mlxtend
    def association_rules(self,df, metric="confidence", min_threshold=0.8, support_only=False) -> pd.DataFrame:
        """Generates a DataFrame of association rules including the
        metrics 'score', 'confidence', and 'lift'

        Parameters
        -----------
        df : pandas DataFrame
        pandas DataFrame of frequent itemsets
        with columns ['support', 'itemsets']

        metric : string (default: 'confidence')
        Metric to evaluate if a rule is of interest.
        **Automatically set to 'support' if `support_only=True`.**
        Otherwise, supported metrics are 'support', 'confidence', 'lift',
        'leverage', and 'conviction'
        These metrics are computed as follows:

        - support(A->C) = support(A+C) [aka 'support'], range: [0, 1]\n
        - confidence(A->C) = support(A+C) / support(A), range: [0, 1]\n
        - lift(A->C) = confidence(A->C) / support(C), range: [0, inf]\n
        - leverage(A->C) = support(A->C) - support(A)*support(C),
            range: [-1, 1]\n
        - conviction = [1 - support(C)] / [1 - confidence(A->C)],
            range: [0, inf]\n

        min_threshold : float (default: 0.8)
        Minimal threshold for the evaluation metric,
        via the `metric` parameter,
        to decide whether a candidate rule is of interest.

        support_only : bool (default: False)
        Only computes the rule support and fills the other
        metric columns with NaNs. This is useful if:

        a) the input DataFrame is incomplete, e.g., does
        not contain support values for all rule antecedents
        and consequents

        b) you simply want to speed up the computation because
        you don't need the other metrics.

        Returns
        ----------
        pandas DataFrame with columns "antecedents" and "consequents"
        that store itemsets, plus the scoring metric columns:
        "antecedent support", "consequent support",
        "support", "confidence", "lift",
        "leverage", "conviction"
        of all rules for which
        metric(rule) >= min_threshold.
        Each entry in the "antecedents" and "consequents" columns are
        of type `frozenset`, which is a Python built-in type that
        behaves similarly to sets except that it is immutable
        (For more info, see
        https://docs.python.org/3.6/library/stdtypes.html#frozenset).

        Examples
        -----------
        For usage examples, please see
        http://rasbt.github.io/mlxtend/user_guide/frequent_patterns/association_rules/

        """
        if not df.shape[0]:
            raise ValueError(
                "The input DataFrame `df` containing " "the frequent itemsets is empty."
            )

        # check for mandatory columns
        if not all(col in df.columns for col in ["support", "itemsets"]):
            raise ValueError(
                "Dataframe needs to contain the\
                            columns 'support' and 'itemsets'"
            )
        
        # metrics for association rules
        metric_dict = {
            "antecedent support": lambda _, sA, __: sA,
            "consequent support": lambda _, __, sC: sC,
            "support": lambda sAC, _, __: sAC,
            "confidence": lambda sAC, sA, _: sAC / sA,
            "lift": lambda sAC, sA, sC: metric_dict["confidence"](sAC, sA, sC) / sC,
            "leverage": lambda sAC, sA, sC: metric_dict["support"](sAC, sA, sC) - sA * sC,
        }

        columns_ordered = [
            "antecedent support",
            "consequent support",
            "support",
            "confidence",
            "lift",
            "leverage",
        ]

        # check for metric compliance
        if support_only:
            metric = "support"
        else:
            if metric not in metric_dict.keys():
                raise ValueError(
                    "Metric must be 'confidence' or 'lift', got '{}'".format(metric)
                )

        # get dict of {frequent itemset} -> support
        keys = df["itemsets"].values
        values = df["support"].values
        frozenset_vect = np.vectorize(lambda x: frozenset(x))
        frequent_items_dict = dict(zip(frozenset_vect(keys), values)) # + { () : 1.0}

        # prepare buckets to collect frequent rules
        rule_antecedents = []
        rule_consequents = []
        rule_supports = []

        # iterate over all frequent itemsets
        for k in frequent_items_dict.keys():
            if len(k) == 1:
                continue
            sAC = frequent_items_dict[k]
            for c in k:
                consequent = frozenset([c])
                antecedent = k.difference(consequent)

                if support_only:
                    # support doesn't need these,
                    # hence, placeholders should suffice
                    sA = None
                    sC = None

                else:
                    try:
                        sA = frequent_items_dict[antecedent]
                        sC = frequent_items_dict[consequent]
                    except KeyError as e:
                        s = (
                            str(e) + "You are likely getting this error"
                            " because the DataFrame is missing "
                            " antecedent and/or consequent "
                            " information."
                            " You can try using the "
                            " `support_only=True` option"
                        )
                        raise KeyError(s)
                    # check for the threshold

                score = metric_dict[metric](sAC, sA, sC)
                if score >= min_threshold:
                    rule_antecedents.append(antecedent)
                    rule_consequents.append(consequent)
                    rule_supports.append([sAC, sA, sC])
                #else: # zelf bijgevoegd
                #    cfg.logger.debug(f"Not adding {antecedent} => {consequent} because {score} is less than {min_threshold}")

                    

        # check if frequent rule was generated
        if not rule_supports:
            return pd.DataFrame(columns=["antecedents", "consequents"] + columns_ordered)

        else:
            # generate metrics
            rule_supports = np.array(rule_supports).T.astype(float)
            df_res = pd.DataFrame(
                data=list(zip(rule_antecedents, rule_consequents)),
                columns=["antecedents", "consequents"],
            )

            if support_only:
                sAC = rule_supports[0]
                for m in columns_ordered:
                    df_res[m] = np.nan
                df_res["support"] = sAC

            else:
                sAC = rule_supports[0]
                sA = rule_supports[1]
                sC = rule_supports[2]
                for m in columns_ordered:
                    df_res[m] = metric_dict[m](sAC, sA, sC)

            return df_res