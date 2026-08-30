"""Tests for file size and type analysis."""

from pathlib import Path

from analyzers.files import classify_file_type, file_type_summary, find_largest_files


def _make_files(root: Path, files: dict[str, str | bytes]) -> None:
    for rel, content in files.items():
        p = root / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        if isinstance(content, bytes):
            p.write_bytes(content)
        else:
            p.write_text(content, encoding="utf-8")


def test_find_largest_files_sorted(tmp_path: Path) -> None:
    _make_files(tmp_path, {
        "a.py": "x" * 100,
        "b.py": "y" * 300,
        "c.py": "z" * 50,
    })
    files = [f for f in tmp_path.iterdir() if f.is_file()]
    largest = find_largest_files(files, tmp_path, top_n=2)
    assert [f.name for f, _ in largest] == ["b.py", "a.py"]


def test_classify_binary_via_nul_byte(tmp_path: Path) -> None:
    text = tmp_path / "file.txt"
    text.write_text("hello\n", encoding="utf-8")
    binary = tmp_path / "file.bin"
    binary.write_bytes(b"\x00\x01\x02\x00")

    assert classify_file_type(text) == "text"
    assert classify_file_type(binary) == "binary"


def test_file_type_summary_counts(tmp_path: Path) -> None:
    _make_files(tmp_path, {
        "a.txt": "text",
        "b.bin": b"\x00\x01",
        "c.md": "more",
    })
    files = [f for f in tmp_path.iterdir() if f.is_file()]
    summary = file_type_summary(files, tmp_path)
    assert summary["text"] == 2
    assert summary["binary"] == 1