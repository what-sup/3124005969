from pathlib import Path

import pytest

from plagiarism.errors import InputFileError, OutputFileError, TextDecodeError
from plagiarism.file_io import read_text, write_score


def test_read_text_returns_utf8_content(tmp_path: Path) -> None:
    source = tmp_path / "source.txt"
    source.write_text("中文内容\n", encoding="utf-8")

    assert read_text(source) == "中文内容\n"


def test_read_text_accepts_common_gbk_content(tmp_path: Path) -> None:
    source = tmp_path / "source.txt"
    source.write_bytes("中文内容".encode("gb18030"))

    assert read_text(source) == "中文内容"


def test_read_text_raises_for_missing_file(tmp_path: Path) -> None:
    with pytest.raises(InputFileError):
        read_text(tmp_path / "missing.txt")


def test_read_text_raises_for_undecodable_bytes(tmp_path: Path) -> None:
    source = tmp_path / "binary.txt"
    source.write_bytes(b"\xff\xfe\xff\xfe\x00\x81")

    with pytest.raises(TextDecodeError):
        read_text(source)


def test_write_score_uses_two_decimal_places(tmp_path: Path) -> None:
    answer = tmp_path / "answer.txt"

    write_score(answer, 0.87654)

    assert answer.read_text(encoding="utf-8") == "0.88\n"


def test_write_score_raises_when_parent_does_not_exist(tmp_path: Path) -> None:
    answer = tmp_path / "missing" / "answer.txt"

    with pytest.raises(OutputFileError):
        write_score(answer, 0.5)
