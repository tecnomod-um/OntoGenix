# -*- coding: utf-8 -*-

'''########################################## YAML CONFIG ######################################################'''
import yaml

with open("./testing/config.yaml", 'r') as stream:
    data_loaded = yaml.safe_load(stream)

config = data_loaded["OntoGenixConfig"]

base_path = config["base_path"]
dataset_folder = config["dataset_folder"]
dataset_file = config["dataset_file"]

file = base_path + dataset_folder + '/' + dataset_file + '.csv'
print(file)

'''########################################## CHUNK CSV ######################################################'''
from tools.tools import csv_statistical_description

# get a dataset subsample from a csv file
dataset = csv_statistical_description(file)
print(dataset.head())

'''########################################## DATAFRAME subsample 2 JSON ######################################################'''
from tools.tools import dataframe2prettyjson

# format to json for the LLM_base and write to a file
json_data = dataframe2prettyjson(dataset, base_path + dataset_folder + '/json_data.json', save=True)
print('######## PROMPT ############\n', json_data)

'''########################################## MORPHKG config file ######################################################'''
import configparser

# Initialize Config Parser
config = configparser.ConfigParser()
# Define a new section and its options (key-value pairs)
config['DataSourceCSV'] = {
    'mappings': base_path + dataset_folder + '/' + dataset_file + '_rml_mapping_LLM.csv.ttl',
    'file_path': file
}
# Write the changes back to the file
with open(base_path + dataset_folder + '/config.ini', 'w') as configfile:
    config.write(configfile)

'''########################################## PLAN-INSTRUCTIONS ######################################################'''
from enum import Enum

class OntologyState(Enum):
    DESCRIPTION = "DATA_DESCRIPTION"
    ONTOLOGY_OBJECT_PROPERTIES = "ONTOLOGY_OBJECT_PROPERTIES"
    ONTOLOGY_DATA_PROPERTIES = "ONTOLOGY_DATA_PROPERTIES"
    ONTOLOGY_ENTITY = "ONTOLOGY_ENTITY"
    MAPPING = "MAPPING"

from PlanSage.LLM_planner import LlmPlanner

# set metadata
planner_metadata = {
        'data_description': './PlanSage/data_description.prompt',
        'dataset': base_path + dataset_folder + '/' + dataset_file,
        'role': 'You are a powerful ontology engineer that generates the reasoning steps needed to generate'
                'the context needed to create an ontology from a json data table.',
        'model': 'gpt-4'#'gpt-3.5-turbo'
    }

# build the planner LLM
planner = LlmPlanner(planner_metadata)
# define the high level structure of the ontology in natural language.
input_task='''Generate the steps required to generate an ontology given the input json data table.
I want the ontology to be focused on the "Product" entity as the main class "sales_product". Each product will have 
the following object properties: "BrandName", "Brand", "Category", "eligibleQuantity", "SubCategory", "Image_Url", 
"Absolute_Url". We propose to add an external entity "hasOffer" from the schema.org ontology to be an object property 
of "sales_product". The entities "Price", "DiscountPrice", "priceCurrency" (from schema) and "Quantity" will be set as 
data type properties to the "offer" class.'''

# interact with the LLM model to generate the data description.
async for chunk_data in planner.interaction(
        input_task=input_task,
        json_data=json_data,
        state=OntologyState.DESCRIPTION):
    print(chunk_data, end='') # the LLM answer

'''########################################## ONTOLOGY ######################################################'''
from OntoBuilder.LLM_ontology import LlmOntology
# set metadata
onto_metadata = {
        'object_properties_instructions': './OntoBuilder/object_properties_instructions.prompt',
        'data_properties_instructions': './OntoBuilder/data_properties_instructions.prompt',
        'entity_improvement': './OntoBuilder/entity_improvement.prompt',
        'dataset': base_path + dataset_folder + '/' + dataset_file,
        'role': 'You are a powerful ontology engineer that generates OWL ontologies in RDF/XML format.',
        'model': 'gpt-4'#'gpt-3.5-turbo'
    }

# build the ontology generator LLM
ontology_builder = LlmOntology(onto_metadata)

