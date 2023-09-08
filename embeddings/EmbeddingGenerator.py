from sentence_transformers import SentenceTransformer
from sklearn.decomposition import PCA

class EmbeddingGenerator:

    def __init__(self, model='all-MiniLM-L6-v2'):
        self.model = SentenceTransformer(model)

    def get_embeddings(self, sentences):
        embeddings = self.model.encode(sentences)
        return embeddings

    def get_pca(self, embeddings, n_components=2):
        reduced_dimensions = PCA(n_components=n_components).fit_transform(embeddings)
        return reduced_dimensions