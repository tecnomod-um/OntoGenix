
'''################ SEMANTICO: INTERPRETS ONTOLOGY FOR EMBEDDINGS #########################'''
'''#################### Segment the generated LLM-ontology into chunks ######################'''

'''########################################## YAML CONFIG ######################################################'''
import yaml

with open("config.yaml", 'r') as stream:
    data_loaded = yaml.safe_load(stream)

config = data_loaded["OntoGenixConfig"]

base_path = config["base_path"]
dataset_folder = config["dataset_folder"]
dataset_file = config["dataset_file"]

from tools import split_rdf
#
ontology_file = base_path + dataset_folder + '/' + dataset_file + '_owl_code_LLM_base.txt'
chunks_folder = base_path + dataset_folder + '/chunks/'
# segment the last llm generated ontology into chunks.
split_rdf(ontology_file, chunks_folder)

from SemanticoAI.LLM_semantico import LlmSemantico
from SemanticoAI.utils import save_semantic_descriptions

semanticoAI_metadata = {
    'instructions': './SemanticoAI/instructions.prompt',
    'dataset': base_path + dataset_folder + '/' + dataset_file,
    'role': 'As an expert ontology engineer, SemanticoAI, your task is to analyze an ontology written in rdf/xml syntax.'
}
semanticoAI = LlmSemantico(semanticoAI_metadata)

semanticoAI.chunksTransform(base_path + dataset_folder + '/chunks/')

save_semantic_descriptions(
    base_path + dataset_folder + '/semantic_descriptions.npy',
    semanticoAI.semantic_descriptions
)

# semanticoAI.chunksTransform('./datasets/GoodRelations_V1/chunks/')
#
# save_semantic_descriptions(
#     './datasets/GoodRelations_V1/semantic_descriptions.npy',
#     semanticoAI.semantic_descriptions
# )

'''########################################## SEMANTICO-AI ######################################################'''

from tools import split_rdf
#
ontology_file = base_path + dataset_folder + '/' + dataset_file + '_owl_code_LLM_base.txt'
chunks_folder = base_path + dataset_folder + '/chunks/'
# segment the last llm generated ontology into chunks.
split_rdf(ontology_file, chunks_folder)

from SemanticoAI.LLM_semantico import LlmSemantico
from SemanticoAI.utils import save_semantic_descriptions

semanticoAI_metadata = {
    'instructions': './SemanticoAI/instructions.prompt',
    'dataset': base_path + dataset_folder + '/' + dataset_file,
    'role': 'As an expert ontology engineer, SemanticoAI, your task is to analyze an ontology written in rdf/xml syntax.'
}
semanticoAI = LlmSemantico(semanticoAI_metadata)

semanticoAI.chunksTransform(base_path + dataset_folder + '/chunks/')

save_semantic_descriptions(
    base_path + dataset_folder + '/semantic_descriptions.npy',
    semanticoAI.semantic_descriptions
)


from SemanticoAI.utils import load_semantic_descriptions, process_semantic_descriptions

semantic_descriptions = load_semantic_descriptions(
    base_path + dataset_folder + '/semantic_descriptions.npy'
)

reference_semantic_descriptions = load_semantic_descriptions(
    './datasets/GoodRelations_V1/semantic_descriptions.npy'
)

labels = process_semantic_descriptions(semantic_descriptions, key='proposed_name')
reference_labels = process_semantic_descriptions(reference_semantic_descriptions, key='proposed_name')
all_labels = labels + reference_labels

descriptions = process_semantic_descriptions(semantic_descriptions, key='description')
reference_descriptions = process_semantic_descriptions(reference_semantic_descriptions, key='description')
all_descriptions = descriptions + reference_descriptions

from embeddings.EmbeddingGenerator import EmbeddingGenerator

embedder = EmbeddingGenerator()

ontology_embeddings = embedder.get_embeddings(all_descriptions)
ontology_embeddings_2D = embedder.get_pca(ontology_embeddings)
print(ontology_embeddings.shape)

import matplotlib.pyplot as plt
from tools import plot_word_embeddings

plt.figure()
plot_word_embeddings(ontology_embeddings_2D[:len(labels)], labels)
plot_word_embeddings(ontology_embeddings_2D[len(labels):], reference_labels, color='r')
plt.show()

from SemanticoAI.utils import get_relevant_chunks, load_chunk_samples

selected_chunks = get_relevant_chunks(labels, all_labels, reference_semantic_descriptions, ontology_embeddings_2D)
examples = load_chunk_samples(selected_chunks)

