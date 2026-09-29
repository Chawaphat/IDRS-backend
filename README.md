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

## Performance
- The patient list and search endpoints load patient summaries with a fixed
	number of database queries, rather than one query per patient.
- Startup creates PostgreSQL indexes for common patient, chart, image, AI, and
	dental-status lookup paths. Existing deployments receive them automatically
	when the backend starts; run a deployment during a low-traffic window for a
	large database because index creation can take time.
- Image signed URLs are cached in the backend process for 23 hours. The source
	URL itself is not stored, and a fresh URL is generated before the 24-hour
	Supabase expiry.
- List endpoints support `skip` and `limit`. Keep `limit` modest for responsive
	UI requests.
