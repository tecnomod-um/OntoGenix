
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