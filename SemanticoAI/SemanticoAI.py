from SemanticoAI.LLM_semantico import LlmSemantico
from embeddings.EmbeddingGenerator import EmbeddingGenerator
class Semantico:


    def __init__(self, ontology_path, chunks_path):
        # Setup metadata for LlmSemantico
        self.metadata = dict(
            instructions='./SemanticoAI/instructions.prompt',
            ontology_path=ontology_path,
            chunks_path=chunks_path,# '.datasets/GoodRelations_v1/chunks/'
            role='As an expert ontology engineer your task is to analyze an ontology written in rdf/xml syntax.',
            model='gpt-3.5-turbo'
        )

        self.semantico = LlmSemantico(self.metadata)  # Creating an instance of LlmSemantico with the specified metadata
        self.embedding_generator = EmbeddingGenerator()

    def get_embeddings(self):
        # Generate semantic descriptions using LlmSemantico
        semantic_descriptions = self.semantico.generate_semantic_descriptions()
        # get sentences from descriptions
        sentences = [data['description'] for data in semantic_descriptions.values()]
        print('Sentences len: ', len(sentences))
        # get embeddings
        embeddings = self.embedding_generator.get_embeddings(sentences)
        print('Embeddings shape: ', embeddings.shape)
        return embeddings

