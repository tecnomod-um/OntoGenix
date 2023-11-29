from abc import ABC
from openai import OpenAI
import os
from dotenv import dotenv_values


class AbstractLlm(ABC):

    def __init__(self, metadata: dict):

        config = dotenv_values(metadata['api_key_path'])

        self.client = OpenAI(api_key = config['OPENAI_API_KEY'])

        self.role = metadata['role']
        self.model = metadata['model']
        self.answer = ""
        self.last_prompt = None
        self.current_prompt = None
        self.stream_control = True

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

