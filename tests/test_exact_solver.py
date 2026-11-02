import networkx as nx

import pytest

from kidneylink.exact_solver import (
    enumerate_cycles,
    enumerate_altruistic_paths,
    solve_exact,
)


def test_two_way_exchange():
    g = nx.DiGraph()

    g.add_node("P1", node_type="pair")
    g.add_node("P2", node_type="pair")

    g.add_edges_from([
        ("P1", "P2"),
        ("P2", "P1"),
    ])

    result = solve_exact(g, set(), 2, 2)

    assert result.maximum_patients == 2
    assert len(result.structures) == 1
    assert result.structures[0].structure_type == "cycle"


def test_three_way_cycle_respects_limit():
    g = nx.DiGraph()

    for p in ["P1", "P2", "P3"]:
        g.add_node(p, node_type="pair")

    g.add_edges_from([
        ("P1", "P2"),
        ("P2", "P3"),
        ("P3", "P1"),
    ])

    result = solve_exact(g, set(), 2, 2)

    assert result.maximum_patients == 0


def test_altruistic_path():
    g = nx.DiGraph()

    g.add_node("A1", node_type="altruistic")
    g.add_node("P1", node_type="pair")
    g.add_node("P2", node_type="pair")

    g.add_edges_from([
        ("A1", "P1"),
        ("P1", "P2"),
    ])

    result = solve_exact(g, {"A1"}, 3, 2)

    assert result.maximum_patients == 2
    assert result.structures[0].structure_type == "path"
    assert result.structures[0].vertices == ("A1", "P1", "P2")


def test_two_disjoint_exchanges():
    g = nx.DiGraph()

    for p in ["P1", "P2", "P3", "P4"]:
        g.add_node(p, node_type="pair")

    g.add_edges_from([
        ("P1", "P2"),
        ("P2", "P1"),
        ("P3", "P4"),
        ("P4", "P3"),
    ])

    result = solve_exact(g, set(), 2, 2)

    assert result.maximum_patients == 4
    assert len(result.structures) == 2


def test_overlapping_exchanges_cannot_be_combined():
    g = nx.DiGraph()

    for p in ["P1", "P2", "P3"]:
        g.add_node(p, node_type="pair")

    g.add_edges_from([
        ("P1", "P2"),
        ("P2", "P1"),
        ("P2", "P3"),
        ("P3", "P2"),
    ])

    result = solve_exact(g, set(), 2, 2)

    assert result.maximum_patients == 2


def test_cycle_and_path_can_be_combined():
    g = nx.DiGraph()

    for p in ["P1", "P2", "P3", "P4"]:
        g.add_node(p, node_type="pair")

    g.add_node("A1", node_type="altruistic")

    g.add_edges_from([
        ("P1", "P2"),
        ("P2", "P1"),
        ("A1", "P3"),
        ("P3", "P4"),
    ])

    result = solve_exact(g, {"A1"}, 2, 2)

    assert result.maximum_patients == 4
    assert len(result.structures) == 2


def test_no_feasible_exchange():
    g = nx.DiGraph()
    g.add_node("P1", node_type="pair")

    result = solve_exact(g, set(), 3, 3)

    assert result.maximum_patients == 0
    assert result.structures == []
    assert result.feasible is False


def test_enumeration_functions():
    g = nx.DiGraph()

    g.add_node("A1", node_type="altruistic")
    g.add_node("P1", node_type="pair")
    g.add_node("P2", node_type="pair")

    g.add_edges_from([
        ("A1", "P1"),
        ("P1", "P2"),
        ("P2", "P1"),
    ])

    cycles = enumerate_cycles(g, 2)
    paths = enumerate_altruistic_paths(g, {"A1"}, 2)

    assert len(cycles) == 1
    assert len(paths) == 2


def test_invalid_altruistic_donor():
    g = nx.DiGraph()

    with pytest.raises(ValueError):
        solve_exact(g, {"UNKNOWN"}, 3, 3)


def test_invalid_length():
    g = nx.DiGraph()

    with pytest.raises(ValueError):
        solve_exact(g, set(), -1, 3)
