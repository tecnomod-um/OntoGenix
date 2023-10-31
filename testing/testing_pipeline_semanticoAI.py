
'''########################################## YAML CONFIG ######################################################'''
import yaml

with open("../config.yaml", 'r') as stream:
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
    '../datasets/GoodRelations_V1/semantic_descriptions.npy'
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