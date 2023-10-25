from LLM_base.LlmBase import AbstractLlm


class LlmOntoMapper(AbstractLlm):

    def __init__(self, metadata: dict):
        super().__init__(metadata)
        # initialize prompts
        self.instructions = self.load_string_from_file(metadata['instructions'])
        self.error_instructions = self.load_string_from_file(metadata['error_instructions'])
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

    async def interact(self, rationale: str=None, error: str=None):
        try:
            csv_data = self._dataset_path.split('/')[-1]
            if rationale and not error:
                # format the prompt
                self.current_prompt = self.instructions.format(rationale=rationale, csv_data=csv_data)
            elif rationale and error:
                self.current_prompt = self.error_instructions.format(rationale=rationale, error=error, csv_data=csv_data)
            # Get the response from the LLM_base
            async for chunk in self.get_async_api_response(self.current_prompt):
                yield chunk

        except ValueError as e:
            print(f"An error occurred during interaction: {e}")
        finally:
            self.last_prompt = self.current_prompt

    def get_rml_codeblock(self):
        return self.extract_text(self.answer, start_marker="```turtle", end_marker="```")

