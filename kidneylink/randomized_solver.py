from dataclasses import dataclass
from time import perf_counter
from typing import Hashable, Optional, Set

import networkx as nx

from kidneylink.color_coding import assign_random_colors
from kidneylink.dynamic_programming import solve_coloring_instance


@dataclass
class RandomizedResult:
    decision: bool
    attempts: int
    elapsed_seconds: float
    successful_seed: Optional[int]

    @property
    def status(self) -> str:
        return "YES" if self.decision else "NO"


def solve_randomized(
    graph: nx.DiGraph,
    altruistic_donors: Set[Hashable],
    target: int,
    max_cycle_length: int,
    max_path_length: int,
    repetitions: int = 100,
    base_seed: int = 42,
) -> RandomizedResult:
    """
    Run the randomized color-coding decision algorithm.

    A YES result means a feasible solution covering at least
    target patients was found.

    A NO result means no solution was found in the configured
    number of independent colorings. It is not an absolute
    proof of infeasibility.
    """

    if target <= 0:
        raise ValueError("Target must be positive.")

    if repetitions <= 0:
        raise ValueError("Repetitions must be positive.")

    if max_cycle_length < 0 or max_path_length < 0:
        raise ValueError("Length limits cannot be negative.")

    start = perf_counter()

    for attempt in range(repetitions):
        seed = base_seed + attempt

        coloring = assign_random_colors(
            graph.nodes,
            target,
            seed=seed,
        )

        decision = solve_coloring_instance(
            graph=graph,
            altruistic_donors=altruistic_donors,
            coloring=coloring,
            target=target,
            max_cycle_length=max_cycle_length,
            max_path_length=max_path_length,
        )

        if decision:
            return RandomizedResult(
                decision=True,
                attempts=attempt + 1,
                elapsed_seconds=perf_counter() - start,
                successful_seed=seed,
            )

    return RandomizedResult(
        decision=False,
        attempts=repetitions,
        elapsed_seconds=perf_counter() - start,
        successful_seed=None,
    )
