from __future__ import annotations

"""Utilities for loading Indiana bird data.

This module reads the ``Indiana_Birds.txt`` mapping and converts it into
structures that the app can use. The file contains a Python dictionary mapping
eBird species codes to their common names. We optionally write out a JSON copy
for reuse in other parts of the application.
"""

from pathlib import Path
import json
from typing import Dict

import pandas as pd
import requests

DATA_FILE = Path("data/Indiana_Birds.txt")
JSON_FILE = DATA_FILE.with_suffix(".json")
MEDIA_CACHE_FILE = Path("data/media_cache.json")


def load_mapping() -> Dict[str, str]:
    """Return the mapping of eBird codes to common names.

    The source file is a small Python script that defines
    ``indiana_birds_mapping``. We ``exec`` the file in a temporary namespace and
    return the resulting dictionary. A JSON representation is written next to
    the source file for convenience if it does not already exist.
    """

    namespace: Dict[str, Dict[str, str]] = {}
    with DATA_FILE.open() as f:
        code = f.read()
    exec(code, namespace)
    mapping = namespace.get("indiana_birds_mapping", {})

    if not JSON_FILE.exists():
        JSON_FILE.write_text(json.dumps(mapping, indent=2))
    return mapping


def load_items_df() -> pd.DataFrame:
    """Build a DataFrame of birds.

    The current implementation assigns all birds to a single group because the
    source mapping does not provide family information in a structured form.
    ``get_media`` can be used to retrieve an embed snippet for any species code
    when needed.
    """

    mapping = load_mapping()
    rows = [
        {
            "species_code": code,
            "common_name": name,
            "group_id": "birds",
        }
        for code, name in mapping.items()
    ]
    return pd.DataFrame(rows)


def _load_cache() -> Dict[str, Dict[str, str]]:
    if MEDIA_CACHE_FILE.exists():
        return json.loads(MEDIA_CACHE_FILE.read_text())
    return {}


_MEDIA_CACHE = _load_cache()


def get_media(code: str) -> Dict[str, str]:
    """Return embed HTML and attribution for *code* using eBird's API.

    Results are cached on disk so species only require a network request once.
    When the API is unreachable or returns unexpected data, we fall back to
    placeholders so the app can still function.
    """

    if code in _MEDIA_CACHE:
        return _MEDIA_CACHE[code]

    try:
        search_resp = requests.get(
            "https://search.macaulaylibrary.org/api/v1/search",
            params={"taxonCode": code, "mediaType": "photo", "limit": 1, "sort": "rating_rank_desc"},
            timeout=10,
        )
        search_resp.raise_for_status()
        search_data = search_resp.json()
        result = search_data.get("results", [{}])[0]
        asset_id = result.get("assetId")
        license_code = result.get("licenseCode", "Unknown")
        credit = result.get("userDisplayName", "Unknown")

        embed_resp = requests.get(
            f"https://media.ebird.org/catalog/oembed?url=https://macaulaylibrary.org/asset/{asset_id}",
            timeout=10,
        )
        embed_resp.raise_for_status()
        embed_html = embed_resp.json().get("html", "")

        info = {"embed_html": embed_html, "license": license_code, "credit": credit}
    except Exception:
        info = {"embed_html": "", "license": "Unknown", "credit": "Unknown"}

    _MEDIA_CACHE[code] = info
    try:
        MEDIA_CACHE_FILE.write_text(json.dumps(_MEDIA_CACHE, indent=2))
    except Exception:
        pass
    return info
