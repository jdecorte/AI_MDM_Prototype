import pandas as pd
import numpy as np
import math
from backend.RuleFinding.CR.ColumnRule import ColumnRule, fi_measure, g3_measure, rfi_measure


def test_column_rule_creation():
    rule_string = "A => B"

    value_mapping = {
        frozenset(["A_a1"]): "B_b1",
        frozenset(["A_a2"]): "B_b2",
    }

    df = pd.DataFrame(
        {'A': ["a1", "a1", "a2"],
         'B': ["x", "y", "z"],
         'C': ["c", "c", "c"]}
    )

    cr = ColumnRule(rule_string=rule_string,
                    value_mapping=value_mapping,
                    original_df=df)

    df_to_be_corrected = cr.df_to_correct

    assert df_to_be_corrected.shape == (3, 6)
    assert "SUGGEST_CON" in df_to_be_corrected.columns
    assert "FOUND_CON" in df_to_be_corrected.columns
    assert "RULESTRING" in df_to_be_corrected.columns

    assert df_to_be_corrected['FOUND_CON'].equals(pd.Series(["x", "y", "z"]))
    assert df_to_be_corrected['SUGGEST_CON'].equals(
        pd.Series(["b1", "b1", "b2"]))
    assert df_to_be_corrected['RULESTRING'].equals(
        pd.Series([rule_string, rule_string, rule_string]))

    # Check confidence
    assert cr.confidence == 0.0

    # Check mapping df
    mapping_df = cr.mapping_df
    assert mapping_df.shape == (2, 2)
    assert "A" in mapping_df.columns
    assert "B" in mapping_df.columns
    assert mapping_df['A'].reset_index(drop=True).equals(pd.Series(["a1", "a2"]))
    assert mapping_df['B'].reset_index(drop=True).equals(pd.Series(["b1", "b2"]))


def test_column_rule_creation_bis():
    # Test that correct rows do not appear in the dataframe to correct
    rule_string = "A => B"

    value_mapping = {
        frozenset(["A_a1"]): "B_b1",
        frozenset(["A_a2"]): "B_b2",
    }

    df = pd.DataFrame(
        {'A': ["a1", "a1", "a1", "a1", "a1", "a2", "a2"],
         'B': ["b1", "b1", "b1", "x", "y", "z", "b2"],
         'C': ["c", "c", "c", "c", "c", "c", "c"]}
    )

    cr = ColumnRule(rule_string=rule_string,
                    original_df=df,
                    value_mapping=value_mapping)
    df_to_be_corrected = cr.df_to_correct

    assert df_to_be_corrected.shape == (3, 6)

    assert (df_to_be_corrected['FOUND_CON'].reset_index(drop=True).
            equals(pd.Series(["x", "y", "z"])))
    assert (df_to_be_corrected['SUGGEST_CON'].reset_index(drop=True).
            equals(pd.Series(["b1", "b1", "b2"])))
    assert (df_to_be_corrected['RULESTRING'].reset_index(drop=True).
            equals(pd.Series([rule_string, rule_string, rule_string])))


def test_predict():
    rule_string = "A => B"

    value_mapping = {
        frozenset(["A_a1"]): "B_b1",
        frozenset(["A_a2"]): "B_b2",
    }

    df = pd.DataFrame(
        {'A': ["a1", "a1", "a2"],
         'B': ["x", "y", "z"],
         'C': ["c", "c", "c"]}
    )

    cr = ColumnRule(rule_string=rule_string,
                    value_mapping=value_mapping,
                    original_df=df)

    predicted_values = cr.predict(df)

    assert predicted_values.shape == (df.shape[0], 2)
    assert (predicted_values['A'].reset_index(drop=True).
            equals(pd.Series(["a1", "a1", "a2"])))
    assert (predicted_values['B'].reset_index(drop=True).
            equals(pd.Series(["b1", "b1", "b2"])))


def test_status():
    rule_string = "A => B"

    value_mapping = {
        frozenset(["A_a1"]): "B_b1",
        frozenset(["A_a2"]): "B_b2",
    }

    df = pd.DataFrame(
        {'A': ["a1", "a1", "a2"],
         'B': ["x", "y", "z"],
         'C': ["c", "c", "c"]}
    )

    cr = ColumnRule(rule_string=rule_string,
                    value_mapping=value_mapping,
                    original_df=df)

    df_for_status = pd.DataFrame(
        {'A': ["a1", "a1", "a2", "a2"],
         'B': ["x", "b1", "b2", "y"],
         'C': ["c", "c", "c", "c"]}
    )

    status = cr.status(df_for_status)

    assert np.array_equal(status, np.array([-1, 1, 1, -1]))

# Test some measures


