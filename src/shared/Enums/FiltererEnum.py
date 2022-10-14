# importing enum for enumerations
import enum
 
# creating enumerations using class
class FiltererEnum(str, enum.Enum):
    Z_SCORE= "z_score"
    MIN_LEAFS= "min_leafs"
    ENTROPY= "entropy"
    ONE_OVER_X= "one_over_x"