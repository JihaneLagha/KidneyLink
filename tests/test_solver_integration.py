import networkx as nx

from kidneylink.exact_solver import solve_exact
from kidneylink.randomized_solver import solve_randomized


def compare_solvers(graph, donors, target, max_cycle, max_path):
    exact = solve_exact(
        graph,
        donors,
        max_cycle,
        max_path,
    )

    randomized = solve_randomized(
        graph,
        donors,
        target,
        max_cycle,
        max_path,
        repetitions=500,
        base_seed=42,
    )

    expected = exact.maximum_patients >= target

    assert randomized.decision == expected

    return randomized


def test_two_way_exchange():
    g = nx.DiGraph()

    g.add_node("P1", node_type="pair")
    g.add_node("P2", node_type="pair")

    g.add_edges_from([
        ("P1", "P2"),
        ("P2", "P1"),
    ])

    result = compare_solvers(g, set(), 2, 3, 3)

    assert result.decision is True


def test_altruistic_donor_chain():
    g = nx.DiGraph()

    g.add_node("A1", node_type="altruistic")
    g.add_node("P1", node_type="pair")
    g.add_node("P2", node_type="pair")

    g.add_edges_from([
        ("A1", "P1"),
        ("P1", "P2"),
    ])

    result = compare_solvers(g, {"A1"}, 2, 3, 2)

    assert result.decision is True


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

    result = compare_solvers(g, set(), 4, 3, 3)

    assert result.decision is True


def test_cycle_and_altruistic_path_combination():
    g = nx.DiGraph()

    g.add_node("A1", node_type="altruistic")

    for p in ["P1", "P2", "P3"]:
        g.add_node(p, node_type="pair")

    g.add_edges_from([
        ("P1", "P2"),
        ("P2", "P1"),
        ("A1", "P3"),
    ])

    result = compare_solvers(g, {"A1"}, 3, 2, 1)

    assert result.decision is True


def test_overlapping_exchanges():
    g = nx.DiGraph()

    for p in ["P1", "P2", "P3"]:
        g.add_node(p, node_type="pair")

    g.add_edges_from([
        ("P1", "P2"),
        ("P2", "P1"),
        ("P2", "P3"),
        ("P3", "P2"),
    ])

    result = compare_solvers(g, set(), 3, 2, 2)

    assert result.decision is False


def test_impossible_exchange():
    g = nx.DiGraph()

    for p in ["P1", "P2", "P3"]:
        g.add_node(p, node_type="pair")

    result = compare_solvers(g, set(), 2, 3, 3)

    assert result.decision is False
