from OntoGenix_v_1_0.tools import csv2dataset, dataframe2prettyjson, extract_text, plot_mermaid

dataset_file = 'data'
file = './datasets/' + dataset_file + '.csv'

# get a dataset subsample from a csv file
dataset = csv2dataset(file, max_tokens=200)

# format to json for the LLM and write to a file
file = './datasets/' + dataset_file + '_dataframe_subset.txt'
prompt = dataframe2prettyjson(dataset, file)
print('######## PROMPT ############\n', prompt)

# with open(file, 'r') as file:
#     prompt =  file.read()

# instantiate the LLM that generates an owl ontology from a json subset data
from OntoGenix_v_1_0.OntoBuilder.LLM_ontology import LlmOntology

onto_metadata = {'instructions': './OntoGenix_v_1_0/OntoBuilder/instructions.prompt',
                 'examples': './OntoGenix_v_1_0/OntoBuilder/examples.prompt',
                 'autocompletion': './OntoGenix_v_1_0/OntoBuilder/auto_completion.prompt',
                 'role': 'You are a powerful ontology engineer that generates OWL ontologies in turtle format.'
                 }
ontology_builder = LlmOntology(onto_metadata)

owl_response = ontology_builder.interact(prompt)
print('######## OUTPUT ############\n', owl_response)

aux_owl_response = owl_response[:]
done = False
max_iter = 5
cont = 0
while not done and cont < max_iter:
    try:
        owl_code_str = extract_text(aux_owl_response, "Output Tasks:\n", "FINISH").strip()
        print('################# OWL CODE ####################\n', owl_code_str)
        done = True
    except:
        try:
            aux_owl_response = ontology_builder.interact(owl_response, auto_complete=True)
            print('######## OUTPUT ############\n', aux_owl_response)
        except:
            print('ITERATION: ', cont)
        finally:
            cont += 1

# write the response in a file
file = './datasets/' + dataset_file + '_owl_response.txt'
with open(file, 'w') as f:
    f.write(owl_code_str)

# instantiate the LLM that generates a mermaid class diagram from an owl ontology
from OntoGenix_v_1_0.MermaidOntoFlow.Llm_mermaid import LlmMermaid

mermaid_metadata = {'instructions': './OntoGenix/MermaidOntoFlow/instructions.prompt',
                    'examples': './OntoGenix/MermaidOntoFlow/examples.prompt',
                    'role': 'You are a powerful ontology engineer that translates OWL ontologies in turtle format '
                            'to mermaid diagrams.'
                    }
mermaid = LlmMermaid(mermaid_metadata)

diagram_response = mermaid.interact(owl_response)
print('######## OUTPUT ############\n', diagram_response)

diagram_response_str = extract_text(diagram_response, "Output Tasks:\n", "FINISH").strip()
print('################# OWL CODE ####################\n', diagram_response_str)

# write the response in a file
file = './datasets/' + dataset_file + '_mermaid.txt'
with open(file, 'w') as f:
    f.write(diagram_response_str)

# generate mermaid plot
figure_path = './datasets/' + dataset_file + '_mermaid.png'
plot_mermaid(diagram_response_str, figure_path)
