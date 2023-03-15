import backend.RuleFinding.VR.ValueRuleRepo as vrr


def test_empty_value_rule_repo():
    vr_repo = vrr.ValueRuleRepo({}) # Create with empty dict
    assert len(vr_repo.filter_out_column_rule_strings_from_dict_of_value_rules(min_support=0.0)) == 0
