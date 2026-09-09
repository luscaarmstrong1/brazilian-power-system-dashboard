from scripts.build_model import UF_TO_REGION


def test_uf_region_mapping():
    assert UF_TO_REGION["SP"] == "Southeast"
    assert UF_TO_REGION["BA"] == "Northeast"
