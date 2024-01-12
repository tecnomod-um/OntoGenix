from abc import ABC
from typing import Optional

from GUI.LLM_base.LlmBase import AbstractLlm

class LlmPromptCrafter(AbstractLlm, ABC):
    """
    A class representing a language learning model's ontology for prompt crafting.

    This class extends the AbstractLlm class and specializes in creating and managing prompts for
    interaction with a language learning model. It's responsible for formatting and storing crafted prompts
    based on input data and descriptions.

    Attributes:
        data_description_prompt (str): The template for crafting data description prompts.
        crafted_prompt (Optional[str]): The last crafted prompt, stored after interactions.
    """

    def __init__(self, metadata: dict):
        """
        Initialize the LlmPromptCrafter object.

        Parameters:
            metadata (dict): Metadata for the LLM, including file paths and configurations.
        """
        super().__init__(metadata)
        self.data_description_prompt = self.load_string_from_file(metadata['prompt_crafting'])
        self.crafted_prompt = None  # Container for the crafted prompt

    async def interaction(self, prompt: Optional[str] = None, json_data: Optional[str] = None):
        """
        Perform interaction with the LLM, crafting and returning responses based on the provided prompt and data.

        Parameters:
            prompt (Optional[str]): The initial input prompt for crafting.
            json_data (Optional[str]): The input data in JSON format to be used in crafting the prompt.

        Yields:
            str: Chunks of the response from the LLM.

        Exceptions:
            ValueError: Catches and prints any ValueError that occurs during the interaction.
        """
        try:
            self.current_prompt = self.data_description_prompt.format(prompt=prompt, json_data=json_data)

            async for chunk in self.get_async_api_response(self.current_prompt):
                yield chunk

            self.crafted_prompt = self.extract_text(
                self.answer,
                start_marker="**Prompt:**",
                end_marker="**Critique:**"
            )

        except ValueError as e:
            print(f"An error occurred: {e}")
        finally:
            self.last_prompt = self.current_prompt
