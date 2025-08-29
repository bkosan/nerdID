import pandas as pd
from app import build_options


def test_build_options_adds_fallback_species():
    df = pd.DataFrame([
        {"species_code": "a", "common_name": "A", "group_id": 1, "image_url": "", "license": "", "credit": ""},
        {"species_code": "b", "common_name": "B", "group_id": 2, "image_url": "", "license": "", "credit": ""},
        {"species_code": "c", "common_name": "C", "group_id": 2, "image_url": "", "license": "", "credit": ""},
        {"species_code": "d", "common_name": "D", "group_id": 3, "image_url": "", "license": "", "credit": ""},
        {"species_code": "e", "common_name": "E", "group_id": 4, "image_url": "", "license": "", "credit": ""},
    ])
    item = df.iloc[0]
    options = build_options(df, item)
    assert len(options) == 4
    assert item.species_code in options.species_code.values
    assert options["species_code"].is_unique
