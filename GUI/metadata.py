import configparser
import os


class MetadataManager:

    base_path = None
    dataset_folder = None
    dataset_file = None

    planner_metadata = {
        'instructions': './PlanSage/instructions.prompt',
        'dataset': None,
        'role': 'You are a powerful ontology engineer that generates the reasoning steps needed to generate'
                'the context needed to create an ontology from a json data table.',
        'model': 'gpt-4'#'gpt-3.5-turbo'
    }

    onto_metadata = {
        'instructions': './OntoBuilder/instructions.prompt',
        'entity_improvement': './OntoBuilder/entity_improvement.prompt',
        'dataset': None,
        'role': 'You are a powerful ontology engineer that generates OWL ontologies in RDF/XML format.',
        'model': 'gpt-4'#'gpt-3.5-turbo'
    }

    mapper_metadata = {
        'instructions': './OntoMapper/instructions.prompt',
        'dataset': None,
        'role': 'You are a powerful ontology engineer that generates RML mappings.',
        'model': 'gpt-4'#'gpt-3.5-turbo'
    }

    mermaid_metadata = {
        'instructions': './MermaidOntoFlow/instructions.prompt',
        'examples': './MermaidOntoFlow/examples.prompt',
        'role': 'You are a mermaid diagramming engineer that generates class Diagrams.',
        'model': 'gpt-3.5-turbo'
    }

    def construct_path(self, *args) -> str:
        return os.path.join(*args)

    def parse_datasetPath(self, given_path: str):
        # Get the relative path from the specified directory
        relative_path = os.path.relpath(given_path, os.getcwd())
        # Now split the relative path into its components
        path_parts = relative_path.split(os.sep)
        # Construct the desired outputs
        self.base_path = os.path.join('.', path_parts[0], '')  # Adding a trailing slash
        self.dataset_folder = path_parts[1]
        self.dataset_file = os.path.splitext(path_parts[2])[0]  # Removing the file extension
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





