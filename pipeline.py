# -*- coding: utf-8 -*-
'''
TODO:
    CODING TASKS:
    - Enhance the semanticoAI prompt: Currently, it merely duplicates the entity name. We could perhaps make it
    generate an additional field in the output, such as:
    {name:'entity_name', description:'entity description', proposed_key_name:'key_name'}. DONE!!
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
            b) preselect a representative set and use always the same set.(current approach)
            c) have a big set of ontologies that are represented in an embedding space as a graph level. The generated
            ontology by the LLM is then embbeded in that space and compared with the ones closer to it, that will be
            used as the set of examples.
        + Synthesize to create an enhanced ontology.
        + Search for related entities in a database of segmented ontologies using semanticoAI and embeddings.
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
    input_task="Generate an ontology given the input json data table.",
    json_data=json_data
)

planner.interaction(
    instructions='''include in the task_6 explicitly as fundational prefix this concrete prefix: "https://vocab.um.es#"'''
)
planner.interaction(
    instructions = '''Add a new task that spefically asks to use this prefix "https://vocab.um.es#" to represent your properties.
As an example, the correct form of a line should be: <um:hasPrice rdf:resource="https://vocab.um.es#Price_3258"/>
'''
)
planner.interaction(
    instructions = '''Add a new task that clearly asks to do not add any type of individuals in the ontology.'''
)
planner.interaction(
    instructions = '''Add a new task with the objective of generating for each entity of the ontology a description of the
    entity and include as a comment, to generate an alternative representative name for the entity as a label and a set
    os synonyms for that alternative name as a synonyms field in the entity.'''
)

############ this section is for a closed loop interaction with the ontology builder ####################
# planner.interaction(
#     instructions='some instructions that comes from the ontology builder during the analysis of human
#     generated ontologies'
# )
# -------------------------------------------------------------------------------------------------------

'''########################################## ONTOLOGY ######################################################'''

# instantiate the LLM_base that generates an owl ontology from a json subset data
from OntoBuilder.LLM_ontology import LlmOntology
from tools import compare_texts, text2dict

onto_metadata = {'instructions': './OntoBuilder/instructions.prompt',
                 'interaction': './OntoBuilder/interaction.prompt',
                 'autocompletion': './OntoBuilder/auto_completion.prompt',
                 'ontology_analysis': './OntoBuilder/ontology_analysis.prompt',
                 'ontology_synthesis': './OntoBuilder/ontology_synthesis.prompt',
                 'entities_analysis': './OntoBuilder/entities_analysis.prompt',
                 'examples': './OntoBuilder/examples/',
                 'dataset': base_path + dataset_folder + '/' + dataset_file,
                 'role': 'You are a powerful ontology engineer that generates OWL ontologies in turtle format.'
                 }

ontology_builder = LlmOntology(onto_metadata)

instructions = text2dict(planner.plan)
[print(key, instructions[key]['step_description']) for key in instructions.keys()]
subset_dict = {k: k + ': ' + instructions[k]['step_description'] for k in list(instructions.keys())}
[print(subset_dict[key]) for key in subset_dict.keys()]




# GENERATE THE FIRST LLM-ONTOLOGY
ontology_builder.interact(json_data=json_data, instructions=subset_dict, ontology=None)
ontology_builder.interact(json_data=json_data, instructions=subset_dict, ontology=prev_ontology)
ontology_builder.interact(json_data=json_data, instructions= 'Update the fundational prefix to "https://vocab.um.es#"', ontology=prev_ontology)
# item = 1
# human_ontology = ontology_builder.examples[item]

# ANALYSIS THROUGH COMPARITION OF THE LLM-ONTOLOGY
for item, human_ontology in enumerate(ontology_builder.examples):
    insights, improved_owl_codeblock = ontology_builder.analyze(
        json_data=json_data,
        instructions=planner.plan,
        previous_ontology=ontology_builder.owl_codeblock,
        human_ontology=human_ontology,
        item=item
    )

    owl_codes_comparition = compare_texts(ontology_builder.owl_codeblock, improved_owl_codeblock)
    print(owl_codes_comparition)

    # REFINE THE LLM-ONTOLOGY TAKING INTO ACCOUNT THE PREVIOUS ANALYSIS
    insights, owl_codeblock = ontology_builder.synthesize(
        owl_codes_comparition=owl_codes_comparition,
        item=item
    )

    # planner.interaction(instructions=insights)


from SemanticoAI.utils import load_semantic_descriptions, process_semantic_descriptions

semantic_descriptions = load_semantic_descriptions(
    base_path + dataset_folder + '/semantic_descriptions.npy'
)

reference_semantic_descriptions = load_semantic_descriptions(
    './datasets/GoodRelations_V1/semantic_descriptions.npy'
)

labels = process_semantic_descriptions(semantic_descriptions)
reference_labels = process_semantic_descriptions(reference_semantic_descriptions)
all_words = labels + reference_labels

from embeddings.EmbeddingGenerator import EmbeddingGenerator

embedder = EmbeddingGenerator()

ontology_embeddings = embedder.get_embeddings(all_words)
ontology_embeddings_2D = embedder.get_pca(ontology_embeddings)
print(ontology_embeddings.shape)

import matplotlib.pyplot as plt
from tools import plot_word_embeddings

plt.figure()
plot_word_embeddings(ontology_embeddings_2D[:len(labels)], labels)
plot_word_embeddings(ontology_embeddings_2D[len(labels):], reference_labels, color='r')
plt.show()

from SemanticoAI.utils import get_relevant_chunks, load_chunk_samples

selected_chunks = get_relevant_chunks(labels, all_words, reference_semantic_descriptions, ontology_embeddings_2D)
examples = load_chunk_samples(selected_chunks)

'''########################################## OntoBuilder synthetize from examples obtained by embedding strategy ######################################################'''

# ANALYSIS THROUGH COMPARITION OF THE LLM-ONTOLOGY
for item, human_ontology in enumerate(examples):
    insights, improved_owl_codeblock = ontology_builder.analyze_segment(
        previous_ontology=ontology_builder.owl_codeblock,
        human_ontology=human_ontology,
        item=5+item
    )

    owl_codes_comparition = compare_texts(ontology_builder.owl_codeblock, improved_owl_codeblock)
    print(owl_codes_comparition)

    # REFINE THE LLM-ONTOLOGY TAKING INTO ACCOUNT THE PREVIOUS ANALYSIS
    insights, owl_codeblock = ontology_builder.synthesize(
        owl_codes_comparition=owl_codes_comparition,
        item=2+item
    )

'''########################################## MAPPING ######################################################'''

from OntoMapper.LLM_ontomapper import LlmOntoMapper

mapper_metadata = {'instructions': './OntoMapper/instructions.prompt',
                   'dataset': base_path + dataset_folder + '/' + dataset_file,
                   'role': 'You are a powerful ontology engineer that generates RML mappings.'
                   }

ontology_mapper = LlmOntoMapper(mapper_metadata)

rml_code_str = ontology_mapper.interact(json_data=json_data, ontology=ontology_builder.owl_codeblock)














