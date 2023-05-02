# importing enum for enumerations
import enum
 
# creating enumerations using class
class DialogEnum(str, enum.Enum):

    # GLOBAL
    gb_PAGE_TITLE = "AI MDM Tool"

    # Sidebar
    sb_PREVIOUS_STATE_button = "Go back to previous phase"

    sb_FUNCTIONALITY_selectbox = "Functionality"
    sb_FUNCTIONALITY_option_DATA_CLEANING = "Data Cleaning"
    sb_FUNCTIONALITY_option_DATA_PROFILING = "Data Profiling"
    sb_FUNCTIONALITY_option_DATA_EXTRACTION = "Data Extraction"
    sb_FUNCTIONALITY_option_DEDUPLICATION = "Deduplication"
    sb_FUNCTIONALITY_option_RULE_LEARNING = "Rule Learning"

    sb_DATA_PROFILING_radio = "Data Profiling: "
    sb_DATA_PROFILING_option_pandas = "Pandas Profiling"
    sb_DATA_PROFILING_option_dataprep = "Dataprep Profiling"

    sb_TYPE_HANDLER_radio = "Type Handler: "
    sb_TYPE_HANDLER_option_REMOTE = "Remote"
    sb_TYPE_HANDLER_option_LOCAL = "Local"

    sb_PREVIOUS_RESULTS = "Previous results on the dataset"

    sb_UPLOAD_DATASET = "Choose a .csv file"
    sb_SEPERATOR = "Seperator"
    sb_OPTIONAL_SEPERATOR = "Optional seperator"
    sb_OPTIONAL_SEPERATOR_DESCRIPTION = "Change when the seperator is not a ','"

    sb_DOWNLOAD_DATASET = "Download currently loaded dataset"

    sb_RELOAD_BUTTON = "Reload"

    # Data Cleaning



    # Data Profiling



    # Data Extraction



    # Deduplication



    # Rule-Learning

