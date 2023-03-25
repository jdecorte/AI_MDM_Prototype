import pandas as pd
import numpy as np
import config as cfg
import math
import pprint
import json
from typing import List
from src.shared.Views.ColumnRuleView import ColumnRuleView


class ColumnRule:
    def __init__(
      self,
      rule_string: str,
      original_df=None,
      value_mapping=False,
      confidence=None,):
        """
        rule_string: string of the form "A,B => C" (or "/ => C" or " => C")
        original_df: dataframe containing the original data (not one-hot encoded),
            but all values should be strings
        value_mapping: should values be mapped to the most frequent value?
        confidence: confidence of the rule, if None then the confidence is calculated
        """
        self.value_mapping = value_mapping
        # Test of het wel stringified is
        self.original_df = original_df
        self.rule_string = rule_string
        antecedent_string = rule_string.split(" => ")
        if antecedent_string[0] == "/" or antecedent_string[0] == "":
            self.antecedent_set = frozenset()
        else:
            self.antecedent_set = frozenset(antecedent_string[0].split(","))
        self.consequent_set = set(rule_string.split(" => ")[1].split(","))

        if value_mapping:
            self.mapping_df = self._create_mapping_df()
            self.df_to_correct = self._create_dataframe_to_be_corrected()

        # Note: if value_mapping is False and confidence is None,
        # then this code will crash
        if confidence is None:
            self.confidence = 1.0 - self.df_to_correct.shape[0]/original_df.shape[0]
        else:
            self.confidence = confidence

    def __str__(self):
        return (self.rule_string
                + " (" + str(self.confidence) + ")"
                + ", met als mapping: "
                + str(self.value_mapping)
                )

    def _create_dataframe_to_be_corrected(self) -> pd.DataFrame:
        """
        Creates a dataframe containing all rows that need to be corrected.
        Contains the following columns:
        - all columns of the original dataframe
        - a column with the rule string (RULESTRING)
        - a column with the value that was found (FOUND_CON)
        - a column with the value that was predicted (SUGGEST_CON)      
        """
        lhs_cols = sorted(list(self.antecedent_set))
        rhs_col = list(self.consequent_set)[0]
        if len(lhs_cols) > 0:
            df_tmp = self.original_df.merge(
                self.mapping_df[[rhs_col]],
                left_on=lhs_cols,
                right_on=lhs_cols,
                left_index=False,
                right_index=True,
                suffixes=["", "_predicted"]
                )
        else:
            # If there are no antecedents, then always predict the most frequent value
            df_tmp = self.original_df.copy()
            df_tmp[rhs_col + "_predicted"] = self.mapping_df[rhs_col].iloc[0]

        df_errors = df_tmp[
                df_tmp[rhs_col] != df_tmp[rhs_col + "_predicted"]].copy()
        # Add three columns to the dataframe, one with the rule string, one
        # with the value that was found and one with the value that was predicted.
        df_errors["RULESTRING"] = self.rule_string
        df_errors["FOUND_CON"] = df_errors[rhs_col]
        df_errors["SUGGEST_CON"] = df_errors[rhs_col + "_predicted"]
        df_errors = df_errors.drop(columns=[rhs_col + "_predicted"])

        return df_errors

    def show_value_mapping(self) -> None:
        pprint.pprint(self.value_mapping)

    def _create_mapping_df(self) -> pd.DataFrame:
        """ Create a mapping dataframe based on the original dataframe.
            We map each combination of antecedents to the most frequent
            consequent.

            We also add columns that indicate the support of the antecedent,
            and the number of times the consequent was found for the given
            antecedent. These columns are called '__SUPPORT_LHS' and
            '__SUPPORT_RHS', respectively.
        """
        lhs_cols = sorted(list(self.antecedent_set))
        rhs_col = list(self.consequent_set)[0]

        if len(lhs_cols) == 0:  # rule with empty antecedent
            value_counts = self.original_df[rhs_col].value_counts()
            most_common_value = value_counts.index[0]
            support = value_counts.iloc[0]
            return pd.DataFrame({rhs_col: [most_common_value],
                                 '__SUPPORT_LHS': [self.original_df.shape[0]],
                                 '__SUPPORT_LHS_AND_RHS': [support]
                                 })

        df_counts = self.original_df.value_counts(subset=lhs_cols+[rhs_col], sort=False)
        level = tuple(i for i in range(len(lhs_cols)))
        tmp = df_counts.groupby(level=level).agg(
            [np.sum, np.max, 'idxmax']
        )

        tmp2 = pd.DataFrame.from_records(tmp['idxmax'], columns=lhs_cols+[rhs_col])
        tmp2.set_index(keys=lhs_cols, inplace=True)

        tmp2['__SUPPORT_LHS'] = tmp['sum']
        tmp2['__SUPPORT_LHS_AND_RHS'] = tmp['amax']

        return tmp2

    def predict(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        df: input DataFrame, NOT one-hot-encoded

        Returns a DataFrame consisting of the relevant columns (i.e. columns
        participating in this rule).
        The antecedent columns are filled with the original values
        in the DataFrame,  the consequent column, however, is filled with
        the predictions made by this rule.
        """

        if len(self.antecedent_set) != 0:
            # Get dataframe with only the columns in the antecedent
            df_relevant = df[list(self.antecedent_set)]
        else:
            df_relevant = pd.DataFrame(index=df.index)

        if self.mapping_df is None:
            self._create_mapping_df()

        cfg.logger.debug("Merging the following 2 dataframes. First DataFrame")
        cfg.logger.debug(df_relevant)
        cfg.logger.debug("Second DataFrame")
        cfg.logger.debug(self.mapping_df)

        rhs_col = list(self.consequent_set)[0]
        if len(self.antecedent_set) != 0:
            return df_relevant.merge(
                self.mapping_df[[rhs_col]], how="left", on=list(self.antecedent_set))
        else:
            df_relevant[list(self.consequent_set)[0]] = self.mapping_df[[rhs_col]].iloc[0, 0]
            return df_relevant

    def status(self, df: pd.DataFrame) -> np.ndarray:
        """
        df: input DataFrame, NOT one-hot-encoded

        Return a series with the same number of entries as the DataFrame `df`
        has rows. Each entry is either +1 is the rule is satisfied by the
        corresponding row, -1 if the rule is not satisfied by the
        corresponding row.
        """
        cfg.logger.debug("Determining status for DataFrame")
        cfg.logger.debug(df)
        # Get predictions
        predictions = self.predict(df)

        assert predictions.shape[0] == df.shape[0], "Error in predict!"

        consequent_col_name = list(self.consequent_set)[0]

        cfg.logger.debug(f"{predictions[consequent_col_name].index}"
                         + f" versus {df[consequent_col_name].index}")

        cfg.logger.debug("The predictions are "
                         + f"{predictions[consequent_col_name]}")
        cfg.logger.debug(f"The actual values are {df[consequent_col_name]}")

        return np.where(
            predictions[consequent_col_name].reset_index(drop=True) ==
            df[consequent_col_name].reset_index(drop=True), +1, -1)

    def parse_self_to_view(self) -> ColumnRuleView:
        return ColumnRuleView(
            rule_string=self.rule_string,
            idx_to_correct=json.dumps(self.df_to_correct.index.tolist()),
            confidence=self.confidence,
            value_mapping=self.mapping_df.reset_index().to_json())

    def compute_c_measure(self) -> float:
        """
        Compute the c-metric for this rule, this is a float in the range [1,5].
        This is based on the flow chart on page 39 of 
        https://documentserver.uhasselt.be/bitstream/1942/35321/1/845d31c7-7084-4c8b-a964-d10bad246e52.pdf
        """
        if not hasattr(self, "fi_measure_"):
            self.compute_fi_measure()
        if not hasattr(self, "g3_measure_"):
            self.compute_g3_measure()
        c_measure = 2.5*(self.fi_measure_ + self.g3_measure_)

        # TODO: make cutoffs configurable
        if self.g3_measure_ >= 0.75 and self.fi_measure_ < 0.75:
            if self.has_predominant_rhs():
                c_measure -= 1
            else:
                c_measure += 1
        elif self.g3_measure_ < 0.75 and self.fi_measure_ >= 0.75:
            if self.compute_rfi_measure() < 0.75:
                c_measure -= 1
            else:
                c_measure += 1
        elif self.g3_measure_ >= 0.75 and self.fi_measure_ >= 0.75:
            if self.has_predominant_rhs() and self.compute_rfi_measure() < 0.75:
                c_measure -= 2
        else:
            raise ValueError("C-measure computed when both g3 and fi are < 0.75")

        # Stage 4 and 5 not yet implemented
        self.c_measure_ = c_measure
        return c_measure

    def has_predominant_rhs(self, threshold=0.85) -> bool:
        """ Returns true is the RHS contains a value that is present in
            at least threshold rows.
        """
        return self.original_df[list(self.consequent_set)[0]].value_counts(
            normalize=True).max() >= threshold

    def compute_fi_measure(self) -> float:
        """ Computes the fraction of information measure for this rule.
            Note: this does NOT take into account the value mapping.
            This measure is computed only on the basis of the values in the
            original dataframe and the columns in the antecedent and consequent
            set.

            The result is cached in self.fi_measure_.
        """
        self.fi_measure_ = fi_measure(self.original_df,
                                      list(self.antecedent_set),
                                      list(self.consequent_set)[0],)
        return self.fi_measure_

    def compute_rfi_measure(self) -> float:
        self.rfi_measure_ = rfi_measure(self.original_df,
                                        list(self.antecedent_set),
                                        list(self.consequent_set)[0],)
        return self.rfi_measure_

    def compute_g3_measure(self) -> float:
        self.g3_measure_ = g3_measure(self.original_df,
                                      list(self.antecedent_set),
                                      list(self.consequent_set)[0],)
        return self.g3_measure_

    def is_more_specific_than(self, other):
        """ Returns true if this rule is more specific than the other rule.
            This is the case if:
            - this rule has a larger antecedent set
            - the consequent sets are equal
        """
        return (self.consequent_set == other.consequent_set and
                other.antecedent_set.issubset(self.antecedent_set))


def fi_measure(df: pd.DataFrame, lhs_cols: List[str], rhs_col: str) -> float:
    """ Fraction of information measure. See section 3.2.3 in
         https://documentserver.uhasselt.be/bitstream/1942/35321/1/845d31c7-7084-4c8b-a964-d10bad246e52.pdf
    """
    y = df[rhs_col].value_counts(normalize=True).values
    if len(y) == 1:  # Return zero if right hand side is constant
        return 0

    # Return 0 if left hand side is empty.
    # This is a special case, because the conditional entropy is
    # the same as the original entropy, so the fraction of information
    # is 0.
    if len(lhs_cols) == 0:
        return 0

    entropy_y = - (y * np.log2(y)).sum()  # Entropy of y

    # Compute conditional entropy
    values = df.value_counts(subset=lhs_cols + [rhs_col], normalize=True, sort=False)
    lhs_values = df.value_counts(subset=lhs_cols, normalize=True, sort=False)

    conditional_entropy = 0
    for x in lhs_values.index:
        y_for_this_x = values.loc[x].values
        px = lhs_values.loc[x]

        conditional_entropy += (y_for_this_x * np.log2(y_for_this_x / px)).sum()

    conditional_entropy = - conditional_entropy

    return (entropy_y - conditional_entropy) / entropy_y


def rfi_measure(df: pd.DataFrame, lhs_cols: List[str], rhs_col: str) -> float:
    # Compute RFI measure as described on page 44 and page 28
    lhs_values = df.value_counts(subset=lhs_cols, sort=False)
    rhs_values = df.value_counts(subset=[rhs_col], sort=False)

    n = df.shape[0]  # number of tuples in the relation

    # Naive implementation. Can be sped up.
    m_zero = 0.0
    for x in lhs_values.index:
        cx = lhs_values.loc[x]
        for y in rhs_values.index:
            cy = rhs_values.loc[y]
            # Start from 1, k = 0 yields zero
            for k in range(max(1, cx+cy - n), min(cx, cy) + 1):  
                p0 = math.comb(cy, k) * math.comb(n - cy, cx - k) / math.comb(n, cx)
                m_zero += p0 * k * np.log2(k * n / (cx * cy))

    m_zero /= n  # Division by n is independent of the loop

    y = df[rhs_col].value_counts(normalize=True).values
    entropy_y = - (y * np.log2(y)).sum()  # Entropy of y
    b_zero = m_zero / entropy_y

    return fi_measure(df, lhs_cols, rhs_col) - b_zero


def g3_measure(df: pd.DataFrame, lhs_cols: List[str], rhs_col: str) -> float:
    """ g3 measure as described in https://documentserver.uhasselt.be/bitstream/1942/35321/1/845d31c7-7084-4c8b-a964-d10bad246e52.pdf
        See section 3.2.1, page 18.
    """
    num_tuples = df.shape[0]  # number of tuples in the relation
    values = df.value_counts(subset=lhs_cols + [rhs_col])

    if len(lhs_cols) == 0:  # Special case: empty antecedent
        return 1 - (num_tuples - values.iloc[0]) / (num_tuples - 1)

    lhs_values = df.value_counts(subset=lhs_cols)

    s = 0
    for x in lhs_values.index:
        # This may cause a performance warning because the index isn't sorted.
        # However, because the index isn't sorted, we know that the most frequent
        # value is the first one. So we can just take the first value.
        s += values.loc[x].iloc[0]

    return 1 - (num_tuples - s)/(num_tuples - lhs_values.shape[0])
