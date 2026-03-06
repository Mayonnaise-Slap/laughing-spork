lint:
    uvx ruff format .
    uvx ruff check .

dev:
    uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
