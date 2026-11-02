from functools import lru_cache
from typing import Dict, Hashable, Set

import networkx as nx

from kidneylink.colorful_structures import f


def _has_altruistic_path_of_length(
    graph: nx.DiGraph,
    altruistic_donors: Set[Hashable],
    length: int,
) -> bool:
    """Check for a simple altruistic path of exactly length edges."""

    def search(current, visited, depth):
        if depth == length:
            return True

        for nxt in graph.successors(current):
            if nxt in visited or nxt in altruistic_donors:
                continue

            if search(nxt, visited | {nxt}, depth + 1):
                return True

        return False

    for donor in altruistic_donors:
        if donor in graph and search(donor, {donor}, 0):
            return True

    return False


def _has_cycle_in_length_range(
    graph: nx.DiGraph,
    minimum_length: int,
    maximum_length: int,
) -> bool:
    """Find a simple directed cycle within the specified edge range."""

    pairs = {
        v for v, data in graph.nodes(data=True)
        if data.get("node_type") == "pair"
    }

    def search(start, current, visited, depth):
        # Count the closing edge before checking the cycle length.
        if graph.has_edge(current, start):
            cycle_length = depth + 1

            if minimum_length <= cycle_length <= maximum_length:
                return True

        if depth >= maximum_length:
            return False

        for nxt in graph.successors(current):
            if nxt not in pairs or nxt in visited:
                continue

            if search(start, nxt, visited | {nxt}, depth + 1):
                return True

        return False

    for start in pairs:
        if search(start, start, {start}, 0):
            return True

    return False


def solve_coloring_instance(
    graph: nx.DiGraph,
    altruistic_donors: Set[Hashable],
    coloring: Dict[Hashable, int],
    target: int,
    max_cycle_length: int,
    max_path_length: int,
) -> bool:
    """Solve one fixed-coloring instance."""

    if target <= 0:
        raise ValueError("Target must be positive.")

    if max_cycle_length < 0 or max_path_length < 0:
        raise ValueError("Length limits cannot be negative.")

    number_of_colors = 3 * target
    full_mask = (1 << number_of_colors) - 1

    if set(coloring) != set(graph.nodes):
        raise ValueError("Every graph vertex must have a color.")

    if any(
        not isinstance(color, int)
        or color < 0
        or color >= number_of_colors
        for color in coloring.values()
    ):
        raise ValueError("Color outside the permitted range.")

    # Special case 1: long altruistic path.
    if max_path_length >= target:
        if _has_altruistic_path_of_length(
            graph, altruistic_donors, target
        ):
            return True

    # Special case 2: long exchange cycle.
    if max_cycle_length >= target:
        if _has_cycle_in_length_range(
            graph, target, max_cycle_length
        ):
            return True

    # Apply the reduced limits only after special cases.
    reduced_path_length = min(max_path_length, target - 1)
    reduced_cycle_length = min(max_cycle_length, target - 1)

    def mask_to_colors(mask):
        return {
            c for c in range(number_of_colors)
            if mask & (1 << c)
        }

    @lru_cache(maxsize=None)
    def f_cached(color_mask, patients):
        return f(
            graph=graph,
            altruistic_donors=altruistic_donors,
            coloring=coloring,
            required_colors=mask_to_colors(color_mask),
            patient_count=patients,
            max_cycle_length=reduced_cycle_length,
            max_path_length=reduced_path_length,
        )

    @lru_cache(maxsize=None)
    def D(color_mask, patients):
        if patients == 0:
            return True

        if color_mask == 0 or patients < 0:
            return False

        submask = color_mask

        while submask:
            for i in range(1, patients + 1):
                if f_cached(submask, i):
                    remaining = color_mask ^ submask

                    if D(remaining, patients - i):
                        return True

            submask = (submask - 1) & color_mask

        return False

    for patients in range(target, 2 * target + 1):
        if D(full_mask, patients):
            return True

    return False
