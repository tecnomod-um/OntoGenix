from abc import ABC, abstractmethod
import openai
import os
from dotenv import load_dotenv, find_dotenv


class AbstractLlm(ABC):

    def __init__(self, metadata: dict):

        _ = load_dotenv(find_dotenv())
        openai.api_key = os.getenv('OPENAI_API_KEY')

        self.instructions = self.load_string_from_file(metadata['instructions'])
        self.examples = self.load_string_from_file(metadata['examples'])
        self.role = metadata['role']

    @abstractmethod
    def interact(self, message: str):
        pass

    def get_api_response(self, content: str, temperature=0.5, max_tokens=None):

        response = openai.ChatCompletion.create(
            model='gpt-3.5-turbo',
            messages=[{
                'role': 'system',
                'content': self.role
            }, {
                'role': 'user',
                'content': content,
            }],
            temperature=temperature,
            max_tokens=max_tokens
        )

        return response['choices'][0]['message']['content']

    @staticmethod
    def load_string_from_file(file_path):
        with open(file_path, 'r') as file:
            return file.read()
