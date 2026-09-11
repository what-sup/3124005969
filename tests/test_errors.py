import subprocess
import sys
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[1]


def run_main(*arguments: Path | str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(PROJECT_ROOT / "main.py"), *(str(arg) for arg in arguments)],
        cwd=PROJECT_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )


@pytest.mark.parametrize("arguments", [(), ("a", "b", "c", "d")])
def test_main_rejects_wrong_argument_count(arguments: tuple[str, ...]) -> None:
    result = run_main(*arguments)

    assert result.returncode == 2
    assert "用法" in result.stderr


def test_main_reports_missing_input_without_creating_answer(tmp_path: Path) -> None:
    answer = tmp_path / "answer.txt"

    result = run_main(tmp_path / "missing.txt", tmp_path / "other.txt", answer)

    assert result.returncode != 0
    assert result.stderr.strip()
    assert not answer.exists()


def test_main_reports_undecodable_input_without_creating_answer(tmp_path: Path) -> None:
    original = tmp_path / "original.txt"
    plagiarized = tmp_path / "plagiarized.txt"
    answer = tmp_path / "answer.txt"
    original.write_bytes(b"\xff\xfe\xff\xfe\x00\x81")
    plagiarized.write_text("valid text", encoding="utf-8")

    result = run_main(original, plagiarized, answer)

    assert result.returncode != 0
    assert "解码" in result.stderr
    assert not answer.exists()


def test_main_reports_output_failure(tmp_path: Path) -> None:
    original = tmp_path / "original.txt"
    plagiarized = tmp_path / "plagiarized.txt"
    answer = tmp_path / "missing" / "answer.txt"
    original.write_text("same", encoding="utf-8")
    plagiarized.write_text("same", encoding="utf-8")

    result = run_main(original, plagiarized, answer)

    assert result.returncode != 0
    assert "写入" in result.stderr
