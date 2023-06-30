def load_rdf(file_name: str):
    with open(file_name, "r") as f:
        rdf_data = f.read()
    return rdf_data

from rdflib import Graph
import networkx as nx

def rdf2graph(rdf_data):
    g = Graph()
    g.parse(data=rdf_data, format='xml')

    # Create a NetworkX graph.
    G = nx.MultiDiGraph()

    # Iterate over the triples in the graph and add each as an edge to the NetworkX graph.
    for s, p, o in g:
        G.add_edge(str(s), str(o), label=str(p))

    return G

def plot_graph(G):
    # draw the graph
    pos = nx.spring_layout(G)
    nx.draw(G, pos, with_labels=True, node_color='lightblue', edge_color='gray', node_size=1000)

    # draw edge labels
    edge_labels = {(u, v): d['label'] for u, v, d in G.edges(data=True)}
    nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_color='red')

    plt.show(block=True)

from node2vec import Node2Vec

def get_embeddings(G):
    # Precompute probabilities and generate walks
    node2vec = Node2Vec(G, dimensions=64, walk_length=30, num_walks=200, workers=4)

    # Embed nodes
    model = node2vec.fit(window=10, min_count=1, batch_words=4)

    # Save embeddings for later use
    # model.wv.save_word2vec_format('./datasets/AmazonRating/embeddings.txt')

    # Save model for later use
    # model.save('./datasets/AmazonRating/model')

    return model

from sklearn.decomposition import PCA
import matplotlib.pyplot as plt

def plot_embeddings(G, model, color='b'):
    # Get all node embeddings
    vectors = [model.wv[node] for node in G.nodes]

    # Perform PCA
    result = PCA(n_components=2).fit_transform(vectors)

    # Create a scatter plot
    plt.scatter(result[:, 0], result[:, 1], color=color)

    # Add labels
    for i, node in enumerate(G.nodes):
        plt.annotate(node, (result[i, 0], result[i, 1]))




file_name = "./datasets/AmazonRating/ratings_Beauty_ontology_LLM.owl"
rdf_data_1 = load_rdf(file_name)
G1 = rdf2graph(rdf_data_1)
model1 = get_embeddings(G1)

file_name = "./datasets/BigBasketProducts/BigBasket_ontology_LLM.owl"
rdf_data_2 = load_rdf(file_name)
G2 = rdf2graph(rdf_data_2)
model2 = get_embeddings(G2)

plt.figure()
plot_embeddings(G1, model1, color='blue')
plot_embeddings(G2, model2, color='red')
plt.show(block=True)




from sentence_transformers import SentenceTransformer
model = SentenceTransformer('all-MiniLM-L6-v2')


sentences_1 = [
    "Product: Represents a product in the system. It is a general entity that encompasses various types of products that can be offered.",
     "Brand: Represents a brand associated with a product. It signifies the manufacturer or company behind a particular product.",
     "Price: Represents the price of a product. It indicates the monetary value assigned to a product without any discounts or promotions.",
     "DiscountPrice: Represents the discounted price of a product. It denotes the reduced price of a product when a discount or promotion is applied.",
     "Image_Url: Represents the URL of an image associated with a product. It stores the web address pointing to an image that visually represents the product.",
     "Quantity: Represents the quantity of a product available. It indicates the number or amount of the product that is in stock or available for purchase.",
     "Category: Represents a category to which a product belongs. It organizes products into broader groups based on shared characteristics or purposes.",
     "SubCategory: Represents a subcategory to which a product belongs. It further refines the categorization of products within a specific category.",
     "hasBrand: Indicates the brand associated with a product. It establishes a relationship between a product and its corresponding brand.",
     "belongsToCategory: Indicates the category to which a product belongs. It establishes a relationship between a product and its assigned category.",
     "belongsToSubCategory: Indicates the subcategory to which a product belongs. It establishes a relationship between a product and its assigned subcategory.",
     "hasPrice: Represents the price of a product. It specifies the monetary value assigned to a product.",
     "hasDiscountPrice: Represents the discounted price of a product. It specifies the reduced price of a product when a discount or promotion is applied.",
     "hasImageUrl Represents the URL of the image associated with a product. It stores the web address pointing to an image that visually represents the product.",
     "hasQuantity: Represents the quantity of a product available. It specifies the number or amount of the product that is in stock or available for purchase."
]
labels_1 = ['Product',
          'Brand',
          'Price',
          'DiscountPrice',
          'Image_Url',
          'Quantity',
          'Category',
          'SubCategory',
          'hasBrand',
          'belongsToCategory',
          'belongsToSubCategory',
          'hasPrice',
          'hasDiscountPrice',
          'hasImageUrl',
          'hasQuantity']

