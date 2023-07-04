# -*- coding: utf-8 -*-

from tools import csv2dataset, dataframe2prettyjson, plot_mermaid, extract_text
import yaml
'''########################################## YAML CONFIG ######################################################'''

with open("config.yaml", 'r') as stream:
    data_loaded = yaml.safe_load(stream)

config = data_loaded["OntoGenixConfig"]

base_path = config["base_path"]
dataset_folder = config["dataset_folder"]
dataset_file = config["dataset_file"]

file = base_path + dataset_folder + '/' + dataset_file + '.csv'


'''########################################## DATA2JSON ######################################################'''

# get a dataset subsample from a csv file
dataset = csv2dataset(file, max_tokens=800)

# format to json for the LLM_base and write to a file
file = base_path + dataset_folder + '/' + dataset_file + '_dataframe_subset.txt'
json_data = dataframe2prettyjson(dataset, file)
print('######## PROMPT ############\n', json_data)

'''#################### Segment the generated LLM-ontology into chunks ######################'''

from tools import split_rdf

ontology_file = base_path + dataset_folder + '/' + dataset_file + '_ontology_LLM.owl'
chunks_folder = base_path + dataset_folder + '/chunks/'
# usage


'''########################################## PLAN-INSTRUCTIONS ######################################################'''

# instantiate the LLM_base that generates an owl ontology from a json subset data
from PlanSage.LLM_planner import LlmPlanner

planner_metadata = {
    'first_instructions': './PlanSage/first_instructions.prompt',
    'interaction': './PlanSage/interaction.prompt',
    'dataset': base_path + dataset_folder + '/' + dataset_file,
    'role': 'You are a powerfull ontology engineer that generates the reasoning steps needed to generate'
            'an ontology from a json data table.'
}

planner = LlmPlanner(planner_metadata)

planner.interaction(
    input_task="Generate an ontology given the input json data table.",
    json_data=json_data
)

planner.interaction(
    instructions='''include as fundational prefix https://vocab.um.es#, include this in the task_6 explicitly'''
)

############ this section is for a closed loop interaction with the ontology builder ####################
# planner.interaction(
#     instructions='some instructions that comes from the ontology builder during the analysis of human
#     generated ontologies'
# )
#-------------------------------------------------------------------------------------------------------

'''########################################## ONTOLOGY ######################################################'''

# instantiate the LLM_base that generates an owl ontology from a json subset data
from OntoBuilder.LLM_ontology import LlmOntology

onto_metadata = {'instructions': './OntoBuilder/instructions.prompt',
                 'autocompletion':  './OntoBuilder/auto_completion.prompt',
                 'ontology_analysis': './OntoBuilder/ontology_analysis.prompt',
                 'ontology_synthesis': './OntoBuilder/ontology_synthesis.prompt',
                 'examples': './OntoBuilder/examples/',
                 'dataset': base_path + dataset_folder + '/' + dataset_file,
                 'role': 'You are a powerful ontology engineer that generates OWL ontologies in turtle format.'
                 }

ontology_builder = LlmOntology(onto_metadata)

# GENERATE THE FIRST LLM-ONTOLOGY
ontology_builder.interact(json_data=json_data, instructions=planner.plan)

# ANALYSIS THROUGH COMPARITION OF THE LLM-ONTOLOGY
for human_ontology in ontology_builder.examples:
    insights = ontology_builder.analyze(
        json_data=json_data,
        instructions=planner.plan,
        previous_ontology=ontology_builder.owl_codeblock,
        human_ontology=human_ontology
    )

    planner.interaction(instructions=insights) # algo no funciona bien aqui!!!

# REFINE THE LLM-ONTOLOGY TAKING INTO ACCOUNT THE PREVIOUS ANALYSIS
ontology_builder.synthesize()

# segment the llm generated ontology into chunks.
split_rdf(ontology_file, chunks_folder)

'''################ SEMANTICO: INTERPRETS ONTOLOGY FOR EMBEDDINGS #########################'''

from SemanticoAI.LLM_semantico import LlmSemantico

