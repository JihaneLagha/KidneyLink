import pytest

from kidneylink.color_coding import (
    assign_random_colors,
    is_colorful
)


def test_number_of_colors_is_three_times_target():
    colors = assign_random_colors(
        ["P1", "P2", "P3"],
        target=4,
        seed=42
    )

    assert all(0 <= color < 12 for color in colors.values())


def test_every_vertex_receives_a_color():
    vertices = ["P1", "P2", "P3"]

    colors = assign_random_colors(
        vertices,
        target=2,
        seed=42
    )

    assert set(colors.keys()) == set(vertices)


def test_same_seed_produces_same_coloring():
    vertices = ["P1", "P2", "P3"]

    first = assign_random_colors(vertices, 3, seed=100)
    second = assign_random_colors(vertices, 3, seed=100)

    assert first == second


def test_different_seeds_can_produce_different_colorings():
    vertices = [f"P{i}" for i in range(20)]

    first = assign_random_colors(vertices, 3, seed=10)
    second = assign_random_colors(vertices, 3, seed=20)

    assert first != second


def test_colorful_vertices():
    coloring = {"P1": 0, "P2": 1, "P3": 2}

    assert is_colorful(["P1", "P2", "P3"], coloring)


def test_repeated_color_is_not_colorful():
    coloring = {"P1": 0, "P2": 1, "P3": 1}

    assert not is_colorful(["P1", "P2", "P3"], coloring)


def test_invalid_target_rejected():
    with pytest.raises(ValueError):
        assign_random_colors(["P1"], 0)


def test_empty_graph():
    assert assign_random_colors([], 3) == {}
