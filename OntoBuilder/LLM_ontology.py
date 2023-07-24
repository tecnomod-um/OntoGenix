from LLM_base.LlmBase import AbstractLlm
from typing import Optional
import os

class LlmOntology(AbstractLlm):

    def __init__(self, metadata: dict):
        super().__init__(metadata)
        # initialize prompts
        self.instructions_prompt = self.load_string_from_file(metadata['instructions'])
        self.autocompletion_prompt = self.load_string_from_file(metadata['autocompletion'])
        self.entities_analysis_prompt = self.load_string_from_file(metadata['entities_analysis'])
        self.entity_improvement_prompt = self.load_string_from_file(metadata['entity_improvement'])
        # path setting to write outputs
        self.dataset_path = metadata['dataset']
        # initialize memories
        self.owl_codeblock = None

    def interactByEntity(self,
                         ontology: str = None,
                         task: str = None,
                         entity: str = None,
                         improved_version: str = None,
                         reasoning: str = None,
                         next_entity: str = None):

        self.current_prompt = self.entity_improvement_prompt.format(
            ontology=ontology,
            task=task,
            entity=entity,
            improved_version=improved_version,
            reasoning=reasoning,
            next_entity=next_entity
        )

        try:
            response = self.get_api_response(self.current_prompt)

            owl_entity_codeblock = self.extract_text(response, "START", "FINISH")

            self.save_response(response, self.dataset_path + '_debugging_interactByEntityPrompt.txt', mode='w')

        except ValueError as e:
            print(f"An error occurred while extracting text: {e}")
        finally:
            self.last_prompt = self.current_prompt

        return owl_entity_codeblock

    def interact(self,
                 json_data: str = None,
                 rationale: str = None,
                 instructions: str = None,
                 ontology: str = None,
                 human_ontology: str = None):

        if json_data and rationale and instructions and not ontology:
            self.current_prompt = self.instructions_prompt.format(
                json_data=json_data,
                rationale=rationale,
                instructions=instructions
            )
        elif json_data and rationale and instructions and ontology:
            self.current_prompt = self.instructions_prompt.format(
                json_data=json_data,
                rationale=rationale,
                instructions=instructions,
                previous_ontology=ontology
            )
        elif rationale and ontology and human_ontology:
            self.current_prompt = self.entities_analysis_prompt.format(
                rationale=rationale,
                previous_ontology=ontology,
                human_ontology=human_ontology
            )

        self.generate_response()

    def generate_response(self):
        try:
            response = self.get_api_response(self.current_prompt)

            response, self.owl_codeblock = self.autocompletion(previous_input=self.current_prompt, response=response)

            self.save_response(response, self.dataset_path + '_debugging_GPT_RESPONSE.txt', mode='w')

        except ValueError as e:
            print(f"An error occurred while extracting text: {e}")
        finally:
            self.last_prompt = self.current_prompt

    def regenerate(self):
        self.generate_response()

    def autocompletion(self, previous_input: str, response: str, max_iter=5):
        owl_codeblock = None
        done = False
        cont = 0
        while not done and cont < max_iter:
            print('Autocompletion ITERATION: ', cont)
            try:
                owl_codeblock = self.extract_text(response, "START", "FINISH")
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