sentences_2 = [
    "User: Represents a user in the system. It refers to an individual who interacts with the system, such as providing ratings or making purchases.",
    "Product: Represents a product in the system. It encompasses various types of products that can be offered for sale or rated by users.",
    "Rating: Represents a rating given by a user to a product. It captures the feedback or evaluation provided by a user regarding a specific product.",
    "Timestamp: Represents a timestamp associated with a rating. It signifies the date and time when a user submitted a rating.",
    "City: Represents a city. It is a subclass of 'City' and is related to a specific zip code prefix through the 'hasZipCodePrefix' property.",
    "Customer: Represents a customer. It is a subclass of 'City' and has a zip code prefix, a city, and a customer reference associated with it.",
    "State: Represents a state. It is related to cities through the 'hasCity' property.",
    "ZipCodePrefix: Represents a zip code prefix. It is related to a city through the 'hasCity' property.",
    "Invoice: Represents an invoice. It is associated with sales articles, invoice price, and sales country.",
    "InvoicePrice: Represents the price of an invoice. It is a subclass of 'UnitPriceSpecification' from the schema.org vocabulary.",
    "SalesArticle: Represents a sales article. It is associated with invoices and has a GTIN/EAN identifier.",
    "Country: Represents a country according to the schema.org vocabulary.",
    "hasRated: Relates a user to a product for which they have given a rating. The domain is 'User', and the range is 'Product'.",
    "hasUser: Relates a rating to the user who provided it. The domain is 'Rating', and the range is 'User'.",
    "hasProduct: Relates a rating to the product being rated. The domain is 'Rating', and the range is 'Product'.",
    "hasTimestamp: Relates a rating to the timestamp when it was submitted. The domain is 'Rating', and the range is 'Timestamp'.",
    "hasCity: Relates an entity to a city. It is a general object property, and its range is 'City'.",
    "hasState: Relates an entity to a state. It is a general object property, and its range is 'State'.",
    "hasZipCodePrefix: Relates an entity to a zip code prefix. It is a general object property, and its range is 'ZipCodePrefix'.",
    "ThasSalesArticle: Relates an invoice to a sales article. The domain is 'Invoice', and the range is 'SalesArticle'.",
    "TsalesCountry: Relates an invoice to a sales country. The domain is 'Invoice', and the range is 'Country'.",
    "PriceSpecification: Relates an invoice to its price specification. The domain is 'Invoice', and the range is 'UnitPriceSpecification' from the schema.org vocabulary.",
    "Tcomment: Represents a comment associated with an entity. It is a datatype property with a string value.",
    "Tidentifier: Represents an identifier associated with an invoice. It is a datatype property with a string value.",
    "customer_id: Represents a customer ID associated with an invoice. It is a datatype property with a string value.",
    "date: Represents a date associated with an invoice. It is a datatype property with a dateTime value.",
    "quantity: Represents a quantity associated with an invoice. It is a datatype property with an integer value.",
    "MT/GTIN_EAN: Represents a GTIN/EAN identifier associated with a sales article. It is a datatype property with a string value."
]
labels_2 = [
    'User',
    'Product',
    'Rating',
    'Timestamp',
    'City',
    'Customer',
    'State',
    'ZipCodePrefix',
    'Invoice',
    'InvoicePrice',
    'SalesArticle',
    'Country',
    'hasRated',
    'hasUser',
    'hasProduct',
    'hasTimestamp',
    'hasCity',
    'hasState',
    'hasZipCodePrefix',
    'ThasSalesArticle',
    'TsalesCountry',
    'PriceSpecification',
    'Tcomment',
    'Tidentifier',
    'customer_id',
    'date',
    'quantity',
    'MT/GTIN_EAN'
]

def plot_word_embeddings(result, labels, color='b'):
    plt.scatter(result[:, 0], result[:, 1], color=color)
    for i, node in enumerate(labels):
        plt.annotate(node, (result[i, 0], result[i, 1]))


sentence_embeddings_1 = model.encode(sentences_1)
sentence_embeddings_2 = model.encode(sentences_2)

result_1 = PCA(n_components=2).fit_transform(sentence_embeddings_1)
result_2 = PCA(n_components=2).fit_transform(sentence_embeddings_2)

plt.figure()
plot_word_embeddings(result_1, labels_1, color='cyan')
plot_word_embeddings(result_2, labels_2, color='magenta')
plt.show(block=True)



import os
from rdflib import Graph, URIRef

def split_rdf(input_file, output_folder, chunk_size):
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

# usage
# split_rdf("./datasets/GoodRelations_V1/v1.owl", "./datasets/GoodRelations_V1/", 10) hecho!!!


import yaml

with open("config.yaml", 'r') as stream:
    data_loaded = yaml.safe_load(stream)

config = data_loaded["OntoGenixConfig"]

base_path = config["base_path"]
dataset_folder = config["dataset_folder"]
dataset_file = config["dataset_file"]

from SemanticoAI.LLM_semantic import LlmSemantic

semantico_metadata = {
    'instructions': './SemanticoAI/instructions.prompt',
    'dataset': base_path + dataset_folder + '/' + dataset_file,
    'role': 'As an expert ontology engineer, SemanticoAI, your task is to analyze an ontology written in rdf/xml syntax.'
}
semantico = LlmSemantic(semantico_metadata)

import os

# Path to the directory
directory_path = './datasets/GoodRelations_V1/chunked/'

# List all files in the directory
files = os.listdir(directory_path)

dictionaries = dict()

# Read each file
for file in files:
    # Construct full file path
    file_path = os.path.join(directory_path, file)

    # Open each file and read its content
    if os.path.isfile(file_path):  # Check if it's a file, not a directory
        with open(file_path, 'r') as f:
            chunk = f.read()

        semantico.interact(chunk)

        dictionaries.update( semantico.semantic_descriptions )



sentences = list(dictionaries.values())
labels = dictionaries.keys()


from sentence_transformers import SentenceTransformer
model = SentenceTransformer('all-MiniLM-L6-v2')

sentence_embeddings = model.encode(sentences)

from sklearn.decomposition import PCA

result = PCA(n_components=2).fit_transform(sentence_embeddings)

import matplotlib.pyplot as plt

plt.figure()
plot_word_embeddings(result, labels, color='cyan')
plt.show(block=True)
