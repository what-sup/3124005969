"""TF-IDF vector construction using sparse dictionaries."""

import math
from collections import Counter
from typing import Dict, List, Sequence


Vector = Dict[str, float]


def build_tfidf_vectors(documents: Sequence[Sequence[str]]) -> List[Vector]:
    """Build one smoothed TF-IDF vector for each tokenized document."""
    document_counts = [Counter(document) for document in documents]
    document_total = len(document_counts)
    if document_total == 0:
        return []

    document_frequency: Counter[str] = Counter()
    for counts in document_counts:
        for token in counts:
            document_frequency[token] += 1

    idf = {
        token: math.log((document_total + 1) / (frequency + 1)) + 1
        for token, frequency in document_frequency.items()
    }

    vectors: List[Vector] = []
    for counts in document_counts:
        token_total = sum(counts.values())
        if token_total == 0:
            vectors.append({})
            continue

        vectors.append(
            {
                token: (count / token_total) * idf[token]
                for token, count in counts.items()
            }
        )
    return vectors
