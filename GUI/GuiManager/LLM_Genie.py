from abc import ABC
from typing import Optional

from GUI.LLM_base.LlmBase import AbstractLlm
from GUI.GuiManager.automata_manager import Automata_Manager


class Genie(AbstractLlm, ABC):
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
        self.query = None
        self.available_functions = metadata['available_functions']
        self.tools = metadata['tools']
        # Initialize automata
        self.automata = Automata_Manager()

    async def interaction(self, prompt: str = ""):
        try:
            self.query = prompt
            # format the current prompt
            self.current_prompt = self.instructions.format(
                prompt=prompt,
                current_state=self.automata.droid.current_state.name,
                transitions=self.automata.droid.possible_next_states()
            )

            # Get the response from the LLM_base
            async for chunk in self.get_async_api_response(content=self.current_prompt):
                yield chunk

            # update the short term memory
            if self.update_memories(self.answer):
                # let's perform the corresponding action.
                await self.select_process()

        except ValueError as e:
            print(f"An error occurred: {e}")
        finally:
            self.last_prompt = self.current_prompt

    async def select_process(self):
        try:
            if self.automata.droid.action in self.available_functions.keys():
                self.function_calling(
                    content='Action: ' + self.automata.droid.action + ' prompt: ' + self.query,
                    tools=self.tools
                )
                await self._process_function_response()

        except Exception as e:
            print("Exception: {e}".format(e=e))


    def update_memories(self, response: str):
        try:
            self.automata.droid.action = self.extract_text(response, "Action:", "**Next state:**").strip()
            next_state = self.extract_text(response, "Next State:", "**Confirmation:**").strip()
            return self.automata.droid.perform_transition(self.automata.droid.states[next_state])
        except ValueError as e:
            print(f"An error occurred: {e}")
            return False