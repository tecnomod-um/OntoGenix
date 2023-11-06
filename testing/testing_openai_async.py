

from LLM_base.LlmBase import AbstractLlm

metadata = {
    'role': 'You are a nice person',
    'model':'gpt-4'
}

base_LLM = AbstractLlm(metadata)

async for data_chunk in base_LLM.get_async_api_response("hola"):
    print(data_chunk)

print(base_LLM.answer)

'''########################################## CHUNK CSV ######################################################'''

import yaml

with open("config.yaml", 'r') as stream:
    data_loaded = yaml.safe_load(stream)

config = data_loaded["OntoGenixConfig"]

base_path = config["base_path"]
dataset_folder = config["dataset_folder"]
dataset_file = config["dataset_file"]

file = base_path + dataset_folder + '/' + dataset_file + '.csv'
print(file)

from tools.tools import csv2dataset

# get a dataset subsample from a csv file
dataset = csv2dataset(file, max_tokens=200)
print(dataset.head())

from tools.tools import dataframe2prettyjson

# format to json for the LLM_base and write to a file
json_data = dataframe2prettyjson(dataset, base_path + dataset_folder + '/json_data.json', save=True)
print('######## PROMPT ############\n', json_data)

from PlanSage.LLM_planner import LlmPlanner

# set metadata
planner_metadata = {
    'instructions': './PlanSage/instructions.prompt',
    'dataset': None,
    'role': 'You are a nice person.',
    'model':'gpt-4'
}
# build the planner LLM
planner = LlmPlanner(planner_metadata)

# interact with the LLM model to generate the context.
async for data_chunk in planner.interaction(
    input_task='''Generate the steps required to generate an ontology given the input json data table. ''',
    json_data=json_data
):
    print(data_chunk)