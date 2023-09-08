from typing import Any, Dict

import os
from rdflib import Graph, URIRef

import difflib

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
        elif line.startswith('  ') and stripped_line in lines1 and stripped_line in lines2:  # Lines in both text1 and text2
            result += '[*] ' + stripped_line + '\n'
    return result



def split_rdf(input_file, output_folder, chunk_size=10):
    g = Graph()
    g.parse(input_file, format="xml")

    subjects = list(set(g.subjects()))
    chunks = [subjects[x:x+chunk_size] for x in range(0, len(subjects), chunk_size)]

    for i, chunk in enumerate(chunks, 1):
        chunk_g = Graph()
        for subject in chunk:
            for p, o in g.predicate_objects(URIRef(subject)):
                chunk_g.add((URIRef(subject), p, o))
        chunk_file = os.path.join(output_folder, f'chunk_{i}.rdf')
        chunk_g.serialize(destination=chunk_file, format='xml')

def plot_word_embeddings(result, labels, color='b'):
    plt.scatter(result[:, 0], result[:, 1], color=color)
    for i, node in enumerate(labels):
        plt.annotate(node, (result[i, 0], result[i, 1]))

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


def count_tokens(data: Dict[str, Any]) -> int:
    """
    Count the number of tokens in a nested dictionary.

    Args:
        data (Dict[str, Any]): The input nested dictionary.

    Returns:
        int: The total number of tokens in the nested dictionary.
    """
    try:
        num_tokens = 0
        for key, value in data.items():
            num_tokens += 1  # Count the key
            num_tokens += 1  # Count the value
            if isinstance(value, dict):
                num_tokens += count_tokens(value)
    except Exception as e:
        # Handle any exception that occurs during the token counting process
        print(f"An error occurred: {str(e)}")
        return -1

    return num_tokens


import re
import yaml



def preprocess_yaml(yaml_string: str, parse: str) -> str:
    # Regular expression to find lines starting with "task_"
    pattern = re.compile(r'^\s*'+parse, re.MULTILINE)
    # Dedent these lines
    return pattern.sub(parse, yaml_string)


def text2dict(text: str, parse: str="task_") -> dict:
    try:
        preprocessed_text = preprocess_yaml(text, parse)
        plan_dict = yaml.safe_load(preprocessed_text)
        return plan_dict

    except ValueError as e:
        print(f"An error occurred while preprocessing the text: {e}")
        return None


import json
import pandas as pd


def dataframe2prettyjson(dataframe: pd.DataFrame, file: str = None, save: bool = False) -> None:
    """
    Convert a Pandas DataFrame to pretty JSON and save it to a file.

    Args:
        dataframe (pd.DataFrame): The input DataFrame.
        file (str): The file path to save the pretty JSON.

    Returns:
        None
    """
    try:
        json_data = dataframe.to_json(orient='columns')

        parsed = json.loads(json_data)
        pretty_json = json.dumps(parsed, indent=4)

        if save and file:
            with open(file, 'w') as f:
                f.write(pretty_json)

        return pretty_json
    except Exception as e:
        # Handle any exception that occurs during the JSON conversion and file writing process
        print(f"An error occurred: {str(e)}")
        return None


import matplotlib.pyplot as plt
import matplotlib

matplotlib.use('Qt5Agg')
import base64
import requests
from PIL import Image
from io import BytesIO


def plot_mermaid(diagram: str, path: str = None) -> None:
    """
    Plot a Mermaid diagram by converting it to an image and displaying it using Matplotlib.

    Args:
        diagram (str): The Mermaid diagram string.

    Returns:
        None
    """
    try:
        graphbytes = diagram.encode("ascii")
        base64_bytes = base64.b64encode(graphbytes)
        base64_string = base64_bytes.decode("ascii")
        url = "https://mermaid.ink/img/" + base64_string
        response = requests.get(url)
        print('response status code should be 200: ', response.status_code)
        img = Image.open(BytesIO(response.content))

        # plot
        fig, ax = plt.subplots(figsize=(10, 8))
        ax.set_aspect('equal')
        ax.imshow(img)
        plt.axis('off')
        ax.axis('off')
        # Maximize the figure
        manager = plt.get_current_fig_manager()
        manager.window.showMaximized()
        # save figure
        if path:
            plt.savefig(path, format='png', dpi=300)
        plt.show()

    except Exception as e:
        # Handle any exception that occurs during the diagram plotting process
        print(f"An error occurred: {str(e)}");



def csv2dataset(file: str, max_tokens: int = 100, encoding: str = 'latin1') -> pd.DataFrame:
    """
    This function reads a CSV file into a pandas DataFrame and then reduces the dataset until the number of tokens is less than a maximum limit.

    Parameters:
    file (str): The file path to the CSV file.
    max_tokens (int, optional):  The number of tokens must be less than the maximum limit.
    encoding (str, optional): The type of encoding to use when reading the CSV file. Defaults to 'latin1'.

    Returns:
    pd.DataFrame: The reduced dataset.
    """

    # Read the CSV file into a pandas DataFrame
    dataset = pd.read_csv(file, low_memory=False, encoding=encoding)

    # Print the first few rows of the dataset
    print(dataset.head())

    # Print the shape of the dataset, the number of tokens, and the column names
    print('shape: ', dataset.shape, '\nnum tokens: ', count_tokens(dataset.to_dict()), '\ncolumns: ', dataset.columns)

    # Define the initial ratio of the dataset to sample
    initial_ratio = .1

    # Define the step size for the decay function
    step = 1  # We'll increase this by 1 each time

    # Define the decay rate for the decay function
    decay_rate = 0.95  # This is the 'b' in the formula, adjust as needed

    # Take a subset of N random samples
    dataset = dataset.sample(frac=initial_ratio)

    # Continue to sample a smaller subset of the dataset until the number of tokens is less than the maximum limit
    while count_tokens(dataset.to_dict()) > max_tokens:
        # Calculate the new ratio for the decay function
        ratio = initial_ratio * (decay_rate ** step)

        # Sample a subset of the dataset based on the new ratio
        dataset = dataset.sample(frac=ratio)

        # Print the new ratio, the shape of the dataset, and the number of tokens
        print('ratio: ', ratio, 'shape: ', dataset.shape, '\nnum tokens: ', count_tokens(dataset.to_dict()))

        # Increase the step size by 1
        step += 1

    # Return the reduced dataset
    return dataset
