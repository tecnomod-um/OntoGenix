import os
from typing import Dict, Any, List, Union
import numpy as np
from .LLM_semantico import LlmSemantico
from embeddings.EmbeddingGenerator import EmbeddingGenerator
from tools.tools import list_files
from tools.rdf_tools import split_rdf


class Semantico:

    def __init__(self):
        # Setup metadata for LlmSemantico
        self.metadata = dict(
            instructions='./SemanticoAI/instructions.prompt',
            role='As an expert ontology engineer your task is to analyze an ontology written in rdf/xml syntax.',
            model='gpt-3.5-turbo'
        )
        # Creating an instance of LlmSemantico with the specified metadata
        self.semantico = LlmSemantico(self.metadata)
        self.embedding_generator = EmbeddingGenerator()

    def get_oneEmbedding(self, entity: str) -> np.ndarray:
        """
        Get the embedding for a given entity.

        Parameters:
        - entity (str): The name of the entity for which the embedding is required.

        Returns:
        - np.ndarray: The embedding of the entity as a 1D array.
        """
        # Interact with the `semantico` to get information about the entity
        self.semantico.interact(entity)
        # Convert the codeblock returned by `semantico` to a dictionary
        answer_dict: Dict[str, Any] = eval(self.semantico.codeblock)
        # Extract the description of the entity from the dictionary
        sentence = answer_dict['description']
        # Generate the embedding for the description using `embedding_generator`
        embedding = self.embedding_generator.get_embeddings(sentence)
        # Return the generated embedding
        return embedding

    def get_embeddings(self, ontology_path: str, chunks_path: str) -> np.ndarray:
        """
        Generate embeddings for an ontology provided its path.

        Parameters:
        - ontology_path (str): Path to the ontology file.
        - chunks_path (str): Path where ontology chunks will be stored.

        Returns:
        - np.ndarray: The generated embeddings.
        """
        # Get semantic descriptions using LlmSemantico
        semantic_descriptions = self.generate_semantic_descriptions(ontology_path, chunks_path)
        # Extract sentences from the semantic descriptions
        sentences = [data['description'] for data in semantic_descriptions.values()]
        print('Sentences len: ', len(sentences))
        # Get embeddings for the extracted sentences
        embeddings = self.embedding_generator.get_embeddings(sentences)
        print('Embeddings shape: ', embeddings.shape)
        return embeddings

    def generate_semantic_descriptions(self, ontology_path: str, chunks_path: str, chunk_size: int = 1) -> Dict[str, Dict[str, Union[str, Any]]]:
        """
        Generates semantic descriptions for a previously chunked ontology using SemanticoAI.

        Args:
        ontology_path (str): The path where the ontology to be chunked is in rdf/xml format.
        chunks_path (str): The path where the chunks will be stored.
        chunk_size (int): The size in number of entities for the segmentation of the ontology.

        Returns:
        Dict[str, Dict[str, Union[str, Any]]]: A dictionary containing semantic descriptions.
        Each key is a name from the ontology, and the value is another dictionary containing
        'proposed_name', 'description', and 'file' (path to the chunk file containing the ontology).
        """
        # Calling split_rdf to segment the ontology and save the chunks
        split_rdf(
            ontology_path,
            chunks_path,
            chunk_size=chunk_size
        )
        # List all files in the chunks_path directory
        sorted_files: List[str] = list_files(chunks_path)

        # Initialize the dictionary to hold the semantic descriptions
        semantic_descriptions: Dict[str, Dict[str, Union[str, Any]]] = {}

        # Iterate over each file in the sorted_files list
        for it, file in enumerate(sorted_files):
            # Print the current iteration number and total number of files
            print(f'iteration: {it} of {len(sorted_files)}')

            # Construct the full file path by joining chunks_path and the file name
            file_path: str = os.path.join(chunks_path, file)

            # Open and read the content of the file
            with open(file_path, 'r') as f:
                ontology_chunk: str = f.read()

            # Interact with the SemanticoAI to get semantic descriptions
            self.semantico.interact(ontology_chunk)

            # Evaluate the answer string to convert it to a dictionary
            answer_dict: Dict[str, Any] = eval(self.semantico.codeblock)

            # Construct a dictionary containing the semantic descriptions obtained from SemanticoAI
            descriptions: Dict[str, Dict[str, Union[str, Any]]] = {
                answer_dict[key]['name']: {
                    'proposed_name': answer_dict[key]['proposed_name'],
                    'description': answer_dict[key]['description'],
                    'file': file_path  # Include the file path to the chunk file containing the ontology
                } for key in answer_dict.keys()
            }

            # Update the main semantic_descriptions dictionary with the newly obtained descriptions
            semantic_descriptions.update(descriptions)

        # Return the final semantic_descriptions dictionary
        return semantic_descriptions
