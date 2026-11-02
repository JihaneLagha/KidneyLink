import networkx as nx
import pytest

from kidneylink.long_path import find_altruistic_path


def make_graph():
    g = nx.DiGraph()
    g.add_node("A1", node_type="altruistic")
    g.add_node("P1", node_type="pair")
    g.add_node("P2", node_type="pair")
    g.add_node("P3", node_type="pair")
    return g


def test_path_exactly_target():
    g = make_graph()
    g.add_edges_from([("A1", "P1"), ("P1", "P2")])

    assert find_altruistic_path(g, {"A1"}, 2)


def test_path_longer_than_target():
    g = make_graph()
    g.add_edges_from([
        ("A1", "P1"),
        ("P1", "P2"),
        ("P2", "P3"),
    ])

    assert find_altruistic_path(g, {"A1"}, 2)


def test_path_shorter_than_target():
    g = make_graph()
    g.add_edges_from([("A1", "P1"), ("P1", "P2")])

    assert not find_altruistic_path(g, {"A1"}, 3)


def test_no_altruistic_donor():
    g = make_graph()

    assert not find_altruistic_path(g, set(), 1)


def test_unknown_donor():
    g = make_graph()

    with pytest.raises(ValueError):
        find_altruistic_path(g, {"UNKNOWN"}, 1)


def test_invalid_target():
    g = make_graph()

    with pytest.raises(ValueError):
        find_altruistic_path(g, {"A1"}, 0)
