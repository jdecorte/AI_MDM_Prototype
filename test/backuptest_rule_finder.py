import pandas as pd
import numpy as np

import math

from sklearn.feature_selection import SequentialFeatureSelector

from rule_finder import *

def test_findsubsets():
    subsets : List[Set[Any]] = findsubsets("a")
    assert len(subsets) == 2
    assert subsets[0] == set()
    assert subsets[-1] == set("a")

    subsets : List[Set[Any]] = findsubsets(set("a"))
    assert len(subsets) == 2
    assert subsets[0] == set()
    assert subsets[-1] == set("a")

    subsets : List[Set[Any]] = findsubsets(["a", "b"])
    assert len(subsets) == 4
    assert subsets[-1] == set("ab")


def test_subsets_minus_one():
    s = set(["A", "B", "C"])
    subsets = subsets_minus_one(s)

    assert len(subsets) == len(s)

    assert set(["A", "B"]) in subsets
    assert set(["A", "C"]) in subsets
    assert set(["B", "C"]) in subsets

    # Check that it also works for frozenset
    s = frozenset(["A", "B", "C"])
    subsets = subsets_minus_one(s)

    assert len(subsets) == len(s)

    assert set(["A", "B"]) in subsets
    assert set(["A", "C"]) in subsets
    assert set(["B", "C"]) in subsets
    
def test_filter_constant_columns():
    # Test whether column with nothing but Na values gets removed

    df = pd.DataFrame(data = {
            'Missing' : [None, None, None, None, None],
            'SomeMissing' : [None, None, 42, 43, 44],
            'A' : [1,2,3,4,5],
            'Constant' : ["c", "c", "c", "c", "c"],
            'ConstantAndMissing' : ["d", None, "d", None, "d"],
            'ConstantAndEmptyString' :  ["d", "", "d", "", "d"]
        })

    df_filtered = filter_constant_columns(df, do_not_count_nan_values=False)

    # Check that columns are removed
    assert 'Missing' not in df_filtered.columns
    assert 'Constant' not in df_filtered.columns

    # Check that columns are still present
    assert 'SomeMissing' in df_filtered.columns
    assert 'A' in df_filtered.columns
    assert 'ConstantAndMissing' in df_filtered.columns
    assert 'ConstantAndEmptyString' in df_filtered.columns


    # Check that no rows were removed
    assert df_filtered.shape[0] == df.shape[0]

    # Try to check that original DataFrame has no columns removed
    assert 'Missing' in df.columns

def test_filter_constant_columns_2():
    df = pd.DataFrame(data = {
            'Missing' : [None, None, None, None, None],
            'SomeMissing' : [None, None, 42, 43, 44],
            'A' : [1,2,3,4,5],
            'Constant' : ["c", "c", "c", "c", "c"],
            'ConstantAndMissing' : ["d", np.nan, "d", np.nan, "d"],
            'TweeWaarden' : [1,2,2,1,2],
            'ConstantAndEmptyString' :  ["d", "", "d", "", "d"]
        })

    print(df.head())

    print(df['ConstantAndMissing'].unique())


    df_filtered = filter_constant_columns(df, do_not_count_nan_values=True)

    # Check that columns are removed
    assert 'Missing' not in df_filtered.columns
    assert 'Constant' not in df_filtered.columns
    assert 'ConstantAndMissing' not in df_filtered.columns
    assert 'ConstantAndEmptyString' not in df_filtered.columns


    # Check that columns are still present
    assert 'SomeMissing' in df_filtered.columns
    assert 'A' in df_filtered.columns

    assert 'TweeWaarden' in df_filtered.columns


    # Check that no rows were removed
    assert df_filtered.shape[0] == df.shape[0]

    # Try to check that original DataFrame has no columns removed
    assert 'Missing' in df.columns

