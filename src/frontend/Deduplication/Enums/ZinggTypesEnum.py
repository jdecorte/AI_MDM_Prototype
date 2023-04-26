# importing enum for enumerations
import enum
 
# creating enumerations using class
class ZinggTypesEnum(str, enum.Enum):
    FUZZY= 'Broad matches with typos, abbreviations, and other variations.'
    EXACT= 'No tolerance with variations, Preferable for country codes, pin codes, and other categorical variables where you expect no variations.'
    DONT_USE= 'Appears in the output but no computation is done on these. Helpful for fields like ids that are required in the output.'
    EMAIL = 'Matches only the id part of the email before the @ character'
    PINCODE = 'Matches pin codes like xxxxx-xxxx with xxxxx'
    NULL_OR_BLANK = "By default Zingg marks matches as"
    TEXT = "Compares words overlap between two strings."
    NUMERIC = "extracts numbers from strings and compares how many of them are same across both strings"
    NUMERIC_WITH_UNITS = "extracts product codes or numbers with units, for example 16gb from strings and compares how many are same across both strings"
    ONLY_ALPHABETS_EXACT = "only looks at the alphabetical characters and compares if they are exactly the same"
    ONLY_ALPHABETS_FUZZY = "ignores any numbers in the strings and then does a fuzzy comparison"