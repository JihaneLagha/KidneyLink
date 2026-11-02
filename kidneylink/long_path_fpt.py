import random
from typing import Hashable, Set

import networkx as nx


def find_altruistic_path_fpt(
    graph: nx.DiGraph,
    altruistic_donors: Set[Hashable],
    target: int,
    repetitions: int = 100,
    seed: int = 42,
) -> bool:
    """
    Randomized color-coding algorithm for a directed
    altruistic path covering at least target patients.

    Uses target + 1 colors and subset dynamic programming.

    This is a randomized FPT decision algorithm.
    A negative result after finite repetitions is probabilistic.
    """

    if target <= 0 or repetitions <= 0:
        raise ValueError("Target and repetitions must be positive.")

    if not altruistic_donors.issubset(graph.nodes):
        raise ValueError("Unknown altruistic donor.")

    donors = set(altruistic_donors)

    for donor in donors:
        if graph.nodes[donor].get("node_type") != "altruistic":
            raise ValueError("Invalid altruistic donor vertex.")

    pair_vertices = {
        v for v, data in graph.nodes(data=True)
        if data.get("node_type") == "pair"
    }

    k = target + 1
    rng = random.Random(seed)

    for _ in range(repetitions):
        coloring = {
            v: rng.randrange(k)
            for v in graph.nodes
        }

        # DP[mask] contains endpoints of colorful paths
        # starting at an altruistic donor.
        dp = {}

        for donor in donors:
            mask = 1 << coloring[donor]
            dp.setdefault(mask, set()).add(donor)

        for mask_size in range(1, k):
            current_masks = [
                mask for mask in list(dp)
                if mask.bit_count() == mask_size
            ]

            for mask in current_masks:
                for last in list(dp[mask]):
                    for nxt in graph.successors(last):

                        if nxt not in pair_vertices:
                            continue

                        bit = 1 << coloring[nxt]

                        if mask & bit:
                            continue

                        new_mask = mask | bit

                        dp.setdefault(new_mask, set()).add(nxt)

                        if new_mask.bit_count() == k:
                            return True

    return False
