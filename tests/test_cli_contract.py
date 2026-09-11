"""First red test for the command-line contract.

This test is intentionally written before main.py.  It should fail until
there is a working implementation of the required three-path interface.
"""

import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]


def test_main_accepts_three_paths_and_writes_two_decimal_score(tmp_path: Path) -> None:
    original = tmp_path / "original.txt"
    plagiarized = tmp_path / "plagiarized.txt"
    answer = tmp_path / "answer.txt"
    original.write_text("今天天气晴朗。", encoding="utf-8")
    plagiarized.write_text("今天天气晴朗。", encoding="utf-8")

    result = subprocess.run(
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

    assert result.returncode == 0, result.stderr
    assert answer.read_text(encoding="utf-8").strip() == "1.00"
