available_functions = {
    "prompt_crafting": None,
    "data_description": None,
    "ontology_building": None,
    "ontology_entity_enrichment": None,
    "mapping": None
}


tools=[
    {
        "type": "function",
        "function": {
            "name": "prompt_crafting",
            "description": "Helps to craft a prompt.",
            "parameters": {
                "type": "object",
                "properties": {
                    "prompt": {
                        "type": "string",
                        "description": "The user query.",
                    }
                },
                "required": ["prompt"]
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
                "properties": {
                    "prompt": {
                        "type": "string",
                        "description": "The user query.",
                    }
                },
                "required": ["prompt"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "ontology_building",
            "description": "Define the ontology in turtle format.",
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
                    "prompt": {
                        "type": "string",
                        "description": "The user query.",
                    },
                    "entity": {
                        "type": "string",
                        "description": "The entity to be enriched.",
                    }
                },
                "required": ["prompt", "entity"]
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
                "properties": {
                    "prompt": {
                        "type": "string",
                        "description": "The user query.",
                    }
                },
                "required": ["prompt"]
            }
        }
    }
]
