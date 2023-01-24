import datetime
import pickle
import os
import config as cfg

from src.backend.Deduplication.DeDupeIO import DeDupeIO

class DeduperSessionManager():
 
    def __init__(self, max_number_of_sessions = 10, session_dict = {}) -> None:
        self.session_dict = session_dict
        self.max_number_of_sessions = max_number_of_sessions
    
    def create_member(self, unique_storage_id, dedupe_type_dict, dedupe_data):
        cfg.logger.debug(f"unique_storage_id = {unique_storage_id}")
        try:
            # Check of member reeds aanwezig is, ander roep update aan
            if unique_storage_id in self.session_dict:
                cfg.logger.debug(f"unique_storage_id = {unique_storage_id} is already present")
                self.update_member(unique_storage_id)
                return

            # Check of member reeds aanwezig is als pickled file in file storage, maak anders nieuw object aan
            deduper_object =  self._create_new_or_return_persisted(unique_storage_id, dedupe_type_dict, dedupe_data)
            cfg.logger.debug("deduper object aangemaakt")
            # Check of er nog plaats is
            if len(self.session_dict) < self.max_number_of_sessions:
                self.session_dict[unique_storage_id] = {"time_stamp":datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),"dedupe_object":deduper_object}
                return

            # Zoek de laatst actieve sessie en delete deze, nu dat er plaats is kan ons object worden toegevoegd
            self.delete_member(min(self.session_dict.items(), key=lambda x: x[1]["time_stamp"])[0]) 
            self.session_dict[unique_storage_id] = {"time_stamp":datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),"dedupe_object": deduper_object}

        except Exception as e:
            print(e)

    def read_member(self, unique_storage_id):
        cfg.logger.debug(f"Calling read_member met {unique_storage_id}")
        cfg.logger.debug(f"Huidige keys in session_dict {self.session_dict.keys()}")
        self.update_member(unique_storage_id)
        return self.session_dict[unique_storage_id]

    def update_member(self, unique_storage_id):
        self.session_dict[unique_storage_id]["time_stamp"] = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    def delete_member(self,unique_storage_id):
        with open(f"./storage/{unique_storage_id}/Deduper/deduper_object.bin", "wb") as bin_file:
            pickle.dump(self.session_dict[unique_storage_id]["dedupe_object"],bin_file)

        del self.session_dict[unique_storage_id]

    def save_all_members(self):
        for k,v in self.session_dict.items():
            path = f"storage/{k}/Deduper"
            path_with_file = f"{path}/deduper_object.bin"
            try:
                if not os.path.exists(path):
                    os.makedirs(path)
                with open(path_with_file, "wb") as bin_file:
                    pickle.dump(v["dedupe_object"],bin_file)
            except Exception as e:
                print(e)
     
    def _create_new_or_return_persisted(self, unique_storage_id, dedupe_type_dict, dedupe_data):
        # Check of member reeds aanwezig is als pickled file in file storage
        cfg.logger.debug(f"unique_storage_id = {unique_storage_id}")
        if os.path.exists(f"./storage/{unique_storage_id}/Deduper/deduper_object.bin"):
            # restore deduper_object
            with open(f"./storage/{unique_storage_id}/Deduper/deduper_object.bin", "rb") as bin_file:
                    deduper_object = pickle.load(bin_file)
            self.session_dict[unique_storage_id] = {"time_stamp":datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),"dedupe_object": deduper_object}
            return deduper_object
        else: 
            cfg.logger.debug(f"Creating a new deduper object for {unique_storage_id}")
            return DeDupeIO(dedupe_type_dict, dedupe_data)
    