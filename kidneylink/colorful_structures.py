from typing import Dict, Hashable, Set

import networkx as nx


def has_colorful_cycle(
    graph: nx.DiGraph,
    coloring: Dict[Hashable, int],
    required_colors: Set[int],
    max_cycle_length: int,
) -> bool:
    """
    Determine whether an induced color subgraph contains
    a colorful directed cycle using exactly required_colors.
    """

    k = len(required_colors)

    if k < 2 or k > max_cycle_length:
        return False

    pairs = [
        v for v, data in graph.nodes(data=True)
        if data.get("node_type") == "pair"
        and coloring[v] in required_colors
    ]

    allowed = set(pairs)

    for start in pairs:
        start_color = coloring[start]
        initial_mask = 1 << start_color

        states = {(initial_mask, start)}

        for _ in range(k - 1):
            next_states = set()

            for mask, last in states:
                for nxt in graph.successors(last):
                    if nxt not in allowed:
                        continue

                    bit = 1 << coloring[nxt]

                    if mask & bit:
                        continue

                    next_states.add((mask | bit, nxt))

            states = next_states

            if not states:
                break

        for mask, last in states:
            if mask == sum(1 << c for c in required_colors):
                if graph.has_edge(last, start):
                    return True

    return False


def has_colorful_altruistic_path(
    graph: nx.DiGraph,
    altruistic_donors: Set[Hashable],
    coloring: Dict[Hashable, int],
    required_colors: Set[int],
    patient_count: int,
    max_path_length: int,
) -> bool:
    """
    Determine whether an induced color subgraph contains
    an altruistic path covering exactly patient_count patients.
    """

    if patient_count < 1 or patient_count > max_path_length:
        return False

    if len(required_colors) != patient_count + 1:
        return False

    allowed = {
        v for v in graph.nodes
        if coloring[v] in required_colors
    }

    full_mask = sum(1 << c for c in required_colors)

    for donor in altruistic_donors:
        if donor not in allowed:
            continue

        initial_mask = 1 << coloring[donor]
        states = {(initial_mask, donor)}

        for _ in range(patient_count):
            next_states = set()

            for mask, last in states:
                for nxt in graph.successors(last):

                    if nxt not in allowed:
                        continue

                    if nxt in altruistic_donors:
                        continue

                    bit = 1 << coloring[nxt]

                    if mask & bit:
                        continue

                    next_states.add((mask | bit, nxt))

            states = next_states

            if not states:
                break

        if any(mask == full_mask for mask, _ in states):
            return True

    return False


def f(
    graph: nx.DiGraph,
    altruistic_donors: Set[Hashable],
    coloring: Dict[Hashable, int],
    required_colors: Set[int],
    patient_count: int,
    max_cycle_length: int,
    max_path_length: int,
) -> bool:
    """
    Paper's f(C', i) existence predicate.
    """

    if len(required_colors) == patient_count:
        if has_colorful_cycle(
            graph,
            coloring,
            required_colors,
            max_cycle_length,
        ):
            return True

    if len(required_colors) == patient_count + 1:
        if has_colorful_altruistic_path(
            graph,
            altruistic_donors,
            coloring,
            required_colors,
            patient_count,
            max_path_length,
        ):
            return True

    return False
