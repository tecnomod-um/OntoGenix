from abc import ABC
from openai import OpenAI
import os
from dotenv import dotenv_values
import json

class AbstractLlm(ABC):
    """
    Abstract base class for a Language Learning Model (LLM).
    This class provides methods for interacting with the LLM using OpenAI's GPT-3.

    Attributes:
        client (OpenAI): An instance of the OpenAI client.
        role (str): The role of the user in the conversation.
        model (str): The name of the GPT-3 model to use.
        answer (str): The response received from the LLM.
        tool_calls (dict): Information about tool calls made during conversation.
        available_functions (dict): A dictionary of available functions for processing tool calls.
        last_prompt (str): The last prompt sent to the LLM.
        current_prompt (str): The current prompt being used for interaction.
    """

    def __init__(self, metadata: dict):
        """
        Initialize the AbstractLlm object.

        Args:
            metadata (dict): A dictionary containing metadata for the LLM.
        """
        # Load API key from environment variables
        config = dotenv_values(metadata['api_key_path'])
        # Create a client with the provided API key
        self.client = OpenAI(api_key=config['OPENAI_API_KEY'])
        # Set client properties
        self.role = metadata['role']
        self.model = metadata['model']
        self.answer = ""
        self.tool_calls = None
        self.available_functions = None
        # Set utilities
        self.last_prompt = None
        self.current_prompt = None

    def get_api_response(self, content: str, temperature=0, max_tokens=None, stream=False):
        """
        Get a response from the LLM using the provided content.

        Args:
            content (str): The content of the message to send to the LLM.
            temperature (float): The temperature for response generation.
            max_tokens (int): The maximum number of tokens in the response.
            stream (bool): Whether to stream the response.

        Returns:
            None
        """
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
        """
        Make a function call to the LLM using the provided content and tools.

        Args:
            content (str): The content of the message containing the function call.
            tools (dict): Tools to be used in the function call.

        Returns:
            None
        """
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
        """
        Get asynchronous API responses from the LLM.

        Args:
            content (str): The content of the message to send to the LLM.
            temperature (float): The temperature for response generation.
            max_tokens (int): The maximum number of tokens in the response.
            stream (bool): Whether to stream the response.

        Yields:
            str: The chunks of response data as they are received.
        """
        self.answer = ""  # Initialize the answer as an empty string
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
                self.answer += data  # Append the data to the answer
                yield data  # Yield the data chunk to the caller

    async def regenerate(self):
        """
        Reuse the last prompt and yield chunks of the regenerated response.

        This method sends the last prompt to the LLM to regenerate a response and yields
        chunks of the response data as they are received.

        Yields:
            str: The chunks of the regenerated response data.
        """
        try:
            # Reuse the last prompt by sending it to the LLM
            async for chunk in self.get_async_api_response(self.current_prompt):
                yield chunk  # Yield each chunk of the regenerated response

        except ValueError as e:
            print(f"An error occurred while extracting text: {e}")
        finally:
            self.last_prompt = self.current_prompt  # Update the last prompt to the current prompt

    async def continue_writing(self):
        """
        Continue writing based on the last answer and yield chunks of the response.

        This method generates a prompt that instructs the LLM to continue writing based on
        the last answer. It then sends this prompt to the LLM and yields chunks of the
        response data as they are received.

        Yields:
            str: The chunks of the continued writing response data.
        """
        try:
            # Construct the continue prompt to instruct the LLM
            continue_prompt = f'''You did not finish your writing during your last answer.

                                This is your last answer:
                                {self.answer}

                                Complete the previous answer and continue from where you stopped.'''

            # Reuse the last prompt by sending the continue prompt to the LLM
            async for chunk in self.get_async_api_response(continue_prompt):
                yield chunk  # Yield each chunk of the continued writing response

        except ValueError as e:
            print(f"An error occurred while extracting text: {e}")

    async def _process_function_response(self):
        """
        Processes the response message from the model and calls the intended function.

        This method iterates through the tool calls received from the LLM model, extracts
        the function name and its arguments, and attempts to call the corresponding function
        defined in the metadata.

        Raises:
            json.JSONDecodeError: If there is an error decoding the function arguments as JSON.
            Exception: If there is an error during the function call.

        Note:
            This method assumes that function arguments are provided in JSON format.

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
    def load_string_from_file(file_path: str) -> str:
        """
        Load a string from a text file.

        This static method reads the contents of a text file located at the specified `file_path`
        and returns its content as a string.

        Parameters:
            file_path (str): The path to the text file to be loaded.

        Returns:
            str: The contents of the text file as a string.

        Example:
            content = MyClass.load_string_from_file('example.txt')
        """
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
        """
        Save a response to a file.

        Args:
            response (str): The response text to be saved.
            file (str): The path to the file where the response will be saved.
            mode (str, optional): The mode in which the file will be opened ('w' for write, 'a' for append, etc.).
                Defaults to 'w'.

        Raises:
            ValueError: If an error occurs while saving the response.
        """
        try:
            with open(file, mode) as f:
                f.write(response + '\n')
        except ValueError as e:
            print(f"An error occurred: {e}")
