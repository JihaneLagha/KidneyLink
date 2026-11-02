from dataclasses import dataclass
from time import perf_counter
from typing import Hashable, Literal, Optional, Set

import networkx as nx

from kidneylink.exact_solver import (
    ExactSolution,
    solve_exact,
)

from kidneylink.randomized_solver import (
    RandomizedResult,
    solve_randomized,
)


SolverMethod = Literal["exact", "randomized"]


@dataclass
class KidneyLinkResult:
    """Unified result returned by the KidneyLink solver."""

    decision: bool
    method: SolverMethod
    target: int
    maximum_patients: Optional[int]
    elapsed_seconds: float

    exact_solution: Optional[ExactSolution] = None
    randomized_result: Optional[RandomizedResult] = None

    @property
    def status(self) -> str:
        return "YES" if self.decision else "NO"

    @property
    def successful(self) -> bool:
        return self.decision


def _validate_input(
    graph: nx.DiGraph,
    altruistic_donors: Set[Hashable],
    target: int,
    max_cycle_length: int,
    max_path_length: int,
    method: SolverMethod,
) -> None:
    """Validate the graph and solver parameters."""

    if not isinstance(graph, nx.DiGraph):
        raise TypeError("Graph must be a NetworkX DiGraph.")

    if target <= 0:
        raise ValueError("Target must be positive.")

    if max_cycle_length < 0 or max_path_length < 0:
        raise ValueError("Length limits cannot be negative.")

    if method not in ("exact", "randomized"):
        raise ValueError(
            "Method must be either 'exact' or 'randomized'."
        )

    if not altruistic_donors.issubset(graph.nodes):
        raise ValueError("Unknown altruistic donor.")

    # Validate all altruistic donor vertices.
    for donor in altruistic_donors:

        if graph.nodes[donor].get("node_type") != "altruistic":
            raise ValueError(
                f"Invalid altruistic donor vertex: {donor}"
            )

        # Altruistic donors must only initiate exchange paths.
        if graph.in_degree(donor) != 0:
            raise ValueError(
                f"Altruistic donor {donor} cannot have incoming edges."
            )

    # Validate graph vertex types.
    for vertex, data in graph.nodes(data=True):

        if data.get("node_type") not in ("pair", "altruistic"):
            raise ValueError(
                f"Invalid or missing node_type for vertex: {vertex}"
            )

        if (
            data.get("node_type") == "altruistic"
            and vertex not in altruistic_donors
        ):
            raise ValueError(
                f"Altruistic vertex {vertex} is missing "
                "from altruistic_donors."
            )

    # Self-loops are not valid kidney exchange edges.
    if nx.number_of_selfloops(graph) > 0:
        raise ValueError("Self-loops are not allowed.")


def solve_kidney_exchange(
    graph: nx.DiGraph,
    altruistic_donors: Set[Hashable],
    target: int,
    max_cycle_length: int,
    max_path_length: int,
    method: SolverMethod = "randomized",
    repetitions: int = 100,
    seed: int = 42,
) -> KidneyLinkResult:
    """
    Unified interface for the KidneyLink algorithms.

    Parameters
    ----------
    graph:
        Directed kidney compatibility graph.

    altruistic_donors:
        Set of altruistic donor vertices.

    target:
        Minimum number of patient-donor pairs to cover.

    max_cycle_length:
        Maximum number of vertices in an exchange cycle.

    max_path_length:
        Maximum number of edges in an altruistic path.

    method:
        "exact" for exhaustive optimization.
        "randomized" for randomized FPT decision.

    repetitions:
        Number of independent colorings for randomized mode.

    seed:
        Base random seed for reproducibility.

    Returns
    -------
    KidneyLinkResult
        Unified decision and algorithm execution information.
    """

    _validate_input(
        graph=graph,
        altruistic_donors=altruistic_donors,
        target=target,
        max_cycle_length=max_cycle_length,
        max_path_length=max_path_length,
        method=method,
    )

    # Exact optimization mode.
    if method == "exact":

        start = perf_counter()

        solution = solve_exact(
            graph=graph,
            altruistic_donors=altruistic_donors,
            max_cycle_length=max_cycle_length,
            max_path_length=max_path_length,
        )

        return KidneyLinkResult(
            decision=solution.maximum_patients >= target,
            method="exact",
            target=target,
            maximum_patients=solution.maximum_patients,
            elapsed_seconds=perf_counter() - start,
            exact_solution=solution,
        )

    # Randomized FPT decision mode.
    randomized = solve_randomized(
        graph=graph,
        altruistic_donors=altruistic_donors,
        target=target,
        max_cycle_length=max_cycle_length,
        max_path_length=max_path_length,
        repetitions=repetitions,
        base_seed=seed,
    )

    return KidneyLinkResult(
        decision=randomized.decision,
        method="randomized",
        target=target,
        maximum_patients=None,
        elapsed_seconds=randomized.elapsed_seconds,
        randomized_result=randomized,
    )