def test_g3_measure_1():
    """ Result for Table 3.1 in https://documentserver.uhasselt.be/bitstream/1942/35321/1/845d31c7-7084-4c8b-a964-d10bad246e52.pdf
    """
    a = ['a1'] * 10 + ['a2'] * 5
    b = ['b1'] * 9 + ['b2'] + ['b3'] * 4 + ['b2']

    table31 = pd.DataFrame({'A': a, 'B': b})

    result = g3_measure(table31, ['A'], 'B')

    assert math.isclose(result, 11/13)


def test_g3_measure_on_cr_1():
    """ Result for Table 3.1 in https://documentserver.uhasselt.be/bitstream/1942/35321/1/845d31c7-7084-4c8b-a964-d10bad246e52.pdf
    """
    a = ['a1'] * 10 + ['a2'] * 5
    b = ['b1'] * 9 + ['b2'] + ['b3'] * 4 + ['b2']

    # Create a column rule to compute G3 from.
    # Value mapping is not used in this test, but needed to create a ColumnRule.
    cr = ColumnRule("A => B",
                    pd.DataFrame({'A': a, 'B': b}),
                    {frozenset(['A_a1']): 'B_b1', frozenset(['A_a2']): 'B_b2'})

    result = cr.compute_g3_measure()

    assert math.isclose(result, 11/13)


def test_g3_measure_2():
    """ Result for Figure 3.4 in https://documentserver.uhasselt.be/bitstream/1942/35321/1/845d31c7-7084-4c8b-a964-d10bad246e52.pdf
    """
    a = [1] * 10 + [2] * 10
    b = [1] * 9 + [2] + [3] * 9 + [4]

    table32 = pd.DataFrame({'A': a, 'B': b})

    result = g3_measure(table32, ['A'], 'B')

    assert math.isclose(result, 8/9)


def test_g3_measure_3():
    """ Result for Figure 3.5 in https://documentserver.uhasselt.be/bitstream/1942/35321/1/845d31c7-7084-4c8b-a964-d10bad246e52.pdf
    """
    # left
    a = [1] * 10
    b = [1] * 5 + [2] * 5

    table = pd.DataFrame({'B': b, 'A': a})
    result = g3_measure(table, ['A'], 'B')
    assert math.isclose(result, 4/9)

    # right
    a = [1] * 10
    b = [1] * 5 + [2, 3, 4, 5, 6]

    table = pd.DataFrame({'B': b, 'A': a})
    result = g3_measure(table, ['A'], 'B')
    assert math.isclose(result, 4/9)


def test_g3_measure_4():
    a = [1] * 10
    b = [1] * 8 + [2, 3]

    table = pd.DataFrame({'A': a, 'B': b})
    result = g3_measure(table, ['A'], 'B')
    assert math.isclose(result, 7/9)


def test_g3_measure_multiple_columns():
    a = [1] * 5 + [2] * 5 + [3] * 5
    b = [3] * 5 + [3] * 5 + [1] * 5
    c = [4] * 5 + [5] * 5 + [4] * 5  # a + b = c

    table = pd.DataFrame({'A': a, 'B': b, 'C': c})
    result = g3_measure(table, ['A', 'B'], 'C')
    assert math.isclose(result, 1)


def test_g3_measure_multiple_columns_2():
    a = [1] * 5 + [2] * 5 + [3] * 5
    b = [3] * 5 + [3] * 5 + [1] * 5
    c = [4] * 4 + [0] + [5] * 5 + [4] * 5  # a + b = c, but one mistake

    table = pd.DataFrame({'A': a, 'B': b, 'C': c})
    result = g3_measure(table, ['A', 'B'], 'C')
    assert math.isclose(result, 11/12)


def test_g3_measure_multiple_columns_3():
    a = [1] * 5 + [2] * 5 + [3] * 5
    b = [3] * 5 + [3] * 5 + [1] * 5
    c = [4] * 4 + [0] + [5] * 5 + [4] * 5  # a + b = c, but one mistake
    # Add some irrelevant columns
    d = ['d'] * 15
    e = ['e' + str(i) for i in range(15)]

    table = pd.DataFrame({'A': a, 'D': d, 'B': b, 'C': c, 'E': e})
    result = g3_measure(table, ['A', 'B'], 'C')
    assert math.isclose(result, 11/12)


def test_fi_measure_multiple_columns():
    a = [1] * 5 + [2] * 5 + [3] * 5
    b = [3] * 5 + [3] * 5 + [1] * 5
    c = [4] * 5 + [5] * 5 + [4] * 5  # a + b = c

    table = pd.DataFrame({'A': a, 'B': b, 'C': c})
    result = fi_measure(table, ['A', 'B'], 'C')
    assert math.isclose(result, 1)


