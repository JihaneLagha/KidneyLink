import pytest
from kidneylink.graph import KidneyExchangeGraph


def test_add_pairs_and_altruistic_donor():
    g = KidneyExchangeGraph()

    g.add_pair("P1")
    g.add_pair("P2")
    g.add_altruistic_donor("A1")

    assert g.number_of_vertices == 3
    assert len(g.patient_pairs) == 2
    assert len(g.altruistic_donors) == 1


def test_add_compatibility():
    g = KidneyExchangeGraph()

    g.add_pair("P1")
    g.add_pair("P2")
    g.add_compatibility("P1", "P2")

    assert g.graph.has_edge("P1", "P2")


def test_altruistic_donor_can_start_chain():
    g = KidneyExchangeGraph()

    g.add_altruistic_donor("A1")
    g.add_pair("P1")
    g.add_compatibility("A1", "P1")

    assert g.graph.has_edge("A1", "P1")
    assert g.validate()


def test_compatibility_cannot_target_altruistic_donor():
    g = KidneyExchangeGraph()

    g.add_altruistic_donor("A1")
    g.add_pair("P1")

    with pytest.raises(ValueError):
        g.add_compatibility("P1", "A1")


def test_self_loop_rejected():
    g = KidneyExchangeGraph()
    g.add_pair("P1")

    with pytest.raises(ValueError):
        g.add_compatibility("P1", "P1")


def test_unknown_vertex_rejected():
    g = KidneyExchangeGraph()
    g.add_pair("P1")

    with pytest.raises(ValueError):
        g.add_compatibility("UNKNOWN", "P1")

def test_valid_exchange_cycle_is_allowed():
    g = KidneyExchangeGraph()

    for pair in ["P1", "P2", "P3"]:
        g.add_pair(pair)

    g.add_compatibility("P1", "P2")
    g.add_compatibility("P2", "P3")
    g.add_compatibility("P3", "P1")

    assert g.graph.has_edge("P1", "P2")
    assert g.graph.has_edge("P2", "P3")
    assert g.graph.has_edge("P3", "P1")
    assert g.validate()
