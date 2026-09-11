"""Input and output helpers for the command-line program."""

from pathlib import Path

from .errors import InputFileError, OutputFileError, TextDecodeError

PathValue = str | Path
_SUPPORTED_ENCODINGS = ("utf-8", "gb18030")


def read_text(path: PathValue) -> str:
    """Read one input file using the supported Chinese text encodings."""
    try:
        file_path = Path(path)
        raw = file_path.read_bytes()
    except (OSError, TypeError, ValueError) as exc:
        raise InputFileError(f"无法读取输入文件: {path}") from exc

    for encoding in _SUPPORTED_ENCODINGS:
        try:
            return raw.decode(encoding)
        except UnicodeDecodeError:
            continue

    raise TextDecodeError(f"输入文件无法按支持的编码解码: {path}")


def write_score(path: PathValue, score: float) -> None:
    """Write a similarity score with exactly two digits after the decimal point."""
    try:
        file_path = Path(path)
        with file_path.open("w", encoding="utf-8", newline="\n") as answer_file:
            answer_file.write(f"{score:.2f}\n")
    except (OSError, TypeError, ValueError) as exc:
        raise OutputFileError(f"无法写入答案文件: {path}") from exc
