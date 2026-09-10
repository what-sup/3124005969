import math

import pytest

from plagiarism.tfidf import build_tfidf_vectors


def test_build_tfidf_vectors_uses_smoothed_idf() -> None:
    vectors = build_tfidf_vectors(
        [
            ["a", "a", "b"],
            ["a", "c"],
        ]
    )
    shared_idf = 1.0
    unique_idf = math.log(3 / 2) + 1

    assert vectors[0]["a"] == pytest.approx((2 / 3) * shared_idf)
    assert vectors[0]["b"] == pytest.approx((1 / 3) * unique_idf)
    assert vectors[1]["a"] == pytest.approx((1 / 2) * shared_idf)
    assert vectors[1]["c"] == pytest.approx((1 / 2) * unique_idf)


def test_build_tfidf_vectors_keeps_identical_documents_identical() -> None:
    vectors = build_tfidf_vectors(
        [
            ["中文", "文本", "中文"],
            ["中文", "文本", "中文"],
        ]
    )

    assert vectors[0] == vectors[1]


def test_build_tfidf_vectors_represents_empty_document_as_empty_mapping() -> None:
    vectors = build_tfidf_vectors([[], ["only"]])

    assert vectors[0] == {}
    assert vectors[1]["only"] > 0


def test_build_tfidf_vectors_returns_one_vector_per_document() -> None:
    documents = [["a"], [], ["b", "c"]]

    vectors = build_tfidf_vectors(documents)

    assert len(vectors) == len(documents)
