from abc import ABC, abstractmethod
from rdflib import Graph, URIRef


class SearchStrategy(ABC):
    @abstractmethod
    def find_entities(self, graph: Graph, target_entity: str) -> list:
        """Find entities in the graph based on a target entity."""
        pass


class ExactMatchSearch(SearchStrategy):
    def find_entities(self, graph: Graph, target_entity: str) -> list:
        """Find entities in the graph that exactly match the target entity."""
        matched_entities = []
        for s, p, o in graph:
            if str(s) == target_entity or str(p) == target_entity or str(o) == target_entity:
                matched_entities.append((s, p, o))
        return matched_entities


class MergeStrategy(ABC):
    @abstractmethod
    def merge_graphs(self, graph: Graph, subpgraph: Graph, merge_point: URIRef) -> None:
        """Find entities in the graph based on a target entity."""
        pass


class MergePointStrategy(MergeStrategy):
    def merge_graphs(self, graph: Graph, subpgraph: Graph, merge_point: URIRef) -> None:
        """
        Merge another RDF graph into the current graph using a specific entity as the merge point.

        Args:
            other_graph (Graph): The other RDF graph to be merged.
            merge_point (URIRef): The entity in the graph that will be the point of merging.
        """
        # Implement merging logic here
        # This is a placeholder implementation and should be replaced with actual logic
        for s, p, o in subpgraph.triples((None, None, None)):
            if s == merge_point or p == merge_point or o == merge_point:
                graph.add((s, p, o))


class RDFGraphManager:
    def __init__(self, graph: Graph, search_strategy: SearchStrategy, merge_strategy: MergeStrategy) -> None:
        """Initialize the RDFGraphManager with an RDF graph and a specific search strategy."""
        self.graph = graph
        self.search_strategy = search_strategy
        self.merge_strategy = merge_strategy

    def find_similar_entities(self, target_entity: str) -> list:
        """Find entities in the graph similar to the target entity using the configured search strategy."""
        return self.search_strategy.find_entities(self.graph, target_entity)

    def merge_knowledgeGraphs(self, other_graph: Graph, merge_point: URIRef) -> None:
        """Find entities in the graph similar to the target entity using the configured search strategy."""
        return self.merge_strategy.merge_graphs(self.graph, other_graph, merge_point)

