from pathlib import Path


def test_unit_names_keep_power_energy_separate():
    root = Path(__file__).resolve().parents[1]
    dax = (root / "powerbi" / "dax_measures.md").read_text(encoding="utf-8")
    assert "MWmed" in dax
    assert "R$/MWh" in (root / "docs" / "data_sources.md").read_text(encoding="utf-8")
    assert "Do not add to MW capacity" in dax
