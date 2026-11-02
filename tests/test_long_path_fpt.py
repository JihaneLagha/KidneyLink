import networkx as nx
import pytest

from kidneylink.long_path import find_altruistic_path
from kidneylink.long_path_fpt import find_altruistic_path_fpt


def make_graph():
    g = nx.DiGraph()

    g.add_node("A1", node_type="altruistic")
    g.add_node("P1", node_type="pair")
    g.add_node("P2", node_type="pair")
    g.add_node("P3", node_type="pair")

    return g


def test_fpt_finds_path_exactly_target():
    g = make_graph()
    g.add_edges_from([
        ("A1", "P1"),
        ("P1", "P2"),
    ])

    assert find_altruistic_path_fpt(
        g, {"A1"}, 2, repetitions=100, seed=42
    )


def test_fpt_finds_path_longer_than_target():
    g = make_graph()
    g.add_edges_from([
        ("A1", "P1"),
        ("P1", "P2"),
        ("P2", "P3"),
    ])

    assert find_altruistic_path_fpt(
        g, {"A1"}, 2, repetitions=100, seed=42
    )


def test_fpt_rejects_shorter_path():
    g = make_graph()
    g.add_edge("A1", "P1")

    assert not find_altruistic_path_fpt(
        g, {"A1"}, 2, repetitions=100, seed=42
    )


def test_fpt_requires_altruistic_start():
    g = make_graph()
    g.add_edge("P1", "P2")

    assert not find_altruistic_path_fpt(
        g, set(), 1, repetitions=100, seed=42
    )


def test_fpt_supports_multiple_donors():
    g = make_graph()
    g.add_node("A2", node_type="altruistic")

    g.add_edges_from([
        ("A1", "P1"),
        ("A2", "P2"),
        ("P2", "P3"),
    ])

    assert find_altruistic_path_fpt(
        g, {"A1", "A2"}, 2, repetitions=100, seed=42
    )


def test_fpt_is_reproducible():
    g = make_graph()
    g.add_edges_from([
        ("A1", "P1"),
        ("P1", "P2"),
    ])

    first = find_altruistic_path_fpt(
        g, {"A1"}, 2, repetitions=100, seed=123
    )

    second = find_altruistic_path_fpt(
        g, {"A1"}, 2, repetitions=100, seed=123
    )

    assert first == second


def test_fpt_matches_exhaustive_reference():
    g = make_graph()
    g.add_edges_from([
        ("A1", "P1"),
        ("P1", "P2"),
        ("P2", "P3"),
    ])

    exact = find_altruistic_path(g, {"A1"}, 2)

    randomized = find_altruistic_path_fpt(
        g, {"A1"}, 2, repetitions=100, seed=42
    )

    assert randomized == exact


def test_unknown_donor_rejected():
    g = make_graph()

    with pytest.raises(ValueError):
        find_altruistic_path_fpt(
            g, {"UNKNOWN"}, 1
        )


def test_invalid_target_rejected():
    g = make_graph()

    with pytest.raises(ValueError):
        find_altruistic_path_fpt(
            g, {"A1"}, 0
        )


def test_invalid_repetitions_rejected():
    g = make_graph()

    with pytest.raises(ValueError):
        find_altruistic_path_fpt(
            g, {"A1"}, 1, repetitions=0
        )
