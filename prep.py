import argparse
import hashlib
import os
from pathlib import Path
from io import BytesIO

import pandas as pd
import requests
from PIL import Image

REQUIRED_COLS = [
    "image_url",
    "species_code",
    "common_name",
    "group_id",
    "license",
    "credit",
]


def cmd_validate(csv_path: str) -> None:
    df = pd.read_csv(csv_path)
    missing = [c for c in REQUIRED_COLS if c not in df.columns]
    if missing:
        raise SystemExit(f"Missing columns: {', '.join(missing)}")
    if df[REQUIRED_COLS].isnull().any().any():
        raise SystemExit("Blank values found in required columns")
    print("Validation OK")


def cmd_cache(csv_path: str, out_dir: str) -> None:
    df = pd.read_csv(csv_path)
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    for url in df["image_url"].unique():
        h = hashlib.md5(url.encode()).hexdigest() + ".jpg"
        dest = out / h
        if dest.exists():
            continue
        try:
            resp = requests.get(url, timeout=10)
            resp.raise_for_status()
            img = Image.open(BytesIO(resp.content)).convert("RGB")
            img.save(dest, format="JPEG")
            print(f"cached {url} -> {dest}")
        except Exception as e:
            print(f"failed {url}: {e}")


def cmd_species(taxonomy_csv: str, region: str, out_csv: str) -> None:
    api_key = os.environ.get("EBIRD_API_KEY")
    if not api_key:
        raise SystemExit("EBIRD_API_KEY environment variable is required")

    resp = requests.get(
        f"https://api.ebird.org/v2/product/spplist/{region}",
        headers={"X-eBirdApiToken": api_key},
        timeout=10,
    )
    resp.raise_for_status()
    codes = resp.json()

    tax = pd.read_csv(taxonomy_csv)
    code_col = None
    for col in ("species_code", "speciesCode", "SPECIES_CODE", "speciescode"):
        if col in tax.columns:
            code_col = col
            break
    if code_col is None:
        raise SystemExit("Taxonomy CSV missing species code column")

    subset = tax[tax[code_col].isin(codes)]
    subset = subset.set_index(code_col).loc[codes].reset_index()
    subset.to_csv(out_csv, index=False)
    print(f"Wrote {len(subset)} rows to {out_csv}")


def main(argv=None):
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="cmd", required=True)
    p_val = sub.add_parser("validate")
    p_val.add_argument("csv")
    p_cache = sub.add_parser("cache")
    p_cache.add_argument("--csv", required=True)
    p_cache.add_argument("--dir", required=True)
    p_species = sub.add_parser("species")
    p_species.add_argument("--taxonomy", required=True)
    p_species.add_argument("--region", required=True)
    p_species.add_argument("--out", required=True)
    args = parser.parse_args(argv)
    if args.cmd == "validate":
        cmd_validate(args.csv)
    elif args.cmd == "cache":
        cmd_cache(args.csv, args.dir)
    elif args.cmd == "species":
        cmd_species(args.taxonomy, args.region, args.out)


if __name__ == "__main__":
    main()