def test_fi_measure_1():
    # Figure 3.7
    a = []
    b = []
    for i in range(1, 11):
        a += [i] * 1000
        b += [1] * 999 + [2]

    df = pd.DataFrame({'A': a, 'B': b})
    result = fi_measure(df, ['A'], 'B')

    # Compute the result manually
    entropy_y = -(9990/10_000 * np.log2(9990/10_000) + 10/10_000 * np.log2(10/10_000))
    entropy_y_given_x = 0.0
    for x in range(1, 11):
        for y in range(1, 3):
            if y == 1:
                pxy = 999/10_000
            else:
                pxy = 1/10_000
            px = 1/10
            entropy_y_given_x += pxy * np.log2(pxy / px)

    entropy_y_given_x *= -1
    result_manual = (entropy_y - entropy_y_given_x)/entropy_y

    assert math.isclose(result, result_manual)


def test_fi_measure_2():
    # Figure 3.8
    a = []
    for i in range(1, 1001):
        a += [i] * 10
    b = []
    for i in range(1, 2001):
        b += [i] * 5

    df = pd.DataFrame({'A': a, 'B': b})
    result = fi_measure(df, ['A'], 'B')

    # compute result manually
    entropy_y = -2000 * 5/10_000 * np.log2(5/10_000)
    entropy_y_given_x = -2000 * (5/10_000) * np.log2((5/10_000) / (10/10_000))

    result_manual = (entropy_y - entropy_y_given_x)/entropy_y

    assert math.isclose(result, result_manual)


def test_fi_measure_3():
    # Figure 3.9, example 8 (left hand side)
    a = [1] * 5000 + [2] * 5000
    b = [1] * 5000 + [2] * 4500 + [_ for _ in range(3, 503)]
    # Add some random columns to test the implementation
    c = [_ for _ in range(10_000)]

    df = pd.DataFrame({'C': c, 'A': a, 'B': b})
    result = fi_measure(df, ['A'], 'B')

    # compute result manually
    entropy_y = -(0.5 * np.log2(0.5) + 4500/10_000 * np.log2(0.45)
                  + 500 * 1/10_000 * np.log2(1/10_000))
    entropy_y_given_x = -(0.5 * np.log2(0.5/0.5) + 0.45 * np.log2(0.45/0.5)
                          + 500 * 1/10_000 * np.log2(1/10_000/0.5))

    result_manual = (entropy_y - entropy_y_given_x)/entropy_y

    assert math.isclose(result, result_manual)

    # Example on right hand side of figure 3.9
    a = [1] * 5000 + [2] * 5000
    b = [1] * 5000 + [2] * 4500 + [3] * 500
    # Add some random columns to test the implementation
    c = [_ for _ in range(10_000)]

    df = pd.DataFrame({'C': c, 'A': a, 'B': b})
    result = fi_measure(df, ['A'], 'B')

    # compute result manually
    entropy_y = -(0.5 * np.log2(0.5) + 4500/10_000 * np.log2(0.45)
                  + 500/10_000 * np.log2(0.05))
    entropy_y_given_x = -(0.5 * np.log2(0.5/0.5) + 0.45 * np.log2(0.45/0.5)
                          + 500/10_000 * np.log2(0.05/0.5))

    result_manual = (entropy_y - entropy_y_given_x)/entropy_y

    assert math.isclose(result, result_manual)


# This test takes about 90 seconds to run
def test_rfi_measure_1():
    # Figure 3.8
    a = []
    for i in range(1, 1001):
        a += [i] * 10
    b = []
    for i in range(1, 2001):
        b += [i] * 5

    df = pd.DataFrame({'A': a, 'B': b})
    result = rfi_measure(df, ['A'], 'B')

    # Using result from the thesis
    assert math.isclose(result, 0.211, abs_tol=0.001)


def test_c_measure_1():
    a = []
    b = []
    for i in range(1, 11):
        a += [str(i)] * 1000
        b += [str(i)] * 990 + [str(i+1) if i < 10 else '1'] * 10

    df = pd.DataFrame({'A': a, 'B': b})
    value_mapping = {
        frozenset([f"A_{i}"]): f"B_{i}" for i in range(1, 11)
    }
    cr = ColumnRule(rule_string="A => B", original_df=df,
                    value_mapping=value_mapping, confidence=0.0)

    c_measure = cr.compute_c_measure()
    assert math.isclose(c_measure, 4.915, abs_tol=0.001)  # Using result from the thesis

    fi = cr.compute_fi_measure()
    assert math.isclose(fi, 0.976, abs_tol=0.001)  # Using result from the thesis
    g3 = cr.compute_g3_measure()
    assert math.isclose(g3, 0.99, abs_tol=0.01)  # Using result from the thesis
    rfi = cr.compute_rfi_measure()
    assert math.isclose(rfi, 0.974, abs_tol=0.01)  # Using result from the thesis

if __name__ == "__main__":
    a = []
    b = []
    for i in range(1, 11):
        a += [str(i)] * 1000
        b += [str(i)] * 990 + [str(i+1) if i < 10 else '1'] * 10

    df = pd.DataFrame({'A': a, 'B': b})
    value_mapping = {
        frozenset([f"A_{i}"]): f"B_{i}" for i in range(1, 11)
    }    
    cr = ColumnRule("A => B", df, value_mapping)
