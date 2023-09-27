from abc import ABC
import openai
import os
from dotenv import load_dotenv, find_dotenv


class AbstractLlm(ABC):

    def __init__(self, metadata: dict):

        _ = load_dotenv(find_dotenv())
        openai.api_key = os.getenv('OPENAI_API_KEY')

        self.role = metadata['role']
        self.model = metadata['model']
        self.answer = None
        self.last_prompt = None
        self.current_prompt = None

    def get_api_response(self, content: str, temperature=0, max_tokens=None, stream=False):

        response = openai.ChatCompletion.create(
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
        self.answer = response['choices'][0]['message']['content']

    def regenerate(self):
        return self.get_api_response(self.last_prompt)


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

