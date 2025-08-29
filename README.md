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

The species list is derived from `data/Indiana_Birds.txt`, a Python dictionary mapping eBird species codes to their common names. Image URLs are constructed on the fly using those codes.

## Tests

```powershell
python -m unittest
```
