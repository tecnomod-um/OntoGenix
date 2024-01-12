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
        Initialize the Genie object.

        Parameters:
        metadata (dict): A dictionary containing metadata for the Genie model.
        """
        super().__init__(metadata)

        # Initialize prompts and other attributes
        self.instructions = self.load_string_from_file(metadata['instructions'])
        self.query = None
        self.available_functions = metadata['available_functions']
        self.tools = metadata['tools']
        # Initialize automata manager
        self.automata = Automata_Manager()

    async def interaction(self, prompt: str = ""):
        """
        Perform an interaction with the Genie model.

        Parameters:
        prompt (str): The input prompt for the interaction.

        Yields:
        str: Chunks of the response from the Genie model.
        """
        try:
            self.query = prompt
            # Format the current prompt
            self.current_prompt = self.instructions.format(
                prompt=prompt,
                current_state=self.automata.droid.current_state.name,
                transitions=self.automata.droid.possible_next_states()
            )

            # Get the response from the Genie model
            async for chunk in self.get_async_api_response(content=self.current_prompt):
                yield chunk

            # Update the short-term memory
            if self.update_memories(self.answer):
                # Perform the corresponding action
                await self.select_process()

        except ValueError as e:
            print(f"An error occurred: {e}")
        finally:
            self.last_prompt = self.current_prompt

    async def select_process(self):
        """
        Select and perform the appropriate action based on the Genie model's response.
        """
        try:
            if self.automata.droid.action in self.available_functions.keys():
                self.function_calling(
                    content='Action: ' + self.automata.droid.action + ' prompt: ' + self.query,
                    tools=self.tools
                )
                await self._process_function_response()

        except Exception as e:
            print(f"Exception: {e}")

    def update_memories(self, response: str):
        """
        Update the Genie model's short-term memory and perform a transition based on the response.

        Parameters:
        response (str): The response from the Genie model.

        Returns:
        bool: True if a transition was performed, False otherwise.
        """
        try:
            self.automata.droid.action = self.extract_text(response, "Action:", "**Next state:**").strip()
            next_state = self.extract_text(response, "Next State:", "**Confirmation:**").strip()
            return self.automata.droid.perform_transition(self.automata.droid.states[next_state])
        except ValueError as e:
            print(f"An error occurred: {e}")
            return False
