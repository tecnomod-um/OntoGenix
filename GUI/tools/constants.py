"""
    Constants file
"""
import os

OS_SEPARATOR:str = os.path.altsep if (os.path.altsep is not None) else os.path.sep # "/"
ACK_MAPPING_FORMAT:set[str] = frozenset(["ttl", "yarrrml"]) # "yml", "yaml", 
ACK_ONTOLOGY_FORMAT:set[str] = frozenset(["ttl"])
ACK_API_MODELS:set[str] = frozenset(['gpt-3.5-turbo', 'gpt-4-1106-preview', 'gpt-4o-2024-05-13'])
