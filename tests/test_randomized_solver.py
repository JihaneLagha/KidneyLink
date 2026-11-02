import networkx as nx
import pytest

from kidneylink.randomized_solver import solve_randomized


def test_two_way_exchange_returns_yes():
    g = nx.DiGraph()

    g.add_node("P1", node_type="pair")
    g.add_node("P2", node_type="pair")

    g.add_edges_from([
        ("P1", "P2"),
        ("P2", "P1"),
    ])

    result = solve_randomized(
        g, set(), 2, 2, 2,
        repetitions=5,
    )

    assert result.decision is True
    assert result.status == "YES"
    assert result.successful_seed is not None


def test_altruistic_path_returns_yes():
    g = nx.DiGraph()

    g.add_node("A1", node_type="altruistic")
    g.add_node("P1", node_type="pair")
    g.add_node("P2", node_type="pair")

    g.add_edges_from([
        ("A1", "P1"),
        ("P1", "P2"),
    ])

    result = solve_randomized(
        g, {"A1"}, 2, 2, 2,
        repetitions=5,
    )

    assert result.decision is True


def test_impossible_instance_returns_no():
    g = nx.DiGraph()

    g.add_node("P1", node_type="pair")

    result = solve_randomized(
        g, set(), 2, 2, 2,
        repetitions=5,
    )

    assert result.decision is False
    assert result.status == "NO"
    assert result.attempts == 5
    assert result.successful_seed is None


def test_reproducible_results():
    g = nx.DiGraph()

    g.add_node("P1", node_type="pair")
    g.add_node("P2", node_type="pair")

    g.add_edges_from([
        ("P1", "P2"),
        ("P2", "P1"),
    ])

    first = solve_randomized(
        g, set(), 2, 2, 2,
        repetitions=10,
        base_seed=100,
    )

    second = solve_randomized(
        g, set(), 2, 2, 2,
        repetitions=10,
        base_seed=100,
    )

    assert first.decision == second.decision
    assert first.attempts == second.attempts
    assert first.successful_seed == second.successful_seed


def test_invalid_repetitions():
    g = nx.DiGraph()

    with pytest.raises(ValueError):
        solve_randomized(
            g, set(), 1, 2, 2,
            repetitions=0,
        )
