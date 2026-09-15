import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]


def run_main(
    original: Path, plagiarized: Path, answer: Path
) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [
            sys.executable,
            str(PROJECT_ROOT / "main.py"),
            str(original),
            str(plagiarized),
            str(answer),
        ],
        cwd=PROJECT_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )


def test_empty_documents_produce_zero_score_and_quiet_success(tmp_path: Path) -> None:
    original = tmp_path / "original.txt"
    plagiarized = tmp_path / "plagiarized.txt"
    answer = tmp_path / "answer.txt"
    original.write_text("", encoding="utf-8")
    plagiarized.write_text("", encoding="utf-8")

    result = run_main(original, plagiarized, answer)

    assert result.returncode == 0, result.stderr
    assert result.stdout == ""
    assert result.stderr == ""
    assert answer.read_text(encoding="utf-8") == "0.00\n"


def test_punctuation_and_whitespace_do_not_change_same_text_score(
    tmp_path: Path,
) -> None:
    original = tmp_path / "original.txt"
    plagiarized = tmp_path / "plagiarized.txt"
    answer = tmp_path / "answer.txt"
    original.write_text("论文 内容。", encoding="utf-8")
    plagiarized.write_text(" 论文\n内容！", encoding="utf-8")

    result = run_main(original, plagiarized, answer)

    assert result.returncode == 0, result.stderr
    assert answer.read_text(encoding="utf-8") == "1.00\n"


def test_documents_without_common_tokens_produce_zero_score(tmp_path: Path) -> None:
    original = tmp_path / "original.txt"
    plagiarized = tmp_path / "plagiarized.txt"
    answer = tmp_path / "answer.txt"
    original.write_text("alpha beta", encoding="utf-8")
    plagiarized.write_text("gamma delta", encoding="utf-8")

    result = run_main(original, plagiarized, answer)

    assert result.returncode == 0, result.stderr
    assert answer.read_text(encoding="utf-8") == "0.00\n"


def test_repeated_terms_produce_a_partial_score(tmp_path: Path) -> None:
    original = tmp_path / "original.txt"
    plagiarized = tmp_path / "plagiarized.txt"
    answer = tmp_path / "answer.txt"
    original.write_text("alpha alpha alpha beta", encoding="utf-8")
    plagiarized.write_text("alpha beta", encoding="utf-8")

    result = run_main(original, plagiarized, answer)
    answer_text = answer.read_text(encoding="utf-8").strip()
    score = float(answer_text)

    assert result.returncode == 0, result.stderr
    assert 0.0 < score < 1.0
    assert len(answer_text.split(".")[1]) == 2
