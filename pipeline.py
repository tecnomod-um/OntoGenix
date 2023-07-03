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

# CHUNKIZE THE GENERATED LLM-ONTOLOGY
from tools import split_rdf

ontology_file = base_path + dataset_folder + '/' + dataset_file + '_ontology_LLM.owl'
chunks_folder = base_path + dataset_folder + '/chunks/'
# usage
split_rdf(ontology_file, chunks_folder)


'''################ SEMANTICO: INTERPRETS ONTOLOGY FOR EMBEDDINGS #########################'''


from SemanticoAI.LLM_semantico import LlmSemantico

semantico_metadata = {
    'instructions': './SemanticoAI/instructions.prompt',
    'dataset': base_path + dataset_folder + '/' + dataset_file,
    'role': 'As an expert ontology engineer, SemanticoAI, your task is to analyze an ontology written in rdf/xml syntax.'
}
semantico = LlmSemantico(semantico_metadata)

semantico.chunksTransform(chunks_folder)

import numpy as np
dictionaries = np.load(chunks_folder + 'dictionaries.npy', allow_pickle=True).item()
labels = []
sentences = []
for label, sentence in dictionaries.items():
    if type(label) == str and type(sentence) == str:
        cleaned_label = "".join([char for char in label if not char.isnumeric()])
        labels.append(cleaned_label)
        sentences.append(sentence)
print(len(labels), len(sentences))

reference_folder = './datasets/GoodRelations_V1/chunked/'
reference_dictionaries = np.load(reference_folder + 'dictionaries.npy', allow_pickle=True).item()
reference_labels = []
reference_sentences = []
for label, sentence in reference_dictionaries.items():
    if type(label) == str and type(sentence) == str:
        cleaned_label = "".join([char for char in label if not char.isnumeric()])
        reference_labels.append(cleaned_label)
        reference_sentences.append(sentence)
print(len(reference_labels), len(reference_sentences))

final_labels = labels + reference_labels
final_sentences = sentences + reference_sentences
print(len(final_labels), len(final_sentences))


from embeddings.EmbeddingGenerator import EmbeddingGenerator

embedder = EmbeddingGenerator()

ontology_embeddings = embedder.get_embeddings(final_labels)
ontology_embeddings_2D = embedder.get_pca(ontology_embeddings)
print(ontology_embeddings.shape)


import matplotlib.pyplot as plt
from tools import plot_word_embeddings

plt.figure()
plot_word_embeddings(ontology_embeddings_2D[:len(sentences)], labels)
plot_word_embeddings(ontology_embeddings_2D[len(sentences):], reference_labels, color='r')
plt.show()

from sentence_transformers import util

#Compute cosine-similarities for each sentence with each other sentence
cosine_scores = util.cos_sim(ontology_embeddings_2D, ontology_embeddings_2D)

#Find the pairs with the highest cosine similarity scores
pairs = []
for i in range(len(cosine_scores)-1):
    for j in range(i+1, len(cosine_scores)):
        pairs.append({'index': [i, j], 'score': cosine_scores[i][j]})

#Sort scores in decreasing order
pairs = sorted(pairs, key=lambda x: x['score'], reverse=True)

for pair in pairs[:30]:
    i, j = pair['index']
    print("{} \t\t {} \t\t Score: {:.4f}".format(final_labels[i], final_labels[j], pair['score']))


from wordcloud import WordCloud
import matplotlib.pyplot as plt


# Let's assume you have a list of words 'word_list'
wordcloud = WordCloud(width = 1000, height = 500).generate(' '.join(final_labels))

plt.figure(figsize=(15,8))
plt.imshow(wordcloud)
plt.axis("off")
plt.show()

import matplotlib.pyplot as plt
from collections import Counter

word_freq = Counter(final_labels)
# Let's assume 'word_freq' is a dictionary with words as keys and their frequencies as values
words = list(word_freq.keys())
frequencies = list(word_freq.values())

plt.figure()
plt.bar(words, frequencies)
plt.show()
'''########################################## MAPPING ######################################################'''

from OntoMapper.LLM_ontomapper import LlmOntoMapper

mapper_metadata = {'instructions': './OntoMapper/instructions.prompt',
                   'dataset': base_path + dataset_folder + '/' + dataset_file,
                   'role': 'You are a powerful ontology engineer that generates RML mappings.'
}

ontology_mapper = LlmOntoMapper(mapper_metadata)

rml_code_str = ontology_mapper.interact(json_data=json_data, ontology=ontology_builder.owl_codeblock)

