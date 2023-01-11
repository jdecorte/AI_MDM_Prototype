# importing enum for enumerations
import enum
 
# creating enumerations using class
class DroppingEnum(str, enum.Enum):
    DROP_WITH_UNIQUENESS_BOUND= "drop_with_uniqueness_bound"
    DROP_WITH_LOWER_BOUND= "drop_with_lower_bound"
    DROP_WITH_UPPER_BOUND= "drop_with_upper_bound"

    DROP_NAN = "drop_nan"
