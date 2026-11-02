
import networkx as nx

from kidneylink.exact_solver import ExchangeStructure
from kidneylink.solution_validation import validate_solution


def test_valid_two_way_cycle():

    g = nx.DiGraph()

    g.add_node("P1", node_type="pair")
    g.add_node("P2", node_type="pair")

    g.add_edges_from([
        ("P1", "P2"),
        ("P2", "P1"),
    ])

    structures = [
        ExchangeStructure("cycle", ("P1", "P2"))
    ]

    assert validate_solution(
        g, set(), structures, 2, 2, 3
    )


def test_valid_altruistic_path():

    g = nx.DiGraph()

    g.add_node("A1", node_type="altruistic")
    g.add_node("P1", node_type="pair")
    g.add_node("P2", node_type="pair")

    g.add_edges_from([
        ("A1", "P1"),
        ("P1", "P2"),
    ])

    structures = [
        ExchangeStructure("path", ("A1", "P1", "P2"))
    ]

    assert validate_solution(
        g, {"A1"}, structures, 2, 3, 2
    )


def test_invalid_cycle_edge_rejected():

    g = nx.DiGraph()

    g.add_node("P1", node_type="pair")
    g.add_node("P2", node_type="pair")
    g.add_edge("P1", "P2")

    structures = [
        ExchangeStructure("cycle", ("P1", "P2"))
    ]

    assert not validate_solution(
        g, set(), structures, 2, 3, 3
    )


def test_overlapping_structures_rejected():

    g = nx.DiGraph()

    for p in ["P1", "P2", "P3"]:
        g.add_node(p, node_type="pair")

    g.add_edges_from([
        ("P1", "P2"),
        ("P2", "P1"),
        ("P2", "P3"),
        ("P3", "P2"),
    ])

    structures = [
        ExchangeStructure("cycle", ("P1", "P2")),
        ExchangeStructure("cycle", ("P2", "P3")),
    ]

    assert not validate_solution(
        g, set(), structures, 2, 3, 3
    )


def test_cycle_exceeding_limit_rejected():

    g = nx.DiGraph()

    for p in ["P1", "P2", "P3"]:
        g.add_node(p, node_type="pair")

    g.add_edges_from([
        ("P1", "P2"),
        ("P2", "P3"),
        ("P3", "P1"),
    ])

    structures = [
        ExchangeStructure("cycle", ("P1", "P2", "P3"))
    ]

    assert not validate_solution(
        g, set(), structures, 3, 2, 3
    )


def test_unregistered_path_donor_rejected():

    g = nx.DiGraph()

    g.add_node("A1", node_type="altruistic")
    g.add_node("P1", node_type="pair")
    g.add_edge("A1", "P1")

    structures = [
        ExchangeStructure("path", ("A1", "P1"))
    ]

    assert not validate_solution(
        g, set(), structures, 1, 3, 3
    )


def test_insufficient_patient_coverage_rejected():

    g = nx.DiGraph()

    g.add_node("P1", node_type="pair")
    g.add_node("P2", node_type="pair")

    g.add_edges_from([
        ("P1", "P2"),
        ("P2", "P1"),
    ])

    structures = [
        ExchangeStructure("cycle", ("P1", "P2"))
    ]

    assert not validate_solution(
        g, set(), structures, 3, 3, 3
    )


def test_altruistic_donor_with_incoming_edge_rejected():

    g = nx.DiGraph()

    g.add_node("A1", node_type="altruistic")
    g.add_node("P1", node_type="pair")
    g.add_edge("A1", "P1")
    g.add_edge("P1", "A1")

    structures = [
        ExchangeStructure("path", ("A1", "P1"))
    ]

    import pytest

    with pytest.raises(ValueError):
        validate_solution(
            g, {"A1"}, structures, 1, 3, 3
        )


def test_unknown_vertex_in_structure_rejected():

    g = nx.DiGraph()

    g.add_node("P1", node_type="pair")
    g.add_node("P2", node_type="pair")

    structures = [
        ExchangeStructure("cycle", ("P1", "P999"))
    ]

    assert not validate_solution(
        g, set(), structures, 2, 3, 3
    )


def test_path_exceeding_limit_rejected():

    g = nx.DiGraph()

    g.add_node("A1", node_type="altruistic")
    g.add_node("P1", node_type="pair")
    g.add_node("P2", node_type="pair")

    g.add_edges_from([
        ("A1", "P1"),
        ("P1", "P2"),
    ])

    structures = [
        ExchangeStructure("path", ("A1", "P1", "P2"))
    ]

    assert not validate_solution(
        g, {"A1"}, structures, 2, 3, 1
    )


def test_invalid_structure_type_rejected():

    g = nx.DiGraph()

    g.add_node("P1", node_type="pair")

    structures = [
        ExchangeStructure("invalid", ("P1",))
    ]

    assert not validate_solution(
        g, set(), structures, 1, 3, 3
    )


def test_repeated_vertex_in_structure_rejected():

    g = nx.DiGraph()

    g.add_node("P1", node_type="pair")
    g.add_node("P2", node_type="pair")

    structures = [
        ExchangeStructure("cycle", ("P1", "P2", "P1"))
    ]

    assert not validate_solution(
        g, set(), structures, 2, 3, 3
    )


def test_wrong_graph_type_rejected():

    import pytest

    g = nx.Graph()
    g.add_node("P1", node_type="pair")

    with pytest.raises(TypeError):
        validate_solution(
            g, set(), [], 1, 3, 3
        )


def test_unknown_altruistic_donor_rejected():

    import pytest

    g = nx.DiGraph()
    g.add_node("P1", node_type="pair")

    with pytest.raises(ValueError):
        validate_solution(
            g, {"A999"}, [], 1, 3, 3
        )


def test_empty_structure_rejected():

    g = nx.DiGraph()

    structures = [
        ExchangeStructure("cycle", ())
    ]

    assert not validate_solution(
        g, set(), structures, 1, 3, 3
    )

