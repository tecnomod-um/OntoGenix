
def prompt_crafting():
    print('prompt_crafting')

def data_description():
    print('data_description')

def ontology_building():
    print('ontology_building')

def ontology_entity_enrichment(entity: str):
    print('ontology_entity_enrichment: ', entity)

def mapping():
    print('mapping')

tools=[
    {
        "type": "function",
        "function": {
            "name": "prompt_crafting",
            "description": "Helps to craft a prompt.",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "data_description",
            "description": "Generates the high level structure description for the proposed ontology.",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "ontology_building",
            "description": "Define the ontology in turtle format.",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "ontology_entity_enrichment",
            "description": "Define an entity from an ontology in turtle format.",
            "parameters": {
                "type": "object",
                "properties": {
                        "entity": {
                        "type": "string",
                        "description": "The entity from the ontology to be enriched.",
                    }
                },
                "required": ["entity"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "mapping",
            "description": "Define the mapping from a dataset and its ontology in rml format.",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": []
            }
        }
    }
]
