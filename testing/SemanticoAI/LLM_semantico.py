from typing import Dict, Any, List, Union
from LLM_base.LlmBase import AbstractLlm
import os
from tools.tools import list_files
from tools.rdf_tools import split_rdf



class LlmSemantico(AbstractLlm):
    """
    LlmSemantico is a class that inherits from AbstractLlm and is used for interacting with SemanticoAI.
    It initializes with metadata and has methods to interact with the ontology and handle errors gracefully.
    """

    def __init__(self, metadata: Dict[str, Union[str, Any]]):
        """
        Initializes the LlmSemantico instance.

        Args:
        metadata (Dict[str, Union[str, Any]]): A dictionary containing metadata information.
        It should have 'instructions' key with the path to the instructions file and 'dataset' key with the path to the dataset.
        """
        super().__init__(metadata)  # Call the __init__ method of the parent class AbstractLlm with metadata

        # Load the instructions string from the file specified in metadata
        self.instructions: str = self.load_string_from_file(metadata['instructions'])
        # Set the dataset path from metadata
        self.ontology_path: str = metadata['ontology_path']
        self.chunks_path: str = metadata['chunks_path']

    def interact(self, ontology: str) -> None:
        """
        Interacts with SemanticoAI by sending a prompt and receiving a response.

        Args:
        ontology (str): The ontology string to be formatted into the prompt.

        Raises:
        ValueError: If an error occurs while extracting text.
        """
        try:
            # Format the instructions string with the provided ontology to create the prompt
            prompt: str = self.instructions.format(ontology=ontology)

            # Send the prompt to SemanticoAI and get the response
            self.get_api_response(prompt)
        except ValueError as e:
            # Print the error message if a ValueError occurs
            print(f"An error occurred while extracting text: {e}")

    def generate_semantic_descriptions(self, chunk_size: int = 1) -> Dict[str, Dict[str, Union[str, Any]]]:
        """
        Generates semantic descriptions for a previously chunked ontology using SemanticoAI.

        Args:
        chunk_size (int): The size in number of entities for the segmentation of the ontology.

        Returns:
        Dict[str, Dict[str, Union[str, Any]]]: A dictionary containing semantic descriptions.
        Each key is a name from the ontology, and the value is another dictionary containing
        'proposed_name', 'description', and 'file' (path to the chunk file containing the ontology).
        """
        split_rdf(self.ontology_path, self.chunks_path, chunk_size=chunk_size)  # Calling split_rdf to segment the ontology and save the chunks

        # List all files in the chunks_path directory
        sorted_files: List[str] = list_files(self.chunks_path)

        # Initialize the dictionary to hold the semantic descriptions
        semantic_descriptions: Dict[str, Dict[str, Union[str, Any]]] = {}

        # Iterate over each file in the sorted_files list
        for it, file in enumerate(sorted_files):
            # Print the current iteration number and total number of files
            print(f'iteration: {it} of {len(sorted_files)}')

            # Construct the full file path by joining chunks_path and the file name
            file_path: str = os.path.join(self.chunks_path, file)

            # Open and read the content of the file
            with open(file_path, 'r') as f:
                ontology: str = f.read()

            # Interact with the SemanticoAI to get semantic descriptions
            self.interact(ontology)

            # Evaluate the answer string to convert it to a dictionary
            answer_dict: Dict[str, Any] = eval(self.answer)

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
