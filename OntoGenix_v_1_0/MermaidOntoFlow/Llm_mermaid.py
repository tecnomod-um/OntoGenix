from OntoGenix_v_1_0.LLM.LlmBase import AbstractLlm

class LlmMermaid(AbstractLlm):

    def __init__(self, metadata: dict):
        super().__init__(metadata)

    def interact(self, message: str):
        try:
            prompt = self.instructions.format(input=message) + self.examples
            response = self.get_api_response(prompt)
            return response

        except ValueError as e:
            print(f"An error occurred while extracting text: {e}")
            return None