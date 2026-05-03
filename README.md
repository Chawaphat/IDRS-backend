# IDRS Backend

FastAPI backend for the IDRS system. Provides REST APIs for dental charts, evaluations, medical histories, images, and related data.

## Requirements
- Python 3.10+
- PostgreSQL (local or remote)

## Setup
1. Create a virtual environment and install dependencies:
	- `pip install -r requirements.txt`
2. Configure environment variables (see `.env.example` if present):
	- `DATABASE_URL`
	- `SUPABASE_URL`
	- `SUPABASE_KEY`
	- Optional: `DB_POOL_SIZE`, `DB_MAX_OVERFLOW`, `DB_POOL_TIMEOUT`, `DB_POOL_RECYCLE`, `DB_POOL_PRE_PING`

## Run
- `uvicorn app.main:app --reload`

## Notes
- Database tables are created on startup via SQLModel metadata.
