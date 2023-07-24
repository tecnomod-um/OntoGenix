# -*- coding: utf-8 -*-
'''
TODO:
    CODING TASKS:
    - Check openai Embeddings instead of sentence-transformer bert model.
    - Refine the Mapper strategy: At present, it's fairly straightforward and direct. It could be enriched with
    external libraries to generate the kgraph from the data source, the ontology, and the mapping definition, to
    consider the errors produced in the refinement loop. This would necessitate the use of libraries capable of
    automated kgraph creation, if they exist.
    - Code refactoring: This should be an ongoing, daily process.

    IDEAS:
    - The OntoBuilder strategy comprises four stages:
        + Generate a fundamental ontology.
        + Analyze a selection of example ontologies. This phase could be addressed in alternative ways:
            a) let the user select the example set of ontologies.
            b) preselect a representative set and use always the same set.(current approach: NOT WORKING)
            c) have a big set of ontologies that are represented in an embedding space as a graph level. The generated
            ontology by the LLM is then embbeded in that space and compared with the ones closer to it, that will be
            used as the set of examples.
        + Synthesize to create an enhanced ontology.
        + Search for related entities in a database of segmented ontologies using semanticoAI and embeddings. BEST OPTION!!!
        + Incorporate relevant entities if they are deemed beneficial.

'''

'''########################################## YAML CONFIG ######################################################'''
import yaml

with open("config.yaml", 'r') as stream:
    data_loaded = yaml.safe_load(stream)

config = data_loaded["OntoGenixConfig"]

base_path = config["base_path"]
dataset_folder = config["dataset_folder"]
dataset_file = config["dataset_file"]

file = base_path + dataset_folder + '/' + dataset_file + '.csv'

'''########################################## DATA2JSON ######################################################'''
from tools import csv2dataset, dataframe2prettyjson

# get a dataset subsample from a csv file
dataset = csv2dataset(file, max_tokens=800)

# format to json for the LLM_base and write to a file
file = base_path + dataset_folder + '/' + dataset_file + '_dataframe_subset.txt'
json_data = dataframe2prettyjson(dataset, file)
print('######## PROMPT ############\n', json_data)


'''########################################## PLAN-INSTRUCTIONS ######################################################'''
# instantiate the LLM_base that generates an owl ontology from a json subset data
from PlanSage.LLM_planner import LlmPlanner

planner_metadata = {
    'first_instructions': './PlanSage/first_instructions.prompt',
    'interaction': './PlanSage/interaction.prompt',
    'dataset': base_path + dataset_folder + '/' + dataset_file,
    'role': 'You are a powerfull ontology engineer that generates the reasoning steps needed to generate'
            'an ontology from a json data table.'
}

planner = LlmPlanner(planner_metadata)

planner.interaction(
    input_task="Generate the steps required to generate an ontology given the input json data table.",
    json_data=json_data
)

planner.interaction(
    instructions = '''Rewrite task_6 with this text: Specify as a foundational prefix "https://vocab.um.es#" for the ontology to ensure a clear structure.'''
)
planner.interaction(
    instructions = '''Add a new task that to generate, based on the entities and their relationships, clases that you consider will enhance the interoperability and semantics of the ontology.'''
)
planner.interaction(
    instructions = '''Add a new task to do not add any type of individuals in the ontology.'''
)
planner.interaction(
    instructions = '''Add a new task to generate a description field, an alternative name and a set of five alternative labels for each entity such 
    as classes, object properties or data properties.'''
)
planner.interaction(
    instructions = '''Add a new task to generate a new definition in the doctype for the foundational prefix: <!ENTITY um "https://vocab.um.es#"> and the 
    needed one for the rest of the uris defined in the rdf section of the ontology.'''
)
planner.regenerate()

instructions = planner.stable_plan

'''########################################## ONTOLOGY ######################################################'''
# instantiate the LLM_base that generates an owl ontology from a json subset data
from OntoBuilder.LLM_ontology import LlmOntology


