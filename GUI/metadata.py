import configparser
import os

from GUI.GuiManager.tools_definition import tools, available_functions

class MetadataManager:

    base_path = None
    dataset_folder = None
    dataset_file = None
    api_key_path = "./GUI/.env"

    genie_metadata = {
        'role': "you are a powerful ontology engineer that must select the appropriate function to be called.",
        'instructions': "./testing/gui_manager_role.prompt",
        'model': 'gpt-4-1106-preview',
        'api_key_path': "./GUI/.env",
        'available_functions': available_functions,
        'tools': tools
    }

    crafter_metadata =  {
        'prompt_crafting': './GUI/PromptCrafter/prompt_crafting.prompt',
        'role': 'You are a powerful ontology engineer that helps to craft the perfect prompt to define the high level structure of the ontology.',
        'model': 'gpt-4-1106-preview', #'gpt-3.5-turbo'
        'api_key_path':api_key_path
    }

    planner_metadata = {
        'instructions': './GUI/PlanSage/instructions.prompt',
        'data_description': './GUI/PlanSage/data_description.prompt',
        'dataset': None,
        'role': 'You are a powerful ontology engineer that generates the reasoning steps needed to generate'
                'the context needed to create an ontology from a json data table.',
        'model': 'gpt-4-1106-preview', #'gpt-3.5-turbo'
        'api_key_path':api_key_path
    }

    onto_metadata = {
        'ontology_instructions': './GUI/OntoBuilder/ontology_instructions.prompt',
        'entity_improvement': './GUI/OntoBuilder/entity_improvement.prompt',
        'dataset': None,
        'role': 'You are a powerful ontology engineer that generates OWL ontologies in RDF/XML format.',
        'model': 'gpt-4-1106-preview', #'gpt-3.5-turbo'
        'api_key_path':api_key_path
    }

    mapper_metadata = {
        'instructions': './GUI/OntoMapper/instructions.prompt',
        'error_instructions': './GUI/OntoMapper/error_instructions.prompt',
        'dataset': None,
        'role': 'You are a powerful ontology engineer that generates RML mappings.',
        'model': 'gpt-4-1106-preview', #'gpt-3.5-turbo'
        'api_key_path':api_key_path
    }

    mermaid_metadata = {
        'instructions': './GUI/MermaidOntoFlow/instructions.prompt',
        'examples': './GUI/MermaidOntoFlow/examples.prompt',
        'role': 'You are a mermaid diagramming engineer that generates class Diagrams.',
        'model': 'gpt-4-1106-preview',
        'api_key_path':api_key_path
    }

    def construct_path(self, *args) -> str:
        return os.path.join(*args)

    def parse_datasetPath(self, given_path: str):
        # Get the relative path from the specified directory
        relative_path = os.path.relpath(given_path, os.getcwd())

        # Now split the relative path into its components
        path_parts = relative_path.split(os.sep)

        # Handle the base path
        if len(path_parts) > 2:
            self.base_path = os.path.join('.', *path_parts[:-2])
        else:
            self.base_path = "./"

        # Handle the dataset folder
        if len(path_parts) > 2:
            self.dataset_folder = path_parts[-2]
        else:
            self.dataset_folder = ""

        # Handle the dataset file
        self.dataset_file = os.path.splitext(path_parts[-1])[0]  # Removing the file extension

        # Output
        print(f'base_path : "{self.base_path}"')
        print(f'dataset_folder : "{self.dataset_folder}"')
        print(f'dataset_file : "{self.dataset_file}"')

    def dataset_full_path(self) -> str:
        return self.construct_path(self.base_path, self.dataset_folder, f'{self.dataset_file}.csv')

    def dataset_base_path(self) -> str:
        return self.construct_path(self.base_path, self.dataset_folder, self.dataset_file+'/')

    def create_config4morph(self):
        config = configparser.ConfigParser()
        mappings_path = self.construct_path(self.base_path, self.dataset_folder, f'{self.dataset_file}_rml_mapping_LLM.csv.ttl')
        config['DataSourceCSV'] = {
            'mappings': mappings_path,
            'file_path': self.dataset_full_path()
        }
        config_path = self.construct_path(self.base_path, self.dataset_folder, 'config.ini')
        with open(config_path, 'w') as configfile:
            config.write(configfile)





