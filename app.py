import random
import time
from datetime import date, datetime
from pathlib import Path

import pandas as pd
import sqlite3
import streamlit as st
import streamlit.components.v1 as components

import sr
from birds import load_items_df, get_media

REVIEWS_CSV = Path("data/reviews.csv")
DB_PATH = Path("data/sr_state.sqlite")


def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS sr_state (
            species_code TEXT PRIMARY KEY,
            reps INTEGER,
            interval_days INTEGER,
            easiness REAL,
            due_at TEXT
        )
        """
    )
    return conn


def load_state(conn, code):
    cur = conn.execute(
        "SELECT reps, interval_days, easiness, due_at FROM sr_state WHERE species_code=?",
        (code,),
    )
    row = cur.fetchone()
@@ -47,121 +43,109 @@ def load_state(conn, code):
            "reps": reps,
            "interval_days": interval,
            "easiness": easiness,
            "due_at": due_at,
        }
    return {
        "reps": 0,
        "interval_days": 0,
        "easiness": 2.5,
        "due_at": date.today().isoformat(),
    }


def save_state(conn, code, state):
    conn.execute(
        "REPLACE INTO sr_state (species_code,reps,interval_days,easiness,due_at) VALUES (?,?,?,?,?)",
        (
            code,
            state["reps"],
            state["interval_days"],
            state["easiness"],
            state["due_at"],
        ),
    )
    conn.commit()
def pick_item(df, conn):
    today = date.today().isoformat()
    due_codes = [
        code
        for code in df["species_code"].unique()
        if load_state(conn, code)["due_at"] <= today
    ]
    pool = df[df["species_code"].isin(due_codes)] if due_codes else df
    return pool.sample(1).iloc[0]


def build_options(df: pd.DataFrame, item: pd.Series, n: int = 4) -> pd.DataFrame:
    """Return *n* answer options including the correct species.

    If the item's group does not contain enough species to provide all
    options, the remaining slots are filled with random species from other
    groups. The returned DataFrame is shuffled and contains one row per
    species.
    """

    item_df = item.to_frame().T
    group = df[df.group_id == item.group_id].drop_duplicates("species_code")
    group = group[group.species_code != item.species_code]

    needed = n - 1
    from_group = group.sample(min(len(group), needed)) if not group.empty else pd.DataFrame(columns=df.columns)
    needed -= len(from_group)
    if needed > 0:
        others = df[df.group_id != item.group_id].drop_duplicates("species_code")
        from_others = others.sample(min(len(others), needed)) if not others.empty else pd.DataFrame(columns=df.columns)
    else:
        from_others = pd.DataFrame(columns=df.columns)

    options = pd.concat([item_df, from_group, from_others]).sample(frac=1).reset_index(drop=True)
    return options

def rerun_app() -> None:
    """Rerun the Streamlit app using the available API.

    Streamlit renamed ``st.experimental_rerun`` to ``st.rerun`` in newer
    versions. This helper calls the preferred ``st.rerun`` when present while
    remaining compatible with older versions.
    """

    if hasattr(st, "rerun"):
        st.rerun()
    else:  # pragma: no cover - exercised in a test with a stub
        st.experimental_rerun()

def main():
    df = load_items_df()
    conn = get_conn()
    item = pick_item(df, conn)
    options = build_options(df, item)
    correct_index = int(options.index[options.species_code == item.species_code][0])

    media = get_media(item.species_code)
    if media["embed_html"]:
        components.html(media["embed_html"], height=300)
    else:
        st.write("Image unavailable")

    if "start_time" not in st.session_state:
        st.session_state.start_time = time.time()
    choice = st.radio("Which bird is this?", options["common_name"].tolist())

    if st.button("Submit"):
        elapsed = int((time.time() - st.session_state.start_time) * 1000)
        correct = choice == item.common_name
        st.write("Correct!" if correct else f"Nope, it was {item.common_name}")
        with REVIEWS_CSV.open("a") as f:
            chosen_code = options.loc[options.common_name == choice, "species_code"].iloc[0]
            f.write(
                f"{datetime.utcnow().isoformat()},{item.species_code},{chosen_code},{int(correct)},{elapsed}\n"
            )
        grade = 5 if correct else 2
        state = load_state(conn, item.species_code)
        new_state = sr.schedule(state, grade)
        save_state(conn, item.species_code, new_state)
        st.session_state.start_time = time.time()
        rerun_app()

    if REVIEWS_CSV.exists():
        df_rev = pd.read_csv(REVIEWS_CSV)