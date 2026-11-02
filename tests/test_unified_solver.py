import networkx as nx
import pytest

from kidneylink.unified_solver import solve_kidney_exchange


def create_two_way_exchange():
    graph = nx.DiGraph()

    graph.add_node("P1", node_type="pair")
    graph.add_node("P2", node_type="pair")

    graph.add_edges_from([
        ("P1", "P2"),
        ("P2", "P1"),
    ])

    return graph


def test_exact_solver_finds_two_way_exchange():
    graph = create_two_way_exchange()

    result = solve_kidney_exchange(
        graph=graph,
        altruistic_donors=set(),
        target=2,
        max_cycle_length=2,
        max_path_length=3,
        method="exact",
    )

    assert result.decision is True
    assert result.status == "YES"
    assert result.maximum_patients == 2
    assert result.method == "exact"
    assert result.exact_solution is not None
    assert result.randomized_result is None
    assert result.elapsed_seconds >= 0


def test_exact_solver_rejects_insufficient_target():
    graph = create_two_way_exchange()

    result = solve_kidney_exchange(
        graph=graph,
        altruistic_donors=set(),
        target=3,
        max_cycle_length=2,
        max_path_length=3,
        method="exact",
    )

    assert result.decision is False
    assert result.status == "NO"
    assert result.maximum_patients == 2


def test_randomized_solver_finds_two_way_exchange():
    graph = create_two_way_exchange()

    result = solve_kidney_exchange(
        graph=graph,
        altruistic_donors=set(),
        target=2,
        max_cycle_length=2,
        max_path_length=3,
        method="randomized",
        repetitions=100,
        seed=42,
    )

    assert result.decision is True
    assert result.status == "YES"
    assert result.method == "randomized"
    assert result.randomized_result is not None
    assert result.maximum_patients is None


def test_invalid_method_rejected():
    graph = create_two_way_exchange()

    with pytest.raises(ValueError):
        solve_kidney_exchange(
            graph, set(), 2, 2, 3, method="invalid"
        )


def test_invalid_target_rejected():
    graph = create_two_way_exchange()

    with pytest.raises(ValueError):
        solve_kidney_exchange(
            graph, set(), 0, 2, 3
        )


def test_unknown_donor_rejected():
    graph = create_two_way_exchange()

    with pytest.raises(ValueError):
        solve_kidney_exchange(
            graph, {"UNKNOWN"}, 2, 2, 3
        )


def test_invalid_donor_type_rejected():
    graph = create_two_way_exchange()

    with pytest.raises(ValueError):
        solve_kidney_exchange(
            graph, {"P1"}, 2, 2, 3
        )

def test_altruistic_donor_with_incoming_edge_rejected():
    graph = nx.DiGraph()

    graph.add_node("A1", node_type="altruistic")
    graph.add_node("P1", node_type="pair")

    graph.add_edge("P1", "A1")

    with pytest.raises(ValueError, match="incoming"):
        solve_kidney_exchange(
            graph=graph,
            altruistic_donors={"A1"},
            target=1,
            max_cycle_length=2,
            max_path_length=2,
            method="exact",
        )