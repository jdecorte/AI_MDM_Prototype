import src.backend.Suggestions.SuggestionFinder as sf
import src.backend.RuleFinding.CR.ColumnRule as cr
import pandas as pd


def test_suggestions_no_errors():
    """
    When the dataframe contains no errors, then all predictions should be
    the same as the original values.

    Hence, when filter_rows is True, then the returned dataframe should be empty.

    Here, we test this for a single column rule.
    """
    rule_string = "A,B => C"
    value_mapping = True

    # C is the sum of A and B
    # Add another column
    df = pd.DataFrame(
        {'A': ["a1"] * 10 + ["a2"] * 10,
         'C': ["c2"] * 10 + ["c4"] * 10,
         'B': ["b1"] * 10 + ["b2"] * 10,
         'D': ["d"] * 20
         }
    )

    column_rule = cr.ColumnRule(rule_string=rule_string,
                                original_df=df,
                                value_mapping=value_mapping)

    suggestion_finder = sf.SuggestionFinder([column_rule], df)

    suggestion_df = suggestion_finder.highest_scoring_suggestion(df, filter_rows=False)

    assert suggestion_df.shape[0] == df.shape[0]
    assert suggestion_df['__BEST_PREDICTION'].equals(df['C'])

    suggestion_df = suggestion_finder.highest_scoring_suggestion(df, filter_rows=True)
    assert suggestion_df.shape[0] == 0


def test_suggestions_no_errors_2():
    """
    When the dataframe contains no errors, then all predictions should be
    the same as the original values.

    Hence, when filter_rows is True, then the returned dataframe should be empty.

    Here, we test this for a two column rules.
    """
    rule_string = "A,B => C"
    value_mapping = True

    # C is the sum of A and B
    # Add another column
    df = pd.DataFrame(
        {'A': ["a1"] * 10 + ["a2"] * 10,
         'C': ["c2"] * 10 + ["c4"] * 10,
         'B': ["b1"] * 10 + ["b2"] * 10,
         'D': ["d"] * 20
         }
    )

    column_rule = cr.ColumnRule(rule_string=rule_string,
                                original_df=df,
                                value_mapping=value_mapping)

    # Second rule that is completely correct
    column_rule2 = cr.ColumnRule(rule_string="A => B",
                                 original_df=df,
                                 value_mapping=value_mapping)

    suggestion_finder = sf.SuggestionFinder([column_rule, column_rule2], df)

    suggestion_df = suggestion_finder.highest_scoring_suggestion(df, filter_rows=False)

    assert suggestion_df.shape[0] == df.shape[0]
    assert suggestion_df['__BEST_PREDICTION'].equals(df['C'])

    suggestion_df = suggestion_finder.highest_scoring_suggestion(df, filter_rows=True)
    assert suggestion_df.shape[0] == 0
