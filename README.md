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


The species list is derived from `data/Indiana_Birds.txt`, a Python dictionary mapping eBird species codes to their common names. Images and attribution are pulled dynamically from eBird's embed API so photos always include proper credit.

## Tests

```powershell
pytest -q
```
