from typing import Any, Dict
import numpy as np
import os
import json
import pandas as pd


def list_files(path):
    files = os.listdir(path)
    sorted_files = sorted(files, key=lambda x: int(x.split('_')[1].split('.')[0]))
    print(sorted_files)
    return sorted_files


def load_dictionary(path: str) -> dict:
    return np.load(path, allow_pickle=True).item()


def save_dictionary(path, semantic_descriptions):
    np.save(path, semantic_descriptions, allow_pickle=True)


def dataframe2prettyjson(dataframe: pd.DataFrame, file: str = None, save: bool = False) -> str:
    """
    Convert a Pandas DataFrame to pretty JSON and optionally save it to a file.

    Args:
        dataframe (pd.DataFrame): The input DataFrame.
        file (str): The file path to save the pretty JSON.
        save (bool): Whether to save the JSON to a file.

    Returns:
        str: The pretty JSON string representation.
    """
    try:
        json_data = dataframe.to_json(orient='columns')
        parsed = json.loads(json_data)
        pretty_json = json.dumps(parsed, indent=4)

        if save and file:
            with open(file, 'w') as f:
                f.write(pretty_json)

        return pretty_json
    except json.JSONDecodeError as je:
        print(f"JSON Decode Error: {str(je)}")
    except ValueError as ve:
        print(f"Value Error: {str(ve)}")
    except Exception as e:
        print(f"An unexpected error occurred: {str(e)}")
        return ""


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


def csv2dataset(file: str, max_tokens: int = 100, encoding: str = 'latin1') -> pd.DataFrame:
    """
    This function reads a CSV file into a pandas DataFrame and then reduces the dataset until the number of tokens is
    less than a maximum limit.

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
