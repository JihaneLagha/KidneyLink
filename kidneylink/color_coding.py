import random
from typing import Dict, Hashable, Optional


def assign_random_colors(
    vertices,
    target: int,
    seed: Optional[int] = None
) -> Dict[Hashable, int]:
    """
    Assign each graph vertex one of 3 * target colors.

    The assignment is independent and uniformly random.
    """

    if target <= 0:
        raise ValueError("Target must be positive.")

    vertices = list(vertices)

    if len(vertices) == 0:
        return {}

    rng = random.Random(seed)
    number_of_colors = 3 * target

    return {
        vertex: rng.randrange(number_of_colors)
        for vertex in vertices
    }


def is_colorful(vertices, coloring) -> bool:
    """
    Return True if all supplied vertices have distinct colors.
    """

    vertices = list(vertices)
    colors = [coloring[v] for v in vertices]

    return len(colors) == len(set(colors))
