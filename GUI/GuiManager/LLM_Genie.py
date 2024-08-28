from abc import ABC
from typing import Optional

from GUI.LLM_base.LlmBase import AbstractLlm
from GUI.GuiManager.automata_manager import Automata_Manager
from GUI.OntoGenixExceptions import AutomataException
from GUI.tools.text_tools import extract_text

class Genie(AbstractLlm, ABC):
    """
    This class represents a language learning model (LLM_base) ontology. It extends the AbstractLlm class and provides
    methods for intUnionTypeionTypeacting with the model.

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
            # TODO: it would be nice to wait here for the user confirmation before continuing

            # Get the response from the LLM_base
            async for chunk in self.get_async_api_response(content=self.current_prompt, seed=self.seed):
                yield chunk

            # update the short term memory
            if self.update_memories(self.answer):
                # let's perform the corresponding action.
                await self.select_process()
        except GeneratorExit as ge:
            print(f"Process stopped/cancelled by user: {ge}")
            return
        except AutomataException.InvalidTransitionException as e:
            #print(f"An error occurred: {e.message}")
            yield "\n"+e.message
        #except ValueError as e:
        #    print(f"An error occurred: {e}")
        except Exception as e:
            error_message = f"An error occurred: {e}"
            print(error_message)
            yield error_message
        finally:
            self.last_prompt = self.current_prompt

    async def select_process(self):
        try:
            if self.automata.droid.action in self.available_functions.keys():
                self.function_calling(
                    content='Action: ' + self.automata.droid.action + ' prompt: ' + self.query,
                    tools=self.tools,
                    seed=self.seed
                )
                await self._process_function_response()

        except Exception as e:
            print("Exception: {e}".format(e=e))


    def update_memories(self, response: str) -> bool:
        try:
            # TODO: change the extract_text functionality
            self.automata.droid.action = extract_text(response, "Action:", "**Next state:**").strip()
            next_state = extract_text(response, "Next State:", "**Confirmation:**").strip()
            return self.automata.droid.perform_transition(self.automata.droid.states[next_state])
        except AutomataException.InvalidTransitionException as e:
            print(f"An error occurred: {e.message}".format(e=e))
            raise AutomataException.InvalidTransitionException(e.message)
        except ValueError as e:
            print(f"An error occurred: {e}")
        return False
