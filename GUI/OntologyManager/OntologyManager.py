from abc import ABC, abstractmethod
from typing import Dict, Optional
from rdflib import Graph, URIRef
import re
from PyQt5.QtWidgets import QTextEdit # pylint: disable = no-name-in-module


class RDFGraphFactory(ABC):
    @abstractmethod
    def create_graph(self) -> Graph:
        """Create and return a new RDF Graph."""
        pass


class TurtleGraphFactory(RDFGraphFactory):
    def create_graph(self) -> Graph:
        """Create and return a new RDF Graph."""
        return Graph()


class OntologyManager(QTextEdit):
    def __init__(self, parent=None) -> None:
        """Initialize the OntologyManager with a specific RDFGraphFactory."""
        super().__init__(parent)
        # Initialize graph
        graph_factory = TurtleGraphFactory()
        self.graph = graph_factory.create_graph()
        print('Inicializando OntoGenix...')

    def load_ontology(self, file_path: str, format: str = 'turtle') -> None:
        """Load an ontology from a file into the graph."""
        self.graph.parse(file_path, format=format)

    def save_ontology(self, file_path: str, format: str = 'turtle') -> None:
        """Save the current graph (ontology) to a file."""
        self.graph.serialize(destination=file_path, format=format)

    def get_graph(self) -> Graph:
        """Return the current RDF graph instance."""
        return self.graph

    def update_text(self):
        try:
            self.text_to_graph(self.toPlainText(), 'turtle')  # Update the graph
            print("Graph updated successfully.")
        except Exception as e:
            print(f"Error updating graph from text: {e}")

    def graph_to_text(self, extension: str = 'turtle') -> str:
        """Convert the RDF graph to a text representation.

        Args:
            extension (str): The format for serialization (e.g., 'turtle', 'xml', 'nt', ...).

        Returns:
            str: The text representation of the RDF graph.
        """
        return self.graph.serialize(format=extension)

    def text_to_graph(self, text: str, extension: str = 'turtle') -> None:
        """Update the RDF graph with the contents of the text.

        Args:
            text (str): The text representation of an RDF graph.
            extension (str): The format of the text (e.g., 'turtle', 'xml', 'nt', ...).
        """
        try:
            self.graph.parse(data=text, format=extension)
            print(self.graph)
        except SyntaxError as se:
            # TODO: pass error to LLM_ontology.py
            print(f"{se}")
            raise SyntaxError(se)
        except Exception as e:
            print(f"Error parsing graph from text: {e}")

    def entity_update(self, entity: str) -> None:
        """Update the ontology with a new entity definition.

        Args:
            entity (str): Turtle formatted string containing the new entity definition.
        """
        if not self.graph:
            print("Graph not loaded.")
            return

        prefixes = self._get_graph_prefixes()
        uri_entity = self._extract_uri_entity(entity, prefixes)

        if uri_entity:
            ref_entity = URIRef(uri_entity)
            entity = self._prepare_new_definition(entity, prefixes)

            try:
                # Removing the empty triplets ensures less errors in the next step. # noqa
                for s, p, o in self.graph.triples((ref_entity, None, None)): # pylint: disable = not-an-iterable
                    self.graph.remove((s, p, o))
                # Parsing the graph in .ttl format
                self.graph.parse(data=entity, format='turtle')
            except Exception as e:
                print(f"Error updating ontology: {e}")
        else:
            print("The URI entity could not be determined from the new definition.")

    def _get_graph_prefixes(self) -> Dict[str, str]:
        """Extract prefixes and their URIs from the graph.

        Returns:
            Dict[str, str]: A dictionary of prefixes and their corresponding URIs.
        """
        return {prefix: str(uri) for prefix, uri in self.graph.namespace_manager.namespaces()}

    @staticmethod
    def _prepare_new_definition(new_entity: str, prefixes: Dict[str, str]) -> str:
        """Prepare the new definition by appending existing prefixes to it.

        Args:
            new_entity (str): The new entity definition.
            prefixes (Dict[str, str]): Existing prefixes in the graph.

        Returns:
            str: The new definition with prefixes appended.
        """
        prefix_str = '\n'.join([f"@prefix {prefix}: <{uri}> ." for prefix, uri in prefixes.items()])
        return prefix_str + '\n\n' + new_entity

    @staticmethod
    def _extract_uri_entity(new_entity: str, prefixes: Dict[str, str]) -> Optional[URIRef]:
        """Extract the URI of the entity from the new definition.

        Args:
            new_entity (str): The new entity definition.
            prefixes (Dict[str, str]): Existing prefixes in the graph.

        Returns:
            Optional[URIRef]: The URIRef of the entity, if found.
        """
        # First, try to match the pattern with 'a'
        match = re.search(r'(\:\w+)\s+a', new_entity)

        # If no match, try to match the pattern with 'rdf:type'
        if not match:
            match = re.search(r'(\:\w+)\s+rdf:type', new_entity)

        if match:
            entity = match.group(1)
            for prefix, uri in prefixes.items():
                if entity.startswith(f":{prefix}"):
                    return URIRef(uri + entity[len(prefix) + 1:])
            return URIRef(entity)
        return None
