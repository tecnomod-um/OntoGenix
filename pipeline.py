from OntoGenix_v_1_2.tools import csv2dataset, dataframe2prettyjson, plot_mermaid, extract_text

base_path = './datasets/'
dataset_folder = 'AirlinesCustomerSatisfaction'
dataset_file = 'AirlinesCustomerSatisfaction'
file = base_path + dataset_folder + '/' + dataset_file + '.csv'

# get a dataset subsample from a csv file
dataset = csv2dataset(file, max_tokens=800)

# format to json for the LLM and write to a file
file = base_path + dataset_folder + '/' + dataset_file + '_dataframe_subset.txt'
json_data = dataframe2prettyjson(dataset, file)
print('######## PROMPT ############\n', json_data)


# instantiate the LLM that generates an owl ontology from a json subset data
from OntoGenix_v_1_2.PlanSage.LLM_planner import LlmPlanner

planner_metadata = {
    'first_instructions': './OntoGenix_v_1_2/PlanSage/first_instructions.prompt',
    'interaction': './OntoGenix_v_1_2/PlanSage/interaction.prompt',
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

# instantiate the LLM that generates an owl ontology from a json subset data
from OntoGenix_v_1_2.OntoBuilder.LLM_ontology import LlmOntology

onto_metadata = {'instructions': './OntoGenix_v_1_2/OntoBuilder/instructions.prompt',
                 'autocompletion':  './OntoGenix_v_1_2/OntoBuilder/auto_completion.prompt',
                 'ontology_analysis': './OntoGenix_v_1_2/OntoBuilder/ontology_analysis.prompt',
                 'ontology_synthesis': './OntoGenix_v_1_2/OntoBuilder/ontology_synthesis.prompt',
                 'examples': './OntoGenix_v_1_2/OntoBuilder/examples/',
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


from OntoGenix_v_1_2.OntoMapper.LLM_ontomapper import LlmOntoMapper

mapper_metadata = {'instructions': './OntoGenix_v_1_2/OntoMapper/instructions.prompt',
                   'dataset': base_path + dataset_folder + '/' + dataset_file,
                   'role': 'You are a powerful ontology engineer that generates RML mappings.'
}

ontology_mapper = LlmOntoMapper(mapper_metadata)

rml_code_str = ontology_mapper.interact(json_data=json_data, ontology=ontology_builder.owl_codeblock)






#
#
# # instantiate the LLM that generates a mermaid class diagram from an owl ontology
# from OntoGenix_v_1_2.MermaidOntoFlow.Llm_mermaid import LlmMermaid
#
# mermaid_metadata = {'instructions': './OntoGenix_v_1_2/MermaidOntoFlow/instructions.prompt',
#                     'examples': './OntoGenix_v_1_2/MermaidOntoFlow/examples.prompt',
#                     'role': 'You are a powerful ontology engineer that translates OWL ontologies in turtle format '
#                             'to mermaid diagrams.'
#                     }
# mermaid = LlmMermaid(mermaid_metadata)
#
# diagram_response = mermaid.interact(owl_codeblock)
# print('######## OUTPUT ############\n', diagram_response)
#
# diagram_response_str = extract_text(diagram_response, "Output Tasks:\n", "Finish Statement: FINISH").strip()
# print('################# OWL CODE ####################\n', diagram_response_str)
#
# # write the response in a file
# file = './datasets/' + dataset_file + '_mermaid.txt'
# with open(file, 'w') as f:
#     f.write(diagram_response_str)
#
# # generate mermaid plot
# figure_path = './datasets/' + dataset_file + '_mermaid.png'
# plot_mermaid(diagram_response_str, figure_path)
