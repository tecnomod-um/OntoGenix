"""
    Functionality related to text functionality.
    TODO: Improve functions naming
"""
import difflib
import re


def compare_texts(text1 : str, text2 : str):
    """
        Compares two strings (not generic).
        TODO: The name of the function should be representative.

        text1: The first text
        text2: The second text
    """
    text1 = text1.replace(' xmlns', '\nxmlns')
    text2 = text2.replace(' xmlns', '\nxmlns')
    # Split the texts into lines
    lines1 = [line.strip() for line in text1.splitlines()]
    lines2 = [line.strip() for line in text2.splitlines()]

    # Use difflib to compare the lines
    diff = difflib.ndiff(lines1, lines2)

    result = ""
    # Format and print the differences
    for line in diff:
        stripped_line = line[2:].strip()
        if line.startswith('- ') and stripped_line not in lines2:  # Lines in text1 but not in text2
            result += '[-] ' + stripped_line + '\n'
        elif line.startswith('+ ') and stripped_line not in lines1:  # Lines in text2 but not in text1
            result += '[+] ' + stripped_line + '\n'
        elif line.startswith(
                '  ') and stripped_line in lines1 and stripped_line in lines2:  # Lines in both text1 and text2
            result += '[*] ' + stripped_line + '\n'

    return result


def text2dict(text: str) -> dict:
    """
        Transforms a string into a dictionary (not generic).
        TODO: The name of the function should be representative.

        text: string with a specific formatting.

        It uses '\n' as delimiter and spects the 'task_*' prefix in the line.
        The prefix is used as key, and the value is the first value with ':' separator.
    """
    try:
        # split the text into tasks
        tasks = re.split('\n', text.strip())
        # initialize an empty dictionary
        task_dict = {}
        # loop over each task
        for task in tasks:
            if 'task_' in task:
                # split the task into number and description
                task_split = re.split(': ', task, maxsplit=1)
                # add to the dictionary
                task_dict[task_split[0].strip()] = task_split[1].strip()

        return task_dict

    except ValueError as e:
        print(f"An error occurred while preprocessing the text: {e}")
        return None

def rreplace(s : str, old : str, new : str = "", occurrence : int = 1):
    """
        Replaces the last "ocurrence" ocurrences of the given string
        substituing the "old" string and replacing it with the "new" one.
        By default, if no optional parameters are provided, it returns
        the string without the last ocurrence.

        s: string to be transformed
        old: old substring to be replaced
        new: new substring to replace the old one
        ocurrence: number of occurences of the old substring to substitute
    """
    #assert occurrence >= 0
    if occurrence < 0:
        occurrence = 0
    li = s.rsplit(old, occurrence)
    return new.join(li)

def lreplace(s : str, old : str, new : str = "", occurrence : int = 1):
    """
        Replaces the first "ocurrence" ocurrences of the given string
        substituing the "old" string and replacing it with the "new" one.
        By default, if no optional parameters are provided, it returns
        the string without the first ocurrence.

        s: string to be transformed
        old: old substring to be replaced
        new: new substring to replace the old one
        ocurrence: number of occurences of the old substring to substitute
    """
    #assert occurrence >= 0
    if occurrence < 0:
        occurrence = 0
    li = s.split(old, occurrence)
    return new.join(li)

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

def get_marker_codeblock(text: str, marker: str = "") -> str:
        """
        Extract a code block from the LLM's response.

        Returns:
            str: The extracted XML code block from the LLM's response.
        """
        if marker is None:
            marker = ""
        return extract_text(text, start_marker=f"```{marker}", end_marker="```")