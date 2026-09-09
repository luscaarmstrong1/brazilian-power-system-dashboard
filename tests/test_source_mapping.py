from src.source_mapping import classify_source


def test_renewable_mapping():
    assert classify_source("UFV")["FonteAgrupada"] == "Solar"
    assert classify_source("EOL")["Renovavel"] is True
    assert classify_source("Carvao mineral")["Renovavel"] is False
