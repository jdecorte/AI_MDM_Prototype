import glob
import datetime
import pickle
import os

from src.backend.Deduplication.DeDupeIO import DeDupeIO

class DeduperSessionManager():
 
    def __init__(self, max_number_of_sessions = 10, session_dict = {}) -> None:
        self.session_dict = session_dict
        self.max_number_of_sessions = max_number_of_sessions
    
    def create_member(self, unique_storage_id, dedupe_type_dict, dedupe_data):

        try:
            # Check of member reeds aanwezig is, ander roep update aan
            if unique_storage_id in self.session_dict:
                self.update_member(unique_storage_id)
                return

            # Check of er nog plaats is
            if len(self.session_dict) < self.max_number_of_sessions:
                self.session_dict[unique_storage_id] = {"time_stamp":datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),"dedupe_object": DeDupeIO(dedupe_type_dict, dedupe_data)}
                return

            # Zoek de laatst actieve sessie en delete deze
            self.delete_member(min(self.session_dict.items(), key=lambda x: x[1]["time_stamp"])[0]) 

            # Check of member reeds aanwezig is als pickled file in file storage
            if f"deduper_object.bin" in glob.glob(f"storage/{unique_storage_id}/Deduper/*"):
                # restore deduper_object
                with open("storage/{unique_storage_id}/Deduper/deduper_object.bin", "rb") as bin_file:
                        deduper_object = pickle.load(bin_file)
                self.session_dict[unique_storage_id] = {"time_stamp":datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),"dedupe_object": deduper_object}
                return

            self.session_dict[unique_storage_id] = {"time_stamp":datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),"dedupe_object": DeDupeIO(dedupe_type_dict, dedupe_data)}
        except Exception as e:
            print(e)

    def read_member(self, unique_storage_id):
        self.update_member(unique_storage_id)
        return self.session_dict[unique_storage_id]

    def update_member(self, unique_storage_id):
        self.session_dict[unique_storage_id]["time_stamp"] = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    def delete_member(self,unique_storage_id):
        with open("storage/{unique_storage_id}/Deduper/deduper_object.bin", "wb") as bin_file:
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