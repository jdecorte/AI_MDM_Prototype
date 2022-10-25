from src.backend.RuleFinding.VR.ValueRuleElement import ValueRuleElement
from typing import List

class ValueRule:
    """
        Class representing a value rule.

        A value rule represents a logical consequence as follows:
        if A_1 = a_1 and A_2 = a_2 and ... A_n = a_n then C = c

        The column names A_i and their corresponding values a_i are stored (using `ValueRuleElement`) 
        as well as the column name C and its corresponding values c.

        Furthermore, a value rule has a support, lift and confidence.
    """

    ## TODO: ValueRule should be safe to use in a set

    def __init__(self, antecedents : List[ValueRuleElement], consequent : ValueRuleElement, support : float, lift : float, confidence: float):
        self.antecedents : List[ValueRuleElement] = antecedents
        self.consequent : ValueRuleElement = consequent
        self.support : float                 = support
        self.lift : float                    = lift
        self.confidence : float              = confidence

    def __str__(self) -> str:                
        s = ",".join([str(a) for a in self.antecedents])
        s += " || "
        s += str(self.consequent)
        s += " || "    
        s += str(self.support)
        s += " || "
        s += str(self.lift)
        s += " || "
        s += str(self.confidence)
        return s

    def get_column_rule_string(self) -> str:
        """
            Creates a string of the form antecedents => consequents.
            The antecedents are the column names of the columns that participate 
            in the ValueRule and likewise for the columns.
            Both the antecedents and consequents are sorted alphabetically. 
        """

        return ','.join(sorted([str(a.attribute) for a in self.antecedents])) \
                 + " => " \
                 + str(self.consequent.attribute)