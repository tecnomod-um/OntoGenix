from abc import ABC
from typing import Optional

from GUI.LLM_base.LlmBase import AbstractLlm
from GUI.PlanSage.RAG_google import Searcher
from GUI.tools.text_tools import extract_text

class LlmPlanner(AbstractLlm, ABC):
    """
    This class represents a language learning model (LLM_base) ontology. It extends the AbstractLlm class and provides
    methods for interacting with the model.
    """

    name = 'PlanSage'
    def __init__(self, metadata: dict):
        """
        Initialize the LlmOntology object.

        Parameters:
        metadata (dict): A dictionary containing metadata for the LLM_base.
        """
        super().__init__(metadata)

        # initialize prompts
        self.data_description_prompt = self.load_string_from_file(metadata['data_description'])
        self.interoperability_management_prompt = self.load_string_from_file(metadata['interoperability_management'])
        # initialize containers
        self._dataset_path = metadata['dataset']
        self._data_description = None # TODO: differentiate between "data_description" and "answer" (parent class)
        self._image_file = None
        self._text_file = None
        # initialize RAG
        self.RAG = Searcher(metadata)

    @property
    def text_file(self):
        return self._text_file

    # Setter for name
    @text_file.setter
    def text_file(self, path):
        if not isinstance(path, str):
            raise ValueError("Image file path must be a string!")
        self._text_file = path

    @property
    def image_file(self):
        return self._image_file

    # Setter for name
    @image_file.setter
    def image_file(self, path):
        if not isinstance(path, str):
            raise ValueError("Image file path must be a string!")
        self._image_file = path

    @property
    def dataset_path(self):
        return self._dataset_path

    @dataset_path.setter
    def dataset_path(self, path):
        if not isinstance(path, str):
            raise ValueError("Name must be a string!")
        self._dataset_path = path

    async def interaction(self,
                          input_task: Optional[str] = None,
                          json_data: Optional[str] = None):
        """
        Perform the first interaction or a subsequent interaction with the LLM_base based on the arguments provided.

        Parameters:
        input_task (str): The input message.
        json_data (str): The input data in JSON format.
        Yields:
        str: Chunks of the response from the LLM_base.
        """
        try:
            additional_metadata = self.load_string_from_file(self.text_file) if self.text_file is not None else None
            self.current_prompt = self.data_description_prompt.format(input_task=input_task, json_data=json_data, additional_metadata=additional_metadata)
            #print(self.current_prompt)
            # Get the response from the LLM_base
            if self.image_file is not None:
                async for chunk in self.image_interpretation(self.current_prompt, self.image_file):
                    yield chunk
            else:
                async for chunk in self.get_async_api_response(self.current_prompt):
                    yield chunk
            # permanently store the generated data description answer
            self._data_description = self.answer
        except GeneratorExit as ge:
            print(f"Process stopped/cancelled by user: {ge}")
            return
        except ValueError as e:
            print(f"An error occurred: {e}")
        finally:
            self.last_prompt = self.current_prompt

    async def update(self, schema_description: str, interoperable_entities: str):
        """
        Perform the first interaction or a subsequent interaction with the LLM_base based on the arguments provided.

        Parameters:
        schema_description (str): The input schema description.
        interoperable_entities (str): The input data interoperable entities.
        Yields:
        str: Chunks of the response from the LLM_base.
        """
        try:
            # Act as first_interaction
            self.current_prompt = self.interoperability_management_prompt.format(
                schema_description=schema_description,
                interoperable_entities=interoperable_entities
            )

            # Get the response from the LLM_base
            async for chunk in self.get_async_api_response(self.current_prompt, seed=self.seed):
                yield chunk

            # permanently store the generated data description answer
            self._data_description = '\n' + self.answer
        except GeneratorExit as ge:
            print(f"Process stopped/cancelled by user: {ge}")
            return
        except ValueError as e:
            print(f"An error occurred: {e}")
        finally:
            self.last_prompt = self.current_prompt

    def get_from_schema(self, full_text: str):
        # TODO: check this non-deterministic code
        try:
            # Split the full text into sections
            classes = extract_text(full_text, start_marker="**Classes:**", end_marker="**Subclasses:**")
            subclasses = extract_text(full_text, start_marker="**Subclasses:**", end_marker="**Object Properties:**")
            object_properties = extract_text(full_text, start_marker="**Object Properties:**", end_marker="**Data Type Properties:**")
            data_properties = extract_text(full_text, start_marker="**Data Type Properties:**", end_marker="**")
            # TODO: check how to reformat this code
            classes_list = self.RAG._extract_items(classes)
            subclasses_list = self.RAG._extract_items(subclasses)
            object_properties_list = self.RAG._extract_items(object_properties)
            data_properties_list = self.RAG._extract_items(data_properties)

            entities = classes_list + subclasses_list + object_properties_list + data_properties_list

            schema_entities = [self.RAG._search_schema_org(entity) for entity in entities]

            return schema_entities

        except:
            return None
