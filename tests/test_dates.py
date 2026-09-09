from scripts.build_model import parse_date


def test_parse_common_dates():
    assert parse_date("2026-09-08") == "2026-09-08"
    assert parse_date("08/09/2026") == "2026-09-08"