def  test_lemma_df_to_rule_map():
    rule_string_2_valuerule : Dict[str, Set[ValueRule]] = {}

    row = np.array([frozenset(["A_a1"]), frozenset(["C_c1"]), 1.0, 0.5, 2.0])
    lemma_df_to_rule_map(row, rule_string_2_valuerule)

    # Check that key is in dictionary
    assert "A => C" in rule_string_2_valuerule.keys()
    # Check that the set contains a single item
    assert len(rule_string_2_valuerule["A => C"] ) == 1

    row2 = np.array([frozenset(["A_a2"]), frozenset(["C_c2"]), 1.0, 0.5, 2.0])

    lemma_df_to_rule_map(row2, rule_string_2_valuerule)

    # Check that key is (still) in dictionary
    assert "A => C" in rule_string_2_valuerule.keys()
    # Check that the set contains a single item
    assert len(rule_string_2_valuerule["A => C"] ) == 2

    print(rule_string_2_valuerule["A => C"])

    row3 = np.array([frozenset(["B_b1","A_a3"]), frozenset(["C_c3"]), 0.99, 0.5, 2.0])

    lemma_df_to_rule_map(row3, rule_string_2_valuerule)

    assert "A => C" in rule_string_2_valuerule.keys()
    assert "A,B => C" in rule_string_2_valuerule.keys()

    assert len(rule_string_2_valuerule["A => C"] ) == 2
    assert len(rule_string_2_valuerule["A,B => C"] ) == 1


def test_filter_low_support_moves():
    rs_2_vr : Dict[str, Set[ValueRule]] = {
        "A => B" : set([ValueRule([RuleElement("A", "a1")], [RuleElement("B", "b1")], 0.5, 2, 1.0),
                       ValueRule([RuleElement("A", "a2")], [RuleElement("B", "b2")], 0.3, 2, 1.0)]
                       ),
        "A => C" : set([ValueRule([RuleElement("A", "a1")], [RuleElement("C", "c1")], 0.5, 2, 1.0)])
    }

    min_support = 0.4 # no rules should be removed
    removed_rules, kept_rules = filter_low_support_rules(rs_2_vr, min_support=min_support)
    assert len(removed_rules) == 0
    assert len(kept_rules) == 2
    assert len(rs_2_vr) == 2

    min_support = 0.5 # Still no rules should be removed (equal)
    removed_rules, kept_rules = filter_low_support_rules(rs_2_vr, min_support=min_support)
    assert len(removed_rules) == 0
    assert len(kept_rules) == 2
    assert len(rs_2_vr) == 2

    min_support = 0.6 # one rule should be removed A => C
    removed_rules, kept_rules = filter_low_support_rules(rs_2_vr, min_support=min_support)
    assert len(removed_rules) == 1
    assert "A => C" in removed_rules
    assert len(kept_rules) == 1
    assert "A => B" in kept_rules
    assert len(rs_2_vr) == 2
    assert "A => B" in rs_2_vr
    assert "A => C" in rs_2_vr

    min_support = 0.8 # one rule should be removed A => C
    removed_rules, kept_rules = filter_low_support_rules(rs_2_vr, min_support=min_support)
    assert len(removed_rules) == 1
    assert "A => C" in removed_rules
    assert len(kept_rules) == 1
    assert "A => B" in kept_rules
    assert len(rs_2_vr) == 2
    assert "A => B" in rs_2_vr
    assert "A => C" in rs_2_vr

    min_support = 0.9 # two rules should be removed
    removed_rules, kept_rules = filter_low_support_rules(rs_2_vr, min_support=min_support)
    assert len(removed_rules) == 2
    assert "A => C" in removed_rules
    assert "A => B" in removed_rules
    assert len(kept_rules) == 0
    assert len(rs_2_vr) == 2
    assert "A => B" in rs_2_vr
    assert "A => C" in rs_2_vr    


def test_calculate_max_confidence():
    # Singe value rule with confidence 1 should result in max confidence of 1
    vrs = set([ValueRule([RuleElement("A", "a1")], [RuleElement("C", "c1")], 0.5, 2, 1.0)])

    max_confidence = calculate_max_confidence(vrs)
    assert max_confidence == 1.0

    # Multiple value rules with confidence should result in max confidence of 1
    vrs = set([
        ValueRule([RuleElement("A", "a1")], [RuleElement("C", "c1")], 0.5, 2, 1.0),
        ValueRule([RuleElement("A", "a2")], [RuleElement("C", "c2")], 0.2, 2, 1.0)
        ])

    max_confidence = calculate_max_confidence(vrs)
    assert max_confidence == 1.0

    # Multiple value rules with confidence 0 should result in max confidence of 1 - total_support
    vrs = set([
        ValueRule([RuleElement("A", "a1")], [RuleElement("C", "c1")], 0.5, 2, 0.0),
        ValueRule([RuleElement("A", "a2")], [RuleElement("C", "c2")], 0.2, 2, 0.0)        
        ])
    max_confidence = calculate_max_confidence(vrs)
    assert math.isclose(max_confidence, 0.3)

    # General case
    vrs = set([
        ValueRule([RuleElement("A", "a1")], [RuleElement("C", "c1")], 0.5, 2, 1.0),
        ValueRule([RuleElement("A", "a2")], [RuleElement("C", "c2")], 0.2, 2, 0.8)        
        ])
    max_confidence = calculate_max_confidence(vrs)
    assert math.isclose(max_confidence, 0.5*1.0 + 0.2*0.8 + 0.3)


