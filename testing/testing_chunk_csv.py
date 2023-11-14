from typing import Any, Dict
import numpy as np
import os
import json
import pandas as pd
import re
import urllib.parse
import hashlib

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


def csv2dataset(file: str, max_rows: int = 100, encoding: str = 'latin1') -> pd.DataFrame:
    """
    This function reads a CSV file into a pandas DataFrame and then reduces the dataset until the number of rows is
    less than a maximum limit.

    Parameters:
    file (str): The file path to the CSV file.
    max_rows (int, optional): The number of rows must be less than the maximum limit.
    encoding (str, optional): The type of encoding to use when reading the CSV file. Defaults to 'latin1'.

    Returns:
    pd.DataFrame: The reduced dataset.
    """

    # Read the CSV file into a pandas DataFrame
    dataset = pd.read_csv(file, low_memory=False, encoding=encoding)
    # Print the first few rows of the dataset
    print(dataset.head())
    # Print the shape of the dataset and the column names
    print('shape: ', dataset.shape, '\ncolumns: ', dataset.columns)

    # Define the initial ratio of the dataset to sample
    initial_ratio = .1
    # Define the step size for the decay function
    step = 1
    # Define the decay rate for the decay function
    decay_rate = 0.95

    # Sample the dataset based on the initial ratio
    dataset = dataset.sample(frac=initial_ratio)

    # Continue to sample a smaller subset of the dataset until the number of rows is less than the maximum limit
    while len(dataset) > max_rows:
        # Calculate the new ratio for the decay function
        ratio = initial_ratio * (decay_rate ** step)
        # Sample a subset of the dataset based on the new ratio
        dataset = dataset.sample(frac=ratio)
        # Ensure that the sample does not exceed max_rows
        if len(dataset) > max_rows:
            dataset = dataset.sample(n=max_rows)
        # Print the new ratio and the shape of the dataset
        print('ratio: ', ratio, 'shape: ', dataset.shape)
        # Increase the step size by 1
        step += 1

    # Return the reduced dataset
    return dataset


def saveAsCsv(file: str, dataset: pd.DataFrame):
    dataset.to_csv(file, index=False)

file = "datasets/WalmartProductDetails/walmart_com-ecommerce_product_details__20190311_20191001_sample.csv"

dataset = csv2dataset(file, max_rows=1000)
print(dataset.shape)

fileNew = "datasets/WalmartProductDetails/Chunk_walmart_com-ecommerce_product_details__20190311_20191001_sample.csv"
saveAsCsv(fileNew, dataset)