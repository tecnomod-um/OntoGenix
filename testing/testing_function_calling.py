import os
import json
import openai
from abc import ABC
import openai
import os
from dotenv import dotenv_values
from GUI.LLM_base.LlmBase import AbstractLlm

from abc import ABC
from typing import Optional

from GUI.LLM_base.LlmBase import AbstractLlm
from enum import Enum

class OntologyState(Enum):
    """Enum class to represent different states of ontology."""
    PROMPT_CRAFT = "PROMPT_CRAFT"
    DESCRIPTION = "DATA_DESCRIPTION"
    ONTOLOGY_OBJECT_PROPERTIES = "ONTOLOGY_OBJECT_PROPERTIES"
    ONTOLOGY_DATA_PROPERTIES = "ONTOLOGY_DATA_PROPERTIES"
    ONTOLOGY_ENTITY = "ONTOLOGY_ENTITY"
    MAPPING = "MAPPING"

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
        self.role = self.load_string_from_file(metadata['role'])
        self.instructions = self.load_string_from_file(metadata['instructions'])
        # Initialize memories
        self.short_term_memory = None

    async def interaction(self, prompt: str, current_state: str):
        try:
            self.current_prompt = self.instructions.format(
                prompt=prompt,
                current_state=current_state,
                short_term_memory=self.short_term_memory)
            # Get the response from the LLM_base
            async for chunk in self.get_async_api_response(self.current_prompt):
                yield chunk

        except ValueError as e:
            print(f"An error occurred: {e}")
        finally:
            self.last_prompt = self.current_prompt

    def update_memories(self, response: str, first: bool = True):
        try:
            if first:
                self.short_term_memory = self.extract_text(response, "**Output Memory:**", "**Output Tasks:**").strip()
            else:
                self.short_term_memory = self.extract_text(response, "**Updated Memory:**", "**Output Tasks:**").strip()
        except ValueError as e:
            print(f"An error occurred: {e}")


class FunctionCaller(ABC):

    def __init__(self, metadata: dict):

        config = dotenv_values(metadata['api_key_path'])
        openai.api_key = config['OPENAI_API_KEY']

        self.role = metadata['role']
        self.model = metadata['model']
        self.functions_data = metadata['functions_data']

    def interaction(self, content: str, function_name: object, temperature=0):
        try:
            response = openai.ChatCompletion.create(
                    model=self.model,
                    messages=[{
                        'role': 'system',
                        'content': self.role
                    }, {
                        'role': 'user',
                        'content': content,
                    }],
                    temperature=temperature,
                    functions=self.functions_data,
                    function_call={"name": "select_process"}
            )
            self._process_function_response(response, function_name)

        except Exception as e:
            print("Exception: {e}".format(e=e))

    def _process_function_response(self, response, function_callback):
        """Processes the response message from model and calls the intended function.
        :param function_callback: callback function which be called with the corresponding arguments.
        :return: the function to be returned
        """
        response_message = response["choices"][0]["message"]
        function_args = json.loads(response_message["function_call"]["arguments"])
        function_response = function_callback(**function_args)
        return function_response




def load_dataset():
    print("dataset loaded")

def structure_definition():
    print('structure_definition')

def ontology_building():
    print('ontology_building')

def mapping():
    print('mapping')

def exit():
    print("exit")

def select_process(method: str):
    AVAILABLE_FUNCTIONS[method]()


AVAILABLE_FUNCTIONS = {
    "load_dataset": load_dataset,
    "structure_definition": structure_definition,
    "ontology_building": ontology_building,
    "mapping": mapping,
    "exit": exit
}
functions_data = [
    {
        "name": "select_process",
        "description": "Can select the engineering step for creating an ontology using LLMs",
        "parameters": {
            "type": "object",
            "properties": {
                "method": {
                    "type": "string",
                    "enum": ["load_dataset", "structure_definition", "ontology_building", "mapping", "exit"],
                    "description": "Ontology engineering self-assembling program interface."},
            }
        }
    }
]

metadata = {
    'role': "you are a powerful ontology engineer that must select the appropriate function to be called.",
    'model': 'gpt-3.5-turbo',
    'api_key_path': "./GUI/.env",
    'functions_data': functions_data
}

function_caller = FunctionCaller(metadata)

prompt = "hello"
function_caller.interaction(prompt, select_process)


metadata = {
    'role': "./testing/gui_manager_role.prompt",
    'instructions': "./testing/gui_manager_role.prompt",
    'model': 'gpt-3.5-turbo',
    'api_key_path': "./GUI/.env"
}
gui_manager = GuiManager(metadata)

prompt = "i want to focus on the product class"
state = "PROMPT_CRAFT"
async for chunk in gui_manager.interaction(prompt, state):
    print(chunk, end="")

# gui_manager.update_memories(gui_manager.answer, first=True)