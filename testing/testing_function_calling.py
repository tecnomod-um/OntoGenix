import os
import json
from openai import OpenAI
from abc import ABC
import os
from dotenv import dotenv_values

from abc import ABC
from typing import Optional
from enum import Enum


class AbstractLlm(ABC):

    def __init__(self, metadata: dict):
        # set api key path
        config = dotenv_values(metadata['api_key_path'])
        # create a client with its api key
        self.client = OpenAI(api_key = config['OPENAI_API_KEY'])
        # set client properties
        self.model = metadata['model']
        self.role = metadata['role']
        self.answer = ""
        self.tool_calls = None

        # set utilities
        self.last_prompt = None
        self.current_prompt = None

    def function_calling(self, content: str, tools=None):
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[{
                'role': 'system',
                'content': self.role
            }, {
                'role': 'user',
                'content': content,
            }],
            tools=tools,
            temperature=0
        )

        self.tool_calls = response.choices[0].message.tool_calls

    async def get_async_api_response(self, role: str, content: str, temperature=0, stream=True):
        self.answer = ""
        completion = self.client.chat.completions.create(
                model=self.model,
                messages=[{
                    'role': role,
                    'content': content,
                }],
                temperature=temperature,
                stream=stream
        )

        for chunk in completion:
            data = chunk.choices[0].delta.content
            if data is not None:
                self.answer += data
                yield data

    def _process_function_response(self):
        """Processes the response message from model and calls the intended function.
        :param function_callback: callback function which be called with the corresponding arguments.
        :return: the function to be returned
        """
        for tool_call in self.tool_calls:
            function_name = tool_call.function.name
            print("function_name: ", function_name)

            # Check if the function exists in metadata
            if function_name in metadata['available_functions']:
                function_to_call = metadata['available_functions'][function_name]

                try:
                    # Assuming arguments are in JSON format
                    function_args = json.loads(tool_call.function.arguments)
                    # Calling the function with unpacked arguments
                    function_to_call(**function_args)
                except json.JSONDecodeError as e:
                    print(f"Error decoding JSON: {e}")
                except Exception as e:
                    print(f"Error during function call: {e}")
            else:
                print(f"Function {function_name} not found in metadata.")

    @staticmethod
    def load_string_from_file(file_path):
        with open(file_path, 'r') as file:
            return file.read()

    @staticmethod
    def extract_text(text: str, start_marker: str, end_marker: str) -> str:
        """
        Extracts a substring of text between two markers and returns it.

        Args:
            text (str): The text to be searched.
            start_marker (str): The start marker of the substring.
            end_marker (str): The end marker of the substring.

        Returns:
            The substring of text between start_marker and end_marker.

        Raises:
            ValueError: If start_marker or end_marker is not found in text.
        """
        start_index = text.find(start_marker) + len(start_marker)
        end_index = text.find(end_marker, start_index)
        if start_index == -1:
            raise ValueError("Start marker not found in text.")
        elif end_index == -1:
            raise ValueError("End marker not found in text.")
        return text[start_index:end_index].strip()


class GuiManager(AbstractLlm, ABC):
    """
    This class represents a language learning model (LLM_base) ontology. It extends the AbstractLlm class and provides
    methods for interacting with the model.

    TODO: the long_term_memory mechanism is not implemented.
    """

    def __init__(self, metadata: dict):
        """
        Initialize the LlmOntology object.

        Parameters:
        metadata (dict): A dictionary containing metadata for the LLM_base.
        """
        super().__init__(metadata)

        # initialize prompts
        self.instructions = self.load_string_from_file(metadata['instructions'])
        self.available_functions = metadata['available_functions']
        # Initialize memories
        self.short_term_memory = ""


    async def interaction(self, prompt: str = "", current_state: str = ""):
        try:
            # format the current prompt
            self.current_prompt = self.instructions.format(
                prompt=prompt,
                current_state=current_state,
                short_term_memory=self.short_term_memory)

            # Get the response from the LLM_base
            async for chunk in self.get_async_api_response(role='system', content=self.current_prompt):
                yield chunk

            self.update_memories(self.answer)

        except ValueError as e:
            print(f"An error occurred: {e}")
        finally:
            self.last_prompt = self.current_prompt

    def select_process(self, content: str, tools=None):
        try:
            self.function_calling(content=content, tools=tools)
            self._process_function_response()

        except Exception as e:
            print("Exception: {e}".format(e=e))

    def update_memories(self, response: str):
        try:
            self.short_term_memory = self.extract_text(response, "**Updated Memory:**", "**Actions:**").strip()
        except ValueError as e:
            print(f"An error occurred: {e}")



from testing.auxiliar_api import *

available_functions = {
    "prompt_crafting": prompt_crafting,
    "data_description": data_description,
    "ontology_building": ontology_building,
    "ontology_entity_enrichment": ontology_entity_enrichment,
    "mapping": mapping
}

metadata = {
    'role': "you are a powerful ontology engineer that must select the appropriate function to be called.",
    'instructions': "./testing/gui_manager_role.prompt",
    'model': 'gpt-4-1106-preview',
    'api_key_path': "./GUI/.env",
    'available_functions': available_functions
}

gui_manager = GuiManager(metadata)

class OntologyState(Enum):
    """Enum class to represent different states of ontology."""
    PROMPT_CRAFT = "PROMPT_CRAFT"
    HIGH_LEVEL_STRUCTURE = "HIGH_LEVEL_STRUCTURE"
    ONTOLOGY = "ONTOLOGY"
    ONTOLOGY_ENTITY = "ONTOLOGY_ENTITY"
    MAPPING = "MAPPING"


prompt = '''lets define the structure of the ontology and then generate the ontology and the mapping.
'''
current_state = OntologyState.PROMPT_CRAFT
async for chunk in gui_manager.interaction(prompt=prompt, current_state=current_state.value):
    print(chunk, end="")


prompt = gui_manager.extract_text(gui_manager.answer, "Action:", "Rationale:").strip()
gui_manager.select_process(content=prompt, tools=tools)




