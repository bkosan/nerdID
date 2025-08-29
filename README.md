# nerdID

Simple Streamlit app for bird identification practice. The app quizzes you with one image and four options, logs your attempts, and tracks spaced-repetition state.

## Setup (Windows PowerShell)

```powershell
python -m venv .venv
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1
pip install streamlit pandas requests pillow
```

## Running the app

```powershell
streamlit run app.py
```

## Preparing data

```powershell
python prep.py validate data/items.csv
python prep.py cache --csv data/items.csv --dir cache
```

## Tests

```powershell
python -m unittest
```

Replace the placeholder image URLs in `data/items.csv` with real Macaulay Library assets and fill in the proper license and credit information.
