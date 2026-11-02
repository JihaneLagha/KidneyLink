from dataclasses import dataclass
from typing import Hashable, List, Set, Tuple

import networkx as nx


@dataclass(frozen=True)
class ExchangeStructure:
    """One feasible kidney exchange."""

    structure_type: str
    vertices: Tuple[Hashable, ...]

    @property
    def patient_count(self) -> int:
        return len(self.vertices) - (
            1 if self.structure_type == "path" else 0
        )


@dataclass
class ExactSolution:
    """Optimal solution returned by the exhaustive solver."""

    maximum_patients: int
    structures: List[ExchangeStructure]

    @property
    def feasible(self) -> bool:
        return self.maximum_patients > 0


def enumerate_cycles(
    graph: nx.DiGraph,
    max_cycle_length: int,
) -> List[ExchangeStructure]:
    """Enumerate all feasible directed exchange cycles."""

    if max_cycle_length < 2:
        return []

    structures = []

    for cycle in nx.simple_cycles(graph):
        if len(cycle) < 2 or len(cycle) > max_cycle_length:
            continue

        if not all(
            graph.nodes[v].get("node_type") == "pair"
            for v in cycle
        ):
            continue

        structures.append(
            ExchangeStructure("cycle", tuple(cycle))
        )

    return structures


def enumerate_altruistic_paths(
    graph: nx.DiGraph,
    altruistic_donors: Set[Hashable],
    max_path_length: int,
) -> List[ExchangeStructure]:
    """
    Enumerate all simple altruistic paths.

    Path length is measured in edges.
    The starting altruistic donor is not counted as a patient.
    """

    if max_path_length < 1:
        return []

    structures = []

    def search(current, path, visited, depth):
        if depth > 0:
            structures.append(
                ExchangeStructure("path", tuple(path))
            )

        if depth >= max_path_length:
            return

        for nxt in graph.successors(current):
            if nxt in visited:
                continue

            if nxt in altruistic_donors:
                continue

            if graph.nodes[nxt].get("node_type") != "pair":
                continue

            search(
                nxt,
                path + [nxt],
                visited | {nxt},
                depth + 1,
            )

    for donor in altruistic_donors:
        if donor not in graph:
            continue

        search(donor, [donor], {donor}, 0)

    return structures


def solve_exact(
    graph: nx.DiGraph,
    altruistic_donors: Set[Hashable],
    max_cycle_length: int,
    max_path_length: int,
) -> ExactSolution:
    """
    Find the maximum number of patients covered by
    vertex-disjoint feasible cycles and altruistic paths.

    This is an exhaustive exact solver intended for
    small validation instances, not large production graphs.
    """

    if max_cycle_length < 0 or max_path_length < 0:
        raise ValueError("Length limits cannot be negative.")

    if not altruistic_donors.issubset(graph.nodes):
        raise ValueError("Unknown altruistic donor.")

    cycles = enumerate_cycles(graph, max_cycle_length)

    paths = enumerate_altruistic_paths(
        graph,
        altruistic_donors,
        max_path_length,
    )

    candidates = cycles + paths

    # Try larger exchanges first to obtain a useful
    # incumbent solution early.
    candidates.sort(
        key=lambda s: s.patient_count,
        reverse=True,
    )

    best_count = 0
    best_structures = []

    def search(index, used_vertices, patient_count, chosen):
        nonlocal best_count, best_structures

        if patient_count > best_count:
            best_count = patient_count
            best_structures = chosen.copy()

        if index >= len(candidates):
            return

        # No solution can cover more than all remaining pairs.
        remaining_pairs = sum(
            1 for v, data in graph.nodes(data=True)
            if data.get("node_type") == "pair"
            and v not in used_vertices
        )

        if patient_count + remaining_pairs <= best_count:
            return

        structure = candidates[index]
        vertices = set(structure.vertices)

        # Include this structure if it is vertex-disjoint.
        if not vertices.intersection(used_vertices):
            search(
                index + 1,
                used_vertices | vertices,
                patient_count + structure.patient_count,
                chosen + [structure],
            )

        # Or exclude it.
        search(
            index + 1,
            used_vertices,
            patient_count,
            chosen,
        )

    search(0, set(), 0, [])

    return ExactSolution(
        maximum_patients=best_count,
        structures=best_structures,
    )