def test_transform_rulemap_2_filtered_rulemap():
    rs_2_vr : Dict[str, Set[ValueRule]] = {
        "A => B" : set([ValueRule([RuleElement("A", "a1")], [RuleElement("B", "b1")], 0.5, 2, 1.0),
                       ValueRule([RuleElement("A", "a2")], [RuleElement("B", "b2")], 0.3, 2, 1.0)]
                       ),
        "A => C" : set([ValueRule([RuleElement("A", "a1")], [RuleElement("C", "c1")], 0.5, 2, 1.0)])
    }

    # Check that a rule is removed
    removed_rules, kept_rules = transform_rulemap_2_filtered_rulemap(rs_2_vr, min_support=0.6)
    assert len(removed_rules) == 1
    assert "A => C" in removed_rules

    assert len(kept_rules) == 1
    assert "A => B" in kept_rules

    assert len(rs_2_vr) == 2

    # Check that a rule A,B => C will be removed if B => C has higher potential confidence
    rs_2_vr : Dict[str, Set[ValueRule]] = {
        "A,B => C" : set([ValueRule([RuleElement("A", "a1"), RuleElement("B", "b1")], 
                        [RuleElement("C", "c1")], 0.5, 2, 0.8),
                       ValueRule([RuleElement("A", "a2"), RuleElement("B", "b2")],
                        [RuleElement("C", "c2")], 0.3, 2, 0.8)]
                       ),
        "B => C" : set([ValueRule([RuleElement("B", "b1")], [RuleElement("C", "c1")], 0.7, 2, 0.9)])
    }

    removed_rules, kept_rules = transform_rulemap_2_filtered_rulemap(rs_2_vr, 0.6)
    assert len(removed_rules) == 0
    assert len(kept_rules) == 1
    assert "B => C" in kept_rules

     # Check that a rule A,B => D will be kept, even if B => C has higher confidence
    rs_2_vr : Dict[str, Set[ValueRule]] = {
        "A,B => C" : set([ValueRule([RuleElement("A", "a1"), RuleElement("B", "b1")], 
                        [RuleElement("C", "c1")], 0.5, 2, 0.8),
                       ValueRule([RuleElement("A", "a2"), RuleElement("B", "b2")],
                        [RuleElement("C", "c2")], 0.3, 2, 0.8)]
                       ),
        "B => C" : set([ValueRule([RuleElement("B", "b1")], [RuleElement("C", "c1")], 0.7, 2, 0.9)]),
        "A,B => D" : set([ValueRule([RuleElement("A", "a1"), RuleElement("B", "b1")], 
                         [RuleElement("D", "d1")], 0.5, 2, 0.8),
                       ValueRule([RuleElement("A", "a2"), RuleElement("B", "b2")],
                         [RuleElement("D", "d2")], 0.3, 2, 0.8)]
                       ),
    }

    removed_rules, kept_rules = transform_rulemap_2_filtered_rulemap(rs_2_vr, 0.6)
    assert len(removed_rules) == 0
    assert len(kept_rules) == 2
    assert "B => C" in kept_rules
    assert "A,B => D" in kept_rules



def test_df_2_rulemap():
    df = pd.DataFrame({
       'antecedents' : [frozenset(["A_a1"]), frozenset(["A_a2"])],
       'consequents' : [frozenset(["B_b1"]), frozenset(["B_b2"])],
       'support'     : [0.5,                 0.3],
       'confidence'  : [1.0,                 1.0],
       'lift'        : [2.0,                 3.0]
    })

    removed_rules, kept_rules = df_2_rulemap(df, 0.7)

    assert len(removed_rules) == 0
    assert len(kept_rules) == 1
    assert "A => B" in kept_rules
    # set of value rules should consist of two value rules
    assert len(kept_rules["A => B"]) == 2

    # Set the support threshold really high, so that the rule is removed
    removed_rules, kept_rules = df_2_rulemap(df, min_support=0.9)
    assert len(kept_rules) == 0

    assert len(removed_rules) == 1
    assert "A => B" in removed_rules
    # set of value rules should consist of two value rules
    assert len(removed_rules["A => B"]) == 2

