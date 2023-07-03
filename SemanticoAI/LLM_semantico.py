from LLM_base.LlmBase import AbstractLlm
import os
import numpy as np

class LlmSemantico(AbstractLlm):

    def __init__(self, metadata: dict):
        super().__init__(metadata)
        # initialize prompts
        self.instructions = self.load_string_from_file(metadata['instructions'])
        # path setting to write outputs
        self.dataset_path = metadata['dataset']
        # initialize memories
        self.semantic_descriptions = dict()

    def interact(self, ontology: str, auto_complete: bool = False):
        try:
            prompt = self.instructions.format(
                ontology=ontology
            )

            response = self.get_api_response(prompt)
            print('##################################\n', response)
            dictionary_str = self.extract_text(response, "START", "FINISH")

            self.save_response(dictionary_str, self.dataset_path + '_ontology_semantic_description_LLM.ttl', mode='w')
            print(type(dictionary_str))

            self.semantic_descriptions = eval(dictionary_str)

        except ValueError as e:
            print(f"An error occurred while extracting text: {e}")

    def chunksTransform(self, directory_path):
        # List all files in the directory
        files = os.listdir(directory_path)
        print(files)

        dictionaries = dict()

        # Read each file
        for it, file in enumerate(files):  # el chunk_32 da fallos porque salen 4 diccionarios
            print('iteration: ', it, ' of ', len(files))
            # Construct full file path
            file_path = os.path.join(directory_path, file)

            # Open each file and read its content
            if os.path.isfile(file_path):  # Check if it's a file, not a directory
                with open(file_path, 'r') as f:
                    chunk = f.read()

                self.interact(chunk)

                dictionaries.update(self.semantic_descriptions)

        np.save(directory_path + 'dictionaries.npy', dictionaries, allow_pickle=True)
        sentences = list(dictionaries.keys())
        np.save(directory_path + 'sentences.npy', sentences)

