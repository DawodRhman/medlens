# Backend (FastAPI)


Quick start:

1. Create a virtual environment and install dependencies:
	```powershell
	python -m venv .venv; .\.venv\Scripts\Activate.ps1
	pip install -r requirements.txt
	pip install alembic
	```

2. Initialize the database (PostgreSQL must be running):
	```powershell
	alembic upgrade head
	python app/db/seed_admin.py
	```

3. Run the app locally:
	```powershell
	uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
	```

API docs available at `/docs` once server runs.
