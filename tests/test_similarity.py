import math

import pytest

from plagiarism.similarity import cosine_similarity


def test_cosine_similarity_of_identical_vectors_is_one() -> None:
    assert cosine_similarity({"a": 2.0, "b": 1.0}, {"a": 2.0, "b": 1.0}) == pytest.approx(1.0)


def test_cosine_similarity_of_disjoint_vectors_is_zero() -> None:
    assert cosine_similarity({"a": 1.0}, {"b": 1.0}) == pytest.approx(0.0)


def test_cosine_similarity_uses_union_of_sparse_vector_keys() -> None:
    expected = 1 / math.sqrt(2)

    assert cosine_similarity({"a": 1.0, "b": 1.0}, {"a": 1.0}) == pytest.approx(expected)


def test_cosine_similarity_returns_zero_when_a_vector_is_empty() -> None:
    assert cosine_similarity({}, {"a": 1.0}) == 0.0
    assert cosine_similarity({}, {}) == 0.0


def test_cosine_similarity_returns_zero_for_a_zero_norm_vector() -> None:
    assert cosine_similarity({"a": 0.0}, {"a": 1.0}) == 0.0
