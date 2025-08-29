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

DATA_FILE = Path("data/Indiana_Birds.txt")
JSON_FILE = DATA_FILE.with_suffix(".json")


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
    """Build a DataFrame of birds with image URLs.

    The current implementation assigns all birds to a single group because the
    source mapping does not provide family information in a structured form.
    """

    mapping = load_mapping()
    rows = [
        {
            "species_code": code,
            "common_name": name,
            "group_id": "birds",
            "license": "Unknown",
            "credit": "Unknown",
            "image_url": f"https://cdn.download.ams.birds.cornell.edu/api/v1/asset/{code}/320",
        }
        for code, name in mapping.items()
    ]
    return pd.DataFrame(rows)

