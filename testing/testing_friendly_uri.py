import pandas as pd
import urllib.parse
import hashlib
import json

def read_csv_file(file: str, encoding: str = 'latin1') -> pd.DataFrame:
    """Read the CSV file into a pandas DataFrame."""
    return pd.read_csv(file, low_memory=False, encoding=encoding)



def clean_slug(text):
    # Decode percent-encoded characters
    text = urllib.parse.unquote_plus(text)

    # Remove URL scheme and domain
    parts = text.split('/')
    if parts[0].startswith('http'):  # Check if there is a scheme to remove
        text = '-'.join(parts[3:])  # Skip the scheme and domain part

    # Replace unwanted characters with a hyphen
    text = (
        text.lower()
        .replace(' ', '-')
        .replace('(', '')
        .replace(')', '')
        .replace(',', '')
        .replace('/', '-')
        .replace('---', '-')
        .replace('--', '-')
        .replace('&', 'and')
    )

    # Remove multiple consecutive hyphens
    while '--' in text:
        text = text.replace('--', '-')

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


def generate_fair_uris(dataframe, columns_to_use):
    # List to store the generated FAIR URIs
    fair_uris = []

    # Loop through the specified number of rows in the dataframe
    for row_index in range(len(dataframe)):
        # Generate the FAIR URI for the current row
        fair_uri = create_fair_friendly_uri(dataframe, row_index, columns_to_use)
        # Append the FAIR URI to the list
        fair_uris.append(fair_uri)

    return fair_uris

def find_unique_identifier(df):
    for column in df.columns:
        # Check if all values in the column are unique
        if df[column].is_unique and not df[column].hasnans:
            return column
    return None





def describe_numeric_columns(dataset: pd.DataFrame) -> pd.DataFrame:
    summary = dataset.describe(percentiles=[])
    desired_stats = summary.loc[['count', 'mean', 'std', 'min', 'max']]
    desired_stats = desired_stats.transpose()
    desired_stats['type'] = 'Numerical'
    return desired_stats.drop(columns=['non_null_count', 'unique_count'], errors='ignore')

def summarize_text_columns(dataset: pd.DataFrame, threshold: int = 10) -> pd.DataFrame:
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
    return pd.DataFrame(index=dataset.columns)  # Cambiado a dataset.columns



def merge_summaries(*args) -> pd.DataFrame:
    # Inicializar un DataFrame vacío con los nombres de las columnas como índice
    merged_summary = pd.DataFrame(index=args[0].index)

    # Combinar cada resumen en el resumen fusionado, reemplazando los valores ausentes
    for arg in args:
        merged_summary = merged_summary.combine_first(arg)

    # Llenar los valores NaN restantes con '-'
    merged_summary = merged_summary.fillna('-')

    return merged_summary

def remove_dash_entries(summary):
    cleaned_summary = {col: {k: v for k, v in data.items() if v != "-"} for col, data in summary.items()}
    return cleaned_summary


def csv_statistical_description(dataset: pd.DataFrame) -> pd.DataFrame:
    categorical_summary = summarize_categorical_columns(dataset)
    numeric_summary = describe_numeric_columns(dataset)
    text_summary = summarize_text_columns(dataset)

    summary = merge_summaries(categorical_summary, text_summary, numeric_summary)

    # Convertir el DataFrame a un diccionario y luego limpiar las entradas que tienen un valor de "-"
    summary_dict = summary.to_dict(orient='index')
    cleaned_summary_dict = remove_dash_entries(summary_dict)

    # Opcional: Convertir el diccionario limpio de nuevo a un DataFrame si es necesario
    cleaned_summary_df = pd.DataFrame.from_dict(cleaned_summary_dict, orient='index')

    return cleaned_summary_df


def csv_data_preprocessing(file: str, encoding: str = 'latin1'):
    dataset = read_csv_file(file, encoding)

    unique_id_column = find_unique_identifier(dataset)

    if unique_id_column and not unique_id_column == 'FAIR_URI':
        print(f"The column '{unique_id_column}' is a suitable unique identifier.")
        dataset['FAIR_URI'] = generate_fair_uris(dataset, [unique_id_column])
    else:
        print("No suitable unique identifier column found.")
        dataset['FAIR_URI'] = generate_fair_uris(dataset, [])

    print(dataset.head())
    return csv_statistical_description(dataset)



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

file = 'datasets/AirlinesCustomerSatisfaction/AirlinesCustomerSatisfaction.csv'
# Example usage:
summary_df = csv_data_preprocessing(file)

json = dataframe2prettyjson(summary_df)

print(json)

