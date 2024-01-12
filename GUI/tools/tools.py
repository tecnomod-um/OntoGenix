from typing import Any, Dict, List
import numpy as np
import os
import json
import pandas as pd
import re
import urllib.parse
import hashlib


def list_files(path: str) -> List[str]:
    """
    List and sort files in the given directory.

    This function lists all files in the specified directory and sorts them numerically based on a specific part
    of the filename. It assumes that files are named in a way that includes an underscore ('_') followed by a
    numeric value before the file extension.

    Args:
        path (str): The path to the directory containing the files.

    Returns:
        List[str]: A list of sorted filenames.
    """
    files = os.listdir(path)
    sorted_files = sorted(files, key=lambda x: int(x.split('_')[1].split('.')[0]))
    print(sorted_files)  # Optional: print the sorted file list
    return sorted_files


def load_dictionary(path: str) -> Dict[Any, Any]:
    """
    Load a dictionary from a numpy (.npy) file.

    This function loads a dictionary saved in a numpy file format. The numpy file is expected to contain
    a single dictionary object.

    Args:
        path (str): The file path of the numpy file to load.

    Returns:
        Dict[Any, Any]: The dictionary loaded from the file.
    """
    return np.load(path, allow_pickle=True).item()


def save_dictionary(path: str, semantic_descriptions: Dict[Any, Any]) -> None:
    """
    Save a dictionary to a numpy (.npy) file.

    This function saves the given dictionary into a numpy file format. The dictionary is saved with
    'allow_pickle' set to True.

    Args:
        path (str): The file path where the dictionary will be saved.
        semantic_descriptions (Dict[Any, Any]): The dictionary to save.
    """
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
        json_data = dataframe.to_json(orient='index')
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


def read_csv_file(file: str, encoding: str = 'latin1') -> pd.DataFrame:
    """
    Read the CSV file into a pandas DataFrame.

    Args:
        file (str): The path to the CSV file.
        encoding (str, optional): The encoding format of the CSV file. Defaults to 'latin1'.

    Returns:
        pd.DataFrame: A DataFrame containing the data read from the CSV file.
    """
    return pd.read_csv(file, low_memory=False, encoding=encoding)

def find_unique_identifier(df: pd.DataFrame) -> str:
    """
    Identify a column in the DataFrame that can be used as a unique identifier.

    This function iterates through each column of the DataFrame to find a column where all values are unique
    and there are no missing values (NaNs).

    Args:
        df (pd.DataFrame): The DataFrame to search for a unique identifier.

    Returns:
        str: The name of the column that can be used as a unique identifier, or None if no such column exists.
    """
    for column in df.columns:
        if df[column].is_unique and not df[column].hasnans:
            return column
    return None

def describe_numeric_columns(dataset: pd.DataFrame) -> pd.DataFrame:
    """
    Generate a summary of numeric columns in a DataFrame.

    This function provides statistical summaries (like count, mean, standard deviation, min, max) for columns
    in the DataFrame that contain numeric data.

    Args:
        dataset (pd.DataFrame): The DataFrame to summarize.

    Returns:
        pd.DataFrame: A DataFrame containing statistical summaries of numeric columns.
    """
    summary = dataset.describe(percentiles=[])
    desired_stats = summary.loc[['count', 'mean', 'std', 'min', 'max']]
    desired_stats = desired_stats.transpose()
    desired_stats['type'] = 'Numerical'
    return desired_stats.drop(columns=['non_null_count', 'unique_count'], errors='ignore')

def summarize_text_columns(dataset: pd.DataFrame, threshold: int = 10) -> pd.DataFrame:
    """
    Generate a summary of text columns in a DataFrame.

    This function identifies columns that are likely to be textual based on the number of unique values
    (exceeding a specified threshold) and provides a summary of these columns.

    Args:
        dataset (pd.DataFrame): The DataFrame to summarize.
        threshold (int, optional): The threshold for identifying a column as text based on its unique value count. Defaults to 10.

    Returns:
        pd.DataFrame: A DataFrame containing summaries of text columns.
    """
    likely_text = dataset.select_dtypes(include='object').apply(lambda col: col.nunique() > threshold)
    text_columns = dataset[likely_text.index[likely_text]]
    if not text_columns.empty:
        summary = pd.DataFrame({
            'non_null_count': text_columns.apply(lambda col: col.notnull().sum()),
            'unique_count': text_columns.apply(lambda col: col.nunique()),
            'type': 'text'
        }, index=text_columns.columns)
        return summary.drop(columns=['count', 'mean', 'std', 'min', 'max'], errors='ignore')
    return pd.DataFrame(index=text_columns.index)


