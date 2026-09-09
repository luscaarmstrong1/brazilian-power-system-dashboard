from pathlib import Path


def test_mmgd_is_separate_module():
    root = Path(__file__).resolve().parents[1]
    text = (root / "README.md").read_text(encoding="utf-8")
    assert "MMGD is modeled separately" in text
