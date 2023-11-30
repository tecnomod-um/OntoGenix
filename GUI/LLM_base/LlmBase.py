from abc import ABC
from openai import OpenAI
import os
from dotenv import dotenv_values
import json

class AbstractLlm(ABC):

    def __init__(self, metadata: dict):
        # set api key path
        config = dotenv_values(metadata['api_key_path'])
        # create a client with its api key
        self.client = OpenAI(api_key = config['OPENAI_API_KEY'])
        # set client properties
        self.role = metadata['role']
        self.model = metadata['model']
        self.answer = ""
        self.tool_calls = None
        self.available_functions = None
        # set utilities
        self.last_prompt = None
        self.current_prompt = None

    def get_api_response(self, content: str, temperature=0, max_tokens=None, stream=False):
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
                stream=stream
        )

        self.answer = completion.choices[0].message.content

    def function_calling(self, content: str, tools=None):
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
            temperature=0
        )

        self.tool_calls = response.choices[0].message.tool_calls

    async def get_async_api_response(self, content: str, temperature=0, max_tokens=None, stream=True):
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
                stream=stream
        )

        for chunk in completion:
            data = chunk.choices[0].delta.content
            if data is not None:
                self.answer += data
                yield data

    async def regenerate(self):
        try:
            # Reuse the last prompt
            async for chunk in self.get_async_api_response(self.current_prompt):
                yield chunk

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

        except ValueError as e:
            print(f"An error occurred while extracting text: {e}")

    async def _process_function_response(self):
        """Processes the response message from model and calls the intended function.
        :param function_callback: callback function which be called with the corresponding arguments.
        :return: the function to be returned
        """
        for tool_call in self.tool_calls:
            function_name = tool_call.function.name
            print("function_name: ", function_name)

            # Check if the function exists in metadata
            if function_name in self.available_functions:
                function_to_call = self.available_functions[function_name]

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
    def load_string_from_file(file_path):
        with open(file_path, 'r') as file:
            return file.read()

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
        if start_index == -1:
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

