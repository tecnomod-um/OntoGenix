from OntoGenix_v_1_2.LLM.LlmBase import AbstractLlm


class LlmOntology(AbstractLlm):

    def __init__(self, metadata: dict):
        super().__init__(metadata)
        # initialize prompts
        self.instructions_prompt = self.load_string_from_file(metadata['instructions'])
        self.autocompletion_prompt = self.load_string_from_file(metadata['autocompletion'])
        self.ontology_analysis_prompt = self.load_string_from_file(metadata['ontology_analysis'])
        self.ontology_synthesis_prompt = self.load_string_from_file(metadata['ontology_synthesis'])
        self.examples = self.load_examples(metadata['examples'])
        # path setting to write outputs
        self.dataset_path = metadata['dataset']
        # initialize memories
        self.last_prompt = None
        self.owl_codeblock = None
        self.analysis = []

    def interact(self, json_data: str, instructions: str):
        try:

            self.last_prompt = self.instructions_prompt.format(
                json_data=json_data,
                instructions=instructions
            )

            response = self.get_api_response(self.last_prompt)

            response, self.owl_codeblock = self.autocompletion(previous_input=self.last_prompt, response=response)

            file = self.dataset_path + '_debugging_GPT_RESPONSE.txt'
            with open(file, 'w') as f:
                f.write(response)

        except ValueError as e:
            print(f"An error occurred while extracting text: {e}")

    def analyze(self, json_data: str, instructions: str, previous_ontology: str, human_ontology: str):
        try:

            prompt = self.ontology_analysis_prompt.format(
                json_data=json_data,
                instructions=instructions,
                previous_ontology=previous_ontology,
                human_ontology=human_ontology
            )

            response = self.get_api_response(prompt)

            response, _ = self.autocompletion(previous_input=prompt, response=response)
            print('############ analysis output ########################\n', response)

            file = self.dataset_path + '_debugging_GPT_ANALYSIS.txt'  # HARDCODED !!!
            with open(file, 'a') as f:
                f.write(response)

            insights = self.extract_text(response, "RATIONALE:", "RDF/XML ONTOLOGY:")
            owl_codeblock = self.extract_text(response, "START", "FINISH")
            self.analysis.append(owl_codeblock)
            return insights

        except ValueError as e:
            print(f"An error occurred while extracting text: {e}")
            return None

    def synthesize(self):
        try:
            analysis_str = '\n'.join([
                f'\nHere you have the {i + 1} analysis output you generated previously, that is the rationale followed by the improved ontology:\n{self.analysis[i]}'
                for i in range(len(self.analysis))])

            formatted_prompt = self.ontology_synthesis_prompt.format(analysis_outputs=analysis_str)
            print('################### formatted prompt ####################3\n', formatted_prompt)
            response = self.get_api_response(formatted_prompt)

            file = self.dataset_path + '_debugging_GPT_SYNTHESIS.txt'
            with open(file, 'a') as f:
                f.write(response)

            self.owl_codeblock = self.extract_text(response, "START", "FINISH")

            file = self.dataset_path + '_ontology_LLM.owl'
            with open(file, 'w') as f:
                f.write(self.owl_codeblock)

        except ValueError as e:
            print(f"An error occurred while extracting text: {e}")

    def autocompletion(self, previous_input: str, response: str, max_iter=5):
        owl_codeblock = None
        done = False
        cont = 0
        while not done and cont < max_iter:
            print('Autocompletion ITERATION: ', cont)
            try:
                owl_codeblock = self.extract_text(response, "START", "FINISH")
                print('################# OWL CODE ####################\n', owl_codeblock)
                done = True
            except:
                try:
                    prompt = self.autocompletion_prompt.format(
                        prev_input=previous_input,
                        response=response
                    )
                    response = self.get_api_response(prompt)
                    print('######## OUTPUT ############\n', response)
                except:
                    print('ITERATION: ', cont)
                finally:
                    cont += 1

        return response, owl_codeblock





