import networkx as nx

from kidneylink.colorful_structures import f


def make_graph(nodes, edges):
    g = nx.DiGraph()

    for node, node_type in nodes:
        g.add_node(node, node_type=node_type)

    g.add_edges_from(edges)
    return g


def test_two_way_cycle():
    g = make_graph(
        [("P1", "pair"), ("P2", "pair")],
        [("P1", "P2"), ("P2", "P1")]
    )

    assert f(g, set(), {"P1": 0, "P2": 1},
             {0, 1}, 2, 3, 3)


def test_three_way_cycle():
    g = make_graph(
        [("P1", "pair"), ("P2", "pair"), ("P3", "pair")],
        [("P1", "P2"), ("P2", "P3"), ("P3", "P1")]
    )

    assert f(g, set(), {"P1": 0, "P2": 1, "P3": 2},
             {0, 1, 2}, 3, 3, 3)


def test_cycle_not_found_for_wrong_color_subset():
    g = make_graph(
        [("P1", "pair"), ("P2", "pair")],
        [("P1", "P2"), ("P2", "P1")]
    )

    assert not f(g, set(), {"P1": 0, "P2": 1},
                 {0, 2}, 2, 3, 3)


def test_altruistic_path():
    g = make_graph(
        [("A1", "altruistic"), ("P1", "pair"), ("P2", "pair")],
        [("A1", "P1"), ("P1", "P2")]
    )

    assert f(g, {"A1"}, {"A1": 0, "P1": 1, "P2": 2},
             {0, 1, 2}, 2, 3, 2)


def test_path_wrong_color_subset():
    g = make_graph(
        [("A1", "altruistic"), ("P1", "pair"), ("P2", "pair")],
        [("A1", "P1"), ("P1", "P2")]
    )

    assert not f(g, {"A1"}, {"A1": 0, "P1": 1, "P2": 2},
                 {0, 1, 3}, 2, 3, 2)


def test_path_length_limit():
    g = make_graph(
        [("A1", "altruistic"), ("P1", "pair"), ("P2", "pair")],
        [("A1", "P1"), ("P1", "P2")]
    )

    assert not f(g, {"A1"}, {"A1": 0, "P1": 1, "P2": 2},
                 {0, 1, 2}, 2, 3, 1)


def test_cycle_length_limit():
    g = make_graph(
        [("P1", "pair"), ("P2", "pair"), ("P3", "pair")],
        [("P1", "P2"), ("P2", "P3"), ("P3", "P1")]
    )

    assert not f(g, set(), {"P1": 0, "P2": 1, "P3": 2},
                 {0, 1, 2}, 3, 2, 3)


def test_no_altruistic_donor_means_no_path():
    g = make_graph(
        [("P1", "pair"), ("P2", "pair")],
        [("P1", "P2")]
    )

    assert not f(g, set(), {"P1": 0, "P2": 1},
                 {0, 1}, 1, 3, 2)

def test_altruistic_path_rejects_unknown_intermediate_vertex():
    g = make_graph(
        [
            ("A1", "altruistic"),
            ("X", "unknown"),
            ("P1", "pair"),
        ],
        [
            ("A1", "X"),
            ("X", "P1"),
        ],
    )

    coloring = {
        "A1": 0,
        "X": 1,
        "P1": 2,
    }

    assert not f(
        g,
        {"A1"},
        coloring,
        {0, 1},
        1,
        3,
        2,
    )
