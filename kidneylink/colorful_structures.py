from typing import Dict, Hashable, Set

import networkx as nx


def has_colorful_cycle(
    graph: nx.DiGraph,
    coloring: Dict[Hashable, int],
    required_colors: Set[int],
    max_cycle_length: int,
) -> bool:
    """
    Determine whether the graph contains a colorful
    directed cycle using exactly required_colors.

    Every vertex in an exchange cycle must be a patient pair.
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
    full_mask = sum(1 << c for c in required_colors)

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
            if mask == full_mask and graph.has_edge(last, start):
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
    Determine whether the graph contains a colorful
    altruistic path covering exactly patient_count patients.

    The starting altruistic donor is not counted as a patient.
    Every subsequent vertex must be a patient-donor pair.
    """

    if patient_count < 1 or patient_count > max_path_length:
        return False

    if len(required_colors) != patient_count + 1:
        return False

    donors = set(altruistic_donors)

    # Validate donor vertices.
    for donor in donors:
        if donor not in graph:
            raise ValueError(f"Unknown altruistic donor: {donor}")

        if graph.nodes[donor].get("node_type") != "altruistic":
            raise ValueError(f"Invalid altruistic donor: {donor}")

    # Only patient-donor pairs can follow an altruistic donor.
    allowed_pairs = {
        v for v, data in graph.nodes(data=True)
        if data.get("node_type") == "pair"
        and coloring[v] in required_colors
    }

    full_mask = sum(1 << c for c in required_colors)

    for donor in donors:

        if coloring[donor] not in required_colors:
            continue

        initial_mask = 1 << coloring[donor]

        states = {(initial_mask, donor)}

        for _ in range(patient_count):

            next_states = set()

            for mask, last in states:

                for nxt in graph.successors(last):

                    # Reject altruistic and unknown vertex types.
                    if nxt not in allowed_pairs:
                        continue

                    bit = 1 << coloring[nxt]

                    # A colorful path cannot repeat a color.
                    if mask & bit:
                        continue

                    next_states.add((mask | bit, nxt))

            states = next_states

            if not states:
                break

        if any(
            mask == full_mask
            for mask, _ in states
        ):
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
