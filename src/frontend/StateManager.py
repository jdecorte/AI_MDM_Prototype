import streamlit as st
import json
import hashlib
from src.shared.Views.ColumnRuleView import ColumnRuleView
from src.frontend.Handler.IHandler import IHandler
class StateManager:
    def __init__(self) -> None:
        pass

    @staticmethod
    def turn_state_button_true(id):
        st.session_state[id] = True

    @staticmethod
    def turn_state_button_false(id):
        st.session_state[id] = False

    @staticmethod
    def clear_session_state():
        st.session_state = {}


    @staticmethod
    def restore_state(**kwargs) -> None:
        file_string = kwargs["file_path"].split("\\")[1]
        content = kwargs["handler"].fetch_file_from_filepath(filepath=kwargs["file_path"])
        past_result_content_dict = json.loads(content)
        part_to_check_functionality = file_string.split('_')[0]
        part_to_check_state = file_string.split('_')[1]

        # SET CURRENT_SEQ TO CHOSEN ONE
        st.session_state["current_seq"] = kwargs["chosen_seq"]

        # Grote If statement
        if part_to_check_functionality == "Rule-learning":
            if part_to_check_state == 'rules':
                st.session_state["gevonden_rules_dict"] = {k: ColumnRuleView.parse_from_json(v) for k,v in past_result_content_dict["result"].items()}
                for k,v in json.loads(past_result_content_dict["params"]["rule_finding_config_in_json"]).items():
                    st.session_state[k] = v
                st.session_state["currentState"] = "BekijkRules"
                
            if part_to_check_state == 'suggestions':
                # Zoek de rules-file die hieraan gelinkt is, om zo ook de 
                st.session_state["suggesties_df"] = json.dumps(past_result_content_dict["result"])
                # FETCH PATH OF OTHER FILE FROM SESSION_MAP
                StateManager.restore_state(**{"handler" : kwargs["handler"], "file_path": st.session_state["session_map"][kwargs["chosen_seq"]]["rules"], "chosen_seq": kwargs["chosen_seq"]})
                st.session_state["currentState"] = "BekijkSuggesties"
            return
        return       

    @staticmethod
    def go_back_to_previous_in_flow(current_state: str) -> None:
        # RULE LEARNER
        if current_state == "BekijkRules":
            st.session_state["currentState"] = None

            # Verschillende knoppen vanop de pagina terug False maken
            st.session_state["validate_own_rule_btn"] = False
            st.session_state["calculate_entropy_btn"] = False
            st.session_state["add_own_rule_btn"]  = False
            
            return
        if current_state == "BekijkSuggesties":
            st.session_state["currentState"] = "BekijkRules"
            return

        # DEDUPE
        if current_state == "LabelRecords":
            st.session_state["currentState"] = None
            return
        if current_state == "ViewClusters":
            st.session_state["currentState"] = "LabelRecords_get_record_pair"
            return
        if current_state == "ViewClusters":
            st.session_state["currentState"] = "LabelRecords_get_record_pair"
            return   
            

    @staticmethod
    def initStateManagement():

        # SESSION
        if 'session_flask' not in st.session_state:
            st.session_state['session_flask'] = None


        if 'profile_report' not in st.session_state:
            st.session_state['profile_report'] = None
            
        if 'currentState' not in st.session_state:
            st.session_state['currentState'] = None

        if 'current_functionality' not in st.session_state:
            st.session_state['current_functionality'] = None

        if 'currentRegel_LL' not in st.session_state:
            st.session_state['currentRegel_LL'] = None

        if 'currentRegel_RL' not in st.session_state:
            st.session_state['currentRegel_RL'] = None

        if 'ruleEdit' not in st.session_state:
            st.session_state["ruleEdit"] = {}

        if "ListActiveMergeDuplicates" not in  st.session_state:
            st.session_state["ListActiveMergeDuplicates"] = {}

        if "ListEditDuplicates" not in  st.session_state:
            st.session_state["ListEditDuplicates"] = {}

        if "AdviseerOpslaan" not in st.session_state:
            st.session_state["AdviseerOpslaan"] = False

        if "dataframe" not in st.session_state:
            # Clearen van caches
            st.cache_resource.clear()
            st.session_state["dataframe"] = None

        if "dataframe_name" not in st.session_state:
            st.session_state["dataframe_name"] = None

        # BUTTONS

        if "validate_own_rule_btn" not in st.session_state:
            st.session_state["validate_own_rule_btn"] = False

        if "add_own_rule_btn" not in st.session_state:
            st.session_state["add_own_rule_btn"] = False

        if "select_all_rules_btn" not in st.session_state:
            st.session_state["select_all_rules_btn"] = False
            
        if "select_all_suggestions_btn" not in st.session_state:
            st.session_state["select_all_suggestions_btn"] = False

        if "calculate_entropy_btn" not in st.session_state:
            st.session_state["calculate_entropy_btn"] = False
        
        if "use_previous_label_btn" not in st.session_state:
            st.session_state["use_previous_label_btn"] = False

        # DEDUPE

        if "dedupe_type_dict" not in st.session_state:
            st.session_state['dedupe_type_dict'] = {}

        if 'number_of_unsure' not in st.session_state:
            st.session_state['number_of_unsure'] = 0

        if "stashed_label_pair" not in st.session_state:
            st.session_state["stashed_label_pair"] = None

        if "record_pair" not in st.session_state:
            st.session_state["record_pair"] = None

        # CLEANER
        if "pipeline" not in st.session_state:
            st.session_state['pipeline'] = {}

        if "cleaned_column_from_pipeline" not in st.session_state:
            st.session_state['cleaned_column_from_pipeline'] = None
        


    @staticmethod
    def reset_all_buttons():
        StateManager.turn_state_button_false("validate_own_rule_btn")
        StateManager.turn_state_button_false("add_own_rule_btn")
        StateManager.turn_state_button_false("select_all_suggestions_btn")
        StateManager.turn_state_button_false("select_all_rules_btn")
        StateManager.turn_state_button_false("calculate_entropy_btn")
        
        