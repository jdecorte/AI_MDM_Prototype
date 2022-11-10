# importing enum for enumerations
import enum
 
# creating enumerations using class
class FiltererEnum(str, enum.Enum):
    Z_SCORE= "z_score"
    ENTROPY= "entropy"