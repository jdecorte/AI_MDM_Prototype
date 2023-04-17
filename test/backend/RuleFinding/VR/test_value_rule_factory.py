import pandas as pd
import src.backend.RuleFinding.VR.ValueRuleFactory as vrf
import src.backend.RuleFinding.VR.ValueRuleElement as vre
import src.backend.RuleFinding.VR.ValueRule as vr


def test_value_rule_factory():
    """
    Very simple test to check is ValueRules can be obtained from a dataframe,
    such as a dataframe that is returned by the fpgrowth algorithm.    
    """
    antecedents = [frozenset([f"A_{i}"]) for i in range(3)]
    consequents = [frozenset([f"B_{i}"]) for i in range(3)]
    support = [i/10 for i in range(3)]
    confidence = [i/5 for i in range(3)]
    lift = [i for i in range(3)]
    df = pd.DataFrame(
        {"antecedents": antecedents,
         "consequents": consequents,
         "support": support,
         "confidence": confidence,
         "lift": lift}
    )

    factory = vrf.ValueRuleFactory()
    value_rules_dict = factory.transform_ar_dataframe_to_value_rules_dict(df)
    assert len(value_rules_dict) == 1
    assert "A => B" in value_rules_dict
    assert len(value_rules_dict["A => B"]) == 3

    for i in range(3):
        antecedents = [vre.ValueRuleElement("A", str(i))]
        consequent = vre.ValueRuleElement("B", str(i))
        rule = vr.ValueRule(
            antecedents=antecedents,
            consequent=consequent,
            support=support[i],
            confidence=confidence[i],
            lift=lift[i])
        assert rule in value_rules_dict["A => B"]


def test_empty_value_rules():
    """
    Test that an empty dataframe results in an empty dictionary of value rules.
    """
    df = pd.DataFrame(
        {"antecedents": [],
         "consequents": [],
         "support": [],
         "confidence": [],
         "lift": []}
    )

    factory = vrf.ValueRuleFactory()
    value_rules_dict = factory.transform_ar_dataframe_to_value_rules_dict(df)
    assert len(value_rules_dict) == 0
