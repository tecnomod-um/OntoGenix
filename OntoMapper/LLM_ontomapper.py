from LLM_base.LlmBase import AbstractLlm


class LlmOntoMapper(AbstractLlm):

    def __init__(self, metadata: dict):
        super().__init__(metadata)
        # initialize prompts
        self.instructions = self.load_string_from_file(metadata['instructions'])
        # path setting to write outputs
        self._dataset_path = metadata['dataset']
        # initialize memories
        self.rml_codeblock = None

    @property
    def dataset_path(self):
        return self._dataset_path

    # Setter for name
    @dataset_path.setter
    def dataset_path(self, path):
        if not isinstance(path, str):
            raise ValueError("Name must be a string!")
        self._dataset_path = path

    async def interact(self, rationale: str):
        try:
            # format the prompt
            self.current_prompt = self.instructions.format(rationale=rationale)
            # Get the response from the LLM_base
            async for chunk in self.get_async_api_response(self.current_prompt):
                yield chunk

        except ValueError as e:
            print(f"An error occurred during interaction: {e}")
        finally:
            self.last_prompt = self.current_prompt

    async def regenerate(self):
        try:
            # Reuse the last prompt
            async for chunk in self.get_async_api_response(self.current_prompt):
                yield chunk

        except ValueError as e:
            print(f"An error occurred while extracting text: {e}")
        finally:
            self.last_prompt = self.current_prompt

    def get_rml_codeblock(self):
        return self.extract_text(self.answer, start_marker="```turtle", end_marker="```")

