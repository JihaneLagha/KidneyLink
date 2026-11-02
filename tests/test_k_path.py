import networkx as nx
import pytest

from kidneylink.k_path import has_directed_k_path


def make_graph():
    g = nx.DiGraph()

    g.add_edges_from([
        ("A", "B"),
        ("B", "C"),
        ("C", "D"),
    ])

    return g


def test_finds_exact_three_vertex_path():
    g = make_graph()

    assert has_directed_k_path(
        g, "A", "C", 3, 100, 42
    )


def test_finds_exact_four_vertex_path():
    g = make_graph()

    assert has_directed_k_path(
        g, "A", "D", 4, 100, 42
    )


def test_rejects_wrong_direction():
    g = make_graph()

    assert not has_directed_k_path(
        g, "D", "A", 3, 100, 42
    )


def test_rejects_wrong_exact_length():
    g = make_graph()

    assert not has_directed_k_path(
        g, "A", "D", 3, 100, 42
    )


def test_single_vertex_path():
    g = nx.DiGraph()
    g.add_node("A")

    assert has_directed_k_path(g, "A", "A", 1)


def test_invalid_k():
    g = make_graph()

    with pytest.raises(ValueError):
        has_directed_k_path(g, "A", "D", 0)


def test_unknown_endpoint():
    g = make_graph()

    with pytest.raises(ValueError):
        has_directed_k_path(g, "A", "Z", 2)


def test_invalid_repetitions():
    g = make_graph()

    with pytest.raises(ValueError):
        has_directed_k_path(
            g, "A", "D", 3, 0
        )
