import pandas as pd
from types import SimpleNamespace

import app
from app import build_options, rerun_app


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


def test_rerun_app_prefers_new_api(monkeypatch):
    calls = []

    def new_rerun():
        calls.append("new")

    def old_rerun():
        calls.append("old")

    dummy = SimpleNamespace(rerun=new_rerun, experimental_rerun=old_rerun)
    monkeypatch.setattr(app, "st", dummy)

    rerun_app()
    assert calls == ["new"]


def test_rerun_app_falls_back_to_experimental(monkeypatch):
    calls = []

    def old_rerun():
        calls.append("old")

    dummy = SimpleNamespace(experimental_rerun=old_rerun)
    monkeypatch.setattr(app, "st", dummy)

    rerun_app()
    assert calls == ["old"]
