import random
from typing import Hashable

import networkx as nx


def has_directed_k_path(
    graph: nx.DiGraph,
    start: Hashable,
    end: Hashable,
    k: int,
    repetitions: int = 100,
    seed: int = 42,
) -> bool:
    """
    Randomized color-coding algorithm for finding a
    simple directed path containing exactly k vertices
    from start to end.

    A negative result after finite repetitions is
    probabilistic, not a proof of non-existence.
    """

    if k <= 0:
        raise ValueError("k must be positive.")

    if repetitions <= 0:
        raise ValueError("Repetitions must be positive.")

    if start not in graph or end not in graph:
        raise ValueError("Start and end must exist in the graph.")

    if k > graph.number_of_nodes():
        return False

    if k == 1:
        return start == end

    if start == end:
        return False

    rng = random.Random(seed)
    vertices = list(graph.nodes)

    for _ in range(repetitions):

        coloring = {
            v: rng.randrange(k)
            for v in vertices
        }

        # Each state stores endpoints reachable using
        # exactly the colors represented by its mask.
        dp = {}

        initial_mask = 1 << coloring[start]
        dp[initial_mask] = {start}

        for size in range(1, k):

            current_masks = [
                mask
                for mask in list(dp)
                if mask.bit_count() == size
            ]

            for mask in current_masks:

                for last in list(dp[mask]):

                    for nxt in graph.successors(last):

                        bit = 1 << coloring[nxt]

                        if mask & bit:
                            continue

                        new_mask = mask | bit

                        dp.setdefault(new_mask, set()).add(nxt)

        full_mask = (1 << k) - 1

        if end in dp.get(full_mask, set()):
            return True

    return False
