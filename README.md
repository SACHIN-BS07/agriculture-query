# KrishiSahay AI Backend

Quick steps to run the FastAPI backend locally.

1. Install dependencies

```bash
pip install -r requirements.txt
```

2. Create a `.env` file (or set env var in your shell). Example using PowerShell:

```powershell
$env:GROQ_API_KEY = "your_real_groq_key_here"
```

Or create a `.env` file next to `app.py` containing:

```
GROQ_API_KEY=your_real_groq_key_here
```

3. Run the server with uvicorn

```bash
uvicorn app:app --reload --host 127.0.0.1 --port 8000
```

4. Open `index.html` in your browser (the frontend fetches `http://127.0.0.1:8000/analyze`).

Notes:
- `app.py` reads `GROQ_API_KEY` from environment or `.env` (via `python-dotenv`).
- If the key is not set the backend will return a helpful error.
