# importing enum for enumerations
import enum
 
# creating enumerations using class
class VarEnum(str, enum.Enum):


    # Configuration
    cfg_WEBSOCKET_SERVER_URL = "WEBSOCKET_SERVER_URL"


    # Global
    gb_CURRENT_STATE = "currentState"
    gb_SESSION_MAP = "session_map"
    gb_SESSION_ID = "session_flask_local_id"
    gb_SESSION_ID_WITH_FILE_HASH = "session_flask"
    gb_CURRENT_SEQUENCE_NUMBER = "current_seq"

    # Sidebar
    sb_LOADED_DATAFRAME = "dataframe"    
    sb_LOADED_DATAFRAME_NAME = "dataframe_name"
    sb_LOADED_DATAFRAME_SEPERATOR = "seperator_input"
    sb_TYPE_HANDLER = "type_handler"
    sb_CURRENT_FUNCTIONALITY = "current_functionality"
    sb_CURRENT_PROFILING = "current_profiling"
    
    # Data Cleaning



    # Data Profiling



    # Data Extraction



    # Deduplication



    # Rule-Learning