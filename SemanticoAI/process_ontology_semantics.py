# ########################################## SEMANTICO-AI ######################################################
from SemanticoAI.LLM_semantico import LlmSemantico

# Setup metadata for SemanticoAI
metadata = {
    'instructions': './SemanticoAI/instructions.prompt',  # Path to the instructions prompt file
    'ontology_path': './datasets/GoodRelations_V1/v1.owl',  # Path to the ontology file
    'chunks_path': '.datasets/GoodRelations_v1/chunks/',  # Path to the folder where ontology chunks will be saved
    'role': 'As an expert ontology engineer, SemanticoAI, your task is to analyze an ontology written in rdf/xml syntax.',
    'model': 'gpt-4'  # Specifying the model to be used
}

semantico = LlmSemantico(metadata)  # Creating an instance of LlmSemantico with the specified metadata

# Generate semantic descriptions using SemanticoAI
semantic_descriptions = semantico.generate_semantic_descriptions()

# ########################################## WRITE IN MEMORY ######################################################
from tools.tools import save_dictionary
import os

# Save the returned dictionary
save_dictionary(os.path.join(metadata['chunks_path'], 'semantic_descriptions.npy'), semantic_descriptions)