def test_df_2_rulemap_bis():
    df = pd.DataFrame({
       'antecedents' : [frozenset(["A_a1", "B_b1"]), 
                        frozenset(["A_a2", "B_b2"]),
                        frozenset(["A_a3"])],
       'consequents' : [frozenset(["C_c1"]),
                        frozenset(["C_c2"]),
                        frozenset(["C_c3"])],
       'support'     : [0.25,
                        0.25,
                        0.5],
       'confidence'  : [0.9,
                        0.9,
                        1.0],
       'lift'        : [2.0,
                        3.0,
                        2.5]
    })

    # Check that rule A,B => C is properly filtered out in favor of A => C
    # Support is so that no rules are filterd out due to low support
    removed_rules, kept_rules = df_2_rulemap(df, 0.5)

    assert len(removed_rules) == 0
    assert len(kept_rules) == 1
    assert "A => C" in kept_rules
    assert len(kept_rules["A => C"]) == 1

def test_get_columns_for_mini_fp_growth():
    rule_string = "A,B => C"
    column_list = ["D_d","A_a1", "A_a2", "B_b1", "C_c1", "X_x", "C_c2", "Z_z"]

    cols_to_use = get_columns_for_mini_fp_growth(rule_string, column_list)

    assert len(cols_to_use) == 5
    for c in ["A_a1", "A_a2", "B_b1", "C_c1", "C_c2"]:
        assert c in cols_to_use 

    rule_string = "LongColumn,B => C"
    column_list = ["D_d","A_a1", "A_a2", "B_b1", "C_c1", "X_x", "LongColumn_x", "LongColumn_y"]

    cols_to_use = get_columns_for_mini_fp_growth(rule_string, column_list)

    assert len(cols_to_use) == 4
    for c in ["LongColumn_x", "LongColumn_y", "B_b1", "C_c1"]:
        assert c in cols_to_use 

    rule_string = "LongColumn,B => VeryLongColumn"
    column_list = ["D_d","A_a1", "A_a2", "B_b1", "VeryLongColumn_c1", "X_x", "LongColumn_x", "LongColumn_y"]

    cols_to_use = get_columns_for_mini_fp_growth(rule_string, column_list)

    assert len(cols_to_use) == 4
    for c in ["LongColumn_x", "LongColumn_y", "B_b1", "VeryLongColumn_c1"]:
        assert c in cols_to_use 

    


def test_create_df_query():
    mapping_dict : Dict[Sequence[str], str] = {
        ("A_a",) : "B_b"
    }

    query = ColumnRule._create_df_query(mapping_dict)

    assert query == '((`A` == "a") & (`B` != "b"))'

    mapping_dict : Dict[FrozenSet[str], str] = {
        ("A_a1", "B_b1") : "C_c1",
        ("A_a2", "B_b2") : "C_c2",
    }
   

    # This test might break due to different dictionary order ?
    query = ColumnRule._create_df_query(mapping_dict)

    assert query == '((`A` == "a1") & (`B` == "b1") & (`C` != "c1"))' + \
         ' | ((`A` == "a2") & (`B` == "b2") & (`C` != "c2"))'

def test_create_single_query_string():
    s = ColumnRule._create_single_query_string(["A_a","B_b"], "C_c")
    assert s == '((`A` == "a") & (`B` == "b") & (`C` != "c"))'


def test_create_mapping():
    value_rules = pd.DataFrame(
        {
            'antecedents' : [frozenset(["A_a1"]), frozenset(["A_a1"]), 
                             frozenset(["A_a2"]), frozenset(["C_c"])],
            'consequents' : [frozenset(["B_b1"]), frozenset(["B_b2"]), 
                            frozenset(["B_b3"]), frozenset(["B_b2"])],
            'confidence'  : [0.3, 0.7, 1.0, 1.0]
        }
    )

    value_mapping = create_mapping(value_rules, "A => B")

    assert len(value_mapping) == 2
    assert value_mapping[frozenset(["A_a1"])] == "B_b2"
    assert value_mapping[frozenset(["A_a2"])] == "B_b3"

    value_rules = pd.DataFrame(
        {
            'antecedents' : [frozenset(["A_a1"]), frozenset(["A_a1"]), 
                             frozenset(["A_a2"]), frozenset(["D_d", "C_c"])],
            'consequents' : [frozenset(["B_b1"]), frozenset(["B_b2"]), 
                            frozenset(["B_b3"]), frozenset(["B_b2"])],
            'confidence'  : [0.3, 0.7, 1.0, 1.0]
        }
    )

    value_mapping = create_mapping(value_rules, "C,D => B")

    assert len(value_mapping) == 1
    assert value_mapping[frozenset(["D_d","C_c"])] == "B_b2"



