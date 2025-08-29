import pandas as pd
import numpy as np
from types import SimpleNamespace

import app
from app import build_options, rerun_app


def test_build_options_adds_fallback_species():
    df = pd.DataFrame([
        {"species_code": "a", "common_name": "A", "group_id": 1},
        {"species_code": "b", "common_name": "B", "group_id": 2},
        {"species_code": "c", "common_name": "C", "group_id": 2},
        {"species_code": "d", "common_name": "D", "group_id": 3},
        {"species_code": "e", "common_name": "E", "group_id": 4},
    ])
    item = df.iloc[0]
    options = build_options(df, item)
    assert len(options) == 4
    assert item.species_code in options.species_code.values
    assert options["species_code"].is_unique


def test_build_options_keeps_correct_when_group_large():
    np.random.seed(0)
    df = pd.DataFrame(
        [{"species_code": s, "common_name": s.upper(), "group_id": 1} for s in list("abcde")]
    )
    item = df.iloc[0]
    options = build_options(df, item)
    assert item.species_code in options.species_code.values
    assert len(options) == 4


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