onto_metadata = {'instructions': './OntoBuilder/instructions.prompt',
                 'interaction': './OntoBuilder/interaction.prompt',
                 'autocompletion': './OntoBuilder/auto_completion.prompt',
                 'entities_analysis': './OntoBuilder/entities_analysis.prompt',
                 'entity_improvement': './OntoBuilder/entity_improvement.prompt',
                 'dataset': base_path + dataset_folder + '/' + dataset_file,
                 'role': 'You are a powerful ontology engineer that generates OWL ontologies in turtle format.'
                 }

ontology_builder = LlmOntology(onto_metadata)

# GENERATE THE FIRST LLM-ONTOLOGY
instructions_subset = str([task for it, task in enumerate(instructions.values()) if it in [0,1,2,10]])
print(instructions_subset)
ontology_builder.interact(
    json_data=json_data,
    rationale=planner.short_term_memory,
    instructions=instructions_subset
)

# REFINEMENT OF THE LLM-ONTOLOGY [INSTRUCTION BY INSTRUCTION]
instructions_subset = str([task for it, task in enumerate(instructions.values()) if it in [10]])
print(instructions_subset)
ontology_builder.interact(
    json_data=json_data,
    rationale=planner.short_term_memory,
    instructions=instructions_subset,
    ontology=ontology_builder.owl_codeblock
)



# REFINEMENT OF AN ENTITY [INSTRUCTION BY INSTRUCTION]
instructions_subset = '''Establish constraints and interrelations between the classes and properties and define them for each entity in rdf/xml format. Besides, 
generate a description field, an alternative name, and a set of five alternative labels for each entity such as classes, object properties, or data properties.'''
print(instructions_subset)
entity = '''<owl:Class rdf:about="https://vocab.um.es#ProductName">
        <rdfs:subClassOf rdf:resource="http://www.w3.org/2002/07/owl#Thing"/>
        <rdfs:comment>An individual instance of ProductName class represents the name of a product.</rdfs:comment>
        <skos:altLabel>ItemName</skos:altLabel>
        <skos:altLabel>ProductTitle</skos:altLabel>
        <skos:altLabel>ItemTitle</skos:altLabel>
        <skos:altLabel>ItemLabel</skos:altLabel>
    </owl:Class>'''
improved_version = '''<owl:Class rdf:about="https://vocab.um.es#ProductName">
        <rdfs:subClassOf rdf:resource="http://www.w3.org/2002/07/owl#Thing"/>
        <rdfs:comment>An individual instance of ProductName class represents the name of a product.</rdfs:comment>
        <skos:altLabel>ItemName</skos:altLabel>
        <skos:altLabel>ProductTitle</skos:altLabel>
        <skos:altLabel>ItemTitle</skos:altLabel>
        <skos:altLabel>ItemLabel</skos:altLabel>
        <rdfs:subClassOf>
            <owl:Restriction>
                <owl:onProperty rdf:resource="https://vocab.um.es#hasPriceValue"/>
                <owl:minCardinality rdf:datatype="http://www.w3.org/2001/XMLSchema#nonNegativeInteger">1</owl:minCardinality>
            </owl:Restriction>
        </rdfs:subClassOf>
        <rdfs:subClassOf>
            <owl:Restriction>
                <owl:onProperty rdf:resource="https://vocab.um.es#hasDiscountPriceValue"/>
                <owl:minCardinality rdf:datatype="http://www.w3.org/2001/XMLSchema#nonNegativeInteger">1</owl:minCardinality>
            </owl:Restriction>
        </rdfs:subClassOf>
    </owl:Class>'''
reasoning = "we have enhanced the ontology's semantics by adding to the entity definition the constraints, interrelations, alternative labels and description."

from tools import extract_sections_from_rdf, dict_to_rdf

rdf_sections = extract_sections_from_rdf(ontology_builder.owl_codeblock)

