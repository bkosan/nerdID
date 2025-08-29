import argparse
import csv
import hashlib
from pathlib import Path
from typing import Iterable
from urllib import request

REQUIRED_COLS = [
    'image_url', 'species_code', 'common_name',
    'group_id', 'license', 'credit'
]


def validate_csv(path: Path) -> int:
    with open(path, newline='') as f:
        reader = csv.DictReader(f)
        missing = [c for c in REQUIRED_COLS if c not in reader.fieldnames]
        if missing:
            print(f"Missing columns: {', '.join(missing)}")
            return 1
        for i, row in enumerate(reader, 1):
            for col in REQUIRED_COLS:
                if not row.get(col):
                    print(f"Blank value in column '{col}' on line {i+1}")
                    return 1
    print('Validation passed')
    return 0


def url_to_path(url: str, directory: Path) -> Path:
    h = hashlib.sha256(url.encode('utf-8')).hexdigest()
    return directory / f"{h}.jpg"


def cache_images(csv_path: Path, directory: Path) -> int:
    directory.mkdir(parents=True, exist_ok=True)
    with open(csv_path, newline='') as f:
        reader = csv.DictReader(f)
        for row in reader:
            url = row['image_url']
            path = url_to_path(url, directory)
            if path.exists():
                continue
            try:
                with request.urlopen(url) as resp, open(path, 'wb') as out:
                    out.write(resp.read())
                print(f"Cached {url} -> {path}")
            except Exception as exc:
                print(f"Failed {url}: {exc}")
    return 0


def main(argv: Iterable[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest='cmd')

    p_val = sub.add_parser('validate')
    p_val.add_argument('csv', type=Path)

    p_cache = sub.add_parser('cache')
    p_cache.add_argument('--csv', type=Path, required=True)
    p_cache.add_argument('--dir', type=Path, default=Path('cache'))

    args = parser.parse_args(argv)
    if args.cmd == 'validate':
        return validate_csv(args.csv)
    if args.cmd == 'cache':
        return cache_images(args.csv, args.dir)
    parser.print_help()
    return 1


if __name__ == '__main__':
    raise SystemExit(main())
