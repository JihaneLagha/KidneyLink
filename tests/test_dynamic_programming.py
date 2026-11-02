import networkx as nx
import pytest

from kidneylink.dynamic_programming import solve_coloring_instance


def test_two_way_exchange_reaches_target():
    g = nx.DiGraph()

    g.add_node("P1", node_type="pair")
    g.add_node("P2", node_type="pair")

    g.add_edges_from([
        ("P1", "P2"),
        ("P2", "P1"),
    ])

    coloring = {"P1": 0, "P2": 1}

    assert solve_coloring_instance(
        g, set(), coloring, 2, 3, 3
    )


def test_two_disjoint_two_way_exchanges():
    g = nx.DiGraph()

    for p in ["P1", "P2", "P3", "P4"]:
        g.add_node(p, node_type="pair")

    g.add_edges_from([
        ("P1", "P2"),
        ("P2", "P1"),
        ("P3", "P4"),
        ("P4", "P3"),
    ])

    coloring = {
        "P1": 0,
        "P2": 1,
        "P3": 2,
        "P4": 3,
    }

    assert solve_coloring_instance(
        g, set(), coloring, 4, 3, 3
    )


def test_single_pair_without_exchange_is_no():
    g = nx.DiGraph()
    g.add_node("P1", node_type="pair")

    assert not solve_coloring_instance(
        g, set(), {"P1": 0}, 1, 3, 3
    )


def test_insufficient_patients_is_no():
    g = nx.DiGraph()

    g.add_node("P1", node_type="pair")
    g.add_node("P2", node_type="pair")

    g.add_edges_from([
        ("P1", "P2"),
        ("P2", "P1"),
    ])

    assert not solve_coloring_instance(
        g,
        set(),
        {"P1": 0, "P2": 1},
        3,
        3,
        3,
    )


def test_altruistic_path_reaches_target():
    g = nx.DiGraph()

    g.add_node("A1", node_type="altruistic")
    g.add_node("P1", node_type="pair")
    g.add_node("P2", node_type="pair")

    g.add_edges_from([
        ("A1", "P1"),
        ("P1", "P2"),
    ])

    coloring = {
        "A1": 0,
        "P1": 1,
        "P2": 2,
    }

    assert solve_coloring_instance(
        g, {"A1"}, coloring, 2, 3, 2
    )


def test_invalid_target_rejected():
    g = nx.DiGraph()

    with pytest.raises(ValueError):
        solve_coloring_instance(
            g, set(), {}, 0, 3, 3
        )


def test_long_cycle_special_case():
    g = nx.DiGraph()

    g.add_node("P1", node_type="pair")
    g.add_node("P2", node_type="pair")

    g.add_edges_from([
        ("P1", "P2"),
        ("P2", "P1"),
    ])

    coloring = {"P1": 0, "P2": 1}

    assert solve_coloring_instance(
        g, set(), coloring, 2, 3, 3
    )


def test_long_altruistic_path_special_case():
    g = nx.DiGraph()

    g.add_node("A1", node_type="altruistic")
    g.add_node("P1", node_type="pair")
    g.add_node("P2", node_type="pair")

    g.add_edges_from([
        ("A1", "P1"),
        ("P1", "P2"),
    ])

    coloring = {"A1": 0, "P1": 1, "P2": 2}

    assert solve_coloring_instance(
        g, {"A1"}, coloring, 2, 3, 2
    )

def test_unknown_altruistic_donor_rejected():
    g = nx.DiGraph()
    g.add_node("P1", node_type="pair")

    with pytest.raises(ValueError, match="Unknown altruistic donor"):
        solve_coloring_instance(
            g,
            {"A1"},
            {"P1": 0},
            1,
            3,
            3,
        )


def test_invalid_altruistic_donor_type_rejected():
    g = nx.DiGraph()
    g.add_node("P1", node_type="pair")

    with pytest.raises(ValueError, match="Invalid altruistic donor"):
        solve_coloring_instance(
            g,
            {"P1"},
            {"P1": 0},
            1,
            3,
            3,
        )


def test_altruistic_donor_with_incoming_edge_rejected():
    g = nx.DiGraph()
    g.add_node("A1", node_type="altruistic")
    g.add_node("P1", node_type="pair")
    g.add_edge("P1", "A1")

    with pytest.raises(ValueError, match="incoming"):
        solve_coloring_instance(
            g,
            {"A1"},
            {"A1": 0, "P1": 1},
            2,
            3,
            3,
        )