def test_ColumnRule_init():
    rule_string = "A => B"

    value_mapping = {
        frozenset(["A_a1"]) : "B_b1",
        frozenset(["A_a2"]) : "B_b2",
    }

    df = pd.DataFrame(
        {'A' : ["a1", "a1", "a2"],
         'B' : ["x", "y", "z"],
         'C' : ["c", "c", "c"]
        }
    )

    cr = ColumnRule(rule_string, value_mapping, df)

    df_to_be_corrected = cr.df_to_correct

    assert df_to_be_corrected.shape == (3,6)
    assert "SUGGEST_CON" in df_to_be_corrected.columns
    assert "FOUND_CON" in df_to_be_corrected.columns
    assert "RULESTRING" in df_to_be_corrected.columns

    assert df_to_be_corrected['FOUND_CON'].equals(pd.Series(["x", "y", "z"]))
    assert df_to_be_corrected['SUGGEST_CON'].equals(pd.Series(["b1", "b1", "b2"]))
    assert df_to_be_corrected['RULESTRING'].equals(pd.Series([rule_string, rule_string, rule_string]))

def test_ColumnRule_init_bis():
    # Test that correct rows do not appear in the dataframe to correct    
    rule_string = "A => B"

    value_mapping = {
        frozenset(["A_a1"]) : "B_b1",
        frozenset(["A_a2"]) : "B_b2",
    }

    df = pd.DataFrame(
        {'A' : ["a1", "a1", "a1","a1", "a1", "a2", "a2"],
         'B' : ["b1", "b1", "b1", "x", "y", "z", "b2"],
         'C' : ["c", "c", "c","c", "c", "c", "c"]
        }
    )

    cr = ColumnRule(rule_string, value_mapping, df)
    df_to_be_corrected = cr.df_to_correct

    assert df_to_be_corrected.shape == (3,6)

    assert (df_to_be_corrected['FOUND_CON'].reset_index(drop=True).
        equals(pd.Series(["x", "y", "z"])))
    assert (df_to_be_corrected['SUGGEST_CON'].reset_index(drop=True).
        equals(pd.Series(["b1", "b1", "b2"])))
    assert (df_to_be_corrected['RULESTRING'].reset_index(drop=True).
        equals(pd.Series([rule_string, rule_string, rule_string])))


def test_expand_single_column_rule():
    rule_string = "A => B"
    df = pd.DataFrame(
        {
            'A' : ['a1', 'a1', 'a1', 'a2', 'a2', 'a2'],
            'B' : ['b1', 'b1', 'x' ,  'y', 'b2', 'b2']
        }
    )
    df_dummy = pd.get_dummies(df, dtype=np.bool8)

    column_rule = expand_single_column_rule(rule_string, df_dummy, df)

    assert column_rule.antecedent_set == frozenset(['A'])
    assert column_rule.consequent_set == frozenset(['B'])
    assert column_rule.rule_string == "A => B"
    assert column_rule.value_mapping[frozenset(["A_a1"])] == 'B_b1'
    assert column_rule.value_mapping[frozenset(["A_a2"])] == 'B_b2'

    assert column_rule.df_to_correct.shape[0] == 2 # Two rows contain an error

    # TODO: check contents of the dataframe

    assert math.isclose(column_rule.confidence, 4/6)


def test_expand_column_rules():
    df = pd.DataFrame(
        {
            'A' : ['a1', 'a1', 'a1', 'a2', 'a2', 'a2'],
            'B' : ['b1', 'b1', 'x' ,  'y', 'b2', 'b2'],
            'C' : ['c1', 'c1', 'c1', 'c1', 'c1', 'c2']
        }
    )
    rule_strings = ["A => B", "C => B"]
    df_dummy = pd.get_dummies(df, dtype=np.bool8)

    column_rules: Sequence[ColumnRule] = expand_column_rules(rule_strings, df_dummy, df)

    assert len(column_rules) == 2

    # Check mapping A => B
    assert column_rules[0].antecedent_set == frozenset(['A'])
    assert column_rules[0].consequent_set == frozenset(['B'])
    assert column_rules[0].rule_string == "A => B"
    assert column_rules[0].value_mapping[frozenset(["A_a1"])] == 'B_b1'
    assert column_rules[0].value_mapping[frozenset(["A_a2"])] == 'B_b2'

    assert column_rules[0].df_to_correct.shape[0] == 2 # Two rows contain an error

    # Check mapping C => B
    assert column_rules[1].antecedent_set == frozenset(['C'])
    assert column_rules[1].consequent_set == frozenset(['B'])
    assert column_rules[1].rule_string == "C => B"
    assert column_rules[1].value_mapping[frozenset(["C_c1"])] == 'B_b1'
    assert column_rules[1].value_mapping[frozenset(["C_c2"])] == 'B_b2'

    assert column_rules[1].df_to_correct.shape[0] == 3 # Three rows have a mistake


 
