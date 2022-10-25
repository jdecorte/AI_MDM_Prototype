import backend.RuleFinding.VR.ValueRule as vr
import backend.RuleFinding.VR.ValueRuleElement as vre


def test_value_rule():
    rl1 = vre.ValueRuleElement("A", "a")
    rl2 = vre.ValueRuleElement("B", "b")

    rl3 = vre.ValueRuleElement("C", "c")
    
    value_rule = vr.ValueRule([rl1, rl2], rl3, 0.2, 2.5, 0.99)

    assert str(value_rule) == "A=a,B=b || C=c || 0.2 || 2.5 || 0.99"

    value_rule = vr.ValueRule([rl2, rl1], rl3, 0.2, 2.5, 0.99)

    assert str(value_rule) == "B=b,A=a || C=c || 0.2 || 2.5 || 0.99"

def test_get_column_rule_string():
    rl1 = vre.ValueRuleElement("A", "a")
    rl2 = vre.ValueRuleElement("B", "b")

    rl3 = vre.ValueRuleElement("C", "c")
    
    value_rule = vr.ValueRule([rl1, rl2], rl3, 0.2, 2.5, 0.99)

    assert value_rule.get_column_rule_string() == "A,B => C"

    # Andere volgorde
    value_rule = vr.ValueRule([rl2, rl1], rl3, 0.2, 2.5, 0.99)

    # Moet nog steeds dezelfde column_rule string geven
    assert value_rule.get_column_rule_string() == "A,B => C"







if __name__ == "__main__":
    test_value_rule()
    print("done")