import os
import csv
import hashlib
import random
from datetime import datetime

import pandas as pd
import streamlit as st
import requests

DATA_CSV = os.path.join('data', 'items.csv')
REVIEWS_CSV = os.path.join('data', 'reviews.csv')
CACHE_DIR = 'cache'


def url_to_path(url: str) -> str:
    """Return cache path for a URL."""
    h = hashlib.sha256(url.encode('utf-8')).hexdigest()
    return os.path.join(CACHE_DIR, f"{h}.jpg")


def get_image_path(url: str) -> str:
    """Download image if not cached and return local path."""
    os.makedirs(CACHE_DIR, exist_ok=True)
    path = url_to_path(url)
    if not os.path.exists(path):
        try:
            resp = requests.get(url, timeout=10)
            resp.raise_for_status()
            with open(path, 'wb') as f:
                f.write(resp.content)
        except Exception as exc:
            st.error(f"Could not download image: {exc}")
    return path


def log_attempt(image_url: str, species_code: str, choice: str, correct: bool) -> None:
    os.makedirs(os.path.dirname(REVIEWS_CSV), exist_ok=True)
    exists = os.path.exists(REVIEWS_CSV)
    with open(REVIEWS_CSV, 'a', newline='') as f:
        writer = csv.writer(f)
        if not exists:
            writer.writerow(['timestamp', 'image_url', 'species_code', 'choice', 'correct'])
        writer.writerow([
            datetime.utcnow().isoformat(),
            image_url,
            species_code,
            choice,
            int(correct),
        ])


def load_stats():
    if not os.path.exists(REVIEWS_CSV):
        return None, None
    df = pd.read_csv(REVIEWS_CSV)
    overall = df['correct'].mean()
    by_species = df.groupby('species_code')['correct'].mean()
    return overall, by_species


@st.cache_data
def load_items():
    return pd.read_csv(DATA_CSV)


def pick_question(df):
    row = df.sample(1).iloc[0]
    others = df[df['species_code'] != row['species_code']]
    choices = list(others.sample(min(3, len(others)))['common_name'])
    choices.append(row['common_name'])
    random.shuffle(choices)
    return row, choices


def main():
    st.title('NerdID Quiz')
    df = load_items()

    if 'question' not in st.session_state:
        row, choices = pick_question(df)
        st.session_state.question = (row, choices)

    row, choices = st.session_state.question
    img_path = get_image_path(row['image_url'])
    st.image(img_path, width=400)
    choice = st.radio('What species is this?', choices, index=None)

    if st.button('Submit') and choice:
        correct = (choice == row['common_name'])
        log_attempt(row['image_url'], row['species_code'], choice, correct)
        st.success('Correct!' if correct else f"Incorrect: {row['common_name']}")
        row, choices = pick_question(df)
        st.session_state.question = (row, choices)

    overall, by_species = load_stats()
    if overall is not None:
        st.write(f"Overall accuracy: {overall:.1%}")
        st.write('Accuracy by species:')
        st.dataframe(by_species)


if __name__ == '__main__':
    main()
