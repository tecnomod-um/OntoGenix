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

    async def get_async_api_response(self, content: str, temperature=0, stream=True):
        self.answer = ""
        completion = self.client.chat.completions.create(
                model=self.model,
                messages=[{
                    'role': 'system',
                    'content': self.role
                }, {
                    'role': 'user',
                    'content': content,
                }],
                tools=tools,
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



class State:
    def __init__(self, name):
        self.name = name

class Transition:
    def __init__(self, from_state, to_state, action, requires_confirmation):
        self.from_state = from_state
        self.to_state = to_state
        self.action = action
        self.requires_confirmation = requires_confirmation

    def is_valid(self, reached_states):
        if self.from_state.name == "PROMPT_CRAFT" and self.to_state.name == "ONTOLOGY_ENTITY":
            # Check if ONTOLOGY has been reached previously
            return "ONTOLOGY" in [state.name for state in reached_states]
        return True

class Automaton:
    def __init__(self):
        self.states = {}
        self.transitions = []
        self._reached_states = set()

        # Set the automaton initial states
        self.current_state = None
        self.action = None

    @property
    def reached_states(self):
        return list(self._reached_states)

    def add_state(self, name):
        state = State(name)
        self.states[name] = state
        return state

    def add_transition(self, from_state, to_state, action, requires_confirmation):
        transition = Transition(from_state, to_state, action, requires_confirmation)
        self.transitions.append(transition)

    def can_transition(self, from_state, to_state):
        print("can_transition->", ' from_state ', from_state, from_state.name, ' to_state ', to_state, to_state.name )
        for transition in self.transitions:
            if (
                transition.from_state.name == from_state.name
                and transition.to_state.name == to_state.name
            ):
                if not transition.is_valid(self.reached_states):
                    return False  # Transition is not valid based on conditions
                return True
        return False

    def perform_transition(self, to_state):
        print('to_state: ', to_state, to_state.name)
        if self.can_transition(self.current_state, to_state):
            self._reached_states.add(to_state)
            self.current_state = to_state
            print('realizo perform transition')
            return True
        else:
            print('not perform transition')
            return False

    def possible_next_states(self):
        possible_states = []
        for transition in self.transitions:
            if transition.from_state.name == self.current_state.name:
                possible_states.append(transition.to_state.name)
        return possible_states

class Automata_Manager:

    def __init__(self):
        # Create the automaton
        self.droid = Automaton()

        # Define states
        PROMPT_CRAFT = self.droid.add_state("PROMPT_CRAFT")
        HIGH_LEVEL_STRUCTURE = self.droid.add_state("HIGH_LEVEL_STRUCTURE")
        ONTOLOGY = self.droid.add_state("ONTOLOGY")
        ONTOLOGY_ENTITY = self.droid.add_state("ONTOLOGY_ENTITY")
        MAPPING = self.droid.add_state("MAPPING")
        None_STATE = self.droid.add_state("None")

        # Set initial states
        self.droid.current_state = None_STATE

        # Define transitions
        self.droid.add_transition(None_STATE, PROMPT_CRAFT, "prompt_crafting", False)
        self.droid.add_transition(None_STATE, HIGH_LEVEL_STRUCTURE, "data_description", False)

        self.droid.add_transition(PROMPT_CRAFT, PROMPT_CRAFT, "prompt_crafting", True)
        self.droid.add_transition(PROMPT_CRAFT, HIGH_LEVEL_STRUCTURE, "data_description", True)
        self.droid.add_transition(PROMPT_CRAFT, ONTOLOGY_ENTITY, "ontology_building", True)

        self.droid.add_transition(HIGH_LEVEL_STRUCTURE, ONTOLOGY, "ontology_building", False)
        self.droid.add_transition(HIGH_LEVEL_STRUCTURE, MAPPING, "mapping", False)
        self.droid.add_transition(HIGH_LEVEL_STRUCTURE, PROMPT_CRAFT, "prompt_crafting", False)

        self.droid.add_transition(ONTOLOGY, PROMPT_CRAFT, "prompt_crafting", False)
        self.droid.add_transition(ONTOLOGY, HIGH_LEVEL_STRUCTURE, "data_description", False)
        self.droid.add_transition(ONTOLOGY, ONTOLOGY_ENTITY, "ontology_entity_enrichment", False)
        self.droid.add_transition(ONTOLOGY, MAPPING, "mapping", False)

        self.droid.add_transition(ONTOLOGY_ENTITY, PROMPT_CRAFT, "prompt_crafting", False)
        self.droid.add_transition(ONTOLOGY_ENTITY, HIGH_LEVEL_STRUCTURE, "data_description", False)
        self.droid.add_transition(ONTOLOGY_ENTITY, MAPPING, "mapping", False)

        self.droid.add_transition(MAPPING, PROMPT_CRAFT, "prompt_crafting", False)
        self.droid.add_transition(MAPPING, HIGH_LEVEL_STRUCTURE, "data_description", False)
        self.droid.add_transition(MAPPING, ONTOLOGY_ENTITY, "ontology_entity_enrichment", False)


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
        self.tools = metadata['tools']
        # Initialize automata
        self.automata = Automata_Manager()

    async def interaction(self, content: str = ""):
        try:
            # format the current prompt
            self.current_prompt = self.instructions.format(
                prompt=content,
                current_state=self.automata.droid.current_state.name,
                transitions=self.automata.droid.possible_next_states()
            )

            # Get the response from the LLM_base
            async for chunk in self.get_async_api_response(content=self.current_prompt):
                yield chunk

            # update the short term memory
            if self.update_memories(self.answer):
                # let's perform the corresponding action.
                self.select_process()

        except ValueError as e:
            print(f"An error occurred: {e}")
        finally:
            self.last_prompt = self.current_prompt

    def select_process(self):
        try:
            print('\n -----------select_process-------------------')
            print(self.automata.droid.action, ' -> ', self.available_functions.keys())
            if self.automata.droid.action in self.available_functions.keys():
                self.function_calling(
                    content=self.automata.droid.action, 
                    tools=self.tools
                )
                self._process_function_response()

        except Exception as e:
            print("Exception: {e}".format(e=e))


    def update_memories(self, response: str):
        try:
            print('\n ------------update_memories------------------')
            self.automata.droid.action = self.extract_text(response, "Action:", "**Next state:**").strip()
            print('action: ', self.automata.droid.action)
            next_state = self.extract_text(response, "Next State:", "**Confirmation:**").strip()
            return self.automata.droid.perform_transition(self.automata.droid.states[next_state])
        except ValueError as e:
            print(f"An error occurred: {e}")
            return False


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
    'available_functions': available_functions,
    'tools': tools
}

gui_manager = GuiManager(metadata)

prompt = '''lets enrich the entity product'''

async for chunk in gui_manager.interaction(content=prompt):
    print(chunk, end="")

print('------------------final states--------------------')
print("current_state: ", gui_manager.automata.droid.current_state.name)
[print(state.name, end=" ") for state in gui_manager.automata.droid.reached_states]
print("\n possible_next_states: ", gui_manager.automata.droid.possible_next_states())


