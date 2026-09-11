"""Cosine similarity for sparse numeric vectors."""

import math
from collections.abc import Mapping

Vector = Mapping[str, float]


def cosine_similarity(left: Vector, right: Vector) -> float:
    """Return cosine similarity, using zero for either zero-norm vector."""
    if not left or not right:
        return 0.0

    dot_product = sum(value * right.get(token, 0.0) for token, value in left.items())
    left_norm = math.sqrt(sum(value * value for value in left.values()))
    right_norm = math.sqrt(sum(value * value for value in right.values()))
    if left_norm == 0.0 or right_norm == 0.0:
        return 0.0

    # Guard only against floating-point drift outside the mathematical range.
    score = dot_product / (left_norm * right_norm)
    return max(-1.0, min(1.0, score))
