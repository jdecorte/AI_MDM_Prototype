class ValueRuleElement:
    """
        Simple data class keeping track of the name of a column (i.e. an attribute) 
        and the corresponding value.  Both are stored as a string.
    """

    def __init__(self, attribute, value):
        self.attribute = str(attribute)
        self.value = str(value)
        
    def __hash__(self):
        return hash((self.attribute, self.value))
    
    def __eq__(self, other):
         return (self.__class__ == other.__class__ and
             self.attribute == other.attribute and self.value == other.value)
             
    def __str__(self):
         return f"{self.attribute}={self.value}"