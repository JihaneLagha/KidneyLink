from dataclasses import dataclass, field
import networkx as nx


@dataclass
class KidneyExchangeGraph:
    """Directed compatibility graph for kidney exchange."""

    graph: nx.DiGraph = field(default_factory=nx.DiGraph)
    altruistic_donors: set = field(default_factory=set)

    def add_pair(self, pair_id: str):
        if not pair_id:
            raise ValueError("Pair ID cannot be empty.")
        if pair_id in self.graph:
            raise ValueError(f"Vertex already exists: {pair_id}")

        self.graph.add_node(pair_id, node_type="pair")

    def add_altruistic_donor(self, donor_id: str):
        if not donor_id:
            raise ValueError("Donor ID cannot be empty.")
        if donor_id in self.graph:
            raise ValueError(f"Vertex already exists: {donor_id}")

        self.graph.add_node(donor_id, node_type="altruistic")
        self.altruistic_donors.add(donor_id)

    def add_compatibility(self, donor_vertex: str, recipient_pair: str):
        if donor_vertex not in self.graph:
            raise ValueError(f"Unknown donor vertex: {donor_vertex}")

        if recipient_pair not in self.graph:
            raise ValueError(f"Unknown recipient pair: {recipient_pair}")

        if recipient_pair in self.altruistic_donors:
            raise ValueError("Altruistic donors cannot be recipients.")

        if donor_vertex == recipient_pair:
            raise ValueError("Self-loops are not allowed.")

        self.graph.add_edge(donor_vertex, recipient_pair)

    def validate(self):
        if not nx.is_directed_acyclic_graph(self.graph):
            # Directed cycles are valid in kidney exchange.
            pass

        for node in self.graph.nodes:
            if node in self.altruistic_donors:
                if self.graph.in_degree(node) != 0:
                    raise ValueError(
                        f"Altruistic donor {node} must have no incoming edges."
                    )

        for u, v in self.graph.edges:
            if u == v:
                raise ValueError("Self-loops are not allowed.")

        return True

    @property
    def number_of_vertices(self):
        return self.graph.number_of_nodes()

    @property
    def number_of_edges(self):
        return self.graph.number_of_edges()

    @property
    def patient_pairs(self):
        return {
            node for node, data in self.graph.nodes(data=True)
            if data["node_type"] == "pair"
        }

    def summary(self):
        return {
            "vertices": self.number_of_vertices,
            "compatibility_edges": self.number_of_edges,
            "patient_donor_pairs": len(self.patient_pairs),
            "altruistic_donors": len(self.altruistic_donors),
        }
