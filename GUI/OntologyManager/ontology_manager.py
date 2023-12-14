from rdflib import Graph, URIRef, Namespace
import rdflib
import re
from typing import Dict, Optional

class OntologyManager:
    """Class to manage ontology operations such as loading, saving, and updating an RDF graph.

    Attributes:
        file_path (str): Path to the ontology file.
        graph (Graph): Graph object representing the ontology.
    """

    def __init__(self, file_path: str):
        """Initialize the OntologyManager with a file path."""
        self.file_path = file_path
        self.graph: Optional[Graph] = None

    def load(self, file_path: str) -> None:
        """Load an ontology from a file into the graph.

        Args:
            file_path (str): Path to the file containing the ontology.
        """
        self.graph = Graph()
        self.graph.parse(file_path, format='turtle')

    def save(self, file_path: str) -> None:
        """Save the current graph (ontology) to a file.

        Args:
            file_path (str): Path where the ontology will be saved.
        """
        if self.graph:
            self.graph.serialize(destination=file_path, format='turtle')

    def update(self, new_entity_definition: str) -> None:
        """Update the ontology with a new entity definition.

        Args:
            new_entity_definition (str): Turtle formatted string containing the new entity definition.
        """
        if not self.graph:
            print("Graph not loaded.")
            return

        prefixes = self._get_graph_prefixes(self.graph)
        uri_entity = self._extract_uri_entity(new_entity_definition, prefixes)

        if uri_entity:
            ref_entity = URIRef(uri_entity)
            new_entity_definition = self._prepare_new_definition(new_entity_definition, prefixes)

            for s, p, o in self.graph.triples((ref_entity, None, None)):
                self.graph.remove((s, p, o))

            try:
                self.graph.parse(data=new_entity_definition, format='turtle')
            except Exception as e:
                print(f"Error updating ontology: {e}")
        else:
            print("No se pudo determinar la entidad URI a partir de la nueva definición.")

    @staticmethod
    def _get_graph_prefixes(grafo: Graph) -> Dict[str, str]:
        """Extract prefixes and their URIs from the graph.

        Args:
            grafo (Graph): The RDF graph.

        Returns:
            Dict[str, str]: A dictionary of prefixes and their corresponding URIs.
        """
        return {prefix: str(uri) for prefix, uri in grafo.namespace_manager.namespaces()}

    @staticmethod
    def _prepare_new_definition(nueva_definicion: str, prefijos_existentes: Dict[str, str]) -> str:
        """Prepare the new definition by appending existing prefixes to it.

        Args:
            nueva_definicion (str): The new entity definition.
            prefijos_existentes (Dict[str, str]): Existing prefixes in the graph.

        Returns:
            str: The new definition with prefixes appended.
        """
        prefijos_str = '\n'.join([f"@prefix {prefix}: <{uri}> ." for prefix, uri in prefijos_existentes.items()])
        return prefijos_str + '\n\n' + nueva_definicion

    @staticmethod
    def _extract_uri_entity(nueva_definicion: str, prefijos_existentes: Dict[str, str]) -> Optional[URIRef]:
        """Extract the URI of the entity from the new definition.

        Args:
            nueva_definicion (str): The new entity definition.
            prefijos_existentes (Dict[str, str]): Existing prefixes in the graph.

        Returns:
            Optional[URIRef]: The URIRef of the entity, if found.
        """
        match = re.search(r'(\:\w+)\s+a', nueva_definicion)
        if match:
            entidad = match.group(1)
            for prefijo, uri in prefijos_existentes.items():
                if entidad.startswith(f":{prefijo}"):
                    return URIRef(uri + entidad[len(prefijo)+1:])
            return URIRef(entidad)
        return None
