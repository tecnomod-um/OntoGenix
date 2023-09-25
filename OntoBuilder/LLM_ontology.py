from LLM_base.LlmBase import AbstractLlm
from typing import Optional
import copy
import os

class LlmOntology(AbstractLlm):

    def __init__(self, metadata: dict):
        super().__init__(metadata)
        # initialize prompts
        self.instructions_prompt = self.load_string_from_file(metadata['instructions'])
        self.entity_improvement_prompt = self.load_string_from_file(metadata['entity_improvement'])
        # path setting to write outputs
        self.dataset_path = metadata['dataset']
        # initialize memories
        self.codeblock = None

    def interact(self,
                 json_data: str = None,
                 rationale: str = None,
                 next_entity: str = None,
                 task: str = None):

        if json_data and rationale:
            self.current_prompt = self.instructions_prompt.format(
                json_data=json_data,
                rationale=rationale
            )

        elif rationale and next_entity and task:
            self.current_prompt = self.entity_improvement_prompt.format(
                rationale=rationale,
                next_entity=next_entity,
                task=task
            )

        # Get the response from the LLM_base
        self.get_api_response(self.current_prompt)
        # extract the codeblock
        self.codeblock = self.extract_text(self.answer, start_marker="```xml", end_marker="```")
        # write the response in a txt file
        self.save_response(self.answer, self.dataset_path + '_debugging_GPT_RESPONSE.txt', mode='a')


    def regenerate(self):
        try:
            # Reuse the last prompt
            response = self.get_api_response(self.current_prompt)
            # extract the codeblock
            self.codeblock = self.extract_text(self.answer, start_marker="```xml", end_marker="```")
            # write the response in a txt file
            self.save_response(response, self.dataset_path + '_debugging_GPT_RESPONSE.txt', mode='a')

        except ValueError as e:
            print(f"An error occurred while extracting text: {e}")
        finally:
            self.last_prompt = self.current_prompt







