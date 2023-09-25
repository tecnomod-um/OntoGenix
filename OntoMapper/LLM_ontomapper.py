from LLM_base.LlmBase import AbstractLlm


class LlmOntoMapper(AbstractLlm):

    def __init__(self, metadata: dict):
        super().__init__(metadata)
        # initialize prompts
        self.instructions = self.load_string_from_file(metadata['instructions'])
        # path setting to write outputs
        self.dataset_path = metadata['dataset']
        # initialize memories
        self.rml_codeblock = None

    def interact(self, rationale: str):
        try:
            # format the prompt
            self.current_prompt = self.instructions.format(rationale=rationale)
            # generate the answer
            self.get_api_response(self.current_prompt)
            # extract the rml codeblock
            self.rml_codeblock = self.extract_text(self.answer, "'''turtle", "'''")
            # write the answer to a txt file.
            self.save_response(self.rml_codeblock, self.dataset_path + '_rml_mapping_LLM.csv.ttl', mode='w')

        except ValueError as e:
            print(f"An error occurred during interaction: {e}")
        finally:
            self.last_prompt = self.current_prompt

    def regenerate(self):
        try:
            # Reuse the last prompt
            self.get_api_response(self.current_prompt)
            # extract the codeblock
            self.rml_codeblock = self.extract_text(self.answer, start_marker="```xml", end_marker="```")
            # write the response in a txt file
            self.save_response(self.rml_codeblock, self.dataset_path + '_rml_mapping_LLM.csv.ttl', mode='w')

        except ValueError as e:
            print(f"An error occurred while extracting text: {e}")
        finally:
            self.last_prompt = self.current_prompt
