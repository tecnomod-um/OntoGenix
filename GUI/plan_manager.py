from collections import OrderedDict
from typing import Dict, Any
import re
import yaml


class PlanManager:

    def __init__(self,
                 plan_dict: OrderedDict = None,
                 instructions: dict = None,
                 instruction: str = None,
                 short_term_memory: str = None,
                 long_term_memory: str = None) -> None:
        """
        Initialize the PlanManager with the provided plan dictionary.

        :param plan_dict: An ordered dictionary representing the plan.
        :param instructions: A dictionary representing the instructions.
        """
        self.plan_dict = plan_dict
        self.instructions = instructions
        self.instruction = instruction
        self.short_term_memory = short_term_memory
        self.long_term_memory = long_term_memory

    @property
    def short_term_memory(self) -> str:
        """Getter for instructions."""
        return self._short_term_memory

    @short_term_memory.setter
    def short_term_memory(self, value: dict) -> None:
        """Setter for short_term_memory."""
        if isinstance(value, str):
            self._short_term_memory = value
        else:
            raise ValueError("instructions must be a string.")

    @property
    def long_term_memory(self) -> str:
        """Getter for long_term_memory."""
        return self._long_term_memory

    @long_term_memory.setter
    def long_term_memory(self, value: str) -> None:
        """Setter for long_term_memory."""
        if isinstance(value, dict):
            self._long_term_memory = value
        else:
            raise ValueError("instructions must be a string.")

    @property
    def instruction(self) -> dict:
        """Getter for instruction."""
        return self._instruction

    @instruction.setter
    def instruction(self, value: dict) -> None:
        """Setter for instruction."""
        if isinstance(value, dict):
            self._instruction = value
        else:
            raise ValueError("instruction must be a dict.")
    @property
    def instructions(self) -> dict:
        """Getter for instructions."""
        return self._instructions

    @instructions.setter
    def instructions(self, value: dict) -> None:
        """Setter for instructions."""
        if isinstance(value, dict):
            self._instructions = value
        else:
            raise ValueError("instructions must be a dict.")

    @property
    def plan_dict(self) -> OrderedDict:
        """Getter for plan_dict."""
        return self._plan_dict

    @plan_dict.setter
    def plan_dict(self, value: OrderedDict) -> None:
        """Setter for plan_dict."""
        if isinstance(value, OrderedDict):
            self._plan_dict = value
        else:
            raise ValueError("plan_dict must be an OrderedDict.")

    @staticmethod
    def preprocess_yaml(yaml_string: str, parse: str) -> str:
        pattern = re.compile(r'^\s*' + parse, re.MULTILINE)
        return pattern.sub(parse, yaml_string)

    def text2dict(self, text: str, parse: str = "task_") -> 'PlanManager':
        try:
            preprocessed_text = self.preprocess_yaml(text, parse)
            self.plan_dict = yaml.safe_load(preprocessed_text)
        except ValueError as e:
            print(f"An error occurred while preprocessing the text: {e}")

    def plan_dict2text(self) -> str:
        return yaml.dump(self.plan_dict)

    def insert_in_position(self, new_dict: Dict[str, Any]) -> None:
        """
        Insert a new item into the plan dictionary at a specified position.

        :param new_dict: A dictionary with one item to insert.
        :raises ValueError: If the key in new_dict doesn't follow the expected format.
        """
        new_odict = OrderedDict()
        new_key = list(new_dict.keys())[0]
        if not new_key.startswith('task_'):
            raise ValueError("Invalid key format. Expected 'task_N'.")
        position = int(new_key.split('_')[1])
        i = 1
        for key, value in self.plan_dict.items():
            if i == position:
                new_odict[f'task_{i}'] = new_dict[new_key]
                i += 1
            new_odict[f'task_{i}'] = value
            i += 1
        if position >= i:
            new_odict[new_key] = new_dict[new_key]
        self.plan_dict = new_odict
        self.update_gui()

    def move_in_dict(self, index: int, direction: int) -> None:
        """
        Move an item up or down in the plan dictionary.

        :param index: The index of the item to move.
        :param direction: The direction to move the item (-1 for up, 1 for down).
        """
        items = list(self.plan_dict.items())
        if 0 <= index + direction < len(items):
            items[index + direction], items[index] = items[index], items[index + direction]
        self.plan_dict = OrderedDict(items)
        self.update_gui()

    def delete(self, item_data: str) -> None:
        """
        Delete an item from the plan dictionary.

        :param item_data: The key of the item to delete.
        :raises KeyError: If the item is not in the dictionary.
        """
        if item_data in self.plan_dict:
            del self.plan_dict[item_data]
            self.update_gui()
        else:
            raise KeyError(f"No such key: {item_data}")

    def update_gui(self) -> None:
        """
        Update the GUI or other dependent parts of the program.

        This method should be overridden in a subclass or replaced with actual code to update the GUI.
        """
        pass
