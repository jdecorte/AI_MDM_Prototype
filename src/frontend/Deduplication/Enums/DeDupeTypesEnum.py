# importing enum for enumerations
import enum
 
# creating enumerations using class
class DeDupeTypesEnum(str, enum.Enum):
    # String= 'String types are compared using string edit distance, specifically affine gap string distance. This is a good metric for measuring fields that might have typos in them, such as “John” vs “Jon”.'
    # Text= 'If you want to compare fields containing blocks of text e.g. product descriptions or article abstracts, you should use this type. Text type fields are compared using the cosine similarity metric. This is a measurement of the amount of words that two documents have in common. This measure can be made more useful as the overlap of rare words counts more than the overlap of common words.'
    # LatLong= 'A LatLong type field must have as the name of a field and a type declaration of LatLong. LatLong fields are compared using the Haversine Formula'
    # Exists= 'Exists variables are useful if the presence or absence of a field tells you something meaningful about a pair of records. Good for sparsely populated data (when presence is significant)'
    # Categorical = 'Used for comparing keywords or categories with a small number of options (5 or less)'
    # DateTime = 'DateTime variables are useful for comparing dates and timestamps'
    # Price = 'Price variables are useful for comparing positive, non-zero numbers like prices. The values of Price field must be a positive float. If the value is 0 or negative, then an exception will be raised.'

    String= 'String types are compared using string edit distance, specifically affine gap string distance. This is a good metric for measuring fields that might have typos in them, such as “John” vs “Jon”.'
    Text= 'If you want to compare fields containing blocks of text e.g. product descriptions or article abstracts, you should use this type. Text type fields are compared using the cosine similarity metric. This is a measurement of the amount of words that two documents have in common. This measure can be made more useful as the overlap of rare words counts more than the overlap of common words.'
    LatLong= 'A LatLong type field must have as the name of a field and a type declaration of LatLong. LatLong fields are compared using the Haversine Formula'
    Exists= 'Exists variables are useful if the presence or absence of a field tells you something meaningful about a pair of records. Good for sparsely populated data (when presence is significant)'
    Categorical = 'Used for comparing keywords or categories with a small number of options (5 or less)'
    DateTime = 'DateTime variables are useful for comparing dates and timestamps'
    Price = 'Price variables are useful for comparing positive, non-zero numbers like prices. The values of Price field must be a positive float. If the value is 0 or negative, then an exception will be raised.'