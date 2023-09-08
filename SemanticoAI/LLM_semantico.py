from LLM_base.LlmBase import AbstractLlm
import os
import numpy as np


class LlmSemantico(AbstractLlm):

    def __init__(self, metadata: dict) -> object:
        super().__init__(metadata)
        # initialize prompts
        self.instructions = self.load_string_from_file(metadata['instructions'])
        # path setting to write outputs
        self.dataset_path = metadata['dataset']
        # container for semantic descriptions of entities in segmented ontologies
        self.semantic_descriptions = None

    def interact(self, ontology: str, auto_complete: bool = False):
        try:
            prompt = self.instructions.format(
                ontology=ontology
            )

            response = self.get_api_response(prompt)

            return eval(response)

        except ValueError as e:
            print(f"An error occurred while extracting text: {e}")
            return None

    def chunksTransform(self, directory_path):
        # List all files in the directory
        files = os.listdir(directory_path)
        sorted_files = sorted(files, key=lambda x: int(x.split('_')[1].split('.')[0]))
        print(sorted_files)

        self.semantic_descriptions = dict()
        # Read each file
        for it, file in enumerate(sorted_files):  # el chunk_32 da fallos porque salen 4 diccionarios
            print('iteration: ', it, ' of ', len(sorted_files))
            # Construct full file path
            file_path = os.path.join(directory_path, file)

            # Open each file and read its content
            if os.path.isfile(file_path):  # Check if it's a file, not a directory
                with open(file_path, 'r') as f:
                    ontology = f.read()
                try:
                    response_dict = self.interact(ontology)

                    data = {
                        response_dict[key]['name']: {
                            'proposed_name': response_dict[key]['proposed_name'],
                            'description': response_dict[key]['description'],
                            'file': file_path
                        } for key in response_dict.keys()
                    }

                    self.semantic_descriptions.update(data)

                except ValueError as e:
                    print(f"An error occurred while extracting text: {e}")
