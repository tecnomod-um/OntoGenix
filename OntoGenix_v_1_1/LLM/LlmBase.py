from abc import ABC, abstractmethod
import openai
import os
from dotenv import load_dotenv, find_dotenv


class AbstractLlm(ABC):

    def __init__(self, metadata: dict):

        _ = load_dotenv(find_dotenv())
        openai.api_key = os.getenv('OPENAI_API_KEY')

        self.role = metadata['role']

    def get_api_response(self, content: str, temperature=0.5, max_tokens=None, stream=False):

        response = openai.ChatCompletion.create(
            model='gpt-3.5-turbo-16k',
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

        return response['choices'][0]['message']['content']

    @staticmethod
    def load_string_from_file(file_path):
        with open(file_path, 'r') as file:
            return file.read()

    def load_examples(self, folder_path):
        # Get a list of all files in the folder
        files = os.listdir(folder_path)

        examples = []
        # Iterate over the files and perform operations
        for file_name in files:
            # Construct the absolute file path
            file_path = os.path.join(folder_path, file_name)
            # get the content from this file
            content = self.load_string_from_file(file_path)
            examples.append(content)

        return examples

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

