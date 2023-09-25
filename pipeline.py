# -*- coding: utf-8 -*-
'''
TODO:
    CODING TASKS:
    - Check openai Embeddings instead of sentence-transformer bert model.
    - Refine the Mapper strategy: At present, it's fairly straightforward and direct. It could be enriched with
    external libraries to generate the kgraph from the data source, the ontology, and the mapping definition, to
    consider the errors produced in the refinement loop. This would necessitate the use of libraries capable of
    automated kgraph creation, if they exist.
    - Code refactoring: This should be an ongoing, daily process.

    IDEAS:
    - The OntoBuilder strategy comprises four stages:
        + Generate a fundamental ontology.
        + Search for related entities in a database of segmented ontologies using semanticoAI and embeddings. BEST OPTION!!!
        + Incorporate relevant entities if they are deemed beneficial.

'''

'''########################################## YAML CONFIG ######################################################'''
import yaml

with open("config.yaml", 'r') as stream:
    data_loaded = yaml.safe_load(stream)

config = data_loaded["OntoGenixConfig"]

base_path = config["base_path"]
dataset_folder = config["dataset_folder"]
dataset_file = config["dataset_file"]

file = base_path + dataset_folder + '/' + dataset_file + '.csv'
print(file)

'''########################################## CHUNK CSV ######################################################'''
from tools import csv2dataset

# get a dataset subsample from a csv file
dataset = csv2dataset(file, max_tokens=200)
print(dataset.head())

'''########################################## DATAFRAME subsample 2 JSON ######################################################'''
from tools import dataframe2prettyjson

# format to json for the LLM_base and write to a file
json_data = dataframe2prettyjson(dataset, base_path + dataset_folder + '/json_data.json', save=True)
print('######## PROMPT ############\n', json_data)

'''########################################## JSON subsample 2 CSV ######################################################'''
import pandas as pd
import json

# Reading JSON data from a file
with open(base_path + dataset_folder + '/' + "json_data.json") as f:
    json_data = json.load(f)
# Converting JSON data to a pandas DataFrame
df = pd.DataFrame(json_data)
# Writing DataFrame to a CSV file
df.to_csv(base_path + dataset_folder + '/' + "csv_data.csv", index=False)

'''########################################## MORPHKG config file ######################################################'''
import configparser

# Initialize Config Parser
config = configparser.ConfigParser()
# Define a new section and its options (key-value pairs)
config['DataSourceCSV'] = {
    'mappings': base_path + dataset_folder + '/mapping.csv.ttl',
    'file_path': base_path + dataset_folder + '/csv_data.csv'
}
# Write the changes back to the file
with open(base_path + dataset_folder + '/config.ini', 'w') as configfile:
    config.write(configfile)

'''########################################## PLAN-INSTRUCTIONS ######################################################'''
from PlanSage.LLM_planner import LlmPlanner

# set metadata
planner_metadata = {
    'instructions': './PlanSage/instructions.prompt',
    'dataset': base_path + dataset_folder + '/' + dataset_file,
    'role': 'You are a powerful ontology engineer that generates the reasoning steps needed to generate'
            'the context needed to create an ontology from a json data table.',
    'model':'gpt-4'
}
# build the planner LLM
planner = LlmPlanner(planner_metadata)
# define the high level structure of the ontology in natural language.
input_task='''Generate the steps required to generate an ontology given the input json data table. 
    I want the ontology to be focused on the entity "CustomerComplaint". This will be linked to the following entities
    as object properties: "State", "Product", "ProblemOfComplaint" and "Company".
    "CustomerComplaint" connects to "Product" which must have "SubProduct" as object property.  
    "CustomerComplaint" connects to "ProblemOfComplaint" which must have "ProblemSubCategory" as object property.
    "Company" connects to "CompanyResponse" which must have "Resolution" as object property. 
    "CustomerComplaint" connects to "CompanyResponse".
    Define the approppriate data type properties for each class.
    Employ as a foundational prefix "https://vocab.um.es".'''

# interact with the LLM model to generate the context.
planner.interaction(
    input_task=input_task,
    json_data=json_data
)
# planner.regenerate() # run this line of code if you want to regenerate the LLM answer.
print(planner.answer) # the LLM answer

