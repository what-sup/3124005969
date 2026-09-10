"""Command-line entry point for the plagiarism checker."""

import sys
from typing import Optional, Sequence

from plagiarism.errors import PlagiarismError
from plagiarism.file_io import read_text, write_score
from plagiarism.similarity import cosine_similarity
from plagiarism.text_processor import tokenize
from plagiarism.tfidf import build_tfidf_vectors


_USAGE = "用法: python main.py <原文路径> <抄袭版路径> <答案路径>"


def calculate_similarity(original_path: str, plagiarized_path: str) -> float:
    """Read two files and calculate their TF-IDF cosine similarity."""
    original_tokens = tokenize(read_text(original_path))
    plagiarized_tokens = tokenize(read_text(plagiarized_path))
    original_vector, plagiarized_vector = build_tfidf_vectors(
        [original_tokens, plagiarized_tokens]
    )
    return cosine_similarity(original_vector, plagiarized_vector)


def main(argv: Optional[Sequence[str]] = None) -> int:
    """Run the CLI and return a process exit code."""
    arguments = list(sys.argv[1:] if argv is None else argv)
    if len(arguments) != 3:
        print(_USAGE, file=sys.stderr)
        return 2

    original_path, plagiarized_path, answer_path = arguments
    try:
        score = calculate_similarity(original_path, plagiarized_path)
        write_score(answer_path, score)
    except PlagiarismError as exc:
        print(f"错误: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