"""
XXX: Voorlopig uitschakelen totdat precieze gedrag is bepaald. 
XXX: Aan te passen aan nieuwe ColumnRule
def test_get_interesting_columns_rules():

    rules = [
        ColumnRule("A => D", {"a => b"}, 0.95, None, None), # fake dictionary
        ColumnRule("A,B => D", {"a,b =>  d"}, 0.9, None, None),
        ColumnRule("A,B,C => D", {"a,b,c => d"}, 0.9, None, None)
    ]

    interesting_rules = get_interesting_column_rules(rules)

    assert len(interesting_rules) == 1
    assert "A => D" in interesting_rules


    rules = [
        ColumnRule("A => D", {"a => b"}, 0.95, None, None),
        ColumnRule("A,B => D", {"a,b =>  d"}, 0.9, None, None),
        ColumnRule("A,B,C => D", {"a,b,c => d"}, 0.99, None, None) # only last one should be kept
    ]

    interesting_rules = get_interesting_column_rules(rules)

    assert len(interesting_rules) == 1
    assert "A,B,C => D" in interesting_rules

    rules = [
        ColumnRule("A => D", {"a => b"}, 0.95, None, None),
        ColumnRule("A,B => D", {"a,b =>  d"}, 0.99, None, None), # only this one should be kept
        ColumnRule("A,B,C => D", {"a,b,c => d"}, 0.9, None, None)
    ]

    interesting_rules = get_interesting_column_rules(rules)

    assert len(interesting_rules) == 1
    assert "A,B => D" in interesting_rules


    rules = [
        ColumnRule("AA => DD", {"a => b"}, 0.9, None, None), # This one should survive
        ColumnRule("AA,BB => DD",  {"a,b =>  d"}, 0.9, None, None),
        ColumnRule("AA,BB,CC => DD", {"a,b,c => d"}, 0.9, None, None)
    ]

    interesting_rules = get_interesting_column_rules(rules)

    assert len(interesting_rules) == 1
    assert "AA => DD" in interesting_rules
"""

def test_get_definitions():


    df = pd.DataFrame({
        'A' : ["a1", "a1", "a2", "a2"],
        'B' : ["b1", "b1", "b2", "b2"],
        'C' : ["c1", "c1", "c1", "c2"],
        'D' : ["d1", "d1", "d2", "d2"]
        })

    mapping_dict_ab = {
        frozenset(["A_a1"]) : "B_b1",
        frozenset(["A_a2"]) : "B_b2"
    }

    mapping_dict_ba = {frozenset([v]) : list(k)[0] for (k, v) in mapping_dict_ab.items()}

    mapping_dict_ac = {
        frozenset(["A_a1"]) : "C_c1",
        frozenset(["A_a2"]) : "C_c2"
    }

    mapping_dict_ca = {frozenset([v]) : list(k)[0] for (k, v) in mapping_dict_ac.items()}

    mapping_dict_abd = {
        frozenset(["A_a1", "B_b1"]) : "D_d1",
        frozenset(["A_a2", "B_b2"]) : "D_d2"
    }

    rules = [
        ColumnRule("A => B", mapping_dict_ab, df),
        ColumnRule("B => A", mapping_dict_ba, df),
        ColumnRule("A => C", mapping_dict_ac, df),
        ColumnRule("C => A", mapping_dict_ca, df),
        ColumnRule("A,B => D", mapping_dict_abd, df)
    ]

    definitions = get_definitions(rules)

    assert len(definitions) == 2 # There should be two keys
    assert len(definitions["Definitions"]) == 2
    assert len(definitions["NoDefinitions"]) == 3

    assert set([r.rule_string for r in definitions["Definitions"]]) == set(["A => B", "B => A"])

    assert set([r.rule_string for r in definitions["NoDefinitions"]]) == \
            set(["A => C", "C => A", "A,B => D"])


