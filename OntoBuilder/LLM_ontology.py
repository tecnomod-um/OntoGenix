from LLM_base.LlmBase import AbstractLlm
from typing import Optional
import os

class LlmOntology(AbstractLlm):

    def __init__(self, metadata: dict):
        super().__init__(metadata)
        # initialize prompts
        self.instructions_prompt = self.load_string_from_file(metadata['instructions'])
        self.autocompletion_prompt = self.load_string_from_file(metadata['autocompletion'])
        self.ontology_analysis_prompt = self.load_string_from_file(metadata['ontology_analysis'])
        self.ontology_synthesis_prompt = self.load_string_from_file(metadata['ontology_synthesis'])
        self.entities_analysis_prompt = self.load_string_from_file(metadata['entities_analysis'])
        self.examples = self.load_examples(metadata['examples'])
        # path setting to write outputs
        self.dataset_path = metadata['dataset']
        # initialize memories
        self.last_prompt = None
        self.owl_codeblock = None
        self.insights = None
        self.analysis = []

    def interact(self, json_data: str, instructions: str, ontology: Optional[str]):
        try:
            if json_data and instructions and not ontology:
                self.last_prompt = self.instructions_prompt.format(
                    json_data=json_data,
                    instructions=instructions
                )

            elif json_data and instructions and ontology:
                self.last_prompt = self.instructions_prompt.format(
                    json_data=json_data,
                    instructions=instructions,
                    previous_ontology=ontology
                )

            response = self.get_api_response(self.last_prompt)

            response, self.owl_codeblock = self.autocompletion(previous_input=self.last_prompt, response=response)

            self.save_response(response, self.dataset_path + '_debugging_GPT_RESPONSE.txt', mode='w')



        except ValueError as e:
            print(f"An error occurred while extracting text: {e}")

    def analyze(self, json_data: str, instructions: str, previous_ontology: str, human_ontology: str, item: int):
        try:

            self.last_prompt = self.ontology_analysis_prompt.format(
                json_data=json_data,
                instructions=instructions,
                previous_ontology=previous_ontology,
                human_ontology=human_ontology
            )

            response = self.get_api_response(self.last_prompt)

            response, improved_owl_codeblock = self.autocompletion(previous_input=self.last_prompt, response=response)

            self.save_response(response, self.dataset_path + '_debugging_GPT_ANALYSIS_item_' + str(item) + '.txt', mode='w')

            self.insights = self.extract_text(response, "IMPROVEMENT STRATEGY:", "REVISED RDF/XML ONTOLOGY:")

            return self.insights, improved_owl_codeblock

        except ValueError as e:
            print(f"An error occurred while extracting text: {e}")
            return None

    def synthesize(self, owl_codes_comparition: str, item: int):
        try:
            # analysis_str = '\n'.join([
            #     f'\nHere you have the {i + 1} analysis output you generated previously, that is the rationale followed by the improved ontology:\n{self.analysis[i]}'
            #     for i in range(len(self.analysis))])
            analysis_str = '\n'.join(
                    f'\nHere you have the analysis output you generated previously, that is the rationale followed by the improved ontology:\n{owl_codes_comparition}'
                    )

            self.last_prompt = self.ontology_synthesis_prompt.format(analysis_outputs=analysis_str)
            response = self.get_api_response(self.last_prompt)
            response, self.owl_codeblock = self.autocompletion(previous_input=self.last_prompt, response=response)

            self.save_response(response, self.dataset_path + '_debugging_GPT_SYNTHESIS_item_' + str(item) + '.txt', mode='w')

            self.insights = self.extract_text(response, "INIT", "END")

            self.save_response(self.owl_codeblock, self.dataset_path + '_ontology_LLM_item_' + str(item) + '.owl', mode='w')

            return self.insights, self.owl_codeblock

        except ValueError as e:
            print(f"An error occurred while extracting text: {e}")
            return None, None

    def analyze_segment(self, previous_ontology: str, human_ontology: str, item: int):
        try:

            self.last_prompt = self.entities_analysis_prompt.format(
                previous_ontology=previous_ontology,
                human_ontology=human_ontology
            )

            response = self.get_api_response(self.last_prompt)

            response, improved_owl_codeblock = self.autocompletion(previous_input=self.last_prompt, response=response)

            self.save_response(response, self.dataset_path + '_debugging_GPT_SEGMENTED_ANALYSIS_item_' + str(item) + '.txt', mode='w')

            self.insights = self.extract_text(response, "IMPROVEMENT STRATEGY:", "REVISED RDF/XML ONTOLOGY:")

            return self.insights, improved_owl_codeblock

        except ValueError as e:
            print(f"An error occurred while extracting text: {e}")
            return None

    def autocompletion(self, previous_input: str, response: str, max_iter=5):
        owl_codeblock = None
        done = False
        cont = 0
        while not done and cont < max_iter:
            print('Autocompletion ITERATION: ', cont)
            try:
                owl_codeblock = self.extract_text(response, "START", "END")
                done = True
            except:
                try:
                    prompt = self.autocompletion_prompt.format(
                        prev_input=previous_input,
                        response=response
                    )
                    response = self.get_api_response(prompt)
                except:
                    print('ITERATION: ', cont)
                finally:
                    cont += 1

        return response, owl_codeblock

    def load_examples(self, folder_path):
        # Get a list of all files in the folder
        files = os.listdir(folder_path)

        examples = []
        # Iterate over the files and perform operations
        for file_name in files:
            # Construct the absolute file path
            file_path = os.path.join(folder_path, file_name)
            # get the content from this file
            content = self.load_string_from_file(file_path)
            examples.append(content)

        return examples





