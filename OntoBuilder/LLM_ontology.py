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
        self._dataset_path = metadata['dataset']

    @property
    def dataset_path(self):
        return self._dataset_path

    # Setter for name
    @dataset_path.setter
    def dataset_path(self, path):
        if not isinstance(path, str):
            raise ValueError("Name must be a string!")
        self._dataset_path = path

    async def interact(self,
                 json_data: str = None,
                 rationale: str = None,
                 next_entity: str = None,
                 task: str = None):
        try:

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
            async for chunk in self.get_async_api_response(self.current_prompt):
                yield chunk

        except ValueError as e:
            print(f"An error occurred during interaction: {e}")
        finally:
            self.last_prompt = self.current_prompt


    async def regenerate(self):
        try:
            # Reuse the last prompt
            async for chunk in self.get_async_api_response(self.current_prompt):
                yield chunk

        except ValueError as e:
            print(f"An error occurred while extracting text: {e}")
        finally:
            self.last_prompt = self.current_prompt

    def get_xml_codeblock(self):
        return self.extract_text(self.answer, start_marker="```xml", end_marker="```")







