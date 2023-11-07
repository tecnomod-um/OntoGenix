import difflib
import re


def compare_texts(text1, text2):
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