import pandas as pd
import numpy as np
import config as cfg

from src.backend.RuleFinding.CR.ColumnRule import ColumnRule

from typing import Sequence


class SuggestionFinder:

    def __init__(self, column_rules: Sequence[ColumnRule], original_df):
        """
        column_rules: a sequence of column rules.
                      These rules are used to find the rows that need to be corrected.
        original_df: the original dataframe that needs correcting.
        """
        self.column_rules = column_rules
        self.original_df = original_df

        # Create DataFrame with incorrect rows according to the column rules
        cfg.logger.info(f"Using {len(self.column_rules)} for giving suggestions")
        self.df_errors_ = self.combine_all_errors()

        cfg.logger.info("Total number of values that might need correcting: "
                        + f"{self.df_errors_.shape[0]}")

    def combine_all_errors(self) -> pd.DataFrame:
        """
        Gathers all the rows that need to be corrected into a single pandas DataFrame.
        """
        if len(self.column_rules) == 0:
            return pd.DataFrame()
        return pd.concat(
            [column_rule.df_to_correct for column_rule in self.column_rules], axis=0)

    def give_suggestions(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        df: could be a subset of the original dataframe, NOT one-hot-encoded

        Returns: dataframe with additional columns. Two columns per rule.
        One column with the 'score' for this rule '__SCORE:' + rule string,
        and one column with the prediction made by this rule
        with name '__PREDICTION:' + rule string
        """
        cfg.logger.debug("give_suggestions receives the following DataFrame")
        cfg.logger.debug(df)

        for cr in self.column_rules:
            consequent_column_name = list(cr.consequent_set)[0]

            # Take backup up original column in DataFrame
            original_column = df[consequent_column_name].copy()
            predicted_column = cr.predict(df)[consequent_column_name]

            # Change original df, with predicted column
            predicted_column.index = df.index  # Make sure to use the same index !
            cfg.logger.debug(f"The predicted column is {predicted_column}")
            df[consequent_column_name] = predicted_column

            cfg.logger.debug(f"After assigning to df {df[consequent_column_name]}")

            # Check the score for each suggestion
            score = np.zeros(shape=(df.shape[0],))

            for cr2 in self.column_rules:
                score += cr2.status(df)

            score = pd.Series(score, index=df.index)
            cfg.logger.debug(f"The following score was determined {score}")

            df['__SCORE:' + cr.rule_string] = score
            df['__PREDICTION:' + cr.rule_string] = predicted_column

            # Restore original data
            df[consequent_column_name] = original_column

        return df

    def highest_scoring_suggestion(
            self,
            df: pd.DataFrame,
            filter_rows=True) -> pd.DataFrame:
        """
        df: could be a subset of the original dataframe, NOT one-hot-encoded
        filter_rows: if True, only rows that need correcting are returned, i.e.
        rows for which the __BEST_PREDICTION is equal to the original value
        are removed.

        Returns: DataFrame with addition columns as calculated by `give_suggestions`
        and three additional columns
        - "__BEST_SCORE" (containing the best score)
        - "__BEST_RULE" (the rule for which the best score was obtained)
        - "__BEST_PREDICTION" with the best prediction for the consequent
           given in "__BEST_RULE"
        """
        df_with_suggestions = self.give_suggestions(df)
        columns_to_select = [col for col in df_with_suggestions.columns
                             if col[:8] == "__SCORE:"]

        scores = df_with_suggestions[columns_to_select].values
        best_score_indices = np.argmax(scores, axis=1)

        df_with_suggestions["__BEST_SCORE"] = np.amax(scores, axis=1)
        df_with_suggestions["__BEST_RULE"] = \
            [columns_to_select[i][8:] for i in best_score_indices]

        # See: https://pandas.pydata.org/pandas-docs/stable/user_guide/indexing.html#indexing-lookup
        idx, cols = pd.factorize(
            df_with_suggestions['__BEST_RULE'].apply(lambda x: "__PREDICTION:" + x))

        df_with_suggestions['__BEST_PREDICTION'] = \
            (df_with_suggestions.reindex(cols, axis=1)
                                .to_numpy()[np.arange(len(df_with_suggestions)), idx])

        if filter_rows:
            predictions = df_with_suggestions['__BEST_PREDICTION']
            cfg.logger.debug(f"predictions: {predictions}")
            rhs_col = (df_with_suggestions['__BEST_RULE']
                       .apply(lambda x: x.split(' => ')[1].strip()))
            cfg.logger.debug(f"rhs_col: {rhs_col}")
            idx, cols = pd.factorize(rhs_col)
            actual_values = \
                (df_with_suggestions.reindex(cols, axis=1)
                                    .to_numpy()[np.arange(len(df_with_suggestions)), idx])
            # Remove rows for which the best prediction is equal to the original value
            df_with_suggestions = df_with_suggestions[predictions != actual_values]

        return df_with_suggestions
