from pathlib import Path


def test_load_scope_documented_as_sin():
    root = Path(__file__).resolve().parents[1]
    text = (root / "README.md").read_text(encoding="utf-8")
    assert "SIN" in text
    assert "Brazil is not always" in text