semanticoAI_metadata = {
    'instructions': './SemanticoAI/instructions.prompt',
    'dataset': base_path + dataset_folder + '/' + dataset_file,
    'role': 'As an expert ontology engineer, SemanticoAI, your task is to analyze an ontology written in rdf/xml syntax.'
}
semanticoAI = LlmSemantico(semanticoAI_metadata)

semanticoAI.chunksTransform(base_path + dataset_folder + '/chunks/')

# semanticoAI.chunksTransform('./datasets/GoodRelations_V1/chunked/')


import numpy as np
import re

def clean_word(word):
    cleaned = "".join([char.lower().replace('_', ' ') for char in word if not char.isnumeric()])
    cleaned = re.sub('\(.*\)', '', cleaned).replace('.', '').strip()
    return cleaned


def load_dictionaries(path):
    return np.load(path, allow_pickle=True).item()


def process_dictionaries(dictionaries):
    return [clean_word(label) for label in dictionaries.keys() if type(label) == str]


dictionaries = load_dictionaries(base_path + dataset_folder + '/chunks/dictionaries.npy')
labels = process_dictionaries(dictionaries)
reference_dictionaries= load_dictionaries('./datasets/GoodRelations_V1/chunked/dictionaries.npy')
reference_labels = process_dictionaries(reference_dictionaries)

all_words = labels + reference_labels

from embeddings.EmbeddingGenerator import EmbeddingGenerator

embedder = EmbeddingGenerator()

ontology_embeddings = embedder.get_embeddings(all_words)
ontology_embeddings_2D = embedder.get_pca(ontology_embeddings)
print(ontology_embeddings.shape)


import matplotlib.pyplot as plt
from tools import plot_word_embeddings

plt.figure()
plot_word_embeddings(ontology_embeddings_2D[:len(labels)], labels)
plot_word_embeddings(ontology_embeddings_2D[len(labels):], reference_labels, color='r')
plt.show()

from sentence_transformers import util

cosine_scores = util.cos_sim(ontology_embeddings_2D, ontology_embeddings_2D)
print(cosine_scores.shape)


pairs = []
for i in range(len(cosine_scores)-1):
    for j in range(i+1, len(cosine_scores)):
        pairs.append({'index': [i, j], 'score': cosine_scores[i][j]})

sorted_pairs = sorted(pairs, key=lambda x: x['score'].item(), reverse=True)

entities = dict()
for word2check in labels:
    word2check_index = all_words.index(word2check)
    entities[word2check] = []
    cont = 0
    for pair in sorted_pairs:
        i, j = pair['index']
        if i == word2check_index and all_words[i] != all_words[j] and all_words[j] not in entities[word2check]:
            print(all_words[i], ' ', all_words[j], ' ',  pair['score'])

            entities[word2check].append( {'entity':all_words[j], 'i':i, 'j':j} )
            cont+=1
        if cont == 3:
            break

segment_files = []
for key in entities.keys():
    for item in entities[key]:
        for it, ref_key in enumerate(reference_dictionaries.keys()):
            if it == item['j']-len(labels):
                segment_files.append( reference_dictionaries[ref_key]['file'] )
                break


sorted_files = sorted(segment_files, key=lambda x: int(x.split('chunk_')[1].split('.')[0]))
print(sorted_files)

import matplotlib.pyplot as plt
from collections import Counter


# Count the frequency of each string
counter = Counter(sorted_files)

# Separate keys and values for plotting
labels, values = zip(*counter.items())

# Create the histogram
plt.figure(figsize=(10, 6))
plt.bar(labels, values)
plt.xticks(rotation='vertical')
plt.show()

values = np.array(values)
index = [it for it,val in enumerate(values) if val > values.mean()+values.std()]
selected_chunks = [labels[it] for it in index]
print(selected_chunks)

'''########################################## MAPPING ######################################################'''

from OntoMapper.LLM_ontomapper import LlmOntoMapper

mapper_metadata = {'instructions': './OntoMapper/instructions.prompt',
                   'dataset': base_path + dataset_folder + '/' + dataset_file,
                   'role': 'You are a powerful ontology engineer that generates RML mappings.'
}

ontology_mapper = LlmOntoMapper(mapper_metadata)

rml_code_str = ontology_mapper.interact(json_data=json_data, ontology=ontology_builder.owl_codeblock)

