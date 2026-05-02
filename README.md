# habit_tracker_backend

FastAPI service for the habit tracker app.

## Run locally

```bash
cd habit_tracker_backend
python -m venv .venv && source .venv/bin/activate
pip install -e .
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

- API docs: http://127.0.0.1:8000/docs  
- Health: http://127.0.0.1:8000/health  

## CORS

Default allowed origins include the Next dev server on port 3000. Adjust `app/main.py` if your frontend URL differs.
