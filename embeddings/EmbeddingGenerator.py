from sentence_transformers import SentenceTransformer
from sklearn.decomposition import PCA
from typing import Union
import numpy as np


class EmbeddingGenerator:
    """
    A class to generate embeddings for given sentences using SentenceTransformer and to reduce dimensions using PCA.
    """

    def __init__(self, model: str = 'all-MiniLM-L6-v2'):
        """
        Initializes the EmbeddingGenerator with a specified SentenceTransformer model.

        Parameters:
        - model (str): The name or path of the SentenceTransformer model. Defaults to 'all-MiniLM-L6-v2'.
        """
        # Load the SentenceTransformer model
        self.model = SentenceTransformer(model)

    def get_embeddings(self, sentences: Union[str, List[str]]) -> np.ndarray:
        """
        Generate embeddings for the given sentence or list of sentences.

        Parameters:
        - sentences (Union[str, List[str]]): A single sentence or a list of sentences to generate embeddings for.

        Returns:
        - np.ndarray: Numpy array of embeddings for the given sentences.
        """
        # Encode the given sentences to get their embeddings
        embeddings = self.model.encode(sentences)
        return embeddings

    @staticmethod
    def get_pca(embeddings: np.ndarray, n_components: int = 2) -> np.ndarray:
        """
        Reduce the dimensionality of the given embeddings using PCA.

        Parameters:
        - embeddings (np.ndarray): The numpy array of embeddings to be reduced.
        - n_components (int): The number of components to reduce the embeddings to. Defaults to 2.

        Returns:
        - np.ndarray: Numpy array of embeddings with reduced dimensions.
        """
        # Perform PCA to reduce the dimensions of the embeddings
        reduced_dimensions = PCA(n_components=n_components).fit_transform(embeddings)
        return reduced_dimensions
