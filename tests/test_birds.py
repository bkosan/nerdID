import birds


def test_get_media_fetches_and_caches(tmp_path, monkeypatch):
    search_data = {"results": [{"assetId": 123, "licenseCode": "CC", "userDisplayName": "Jane"}]}
    embed_data = {"html": "<div>embed</div>"}

    calls = []

    def fake_get(url, params=None, timeout=10):
        calls.append(url)
        class R:
            def __init__(self, data):
                self._data = data
            def raise_for_status(self):
                pass
            def json(self):
                return self._data
        if "search.macaulaylibrary.org" in url:
            assert params["taxonCode"] == "code"
            return R(search_data)
        elif "media.ebird.org" in url:
            assert "123" in url
            return R(embed_data)
        raise AssertionError("unexpected url")

    monkeypatch.setattr(birds.requests, "get", fake_get)
    cache_file = tmp_path / "cache.json"
    monkeypatch.setattr(birds, "MEDIA_CACHE_FILE", cache_file)
    # reload cache after patching file path
    monkeypatch.setattr(birds, "_MEDIA_CACHE", {})

    info = birds.get_media("code")
    assert info == {"embed_html": "<div>embed</div>", "license": "CC", "credit": "Jane"}
    # Second call should use cache and avoid extra network calls
    calls.clear()
    info2 = birds.get_media("code")
    assert info2 == info
    assert calls == []
