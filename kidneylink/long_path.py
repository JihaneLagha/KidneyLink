import networkx as nx
from typing import Hashable, Set


def find_altruistic_path(
    graph: nx.DiGraph,
    altruistic_donors: Set[Hashable],
    target: int,
) -> bool:
    """
    Detect a simple altruistic path covering at least
    target patient-donor pairs.

    This initial implementation is exhaustive and is intended
    as a correctness reference, not an FPT implementation.
    """

    if target <= 0:
        raise ValueError("Target must be positive.")

    if not altruistic_donors.issubset(graph.nodes):
        raise ValueError("Unknown altruistic donor.")

    def search(current, visited, patients):
        if patients >= target:
            return True

        for nxt in graph.successors(current):
            if nxt in visited:
                continue

            if nxt in altruistic_donors:
                continue

            if graph.nodes[nxt].get("node_type") != "pair":
                continue

            if search(
                nxt,
                visited | {nxt},
                patients + 1,
            ):
                return True

        return False

    for donor in altruistic_donors:
        if search(donor, {donor}, 0):
            return True

    return False
