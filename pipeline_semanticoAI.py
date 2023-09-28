
'''########################################## YAML CONFIG ######################################################'''
import yaml

with open("config.yaml", 'r') as stream:
    data_loaded = yaml.safe_load(stream)

config = data_loaded["OntoGenixConfig"]

base_path = config["base_path"]
dataset_folder = config["dataset_folder"]
dataset_file = config["dataset_file"]

'''################################## ONTOLOGY SEGMENTATION ############################################'''
from tools.rdf_tools import split_rdf

# segments an ontology into chunks to save them in a folder.
split_rdf(
    base_path + dataset_folder + '/' + 'ontology_LLM.owl',
    base_path + dataset_folder + '/chunks/',
    chunk_size=1
)

'''########################################## SEMANTICO-AI ######################################################'''
from SemanticoAI.LLM_semantico import LlmSemantico
from tools.tools import list_files, save_dictionary
import os

# set up metadata for semanticoAI
metadata = {
    'instructions': './SemanticoAI/instructions.prompt',
    'dataset': base_path + dataset_folder + '/' + dataset_file,
    'role': 'As an expert ontology engineer, SemanticoAI, your task is to analyze an ontology written in rdf/xml syntax.',
    'model':'gpt-4'
}
# generate an instance of semanticoAI
semantico = LlmSemantico(metadata)

# for a previously chunked ontology we generate the semantic descriptions with semanticoAI
chunks_path = base_path + dataset_folder + '/chunks/'
sorted_files = list_files(chunks_path)
# Read each file
semantic_descriptions = dict()
for it, file in enumerate(sorted_files):
    print('iteration: ', it, ' of ', len(sorted_files))
    # Construct full file path
    file_path = os.path.join(chunks_path, file)
    print(file_path)
    # read the file content
    with open(file_path, 'r') as f:
        ontology = f.read()

    semantico.interact(ontology)
    answer_dict = eval(semantico.answer)

    descriptions = {
        answer_dict[key]['name']: {
            'proposed_name': answer_dict[key]['proposed_name'],
            'description': answer_dict[key]['description'],
            'file': file_path
        } for key in answer_dict.keys()
    }

    semantic_descriptions.update(descriptions)


save_dictionary(
    base_path + dataset_folder + '/chunks/semantic_descriptions.npy',
    semantic_descriptions
)

'''########################################## YAML CONFIG ######################################################'''
import yaml

with open("config.yaml", 'r') as stream:
    data_loaded = yaml.safe_load(stream)

config = data_loaded["OntoGenixConfig"]

base_path = config["base_path"]
dataset_folder = config["dataset_folder"]
dataset_file = config["dataset_file"]


from tools.tools import load_dictionary
from SemanticoAI.semantico_tools import process_semantic_descriptions

semantic_descriptions = load_dictionary(
    base_path + dataset_folder + '/chunks/semantic_descriptions.npy'
)
reference_semantic_descriptions = load_dictionary(
    './datasets/GoodRelations_V1/semantic_descriptions.npy'
)

labels = process_semantic_descriptions(semantic_descriptions, key='proposed_name')
reference_labels = process_semantic_descriptions(reference_semantic_descriptions, key='proposed_name')
all_labels = labels + reference_labels
print(all_labels)

descriptions = process_semantic_descriptions(semantic_descriptions, key='description')
reference_descriptions = process_semantic_descriptions(reference_semantic_descriptions, key='description')
all_descriptions = descriptions + reference_descriptions
print(all_descriptions)

from embeddings.EmbeddingGenerator import EmbeddingGenerator

embedder = EmbeddingGenerator()

ontology_embeddings = embedder.get_embeddings(all_descriptions)
ontology_embeddings_2D = embedder.get_pca(ontology_embeddings)
print(ontology_embeddings.shape)

import matplotlib.pyplot as plt
from tools.custom_plots import plot_word_embeddings

plt.figure()
plot_word_embeddings(ontology_embeddings_2D[:len(labels)], labels)
plot_word_embeddings(ontology_embeddings_2D[len(labels):], reference_labels, color='r')
plt.show()

from SemanticoAI.semantico_tools import get_relevant_chunks, load_chunk_samples

selected_chunks = get_relevant_chunks(labels, all_labels, reference_semantic_descriptions, ontology_embeddings_2D)
examples = load_chunk_samples(selected_chunks)
