import pandas as pd
import os
from pathlib import Path
import hashlib
import os, shlex, subprocess
from subprocess import Popen, PIPE, STDOUT


class Zingg:
    def __init__(self, dedupe_type_dict, dedupe_data, modelID, number_of_partitions=4, label_data_sample_size=0.5, output="/output_dir") -> None:
        self.dedupe_type_dict = dedupe_type_dict
        # create dataframe from json
        self.dedupe_data = pd.read_json(dedupe_data).astype(str)
        self.modelID = modelID
        self.number_of_partitions = number_of_partitions
        self.label_data_sample_size = label_data_sample_size
        self.location = f"../../../storage/{self.modelID}"
        Path(f"storage/{self.modelID}/input_dir").mkdir(parents=True, exist_ok=True)
        self.dedupe_data.to_csv(f"storage/{self.modelID}/input_dir/input.csv", index=False)

        different_phases = ["findTrainingData", "label", "train"]
        for phase in different_phases:
            self._create_python_files_from_phase(phase)

        Zingg.run_zingg_phase("findTrainingData", self.modelID)    
    @staticmethod
    def run_zingg_phase(phase, modelID):
        # run zingg phase
        # p = subprocess.Popen(["C:/Users/mstr845/AppData/Local/Programs/Git/git-bash.exe",f"C:/Users/mstr845/Documents/GitHub/AI_MDM_Prototype/external/zingg-0.3.4/scripts/zingg.sh --run C:/Users/mstr845/Documents/GitHub/AI_MDM_Prototype/storage/{modelID}/scripts/{phase}/generated_zingg_script.py"], 
        #              bufsize=-1, 
        #              executable=None, 
        #              stdin=None, 
        #              stdout=None, 
        #              stderr=None, 
        #              preexec_fn=None, 
        #              close_fds=True, 
        #              shell=False, 
        #              cwd="C:/Users/mstr845/Documents/dev", 
        #              )
        # gb = fr'C:/Users/mstr845/AppData/Local/Programs/Git/git-bash.exe"'
        # arr = [gb, f"C:/Users/mstr845/Documents/GitHub/AI_MDM_Prototype/external/zingg-0.3.4/scripts/zingg.sh --run C:/Users/mstr845/Documents/GitHub/AI_MDM_Prototype/storage/{modelID}/scripts/{phase}/generated_zingg_script.py"]
        gb= "C:\\Users\\mstr845\\AppData\\Local\\Programs\\Git\\git-bash.exe" 
        # arr = [gb, "-c", "touch hello.txt"]
        # r = subprocess.Popen(arr, shell=True)
        # # print(f"Zingg phase {phase} finished")
        
        cmd = "C:\\Users\\mstr845\\Documents\\GitHub\\AI_MDM_Prototype\\external\\zingg-0.3.4\\scripts\\zingg.sh --run C:\\Users\\mstr845\\Documents\\GitHub\\AI_MDM_Prototype\\storage\\8be17881-85a9-4a01-aa0e-031441ea303b-59c842936079079f6cac55b9fb1abd29\\scripts\\findTrainingData\\generated_zingg_script.py"
        cmd1= "C:\\Users\\mstr845\\Documents\\GitHub\\AI_MDM_Prototype\\external\\zingg-0.3.4\\scripts\\zingg.sh"
        cmd2= "--run"
        cmd3= "C:\\Users\\mstr845\\Documents\\GitHub\\AI_MDM_Prototype\\storage\\8be17881-85a9-4a01-aa0e-031441ea303b-59c842936079079f6cac55b9fb1abd29\\scripts\\findTrainingData\\generated_zingg_script.py"
        start_path = "C:\\Users\\mstr845\\Documents\\GitHub\\AI_MDM_Prototype"
        command_args = [gb, "-c", cmd]
        process = Popen(command_args, stdout=PIPE, stderr=STDOUT, shell=True, cwd="C:\\Users\\mstr845\\AppData\\Local\\Programs\\Git\\" )
        output, err = process.communicate()
        print(output)
        print(err)

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

    def _create_python_files_from_phase(self, phase):
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
        if phase == "findTrainingData":
            fourth_string_to_concat = "options = ClientOptions([ClientOptions.PHASE,\"findTrainingData\"])"
        elif phase == "train":
            fourth_string_to_concat = "options = ClientOptions([ClientOptions.PHASE,\"trainMatch\"])"
        elif phase == "label":
            fourth_string_to_concat = "options = ClientOptions([ClientOptions.PHASE,\"label\"])"
        else:
            raise ValueError("Phase not supported")
        
        Path(f"storage/{self.modelID}/scripts/{phase}/").mkdir(parents=True, exist_ok=True)

        # write to output file
        with open(f"storage/{self.modelID}/scripts/{phase}/generated_zingg_script.py", "w") as f:
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
args.setZinggDir("{self.location}/models")
args.setNumPartitions({self.number_of_partitions})
args.setLabelDataSampleSize({self.label_data_sample_size})

#reading dataset into inputPipe and settint it up in 'args'
#below line should not be required if you are reading from in memory dataset
#in that case, replace df with input df
schema = "{third_string_to_concat}"
inputPipe = CsvPipe("input1", "{self.location}/input_dir/input.csv", schema)

args.setData(inputPipe)

#setting outputpipe in 'args'
outputPipe = CsvPipe("output1", "{self.location}/output_dir")

args.setOutput(outputPipe)

{fourth_string_to_concat}

#Zingg execution for the given phase
zingg = Zingg(args, options)
zingg.initAndExecute()
""")