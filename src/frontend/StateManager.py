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
    def restore_params(file_path:str, handler:IHandler) -> None:
        params_content = handler.fetch_file_from_filepath(filepath=file_path)
        if "rule_finding_config" in params_content:
            for k,v in params_content["rule_finding_config"].items():
                st.session_state[k] = v
            return
        return

    @staticmethod
    def restore_state(**kwargs) -> None:
        file_string = kwargs["file_path"].split("\\")[1]
        content = kwargs["handler"].fetch_file_from_filepath(filepath=kwargs["file_path"])
        past_result_content_dict = json.loads(content)
        part_to_check_functionality = file_string.split('_')[0]
        part_to_check_state = file_string.split('_')[1]

        # Grote If statement
        if part_to_check_functionality == "Rule-learning":
            if part_to_check_state == 'rules':
                st.session_state["currentState"] = "BekijkRules"
                st.session_state["gevonden_rules_dict"] = {k: ColumnRuleView.parse_from_json(v) for k,v in json.loads(past_result_content_dict["response"]).items()}
                for k,v in json.loads(past_result_content_dict["rule_finding_config"]).items():
                    st.session_state[k] = v


                md5_file_name = hashlib.md5(past_result_content_dict["rule_finding_config"].encode('utf-8')).hexdigest()
                param_path = kwargs["file_path"].split('\\')[0] + "/params/" + md5_file_name + '.json'
                StateManager.restore_params(param_path, kwargs["handler"])
                return 
            if part_to_check_state == 'suggestions':
                # Zoek de rules-file die hieraan gelinkt is, om zo ook de 
                st.session_state["currentState"] = "BekijkSuggesties"
                st.session_state["suggesties_df"] = json.dumps(past_result_content_dict["response"])
                return
            return

    @staticmethod
    def go_back_to_previous_in_flow(current_state: str) -> None:
        if current_state == "BekijkRules":
            st.session_state["currentState"] = None
            return
        if current_state == "BekijkSuggesties":
            st.session_state["currentState"] = "BekijkRules"
            return
    
            

    @staticmethod
    def initStateManagement():
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
            st.experimental_singleton.clear()
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

    @staticmethod
    def reset_all_buttons():
        StateManager.turn_state_button_false("validate_own_rule_btn")
        StateManager.turn_state_button_false("add_own_rule_btn")
        StateManager.turn_state_button_false("select_all_rules_btn")
        