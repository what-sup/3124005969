from pathlib import Path

from main import main


def test_main_function_writes_score_without_process_boundary(tmp_path: Path) -> None:
    original = tmp_path / "original.txt"
    plagiarized = tmp_path / "plagiarized.txt"
    answer = tmp_path / "answer.txt"
    original.write_text("直接调用测试", encoding="utf-8")
    plagiarized.write_text("直接调用测试", encoding="utf-8")

    exit_code = main([str(original), str(plagiarized), str(answer)])

    assert exit_code == 0
    assert answer.read_text(encoding="utf-8") == "1.00\n"


def test_main_function_returns_usage_code_for_wrong_arguments(capsys) -> None:
    exit_code = main([])

    captured = capsys.readouterr()
    assert exit_code == 2
    assert "用法" in captured.err
    assert captured.out == ""


def test_main_function_returns_error_code_for_missing_input(tmp_path: Path, capsys) -> None:
    answer = tmp_path / "answer.txt"

    exit_code = main(
        [str(tmp_path / "missing.txt"), str(tmp_path / "other.txt"), str(answer)]
    )

    captured = capsys.readouterr()
    assert exit_code == 1
    assert "错误" in captured.err
    assert not answer.exists()
