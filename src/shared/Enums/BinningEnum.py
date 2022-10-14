# importing enum for enumerations
import enum
 
# creating enumerations using class
class BinningEnum(str, enum.Enum):
    EQUAL_BINS= "equal_bins"
    K_MEANS= "k_means"