for key in rdf_sections.keys():
    if key in ['class_definitions', 'object_property_definitions', 'data_property_definitions']:
        for it,next_entity in enumerate(rdf_sections[key]):
            print('###################################')
            print(next_entity)

            owl_entity_codeblock = ontology_builder.interactByEntity(
                ontology=ontology_builder.owl_codeblock,
                task=instructions_subset,
                entity=entity,
                improved_version=improved_version,
                reasoning=reasoning,
                next_entity=next_entity
            )
            print('%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%')
            print(owl_entity_codeblock)
            rdf_sections[key][it] = owl_entity_codeblock

            ontology_builder.owl_codeblock = dict_to_rdf(rdf_sections)

print(ontology_builder.owl_codeblock)

ontology_builder.regenerate()


'''########################################## SEMANTICO-AI ######################################################'''

from tools import split_rdf
#
ontology_file = base_path + dataset_folder + '/' + dataset_file + '_owl_code_LLM_base.txt'
chunks_folder = base_path + dataset_folder + '/chunks/'
# segment the last llm generated ontology into chunks.
split_rdf(ontology_file, chunks_folder)

from SemanticoAI.LLM_semantico import LlmSemantico
from SemanticoAI.utils import save_semantic_descriptions

semanticoAI_metadata = {
    'instructions': './SemanticoAI/instructions.prompt',
    'dataset': base_path + dataset_folder + '/' + dataset_file,
    'role': 'As an expert ontology engineer, SemanticoAI, your task is to analyze an ontology written in rdf/xml syntax.'
}
semanticoAI = LlmSemantico(semanticoAI_metadata)

semanticoAI.chunksTransform(base_path + dataset_folder + '/chunks/')

save_semantic_descriptions(
    base_path + dataset_folder + '/semantic_descriptions.npy',
    semanticoAI.semantic_descriptions
)


from SemanticoAI.utils import load_semantic_descriptions, process_semantic_descriptions

semantic_descriptions = load_semantic_descriptions(
    base_path + dataset_folder + '/semantic_descriptions.npy'
)

reference_semantic_descriptions = load_semantic_descriptions(
    './datasets/GoodRelations_V1/semantic_descriptions.npy'
)

labels = process_semantic_descriptions(semantic_descriptions, key='proposed_name')
reference_labels = process_semantic_descriptions(reference_semantic_descriptions, key='proposed_name')
all_labels = labels + reference_labels

descriptions = process_semantic_descriptions(semantic_descriptions, key='description')
reference_descriptions = process_semantic_descriptions(reference_semantic_descriptions, key='description')
all_descriptions = descriptions + reference_descriptions

from embeddings.EmbeddingGenerator import EmbeddingGenerator

embedder = EmbeddingGenerator()

ontology_embeddings = embedder.get_embeddings(all_descriptions)
ontology_embeddings_2D = embedder.get_pca(ontology_embeddings)
print(ontology_embeddings.shape)

import matplotlib.pyplot as plt
from tools import plot_word_embeddings

plt.figure()
plot_word_embeddings(ontology_embeddings_2D[:len(labels)], labels)
plot_word_embeddings(ontology_embeddings_2D[len(labels):], reference_labels, color='r')
plt.show()

from SemanticoAI.utils import get_relevant_chunks, load_chunk_samples

selected_chunks = get_relevant_chunks(labels, all_labels, reference_semantic_descriptions, ontology_embeddings_2D)
examples = load_chunk_samples(selected_chunks)

# REFINEMENT OF THE LLM-ONTOLOGY [BY COMPARISON WITH HUMAN ONTOLOGY]
for human_ontology in examples:
    #  human_ontology = examples[3]  # for testing
    ontology_builder.interact(ontology=ontology_builder.owl_codeblock, human_ontology=human_ontology)

'''########################################## MAPPING ######################################################'''

from OntoMapper.LLM_ontomapper import LlmOntoMapper

mapper_metadata = {'instructions': './OntoMapper/instructions.prompt',
                   'dataset': base_path + dataset_folder + '/' + dataset_file,
                   'role': 'You are a powerful ontology engineer that generates RML mappings.'
                   }

ontology_mapper = LlmOntoMapper(mapper_metadata)

rml_code_str = ontology_mapper.interact(json_data=json_data, ontology=ontology_builder.owl_codeblock)









