import pandas as pd
import os
from pathlib import Path
import hashlib


class Zingg:
    def __init__(self, dedupe_type_dict, dedupe_data, modelID, phase, number_of_partitions=4, label_data_sample_size=0.5, 
                 input="/input.csv", output="/output_dir", script_output="/generated_zingg_script.py" ) -> None:
        self.dedupe_type_dict = dedupe_type_dict
        # create dataframe from json
        self.dedupe_data = pd.read_json(dedupe_data).astype(str)
        self.modelID = modelID
        self.phase = phase
        self.number_of_partitions = number_of_partitions
        self.label_data_sample_size = label_data_sample_size
        self.input = f"storage/{self.modelID}"+ input
        # write dedupe_data to temp file, and create input path
        Path(f"storage/{self.modelID}").mkdir(parents=True, exist_ok=True)
        self.dedupe_data.to_csv(self.input, index=False)
        self.output = f"storage/{self.modelID}"+ output
        Path(f"storage/{self.modelID}/{self.phase}/").mkdir(parents=True, exist_ok=True)
        self.script_output = f"storage/{self.modelID}/{self.phase}/"+ script_output
        
    def execute_runnable_script(self):
        # TODO aanpassen wanneer in Linux gerund wordt
        self._create_python_file_from_parameters()
        
    @staticmethod
    def get_unmarked_pairs(modelID):
        # Go to directory and read in parquet files
        dir = f"storage/{modelID}/unmarked"
        files = os.listdir(dir)
        files = [os.path.join(dir, f) for f in files if f.endswith(".parquet")]
        df = pd.concat([pd.read_parquet(f) for f in files])
        return df

    @staticmethod
    def mark_pairs(modelID, dataframe):        
        dir = f"storage/{modelID}/marked"
        Path(dir).mkdir(parents=True, exist_ok=True)

        for z_cluster_id, z_cluster_df in dataframe.groupby('z_cluster'):
            # create md5 hash of z_cluster_id
            z_cluster_id = hashlib.md5(z_cluster_id.encode()).hexdigest()
            label = z_cluster_df['z_isMatch'].iloc[0]
            # save to parquet file
            z_cluster_df.to_parquet(f"{dir}/{label}_{z_cluster_id}.parquet", index=False)
            print(f"Saved {z_cluster_id}.parquet")


    @staticmethod
    def get_stats(modelID):
        # Go to directory and read in parquet files
        dir = f"storage/{modelID}/marked"
        files = os.listdir(dir)

        # check how many files start with 1
        match_files = len([f for f in files if f.startswith("1") & f.endswith(".parquet")])
        no_match_files = len([f for f in files if f.startswith("0") & f.endswith(".parquet")])
        unsure_files = len([f for f in files if f.startswith("2") & f.endswith(".parquet")])
        return {"match_files":match_files, "no_match_files":no_match_files, "unsure_files":unsure_files}

    def get_deduplicated_dataframe(self):
        # Go to directory and read in csv files
        pass

    def _create_python_file_from_parameters(self):
        first_string_to_concat = ""

        for key, value in self.dedupe_type_dict.items():
            first_string_to_concat += f"{key} = FieldDefinition(\"{key}\", \"string\", MatchType.{value})"
            first_string_to_concat += "\n"
        
        second_string_to_concat = str(list(self.dedupe_type_dict.keys())).replace('\'', '')

        third_string_to_concat = ""
        for key in self.dedupe_type_dict.keys():
            third_string_to_concat += f"{key} string, "
        # remove last comma and space
        third_string_to_concat = third_string_to_concat[:-2]

        fourth_string_to_concat = ""
        if self.phase == "findTrainingData":
            fourth_string_to_concat = "options = ClientOptions([ClientOptions.PHASE,\"findTrainingData\"])"
        elif self.phase == "train":
            fourth_string_to_concat = "options = ClientOptions([ClientOptions.PHASE,\"trainMatch\"])"
        elif self.phase == "label":
            fourth_string_to_concat = "options = ClientOptions([ClientOptions.PHASE,\"label\"])"
        else:
            raise ValueError("Phase not supported")

        # write to output file
        with open(self.script_output, "w") as f:
            f.write(
f"""from zingg.client import *
from zingg.pipes import *

#build the arguments for zingg
args = Arguments()
#set field definitions: 
{first_string_to_concat}

fieldDefs = {second_string_to_concat}
args.setFieldDefinition(fieldDefs)
args.setModelId("{self.modelID}")
args.setZinggDir("models")
args.setNumPartitions({self.number_of_partitions})
args.setLabelDataSampleSize({self.label_data_sample_size})

#reading dataset into inputPipe and settint it up in 'args'
#below line should not be required if you are reading from in memory dataset
#in that case, replace df with input df
schema = "{third_string_to_concat}"
inputPipe = CsvPipe("input1", "/vagrant/{self.input}", schema)

args.setData(inputPipe)

#setting outputpipe in 'args'
outputPipe = CsvPipe("output1", "/vagrant/{self.output}")

args.setOutput(outputPipe)

{fourth_string_to_concat}

#Zingg execution for the given phase
zingg = Zingg(args, options)
zingg.initAndExecute()
""")