from OntoGenix_v_1_1.LLM.LlmBase import AbstractLlm

import os


class LlmOntology(AbstractLlm):

    def __init__(self, metadata: dict):
        super().__init__(metadata)
        self.autocompletion_prompt = self.load_string_from_file(metadata['autocompletion'])
        self.instructions = self.load_string_from_file(metadata['instructions'])
        self.last_prompt = None

    def interact(self, json_data: str, instructions: str):
        try:

            self.last_prompt = self.instructions.format(
                json_data=json_data,
                instructions=instructions
            )

            response = self.get_api_response(self.last_prompt)

            file = './datasets/debugging_GPT_RESPONSE.txt'
            with open(file, 'w') as f:
                f.write(response)

            owl_code_str = self.autocompletion(owl_response=response, json_data=json_data, instructions=instructions)
            print('######## OUTPUT ############\n', owl_code_str)
            return owl_code_str

        except ValueError as e:
            print(f"An error occurred while extracting text: {e}")
            return None

    def autocompletion(self, owl_response: str, json_data: str, instructions: str, max_iter=5) -> str:
        owl_code_str = None
        done = False
        cont = 0
        while not done and cont < max_iter:
            try:
                owl_code_str = self.extract_text(owl_response, "RDF/XML ONTOLOGY:\n", "Finish Statement: FINISH")
                print('################# OWL CODE ####################\n', owl_code_str)
                done = True
            except:
                try:
                    owl_response = self.autocompletion_prompt.format(
                        prev_input=owl_response,
                        json_data=json_data,
                        instructions=instructions
                    )
                    print('######## OUTPUT ############\n', owl_response)
                except:
                    print('ITERATION: ', cont)
                finally:
                    cont += 1

        return owl_code_str


