"""
    Base class for the support of the different OntoGenix modules.
    TODO: Document this
"""

import base64
import json
from abc import ABC

from dotenv import dotenv_values
from openai import AzureOpenAI, OpenAI
from typing import Union

class AbstractLlm(ABC):
    error_message = None

    def __init__(self, metadata: dict):
        # set api key path
        config = dotenv_values(metadata['api_key_path'])
        # create a client with its api key
        if metadata['client'] == "azure" and 'AZURE_OPENAI_ENDPOINT' in config.keys():
            # We read the model and the api version either from the .env file or from the metadata dictionary
            model = config['AZURE_DEPLOYMENT'] if config['AZURE_DEPLOYMENT'] is not None else metadata['model']
            api_version = config['OPENAI_API_VERSION'] if config['OPENAI_API_VERSION'] is not None else metadata['api_model']
            # We create an OpenAI Azure client (BASF)
            self.client = AzureOpenAI(
                api_key=config['OPENAI_API_KEY'],
                azure_endpoint=config['AZURE_OPENAI_ENDPOINT'],
                api_version=api_version,
                azure_deployment=model
            )
        elif metadata['client'] == "azure" and 'AZURE_OPENAI_ENDPOINT' not in config.keys():
            print("Detected Azure Client option but no AZURE_OPENAI_ENDPOINT value was specified in the .env file.")
        elif metadata['client'] != "azure" and 'AZURE_OPENAI_ENDPOINT' in config.keys():
            print("""
                  Detected AZURE_OPENAI_ENDPOINT value specified in the .env file.\n
                  If you want to change the client, please use the "-c azure" option.
                  """)
        else:
            self.client = OpenAI(api_key = config['OPENAI_API_KEY'])
        # TODO: error checking and logging here with API keys

        #self.client = OpenAI(api_key = config['OPENAI_API_KEY'])
        # set client properties
        self.role = metadata['role']
        self.model = metadata['model']
        self.answer = ""
        #self.error_message = None
        self.tool_calls = None
        self.available_functions = None
        # set utilities
        self.last_prompt = None
        self.current_prompt = None
        try:
            # NOTE: https://cookbook.openai.com/examples/reproducible_outputs_with_the_seed_parameter
            # NOTE: https://community.openai.com/t/is-the-seed-parameter-being-deprecated/578586/5
            self.seed = int(metadata['seed'])
        except:
            self.seed = None

    def get_api_response(self, content: str, temperature:int=0, max_tokens:Union[int|None]=None,
                         #stream:Union[bool|None]=False, 
                         seed:Union[int|None]=None):
        completion = self.client.chat.completions.create(
                model=self.model,
                messages=[{
                    'role': 'system',
                    'content': self.role
                }, {
                    'role': 'user',
                    'content': content,
                }],
                temperature=temperature,
                max_tokens=max_tokens,
                stream=False,
                seed=seed or self.seed
        )

        try:
            self.answer = completion.choices[0].message.content
            return self.answer
        except:
            #print(">>> empty chunk response")
            return ""


    async def get_async_api_response(self, content: str,temperature:int=0, max_tokens:Union[int|None]=None,
                         #stream:Union[bool|None]=True, 
                         seed:Union[int|None]=None):
        self.answer = ""
        completion = self.client.chat.completions.create(
                model=self.model,
                messages=[{
                    'role': 'system',
                    'content': self.role
                }, {
                    'role': 'user',
                    'content': content,
                }],
                temperature=temperature,
                max_tokens=max_tokens,
                stream=True,
                seed=seed or self.seed
        )

        for chunk in completion:
            try:
                data = chunk.choices[0].delta.content
                if data is not None:
                    self.answer += data
                    yield data
            except:
                #print(">>> empty chunk response")
                yield ""

    async def image_interpretation(self, content: str, image_file: str, seed:Union[int|None]=None):
        base64_image, image_extension = self.image2base64(image_file)

        # Create the API request
        completion = self.client.chat.completions.create(
            model="gpt-4-vision-preview",
            messages=[{
                    'role': 'system',
                    'content': self.role
                },{
                    "role": "user",
                    "content": [
                        {"type": "text", "text": content},
                        {
                            "type": "image_url",
                            "image_url": f"data:image/{image_extension};base64,{base64_image}"
                        },
                    ],
                }
            ],
            temperature=0,
            max_tokens=1024,
            stream=True,
            seed=seed or self.seed
        )

        for chunk in completion:
            data = chunk.choices[0].delta.content
            if data is not None:
                self.answer += data
                yield data

    def function_calling(self, content: str, tools=Union[list|None], seed:Union[int|None]=None):
        # TODO: In Azure, for some reason, the "ontology_entity_enrichment" tool_call is None when trying to enrich the ontology
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[{
                'role': 'system',
                'content': self.role
            }, {
                'role': 'user',
                'content': content,
            }],
            tools=tools,
            temperature=0,
            seed=seed or self.seed
        )

        self.tool_calls = response.choices[0].message.tool_calls

    async def regenerate(self):
        try:
            # Reuse the last prompt
            async for chunk in self.get_async_api_response(self.current_prompt):
                yield chunk
        except GeneratorExit as ge:
            print(f"Process stopped/cancelled by user: {ge}")
            return
        except ValueError as e:
            print(f"An error occurred while extracting text: {e}")
        finally:
            self.last_prompt = self.current_prompt

    async def continue_writing(self):
        try:
            continue_prompt = '''You did not finish your writing during your last answer.

                                        This is your last answer:
                                        {answer}

                                        Complete the previous answer and continue from where you stopped.'''
            continue_prompt.format(answer=self.answer)
            # Reuse the last prompt
            async for chunk in self.get_async_api_response(continue_prompt):
                yield chunk
        except GeneratorExit as ge:
            print(f"Process stopped/cancelled by user: {ge}")
            return
        except ValueError as e:
            print(f"An error occurred while extracting text: {e}")

    async def _process_function_response(self):
        """Processes the response message from model and calls the intended function.
        :param function_callback: callback function which be called with the corresponding arguments.
        :return: the function to be returned
        """
        if not self.tool_calls:
            raise ValueError("No tool_call available for the current action.")
        elif not self.available_functions:
            raise ValueError("No available_function available for the current tool_call.")
        
        for tool_call in self.tool_calls:
            function_name = tool_call.function.name
            print("function_name: ", function_name)

            # Check if the function exists in metadata
            if function_name in self.available_functions:
                function_to_call = self.available_functions[function_name]
                print("function_to_call: ", function_to_call)
                try:
                    # Assuming arguments are in JSON format
                    function_args = json.loads(tool_call.function.arguments)
                    print("function arguments: ", function_args)
                    # Calling the function with unpacked arguments
                    await function_to_call(**function_args)
                except json.JSONDecodeError as e:
                    print(f"Error decoding JSON: {e}")
                except Exception as e:
                    print(f"Error during function call: {e}")
            else:
                print(f"Function {function_name} not found in metadata.")

    @staticmethod
    def image2base64(image_file):
        image_extension = image_file.split('.')[-1]
        # Convert image to base64
        with open(image_file, "rb") as image:
            base64_image = base64.b64encode(image.read()).decode('utf-8')

        return base64_image, image_extension

    @staticmethod
    def load_string_from_file(file_path, encoding:str="utf-8"):
        try:
            with open(file_path, 'r', encoding=encoding) as file:
                return file.read()
        except Exception as e:
            print(e)
        return None
    

    @staticmethod
    def extract_text(text: str, start_marker: str, end_marker: str) -> str:
        """
        Extracts a substring of text between two markers and returns it.

        Args:
            text (str): The text to be searched.
            start_marker (str): The start marker of the substring.
            end_marker (str): The end marker of the substring.

        Returns:
            The substring of text between start_marker and end_marker.

        Raises:
            ValueError: If start_marker or end_marker is not found in text.
        """
        start_index = text.find(start_marker) + len(start_marker)
        end_index = text.find(end_marker, start_index)
        if start_index == (len(start_marker) - 1):
            raise ValueError("Start marker not found in text.")
        elif end_index == -1:
            raise ValueError("End marker not found in text.")
        return text[start_index:end_index].strip()

    @staticmethod
    def save_response(response: str, file: str, mode: str = 'w'):
        try:
            with open(file, mode) as f:
                f.write(response + '\n')
        except ValueError as e:
            print(f"An error occurred: {e}")