def summarize_categorical_columns(dataset: pd.DataFrame, threshold: int = 10) -> pd.DataFrame:
    """
    Summarize the categorical columns in a DataFrame.

    This function identifies categorical columns (those with a number of unique values less than or equal to a threshold)
    and summarizes them in terms of non-null count and unique value count.

    Args:
        dataset (pd.DataFrame): The DataFrame to be summarized.
        threshold (int, optional): The maximum number of unique values a column can have to be considered categorical. Defaults to 10.

    Returns:
        pd.DataFrame: A summary DataFrame for categorical columns.
    """
    likely_categorical = dataset.select_dtypes(include=['object', 'int', 'float']).apply(lambda col: col.nunique() <= threshold)
    categorical_columns = dataset[likely_categorical.index[likely_categorical]]
    if not categorical_columns.empty:
        summary_data = {
            'non_null_count': categorical_columns.apply(lambda col: col.notnull().sum()),
            'unique_count': categorical_columns.apply(lambda col: col.nunique()),
            'type': ['categorical'] * len(categorical_columns.columns)
        }
        summary = pd.DataFrame(summary_data, index=categorical_columns.columns)
        return summary.drop(columns=['count', 'mean', 'std', 'min', 'max'], errors='ignore')
    return pd.DataFrame(index=dataset.columns)  # Return an empty DataFrame with the column names as index if no categorical columns are found


def merge_summaries(*args) -> pd.DataFrame:
    """
    Merge multiple DataFrame summaries into one.

    This function takes multiple DataFrame summaries and merges them into a single summary,
    filling in missing values with '-'.

    Args:
        *args: Variable length argument list of DataFrame summaries.

    Returns:
        pd.DataFrame: A single DataFrame representing the merged summary of all input DataFrames.
    """
    # Initialize an empty DataFrame with column names as index
    merged_summary = pd.DataFrame(index=args[0].index)

    # Merge each summary into the merged summary, replacing missing values
    for arg in args:
        merged_summary = merged_summary.combine_first(arg)

    # Fill any remaining NaN values with '-'
    return merged_summary.fillna('-')


def remove_dash_entries(summary: Dict[str, Dict[str, Any]]) -> Dict[str, Dict[str, Any]]:
    """
    Remove entries with a dash ('-') from a summary dictionary.

    Args:
        summary (Dict[str, Dict[str, Any]]): The summary dictionary to clean.

    Returns:
        Dict[str, Dict[str, Any]]: A cleaned summary dictionary without dash entries.
    """
    cleaned_summary = {col: {k: v for k, v in data.items() if v != "-"} for col, data in summary.items()}
    return cleaned_summary


def csv_statistical_description(dataset: pd.DataFrame) -> pd.DataFrame:
    """
    Generate a comprehensive statistical description for a CSV dataset.

    This function creates summaries for categorical, numeric, and text columns in the dataset,
    merges these summaries, and then cleans the merged summary.

    Args:
        dataset (pd.DataFrame): The dataset for which the statistical description is to be generated.

    Returns:
        pd.DataFrame: A DataFrame containing the cleaned, comprehensive statistical description of the dataset.
    """
    # Generate summaries for different types of columns
    categorical_summary = summarize_categorical_columns(dataset)
    numeric_summary = describe_numeric_columns(dataset)
    text_summary = summarize_text_columns(dataset)

    # Merge the summaries
    summary = merge_summaries(categorical_summary, text_summary, numeric_summary)

    # Convert the merged summary DataFrame to a dictionary and clean dash entries
    summary_dict = summary.to_dict(orient='index')
    cleaned_summary_dict = remove_dash_entries(summary_dict)

    # Optionally, convert the cleaned summary dictionary back to a DataFrame if necessary
    cleaned_summary_df = pd.DataFrame.from_dict(cleaned_summary_dict, orient='index')

    return cleaned_summary_df


def clean_slug(text: str) -> str:
    """
    Clean and format a text string into a slug.

    This function decodes percent-encoded characters in the text, removes the URL scheme and domain if present,
    and replaces specific characters with hyphens or removes them. The goal is to create a standardized, cleaner
    version of a URL slug or similar text string.

    Args:
        text (str): The text to be cleaned and formatted into a slug.

    Returns:
        str: The cleaned and formatted text.
    """
    # Decode percent-encoded characters
    text = urllib.parse.unquote_plus(text)

    # Remove URL scheme and domain
    parts = text.split('/')
    if parts[0].startswith('http'):  # Check if there is a scheme to remove
        text = '-'.join(parts[3:])  # Skip the scheme and domain part

    # Replace unwanted characters with a hyphen and remove certain characters
    text = (
        text.lower()  # Convert to lower case
        .replace(' ', '-')  # Replace spaces with hyphens
        .replace('(', '')   # Remove parentheses
        .replace(')', '')
        .replace(',', '')   # Remove commas
        .replace('/', '-')  # Replace slashes with hyphens
        .replace('---', '-')  # Replace triple hyphens with a single one
        .replace('--', '-')  # Replace double hyphens with a single one
        .replace('&', 'and')  # Replace ampersand with 'and'
    )

    # Remove multiple consecutive hyphens (if any left after the replacements above)
    while '--' in text:
        text = text.replace('--', '-')

    # Strip leading and trailing hyphens
    return text.strip('-')