def test_filter_reverse_rules_with_lower_confidence():


    df = pd.DataFrame({
        'A' : ["a1", "a1", "a2", "a2"],
        'B' : ["b1", "b1", "b2", "b2"],
        'C' : ["c1", "c1", "c1", "c1"],
        'D' : ["d1", "d1", "d2", "d2"]
        })

    mapping_dict_ab = {
        frozenset(["A_a1"]) : "B_b1",
        frozenset(["A_a2"]) : "B_b2"
    }

    mapping_dict_ba = {frozenset([v]) : list(k)[0] for (k, v) in mapping_dict_ab.items()}

    # A => C always maps to c1
    mapping_dict_ac = {
        frozenset(["A_a1"]) : "C_c1",
        frozenset(["A_a2"]) : "C_c1"
    }

    mapping_dict_ca = {
        frozenset(["C_c1"]) : "A_a1",
    }
    mapping_dict_abd = {
        frozenset(["A_a1", "B_b1"]) : "D_d1",
        frozenset(["A_a2", "B_b2"]) : "D_d2"
    }


    rules = [
        ColumnRule("A => B", mapping_dict_ab, df),
        ColumnRule("B => A", mapping_dict_ba, df),
        ColumnRule("A => C", mapping_dict_ac, df),
        ColumnRule("C => A", mapping_dict_ca, df),
        ColumnRule("A,B => D", mapping_dict_abd, df)
    ]

    filtered = filter_reverse_rules_with_lower_confidence(rules)

    assert len(filtered["ToKeep"]) == 4
    assert len(filtered["ToDiscard"]) == 1


def test_cluster_definitions():
    # Only one cluster
    df = pd.DataFrame({
        'AA' : ["a1", "a1", "a2", "a2"],
        'BB' : ["b1", "b1", "b2", "b2"],        
        })

    mapping_dict_ab = {
        frozenset(["AA_a1"]) : "BB_b1",
        frozenset(["AA_a2"]) : "BB_b2"
    }

    mapping_dict_ba = {frozenset([v]) : list(k)[0] for (k, v) in mapping_dict_ab.items()}


    definitions = [
        ColumnRule("AA => BB", mapping_dict_ab, df),
        ColumnRule("BB => AA", mapping_dict_ba, df)
    ]

    clusters = cluster_definitions(definitions)

    assert len(clusters) == 1
    assert clusters[0] == set(["AA", "BB"])


    # Two clusters
    df = pd.DataFrame({
        'AA' : ["a1", "a1", "a2", "a2"],
        'BB' : ["b1", "b1", "b2", "b2"], 
        'CC' : ["c1", "c1", "c2", "c2"],  
        'DD' : ["d1", "d2", "d1", "d2"],
        'EE' : ["e1", "e2", "e1", "e2"],
        })

    mapping_dict_ab = {
        frozenset(["AA_a1"]) : "BB_b1",
        frozenset(["AA_a2"]) : "BB_b2"
    }

    mapping_dict_ba = {frozenset([v]) : list(k)[0] for (k, v) in mapping_dict_ab.items()}

    mapping_dict_ac = {
        frozenset(["AA_a1"]) : "CC_c1",
        frozenset(["AA_a2"]) : "CC_c2"
    }

    mapping_dict_ca = {frozenset([v]) : list(k)[0] for (k, v) in mapping_dict_ac.items()}

    mapping_dict_bc = {
        frozenset(["BB_b1"]) : "CC_c1",
        frozenset(["BB_b2"]) : "CC_c2"
    }

    mapping_dict_cb = {frozenset([v]) : list(k)[0] for (k, v) in mapping_dict_bc.items()}

    mapping_dict_de = {
        frozenset(["DD_d1"]) : "EE_e1",
        frozenset(["DD_d2"]) : "EE_e2"
    }

    mapping_dict_ed = {frozenset([v]) : list(k)[0] for (k, v) in mapping_dict_de.items()}


    definitions = [        
        ColumnRule("AA => BB", mapping_dict_ab, df),
        ColumnRule("BB => AA", mapping_dict_ba, df),
        ColumnRule("AA => CC", mapping_dict_ac, df),
        ColumnRule("CC => AA", mapping_dict_ca, df),
        ColumnRule("BB => CC", mapping_dict_bc, df),
        ColumnRule("CC => BB", mapping_dict_cb, df),
        ColumnRule("DD => EE", mapping_dict_de, df),
        ColumnRule("EE => DD", mapping_dict_ed, df)
    ]

    import random
    random.seed(42)
    random.shuffle(definitions) # Put list in random order

    clusters = cluster_definitions(definitions)
    assert len(clusters) == 2
    assert set(["AA", "BB", "CC"]) in clusters
    assert set(["DD", "EE"]) in clusters


    # 3 clusters



    df = pd.DataFrame({
        'AA' : ["a1", "a1", "a2", "a2"],
        'BB' : ["b1", "b2", "b1", "b2"], 
        'CC' : ["c1", "c2", "c1", "c2"],  
        'DD' : ["d2", "d1", "d1", "d2"],
        'EE' : ["e1", "e1", "e2", "e2"],
        'FF' : ["f2", "f1", "f1", "f2"],
        })

    mapping_dict_ae = {
        frozenset(["AA_a1"]) : "EE_e1",
        frozenset(["AA_a2"]) : "EE_e2"
    }

    mapping_dict_ea = {frozenset([v]) : list(k)[0] for (k, v) in mapping_dict_ae.items()}

    mapping_dict_bc = {
        frozenset(["BB_b1"]) : "CC_c1",
        frozenset(["BB_b2"]) : "CC_c2"
    }

    mapping_dict_cb = {frozenset([v]) : list(k)[0] for (k, v) in mapping_dict_bc.items()}

    mapping_dict_df = {
        frozenset(["DD_d1"]) : "FF_f1",
        frozenset(["DD_d2"]) : "FF_f2"
    }

    mapping_dict_fd = {frozenset([v]) : list(k)[0] for (k, v) in mapping_dict_df.items()}



    definitions = [        
        ColumnRule("AA => EE", mapping_dict_ae, df),
        ColumnRule("EE => AA", mapping_dict_ea, df),
        ColumnRule("BB => CC", mapping_dict_bc, df),
        ColumnRule("CC => BB", mapping_dict_bc, df),
        ColumnRule("DD => FF", mapping_dict_df, df),
        ColumnRule("FF => DD", mapping_dict_fd, df)        
    ]

    random.shuffle(definitions) # Put list in random order

    clusters = cluster_definitions(definitions)
    assert len(clusters) == 3
    assert set(["AA", "EE"]) in clusters
    assert set(["BB", "CC"]) in clusters
    assert set(["FF", "DD"]) in clusters



