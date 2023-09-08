
import yaml

with open("config.yaml", 'r') as stream:
    data_loaded = yaml.safe_load(stream)

config = data_loaded["OntoGenixConfig"]

base_path = config["base_path"]
dataset_folder = config["dataset_folder"]
dataset_file = config["dataset_file"]

directory_path = './datasets/GoodRelations_V1/chunked/'

from SemanticoAI.LLM_semantico import LlmSemantico

semanticoAI_metadata = {
    'instructions': './SemanticoAI/instructions.prompt',
    'dataset': base_path + dataset_folder + '/' + dataset_file,
    'role': 'As an expert ontology engineer, SemanticoAI, your task is to analyze an ontology written in rdf/xml syntax.'
}
semanticoAI = LlmSemantico(semanticoAI_metadata)

semanticoAI.chunksTransform(directory_path)


from sentence_transformers import SentenceTransformer
import numpy as np

model = SentenceTransformer('all-MiniLM-L6-v2')

sentences = np.load(directory_path+'sentences.npy')

sentence_embeddings = model.encode(sentences)

directory_path = './OntoBuilder/embeddings/'
np.save(directory_path + 'embeddings_array.npy', sentence_embeddings)