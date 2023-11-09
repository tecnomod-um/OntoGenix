from GUI.LLM_base.LlmBase import AbstractLlm
from typing import Optional
import copy
import os

from enum import Enum

class OntologyState(Enum):
    ONTOLOGY = "ONTOLOGY"
    ONTOLOGY_ENTITY = "ONTOLOGY_ENTITY"

class LlmOntology(AbstractLlm):

    def __init__(self, metadata: dict):
        super().__init__(metadata)
        # initialize prompts
        self.ontology_instructions = self.load_string_from_file(metadata['ontology_instructions'])
        self.entity_improvement = self.load_string_from_file(metadata['entity_improvement'])
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
                        entity: str = None,
                        state: OntologyState = None):
        try:
            if state.value == OntologyState.ONTOLOGY.value:
                self.current_prompt = self.ontology_instructions.format(
                    data_description=data_description
                )
            elif state.value == OntologyState.ONTOLOGY_ENTITY.value:
                self.current_prompt = self.entity_improvement.format(
                    data_description=data_description,
                    entity=entity
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







