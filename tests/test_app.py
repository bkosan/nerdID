diff --git a//dev/null b/tests/test_app.py
index 0000000000000000000000000000000000000000..e3ebf7e6fe42151ec42108398369f93ee71ff33d 100644
--- a//dev/null
+++ b/tests/test_app.py
@@ -0,0 +1,124 @@
+import pandas as pd
+from types import SimpleNamespace
+
+import app
+from app import build_options, rerun_app
+
+
+def test_build_options_adds_fallback_species():
+    df = pd.DataFrame([
+        {"species_code": "a", "common_name": "A", "group_id": 1, "image_url": "", "license": "", "credit": ""},
+        {"species_code": "b", "common_name": "B", "group_id": 2, "image_url": "", "license": "", "credit": ""},
+        {"species_code": "c", "common_name": "C", "group_id": 2, "image_url": "", "license": "", "credit": ""},
+        {"species_code": "d", "common_name": "D", "group_id": 3, "image_url": "", "license": "", "credit": ""},
+        {"species_code": "e", "common_name": "E", "group_id": 4, "image_url": "", "license": "", "credit": ""},
+    ])
+    item = df.iloc[0]
+    options = build_options(df, item)
+    assert len(options) == 4
+    assert item.species_code in options.species_code.values
+    assert options["species_code"].is_unique
+
+
+def test_rerun_app_prefers_new_api(monkeypatch):
+    calls = []
+
+    def new_rerun():
+        calls.append("new")
+
+    def old_rerun():
+        calls.append("old")
+
+    dummy = SimpleNamespace(rerun=new_rerun, experimental_rerun=old_rerun)
+    monkeypatch.setattr(app, "st", dummy)
+
+    rerun_app()
+    assert calls == ["new"]
+
+
+def test_rerun_app_falls_back_to_experimental(monkeypatch):
+    calls = []
+
+    def old_rerun():
+        calls.append("old")
+
+    dummy = SimpleNamespace(experimental_rerun=old_rerun)
+    monkeypatch.setattr(app, "st", dummy)
+
+    rerun_app()
+    assert calls == ["old"]
+
+
+def test_question_persists_until_submit(monkeypatch, tmp_path):
+    df = pd.DataFrame(
+        [
+            {
+                "species_code": "a",
+                "common_name": "A",
+                "group_id": 1,
+                "image_url": "",
+                "license": "",
+                "credit": "",
+            }
+        ]
+    )
+
+    calls = {"pick": 0}
+
+    def fake_pick(df, conn):
+        calls["pick"] += 1
+        return df.iloc[0]
+
+    def fake_build(df, item, n=4):
+        return pd.concat([df.iloc[:1]] * 4).reset_index(drop=True)
+
+    class Sess(dict):
+        __getattr__ = dict.get
+        __setattr__ = dict.__setitem__
+
+    session_state = Sess()
+
+    def radio(label, opts, index=None, key=None):
+        val = session_state.get(key, opts[0])
+        session_state[key] = val
+        return val
+
+    dummy_st = SimpleNamespace(
+        session_state=session_state,
+        image=lambda *a, **k: None,
+        write=lambda *a, **k: None,
+        radio=radio,
+        button=lambda label: False,
+        sidebar=SimpleNamespace(metric=lambda *a, **k: None, bar_chart=lambda *a, **k: None),
+    )
+
+    rev_path = tmp_path / "reviews.csv"
+
+    def fake_read_csv(path, *a, **k):
+        if str(path) == str(rev_path):
+            return pd.DataFrame([
+                {"species_code": "a", "correct": 1},
+            ])
+        return df
+
+    monkeypatch.setattr(app, "st", dummy_st)
+    monkeypatch.setattr(app.pd, "read_csv", fake_read_csv)
+    monkeypatch.setattr(app, "pick_item", fake_pick)
+    monkeypatch.setattr(app, "build_options", fake_build)
+    monkeypatch.setattr(app, "get_image", lambda url: None)
+    monkeypatch.setattr(app, "get_conn", lambda: None)
+    monkeypatch.setattr(app, "load_state", lambda conn, code: {})
+    monkeypatch.setattr(app, "save_state", lambda conn, code, state: None)
+    monkeypatch.setattr(app, "sr", SimpleNamespace(schedule=lambda state, grade: state))
+    monkeypatch.setattr(app, "REVIEWS_CSV", rev_path)
+    monkeypatch.setattr(app, "rerun_app", lambda: None)
+
+    app.main()
+    assert calls["pick"] == 1
+
+    app.main()
+    assert calls["pick"] == 1
+
+    dummy_st.button = lambda label: True
+    app.main()
+    assert calls["pick"] == 2