'''########################################## ONTOLOGY ######################################################'''
from OntoBuilder.LLM_ontology import LlmOntology
# set metadata
onto_metadata = {'instructions': './OntoBuilder/instructions.prompt',
                 'entity_improvement': './OntoBuilder/entity_improvement.prompt',
                 'dataset': base_path + dataset_folder + '/' + dataset_file,
                 'role': 'You are a powerful ontology engineer that generates OWL ontologies in RDF/XML format.',
                 'model': 'gpt-4'
                 }
# build the ontology generator LLM
ontology_builder = LlmOntology(onto_metadata)

# --------------------- GENERATE THE BASE ONTOLOGY --------------------------------
'''
This section will help to generate the first and most basic ontology version based on the high level definition 
provided using natural language. The outcome should reflect the high level architecture of the ontology description.
'''
ontology_builder.interact(
    json_data=json_data,
    rationale=planner.answer # you first need to generate a proper context with LLM planner.
)
# ontology_builder.regenerate() # run this line of code if you want to regenerate the LLM answer.
ontology_context = ontology_builder.answer # to get the full contextualized answer from the ontology generator LLM.
print(ontology_context) # -> this will be used later for the RML MAPPING step.
print(ontology_builder.codeblock) # to get the ontology codeblox in RDF/XML syntax from the ontology generator LLM.

# --------------- GENERATE CODE FOR EACH ENTITY ----------------------------------
'''
This section will help to generate the codeblock for a specific entity. You must pass to the LLM model the entity to be
improved. The entity to be input could be an existing one in the generated ontology or an alternative one that it is 
not already in the definition of the ontology. In the following I show two different use cases, one for a class entity 
and another one for an [object property/data type property]. 
'''
from tools import extract_sections_from_rdf, dict_to_rdf

# extract sections from the RDF/XML owl codeblock
rdf_sections = extract_sections_from_rdf(ontology_builder.codeblock)
print(rdf_sections.keys())

# --- Class entities improvement suggestions
print(rdf_sections['class_definitions'])
# define the task
'''
This task prompt has been proved useful for class entities. 
DO NOT CHANGE IT! 
'''
task = '''Scrutinize the ontology, the data description and the insights to identify intrinsic constraints and relationships.
Clearly follow the instructions given in the insights to define the constraints and relationships.
Do not forget to reference all the object properties and data properties mentioned in the insights as related with the given entity.
Do not forget to define for object properties restrictions the "onClass" parameter.
Do not forget to define for data type properties restrictions the "onDataRange" parameter.'''
# for each class entity
entity_index = 0 # get the desired section by index
next_entity = rdf_sections['class_definitions'][entity_index]
print(next_entity)
# generate the LLM answer
ontology_builder.interact(
    rationale=ontology_context,
    next_entity=next_entity,
    task=task
)
print(ontology_builder.codeblock) # check the entity codeblock generated by the LLM

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
# for each class entity
print(rdf_sections['object_property_definitions']) # or rdf_sections['data_property_definitions']
entity_index = 0 # get the desired section by index
next_entity = rdf_sections['object_property_definitions'][entity_index] # or rdf_sections['data_property_definitions'][entity_index]
print(next_entity)
# generate the LLM answer
ontology_builder.interact(
    rationale=ontology_context,
    next_entity=next_entity,
    task=task
)
print(ontology_builder.codeblock) # check the entity codeblock generated by the LLM

'''########################################## MAPPING ######################################################'''
from OntoMapper.LLM_ontomapper import LlmOntoMapper

# set metadata
mapper_metadata = {'instructions': './OntoMapper/instructions.prompt',
                   'dataset': base_path + dataset_folder + '/' + dataset_file,
                   'role': 'You are a powerful ontology engineer that generates RML mappings.',
                   'model':'gpt-3.5-turbo-16k'
}
# build the ontology mapping generator LLM
ontology_mapper = LlmOntoMapper(mapper_metadata)
# generate the rml code for mapping the ontology with regards the source data.
ontology_mapper.interact(rationale=ontology_context)
# ontology_mapper.regenerate() # run this line of code if you want to regenerate the LLM answer.
print(ontology_mapper.rml_codeblock)

'''######################### Kowledge Graph Generation from RML code ###############################################'''
import morph_kgc


# You should have first created the config.ini file.
graph = morph_kgc.materialize(base_path + dataset_folder + '/' + 'config.ini')
graph.serialize(destination=base_path + dataset_folder + '/' + 'data.nt', format='ntriples', endoding="utf-8")

