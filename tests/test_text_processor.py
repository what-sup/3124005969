import os
import subprocess
import sys
from pathlib import Path

from plagiarism.text_processor import normalize_text, tokenize

PROJECT_ROOT = Path(__file__).resolve().parents[1]


def test_normalize_text_unifies_newlines_and_width() -> None:
    assert normalize_text("Ａ\r\nＢ\rＣ") == "A\nB\nC"


def test_tokenize_keeps_words_and_discards_punctuation() -> None:
    tokens = tokenize("你好，世界！Python 3.11")

    assert "你好" in tokens
    assert "世界" in tokens
    assert "python" in tokens
    assert "3.11" in tokens
    assert "，" not in tokens
    assert "！" not in tokens


def test_tokenize_preserves_repeated_meaningful_tokens() -> None:
    tokens = tokenize("机器学习机器学习")

    assert tokens.count("机器") == 2
    assert tokens.count("学习") == 2


def test_tokenize_returns_empty_for_blank_or_punctuation_text() -> None:
    assert tokenize(" \n\t") == []
    assert tokenize("，。！？……") == []


def test_tokenize_does_not_create_runtime_cache_files(tmp_path: Path) -> None:
    runtime_tmp = tmp_path / "runtime-tmp"
    runtime_tmp.mkdir()
    environment = os.environ.copy()
    environment["PYTHONPATH"] = str(PROJECT_ROOT)
    environment["TMPDIR"] = str(runtime_tmp)

    result = subprocess.run(
        [
            sys.executable,
            "-c",
            "from plagiarism.text_processor import tokenize; tokenize('缓存检查')",
        ],
        cwd=PROJECT_ROOT,
        env=environment,
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0, result.stderr
    assert list(runtime_tmp.iterdir()) == []
