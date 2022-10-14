import json

class CleaningConfig:
    def __init__(self, cleaning_options):
        self.cleaning_options = cleaning_options
        

    def to_json(self):
        return json.dumps(self.__dict__)



        