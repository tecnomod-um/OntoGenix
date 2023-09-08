
import yaml

with open("config.yaml", 'r') as stream:
    data_loaded = yaml.safe_load(stream)

config = data_loaded["OntoGenixConfig"]

base_path = config["base_path"]
dataset_folder = config["dataset_folder"]
dataset_file = config["dataset_file"]

from SemanticoAI.LLM_semantico import LlmSemantico

semantico_metadata = {
    'instructions': './SemanticoAI/instructions.prompt',
    'dataset': base_path + dataset_folder + '/' + dataset_file,
    'role': 'As an expert ontology engineer, SemanticoAI, your task is to analyze an ontology written in rdf/xml syntax.'
}
semantico = LlmSemantico(semantico_metadata)

import os

# Path to the directory
directory_path = './datasets/GoodRelations_V1/chunked/'

# List all files in the directory
files = os.listdir(directory_path)
print('num chunck files: ', len(files))

dictionaries = dict()

# Read each file
for it, file in enumerate(files[47:]): # el chunk_32 da fallos porque salen 4 diccionarios
    print('iteration: ', it)
    # Construct full file path
    file_path = os.path.join(directory_path, file)

    # Open each file and read its content
    if os.path.isfile(file_path):  # Check if it's a file, not a directory
        with open(file_path, 'r') as f:
            chunk = f.read()

        semantico.interact(chunk)

        dictionaries.update( semantico.semantic_descriptions )

import numpy as np

np.save(directory_path + 'dictionaries.npy', dictionaries, allow_pickle=True)


from sentence_transformers import SentenceTransformer
model = SentenceTransformer('all-MiniLM-L6-v2')

sentences = list(dictionaries.keys())
labels = dictionaries.keys()

sentence_embeddings = model.encode(sentences)

directory_path = './OntoBuilder/embeddings/'
np.save(directory_path + 'embeddings_array.npy', sentence_embeddings)


from sklearn.decomposition import PCA

result = PCA(n_components=2).fit_transform(sentence_embeddings)

import matplotlib.pyplot as plt
from tools import plot_word_embeddings

plt.figure()
plot_word_embeddings(result, labels, color='cyan')
plt.show(block=True)
