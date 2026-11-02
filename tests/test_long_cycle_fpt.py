import networkx as nx
import pytest

from kidneylink.long_cycle_fpt import find_long_directed_cycle


def test_finds_cycle_between_k_and_2k():
    g = nx.DiGraph()
    g.add_edges_from([
        ("A", "B"),
        ("B", "C"),
        ("C", "A"),
    ])

    assert find_long_directed_cycle(g, 3, 100, 100, 42)


def test_finds_cycle_longer_than_2k():
    g = nx.DiGraph()
    g.add_edges_from([
        ("A", "B"),
        ("B", "C"),
        ("C", "D"),
        ("D", "E"),
        ("E", "A"),
    ])

    assert find_long_directed_cycle(g, 2, 100, 1000, 42)


def test_rejects_directed_acyclic_graph():
    g = nx.DiGraph()
    g.add_edges_from([
        ("A", "B"),
        ("B", "C"),
        ("C", "D"),
        ("D", "E"),
    ])

    assert not find_long_directed_cycle(g, 3, 100, 100, 42)


def test_rejects_cycle_shorter_than_k():
    g = nx.DiGraph()
    g.add_edges_from([
        ("A", "B"),
        ("B", "A"),
        ("B", "C"),
    ])

    assert not find_long_directed_cycle(g, 3, 100, 100, 42)


def test_rejects_insufficient_vertices():
    g = nx.DiGraph()
    g.add_edge("A", "B")

    assert not find_long_directed_cycle(g, 3)


def test_invalid_k():
    g = nx.DiGraph()

    with pytest.raises(ValueError):
        find_long_directed_cycle(g, 1)


def test_invalid_path_repetitions():
    g = nx.DiGraph()

    with pytest.raises(ValueError):
        find_long_directed_cycle(g, 2, path_repetitions=0)


def test_invalid_partition_repetitions():
    g = nx.DiGraph()

    with pytest.raises(ValueError):
        find_long_directed_cycle(
            g, 2, partition_repetitions=0
        )
