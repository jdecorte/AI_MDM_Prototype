import pandas as pd
import numpy as np
import config as cfg

from src.backend.RuleFinding.CR.ColumnRule import ColumnRule

from typing import Sequence

class SuggestionFinder:

    def __init__(self, column_rules : Sequence[ColumnRule], original_df):
        self.column_rules = column_rules
        self.original_df = original_df


        # Maak de dataframe met foute rows aan
        cfg.logger.info(f"Found {len(self.column_rules)} interesting rules in the dataset")
        self.df_errors_ = self.combine_all_errors(self.column_rules)         

        cfg.logger.info(f"Total number of values that might need correcting: {self.df_errors_.shape[0]}")



    
    def combine_all_errors(self, column_rules : Sequence[ColumnRule]) -> pd.DataFrame:
        """
        Gathers all the rows that need to be corrected into a single pandas DataFrame.

        column_rules: a sequence of columns rules.
        """
        if len(column_rules) == 0:
            return pd.DataFrame()
        return pd.concat([column_rule.df_to_correct for column_rule in column_rules], axis=0)


    def give_suggestions(self, df : pd.DataFrame) -> pd.DataFrame:
        """ 

        df: could be a subset of the orginal dataframe, NOT one-hot-encoded

        Returns: dataframe with additional columns. Two columns per rule. 
        One column with the 'score' for this rule '__SCORE:' + rulestring, 
        and one column with the prediction made by this rule with name '__PREDICTION:' + rulestring

        """
        cfg.logger.debug(f"give_suggestion receives the following DataFrame")
        cfg.logger.debug(df)

        for cr in self.column_rules:

            consequent_column_name = list(cr.consequent_set)[0]

            # Take backup up original column in DataFrame
            
            original_column = df[consequent_column_name].copy()

            predicted_column = cr.predict(df)[consequent_column_name]

            # Change original df, with predicted column
            predicted_column.index = df.index # Make sure to use the same index ! 
            cfg.logger.debug(f"The predicted column is {predicted_column}")
            df[consequent_column_name] = predicted_column 

            cfg.logger.debug(f"After assigning to df {df[consequent_column_name]}")

            # Check hoeveel de score is voor elke suggestie
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

    def highest_scoring_suggestion(self, df : pd.DataFrame) -> pd.DataFrame:
        """
        df: could be a subset of the orginal dataframe, NOT one-hot-encoded

        Returns: DataFrame with addition columns as calculated by `give_suggestions` 
        and three additional columns "__BEST_SCORE" (containing the best score), "__BEST_RULE"
        (the rule for which the best score was obtained) and "__BEST_PREDICTION" with the 
        best prediction for the consequent given in "__BEST_RULE"
        """
        df_with_suggestions = self.give_suggestions(df)
        columns_to_select =[col for col in df_with_suggestions.columns if col[:8] == "__SCORE:"]

        scores = df_with_suggestions[columns_to_select].values
        best_score_indices = np.argmax(scores, axis=1)
        
        df_with_suggestions["__BEST_SCORE"] = np.amax(scores, axis=1)
        df_with_suggestions["__BEST_RULE"] = [columns_to_select[i][8:] for i in best_score_indices]

        # 
        # See: https://pandas.pydata.org/pandas-docs/stable/user_guide/indexing.html#indexing-lookup
        idx, cols = pd.factorize(df_with_suggestions['__BEST_RULE'].apply(lambda x: "__PREDICTION:" + x))

        df_with_suggestions['__BEST_PREDICTION'] = \
            df_with_suggestions.reindex(cols, axis =1).to_numpy()[np.arange(len(df_with_suggestions)), idx]

        return df_with_suggestions