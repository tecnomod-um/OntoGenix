from LLM_base.LlmBase import AbstractLlm
from typing import Optional
import copy
import os

class LlmOntology(AbstractLlm):

    def __init__(self, metadata: dict):
        super().__init__(metadata)
        # initialize prompts
        self.object_properties_instructions = self.load_string_from_file(metadata['object_properties_instructions'])
        self.data_properties_instructions = self.load_string_from_file(metadata['data_properties_instructions'])
        self.classes_improvement = self.load_string_from_file(metadata['classes_improvement'])
        self.properties_improvement = self.load_string_from_file(metadata['properties_improvement'])
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
                        data_description: str = None,
                        rationale: str = None,
                        class_entity: str = None,
                        next_entity: str = None,
                        mode: str = "properties"):
        try:

            if data_description and rationale and not class_entity:
                self.current_prompt = self.object_properties_instructions.format(
                    data_description=data_description,
                    rationale=rationale
                )
            elif data_description and rationale and class_entity:
                print(data_description)
                print(rationale)
                print(class_entity)
                self.current_prompt = self.data_properties_instructions.format(
                    data_description=data_description,
                    rationale=rationale,
                    class_entity=class_entity
                )
            elif rationale and next_entity and mode == "classes":
                self.current_prompt = self.classes_improvement.format(
                    rationale=rationale,
                    next_entity=next_entity
                )
            elif rationale and next_entity and mode == "properties":
                self.current_prompt = self.properties_improvement.format(
                    rationale=rationale,
                    next_entity=next_entity
                )

            # Get the response from the LLM_base
            async for chunk in self.get_async_api_response(self.current_prompt):
                yield chunk

        except ValueError as e:
            print(f"An error occurred during interaction: {e}")
        finally:
            self.last_prompt = self.current_prompt

    def get_xml_codeblock(self):
        return self.extract_text(self.answer, start_marker="```xml", end_marker="```")







