from tools import csv2dataset, dataframe2prettyjson, plot_mermaid, extract_text

base_path = './datasets/'
dataset_folder = 'BigBasketProducts'
dataset_file = 'BigBasket'
file = base_path + dataset_folder + '/' + dataset_file + '.csv'

# get a dataset subsample from a csv file
dataset = csv2dataset(file, max_tokens=800)

# format to json for the LLM_base and write to a file
file = base_path + dataset_folder + '/' + dataset_file + '_dataframe_subset.txt'
json_data = dataframe2prettyjson(dataset, file)
print('######## PROMPT ############\n', json_data)


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

############ this section is for a closed loop interaction with the ontology builder ####################
# planner.interaction(
#     instructions='some instructions that comes from the ontology builder during the analysis of human
#     generated ontologies'
# )
#-------------------------------------------------------------------------------------------------------

# instantiate the LLM_base that generates an owl ontology from a json subset data
from OntoBuilder.LLM_ontology import LlmOntology

onto_metadata = {'instructions': './OntoBuilder/instructions.prompt',
                 'autocompletion':  './OntoBuilder/auto_completion.prompt',
                 'ontology_analysis': './OntoBuilder/ontology_analysis.prompt',
                 'ontology_synthesis': './OntoBuilder/ontology_synthesis.prompt',
                 'examples': './OntoBuilder/examples/',
                 'dataset': base_path + dataset_folder + '/' + dataset_file,
                 'role': 'You are a powerful ontology engineer that generates OWL ontologies in turtle format.'
                 }

ontology_builder = LlmOntology(onto_metadata)

ontology_builder.interact(json_data=json_data, instructions=planner.plan)

for human_ontology in ontology_builder.examples:
    insights = ontology_builder.analyze(
        json_data=json_data,
        instructions=planner.plan,
        previous_ontology=ontology_builder.owl_codeblock,
        human_ontology=human_ontology
    )

    planner.interaction(instructions=insights) # algo no funciona bien aqui!!!

ontology_builder.synthesize()


from OntoMapper.LLM_ontomapper import LlmOntoMapper

mapper_metadata = {'instructions': './OntoMapper/instructions.prompt',
                   'dataset': base_path + dataset_folder + '/' + dataset_file,
                   'role': 'You are a powerful ontology engineer that generates RML mappings.'
}

ontology_mapper = LlmOntoMapper(mapper_metadata)

rml_code_str = ontology_mapper.interact(json_data=json_data, ontology=ontology_builder.owl_codeblock)