def create_fair_friendly_uri(df, row_index, columns_to_use) -> str:
    """
    Generates a FAIR and friendly URI for an item in a dataset, based on specified columns.

    Args:
        df (pd.DataFrame): The DataFrame with the data.
        row_index (int): The index of the row to generate the URI for.
        columns_to_use (list of str): List of column names to use for generating the URI.
        base_url (str): Base url to generate a FAIR friendly uri.

    Returns:
        str: The FAIR and friendly URI.
    """

    # Get the row data as a Series
    row_data = df.loc[row_index]

    # Verify that all columns exist in the DataFrame
    for column in columns_to_use:
        if column not in df.columns:
            raise ValueError(f"The column '{column}' is not in the DataFrame.")

    # Concatenate the values of the specified columns to create a unique string
    unique_string = '_'.join(str(row_data[column]) for column in columns_to_use if row_data[column]) + f"_{row_index}"


    # Create a unique identifier by hashing the unique string
    unique_identifier = hashlib.sha256(unique_string.encode()).hexdigest()[:10]

    # Clean and prepare the slug for each column
    main_slug = '-'.join(clean_slug(str(row_data[column])) for column in columns_to_use)

    # Combine base URL, the main slug, and the unique identifier to create the URI
    fair_friendly_uri = f"{main_slug}-{unique_identifier}"

    return fair_friendly_uri


def generate_fair_uris(dataframe: pd.DataFrame, columns_to_use: list) -> list:
    """
    Generate FAIR (Findable, Accessible, Interoperable, and Reusable) URIs for each row in a DataFrame.

    This function creates unique URIs for each row in the DataFrame using the specified columns.

    Args:
        dataframe (pd.DataFrame): The DataFrame for which to generate the URIs.
        columns_to_use (list): A list of column names to be used for generating the URIs.

    Returns:
        list: A list of FAIR URIs corresponding to each row of the DataFrame.
    """
    fair_uris = []

    for row_index in range(len(dataframe)):
        fair_uri = create_fair_friendly_uri(dataframe, row_index, columns_to_use)
        fair_uris.append(fair_uri)

    return fair_uris


def csv_data_preprocessing(file: str, encoding: str = 'latin1') -> pd.DataFrame:
    """
    Preprocess a CSV file to add FAIR URIs and return a statistical description.

    This function reads a CSV file, identifies a unique identifier column (if present),
    generates FAIR URIs, writes the updated dataset back to the CSV file, and returns a
    statistical description of the dataset.

    Args:
        file (str): Path to the CSV file.
        encoding (str, optional): Encoding of the CSV file. Defaults to 'latin1'.

    Returns:
        pd.DataFrame: A DataFrame containing the statistical description of the dataset.
    """
    dataset = read_csv_file(file, encoding)
    unique_id_column = find_unique_identifier(dataset)

    if unique_id_column:
        dataset['FAIR_URI'] = generate_fair_uris(dataset, [unique_id_column])
    else:
        dataset['FAIR_URI'] = generate_fair_uris(dataset, [])

    dataset.to_csv(file, encoding=encoding, index=False)

    return csv_statistical_description(dataset)



def preprocess_md(md_text: str) -> str:
    """
    Preprocess a markdown text to escape specific code blocks.

    This function finds all code blocks in the markdown text and escapes the starting and ending
    tags of RDF (Resource Description Framework) within these blocks.

    Args:
        md_text (str): The markdown text to preprocess.

    Returns:
        str: The preprocessed markdown text.
    """
    code_blocks = re.findall(r'```.*?```', md_text, re.DOTALL)

    for block in code_blocks:
        escaped_block = block.replace("<rdf:RDF", "&lt;rdf:RDF")
        escaped_block = escaped_block.replace("</rdf:RDF>", "&lt;/rdf:RDF&gt;")
        md_text = md_text.replace(block, escaped_block)

    return md_text



def load_string_from_file(file_path: str) -> str:
    """
    Load and return the content of a file as a string.

    Args:
        file_path (str): Path to the file to read.

    Returns:
        str: The content of the file.
    """
    with open(file_path, 'r') as file:
        return file.read()
