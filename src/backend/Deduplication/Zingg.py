import pandas as pd
import os
from pathlib import Path
import hashlib
from subprocess import Popen, PIPE, STDOUT
import platform
import shutil
import pyarrow.parquet as pq
import config as cfg


class Zingg:
    def __init__(self, dedupe_type_dict, dedupe_data, modelID, number_of_partitions=4, label_data_sample_size=0.5, output="/output_dir") -> None:
        self.dedupe_type_dict = dedupe_type_dict
        self.dedupe_data = pd.read_json(dedupe_data).astype(str)
        self.modelID = modelID
        self.number_of_partitions = number_of_partitions
        self.label_data_sample_size = label_data_sample_size
        self.location = f"storage/{self.modelID}"
        Path(f"storage/{self.modelID}/input_dir").mkdir(parents=True, exist_ok=True)
        self.dedupe_data.to_csv(f"storage/{self.modelID}/input_dir/input.csv", index=False)

        different_phases = ["findTrainingData", "label", "train"]
        for phase in different_phases:
            self._create_python_files_from_phase(phase)
        Zingg.run_zingg_phase("findTrainingData", self.modelID) 
        

    @staticmethod
    def run_zingg_phase(phase, modelID):

        cfg.logger.debug(f"Running Zingg phase: {phase} on modelID: {modelID}")

        if phase == "findTrainingData":
            # remove existing unmarked pairs and run findTrainingData phase
            if os.path.exists(f"storage/{modelID}/models/{modelID}/trainingData/unmarked"):
                shutil.rmtree(f"storage/{modelID}/models/{modelID}/trainingData/unmarked")

        # If phase is train, clear output directory
        if phase == "train":
            if os.path.exists(f"storage/{modelID}/output_dir"):
                shutil.rmtree(f"storage/{modelID}/output_dir")

        system = platform.system()
        if system == "Windows":           
            cmd = (["C:\\Users\\mstr845\\AppData\\Local\\Programs\\Git\\git-bash.exe"] + ["./external/zingg-0.3.4/scripts/zingg.sh"] + ["--run"] +
                   [f"./storage/{modelID}/scripts/{phase}/generated_zingg_script.py"] + ['>./logginBlabla.txt 2>&1'])
            process = Popen(cmd, stdout=PIPE, stderr=STDOUT)
            _, _ = process.communicate()
        elif system == "Linux":
            cfg.logger.debug("Calling zingg.sh for Linux")
            cmd = (["/bin/bash"] + ["./external/zingg/scripts/zingg.sh"] + ["--run"] +
                   [f"storage/{modelID}/scripts/{phase}/generated_zingg_script.py"])
            #command_args = ["/bin/bash", "-c", cmd]
            #process = Popen(command_args, stdout=PIPE, stderr=STDOUT)
            env = {'SPARK_HOME': './external/spark',
                   'SPARK_MASTER': 'local[*]',
                   'ZINGG_HOME': './external/zingg'}
            process = Popen(cmd, stdout=PIPE, stderr=STDOUT, env=env)
            # cmd_shell = ("source ./envs/ai-mdm/bin/activate"
            #              + " & /bin/bash ./external/zingg/scripts/zingg.sh "
            #              + f"--run storage/{modelID}/scripts/{phase}/"
            #              + "generated_zingg_script.py")
            # process = Popen(cmd_shell, stdout=PIPE, stderr=STDOUT, shell=True, env=env)
            output, err = process.communicate()
            cfg.logger.debug(output.decode("utf-8") if output is not None else "")
            cfg.logger.debug(err.decode("utf-8") if err is not None else "")
        else:
            raise ValueError("Unsupported OS")

        # Verify if model could be trained
        if phase == "train":
            if not os.path.exists(f"storage/{modelID}/models/{modelID}/model"):
                return "500"

        return "200"

    @staticmethod
    def _read_parquet_schema_df(uri: str) -> pd.DataFrame:
        """Return a Pandas dataframe corresponding to the schema of a local URI of a parquet file.

        The returned dataframe has the columns: column, pa_dtype
        """
        # Ref: https://stackoverflow.com/a/64288036/
        schema = pq.read_schema(uri, memory_map=True)
        schema = pd.DataFrame(({"column": name, "pa_dtype": str(pa_dtype)} for name, pa_dtype in zip(schema.names, schema.types)))
        schema = schema.reindex(columns=["column", "pa_dtype"], fill_value=pd.NA)  # Ensures columns in case the parquet file has an empty dataframe.
        return schema

    @staticmethod
    def get_unmarked_pairs(modelID):
        # Go to directory and read in parquet files
        dir = f"storage/{modelID}/models/{modelID}/trainingData/unmarked"

        files = os.listdir(dir)
        files = [os.path.join(dir, f) for f in files if f.endswith(".parquet")]

        return pd.concat([pd.read_parquet(f) for f in files])

    @staticmethod
    def clear_marked_pairs(modelID):
        # remove existing marked pairs
        if os.path.exists(f"storage/{modelID}/models/{modelID}/trainingData/marked"):
            shutil.rmtree(f"storage/{modelID}/models/{modelID}/trainingData/marked")


    @staticmethod
    def mark_pairs(modelID, dataframe):        
        dir = f"storage/{modelID}/models/{modelID}/trainingData/marked"
        Path(dir).mkdir(parents=True, exist_ok=True)

        for z_cluster_id, z_cluster_df in dataframe.groupby('z_cluster'):
            # create md5 hash of z_cluster_id
            z_cluster_id = hashlib.md5(z_cluster_id.encode()).hexdigest()
            label = z_cluster_df['z_isMatch'].iloc[0]

            # Make all String:
            z_cluster_df = z_cluster_df.astype(str)

            # Set the type of the columns to the same as in the unmarked pairs.
            z_cluster_df["z_zid"] = z_cluster_df["z_zid"].astype("int64")
            # z_cluster_df["z_cluster"] = z_cluster_df["z_cluster"].astype("string")
            z_cluster_df["z_prediction"] = z_cluster_df["z_prediction"].astype("double")
            z_cluster_df["z_score"] = z_cluster_df["z_score"].astype("double")
            z_cluster_df["z_isMatch"] = z_cluster_df["z_isMatch"].astype("int32")
            # z_cluster_df["z_score"] = z_cluster_df["z_score"].astype("string")           

            # save to parquet file
            z_cluster_df.to_parquet(f"{dir}/{label}{z_cluster_id}.parquet", index=False, )
            tmp = Zingg._read_parquet_schema_df(f"{dir}/{label}{z_cluster_id}.parquet")
            cfg.logger.debug(f"Saved {z_cluster_id}.parquet")

    @staticmethod
    def get_stats(modelID):
        # Go to directory and read in parquet files
        dir = f"storage/{modelID}/models/{modelID}/trainingData/marked"
        # check if directory exists
        if not os.path.exists(dir):
            return {"match_files":0, "no_match_files":0, "unsure_files":0}
        files = os.listdir(dir)

        match_files = len([f for f in files if f.startswith("1") & f.endswith(".parquet")])
        no_match_files = len([f for f in files if f.startswith("0") & f.endswith(".parquet")])
        unsure_files = len([f for f in files if f.startswith("2") & f.endswith(".parquet")])
        return {"match_files":match_files, "no_match_files":no_match_files, "unsure_files":unsure_files}

    @staticmethod
    def get_clusters(modelID):
        output_dir = f"storage/{modelID}/output_dir"
        files = os.listdir(output_dir)
        files = [os.path.join(output_dir, f) for f in files if f.endswith(".parquet")]
        combined_df = pd.concat([pd.read_parquet(f) for f in files])
        # Delete the row with z_cluster == 0
        return combined_df[combined_df["z_cluster"] != 0]


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
outputPipe = Pipe("output1", JPipe.FORMAT_PARQUET)
outputPipe.addProperty(FilePipe.LOCATION, "{self.location}/output_dir")

args.setOutput(outputPipe)

{fourth_string_to_concat}

#Zingg execution for the given phase
zingg = Zingg(args, options)
zingg.initAndExecute()
""")