import math
import random
from typing import Optional

import networkx as nx

from kidneylink.k_path import has_directed_k_path


def _poly_partition_check(
    graph: nx.DiGraph,
    k: int,
    left: set,
    right: set,
) -> bool:
    """
    Zehavi's polynomial-time PolyAlg for one partition.

    Finds a shortest k-vertex path inside L, then
    searches for a return path avoiding its internal
    vertices.
    """

    for start in left:
        for end in left:

            if start == end:
                continue

            # Find a shortest path from start to end in G[L].
            try:
                path = nx.shortest_path(
                    graph.subgraph(left),
                    source=start,
                    target=end,
                )
            except (nx.NetworkXNoPath, nx.NodeNotFound):
                continue

            # The shortest path must contain exactly k vertices.
            if len(path) != k:
                continue

            # Retain the two endpoints, but remove internal vertices.
            internal_vertices = set(path[1:-1])

            remaining_vertices = set(graph.nodes) - internal_vertices

            remaining_graph = graph.subgraph(remaining_vertices)

            # Find a return path from end to start.
            try:
                nx.shortest_path(
                    remaining_graph,
                    source=end,
                    target=start,
                )
                return True
            except (nx.NetworkXNoPath, nx.NodeNotFound):
                continue

    return False


def find_long_directed_cycle(
    graph: nx.DiGraph,
    k: int,
    path_repetitions: int = 100,
    partition_repetitions: Optional[int] = None,
    seed: int = 42,
) -> bool:
    """
    Randomized FPT algorithm for Long Directed Cycle,
    based on Zehavi (2016).

    Returns True if a directed simple cycle containing
    at least k vertices is found.

    A negative result after finite random repetitions
    is probabilistic, not an absolute proof of absence.
    """

    if k < 2:
        raise ValueError("k must be at least 2.")

    if path_repetitions <= 0:
        raise ValueError("path_repetitions must be positive.")

    if partition_repetitions is not None:
        if partition_repetitions <= 0:
            raise ValueError(
                "partition_repetitions must be positive."
            )

    if graph.number_of_nodes() < k:
        return False

    rng = random.Random(seed)

    # Phase 1:
    # Check cycles containing between k and 2k vertices.
    #
    # An edge (u, v), combined with a simple path
    # from v to u, forms a directed cycle.

    attempt_seed = seed

    for length in range(k, 2 * k + 1):

        for u, v in graph.edges:

            found = has_directed_k_path(
                graph=graph,
                start=v,
                end=u,
                k=length,
                repetitions=path_repetitions,
                seed=attempt_seed,
            )

            attempt_seed += 1

            if found:
                return True

    # Phase 2:
    # Search for cycles longer than 2k using
    # randomized vertex partitions and PolyAlg.

    if partition_repetitions is None:
        partition_repetitions = 10 * (4 ** k)

    for _ in range(partition_repetitions):

        left = set()
        right = set()

        for vertex in graph.nodes:
            if rng.random() < 0.5:
                left.add(vertex)
            else:
                right.add(vertex)

        if _poly_partition_check(
            graph,
            k,
            left,
            right,
        ):
            return True

    return False