def test_find_duplicate_columns():

    df = pd.DataFrame({
        'A' :   ['a1', 'a2', 'a3', 'a4', 'a5'],
        'B' :   ['b1', 'b2', 'b3', 'b4', 'b5'],
        'AA' :  ['a1', 'a2', 'a3', 'a4', 'a5'],
        'AAA':  ['a1', 'a2', 'a3', 'a4', 'a5'],
        'BB' :  ['b1', 'b2', 'b3', 'b4', 'b5'],
        'C' :   [1,2,3,4,5]
    })

    duplicate_cols = find_duplicate_columns(df)
    assert len(duplicate_cols) == 2
    assert set(['A', 'AA', 'AAA']) in duplicate_cols
    assert set(['B', 'BB']) in duplicate_cols  




def test_predict_empty_antecedent():
    df = pd.DataFrame({
        'B' :   ['1', '1', '1', '1', '2'],
    })

    
    assert(pd.DataFrame(['1', '1', '1', '1', '1'], columns=["B"]).equals(get_list_of_columnrules_with_empty_antecedent(["B"], df)[0].predict(df=df) ))

def test_suggestionFinder_with_empty_antecedent_as_rule():

    df = pd.DataFrame({
        'B' :   ['1', '1', '1', '1', '2'],
    })

    sf = SuggestionFinder(get_list_of_columnrules_with_empty_antecedent(["B"], df))
    suggestion_df = sf.highest_scoring_suggestion(df)

    # Check if column B still the original is, and check if the prediction column correct is
    print(suggestion_df["B"])
    print(suggestion_df["__PREDICTION:/ => B"])
    
    
    # NOG ASSERT SCHRIJVEN




if __name__ == "__main__":
    #print(findsubsets("abc"))
    #test_lemma_df_to_rule_map()

    # print(subsets_minus_one(set(["A", "B", "C"])))

    # print(subsets_minus_one(["A", "B", "C"]))

    # print(subsets_minus_one(["A", "A", "C"]))

    # print(subsets_minus_one(set(["A"])))

    #test_create_df_query()

    #test_create_single_query_string()

    # test_cluster_definitions()

    # test_find_duplicate_columns()

    # test_predict_empty_antecedent()

    # test_suggestionFinder_with_empty_antecedent_as_rule()

    #test_df_to_be_corrected_generation()

    test_get_definitions()

