from pathlib import Path


def test_capacity_generation_are_separate_files():
    root = Path(__file__).resolve().parents[1]
    assert (root / "scripts" / "build_model.py").exists()
    text = (root / "powerbi" / "data_model.md").read_text(encoding="utf-8")
    assert "Fato_CapacidadeInstalada" in text
    assert "Fato_Geracao" in text
