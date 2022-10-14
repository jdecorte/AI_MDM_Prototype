# importing enum for enumerations
import enum
 
# creating enumerations using class
class CleaningEnum(str, enum.Enum):
    STRING_TO_FLOAT= "string_to_float"
    TRIM= "trim"