# --------------------- GENERATE THE BASE ONTOLOGY --------------------------------
'''
This section will help to generate the first and most basic ontology version based on the high level definition 
provided using natural language. The outcome should reflect the high level architecture of the ontology description
just for the classes and object properties.
'''
async for chunk_data in ontology_builder.interact(
        data_description=planner.data_description,
        entity=None,
        state=OntologyState.ONTOLOGY_OBJECT_PROPERTIES):
    print(chunk_data, end='') # the LLM answer

'''
This section will help to generate the first and most basic ontology version based on the high level definition 
provided using natural language. The outcome should reflect the high level architecture of the ontology description
just for the classes and data properties.
'''
async for chunk_data in ontology_builder.interact(
        data_description=planner.data_description,
        entity=None,
        state=OntologyState.ONTOLOGY_DATA_PROPERTIES):
    print(chunk_data, end='') # the LLM answer
# --------------- GENERATE CODE FOR EACH ENTITY ----------------------------------
'''
This section will help to generate the codeblock for a specific entity. You must pass to the LLM model the entity to be
improved. The entity to be input could be an existing one in the generated ontology or an alternative one that it is 
not already in the definition of the ontology. In the following I show two different use cases, one for a class entity 
and another one for an [object property/data type property]. 
'''
# define the task
'''
This task prompt has been proved useful for class entities. 
DO NOT CHANGE IT! 
'''
task = '''Scrutinize the ontology, the data description and the insights to identify intrinsic constraints and relationships.
Clearly follow the instructions given in the insights to define the constraints and relationships.
Do not forget to reference all the object properties and data properties mentioned in the insights as related with the given entity.
Do not forget to define for object properties restrictions the "onClass" parameter.
Do not forget to define for data type properties restrictions the "onDataRange" parameter.
All these tasks are to be done for the entity: {next_entity}'''

# for the following entity
next_entity = 'Product'
# generate the LLM answer
async for chunk_data in ontology_builder.interact(
        data_description=planner.data_description,
        entity=task.format(next_entity=next_entity),
        state=OntologyState.ONTOLOGY_ENTITY):
    print(chunk_data, end='') # the LLM answer

# --- Object and Data property entities improvement suggestions
'''
This task prompt has been proved useful for object properties and data type properties. 
DO NOT CHANGE IT! 
'''
# define the task
task = '''Append relevant metadata and annotations to provide context, provenance, or additional insights for each 
entity. Do not change the original entity name. Define a description field, propose an alternative name, and devise 
a set of five alternative labels to ensure comprehensiveness and flexibility in understanding and usage. Consider to 
define equivalent properties if known or it exist in the ontology, otherwise, do not create fictional ones.'''

# for the following entity
next_entity =  'Price'
# generate the LLM answer
async for chunk_data in ontology_builder.interact(
        data_description=planner.data_description,
        entity=task.format(next_entity=next_entity),
        state=OntologyState.ONTOLOGY_ENTITY):
    print(chunk_data, end='') # the LLM answer

'''########################################## MAPPING ######################################################'''
from OntoMapper.LLM_ontomapper import LlmOntoMapper

# set metadata
mapper_metadata = {'instructions': './OntoMapper/instructions.prompt',
                   'dataset': base_path + dataset_folder + '/' + dataset_file,
                   'role': 'You are a powerful ontology engineer that generates RML mappings.',
                   'model':'gpt-4'
}
# build the ontology mapping generator LLM
ontology_mapper = LlmOntoMapper(mapper_metadata)
# generate the rml code for mapping the ontology with regards the source data.
async for chunk_data in ontology_mapper.interact(rationale=planner.data_description):
    print(chunk_data, end='')

ontology_mapper.save_response(
    ontology_mapper.get_rml_codeblock(),
    ontology_mapper.dataset_path + '_rml_mapping_LLM.csv.ttl',
    mode='w'
)


'''######################### Kowledge Graph Generation from RML code ###############################################'''
from KG_Generator.KGEN import KGen

kgen = KGen(
    dataset=base_path+dataset_folder+'/config.ini',
    destination=base_path+dataset_folder+'/data.nt'
)
output = kgen.run()
print(output)
