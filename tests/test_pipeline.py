from pathlib import Path


def test_pipeline_entrypoint_exists():
    root = Path(__file__).resolve().parents[1]
    assert (root / "scripts" / "update_all.py").exists()
    assert (root / "config" / "config.yaml").exists()
