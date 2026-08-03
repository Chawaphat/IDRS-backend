<img width="1391" height="742" alt="image" src="https://github.com/user-attachments/assets/01842a0e-ab0c-4317-a221-38aa76ddba7d" />

# Integrated Dental Record System (IDRS) — Backend

## 📌 Overview
This repository contains the **backend REST API** for IDRS (Integrated Dental Record System), a clinical information system that lets dentists manage patients, run structured dental examinations, and store the results as a relational, auditable dental record. It powers the IDRS frontend web application.

## ✨ Key Features
- **Patient management API** — CRUD endpoints for patient records and clinical profiles.
- **Digital dental charting** — endpoints for dental charts and per-tooth data: caries, fillings, implants, extractions, restorations, periodontal status, vitality, and edentulous status.
- **Structured clinical assessments** — dedicated resources for Medical History, Extraoral Exam, Esthetic Evaluation, Occlusal Analysis, Occlusal Contact, Residual Ridge Assessment, and VDO (vertical dimension) Evaluation.
- **AI detection results** — endpoints to store and retrieve AI-assisted diagnostic outputs tied to a patient's record.
- **Image management** — endpoints for uploading/associating clinical images with a patient chart.
- **Role-aware authentication** — JWT-based auth via Supabase, with dependency-injected guards (`get_current_profile`, `require_admin`, `require_chart_editor`) that restrict write access on clinical data to authorized roles.
- **Auto-provisioned schema** — all SQLModel-defined tables are created on application startup, so a fresh environment is ready to use immediately.
- **Unit-tested services** — backend services are covered by unit tests (see `FullUnitest.md`) to validate business logic independent of the API layer.

## 🛠️ Tech Stack
| Layer | Technology |
|---|---|
| Framework | FastAPI (Python 3.10+) |
| ORM / Data layer | SQLModel on top of SQLAlchemy 2.0 |
| Database | PostgreSQL (via `psycopg2`), hosted on Supabase |
| Auth | Supabase Auth, verified server-side with PyJWT |
| Server | Uvicorn (ASGI) |
| Config | `python-dotenv` for environment-based configuration |

## 🏗️ Architecture (High Level)
```
Client (IDRS Frontend)
        │  HTTPS + JWT (Supabase session)
        ▼
FastAPI App (app/main.py)
  ├── CORS middleware
  ├── Auth dependency layer  (app/core/authen.py) ── verifies JWT, resolves profile & role
  ├── Routers (app/routers/*)      → one router per resource (patients, dental_charts,
  │                                   medical_histories, esthetic_evaluations, occlusal_analyses,
  │                                   extraoral_exams, image_management, ai_detection_results, ...)
  ├── Services (app/services/*)    → business logic per domain, called by routers
  ├── Models (app/models/*)        → SQLModel entities mapped to PostgreSQL tables
  └── Core (app/core/*)            → database engine/session, Supabase client, auth utilities
        │
        ▼
PostgreSQL (Supabase-hosted)
```
The API follows a layered **Router → Service → Model** pattern: routers handle HTTP concerns and auth guards, services encapsulate business/domain logic, and SQLModel models define the persistence schema — keeping request handling, business rules, and data access cleanly separated.

## ⚙️ Setup
```bash
pip install -r requirements.txt

# Required environment variables
DATABASE_URL=...
SUPABASE_URL=...
SUPABASE_KEY=...

uvicorn app.main:app --reload
```

## 🔗 Related Repository
- Frontend: `IDRS-Frontend` (React + TypeScript SPA)

## 📸 Screenshots
<img width="1401" height="713" alt="image" src="https://github.com/user-attachments/assets/4b4e184a-5632-47d4-af38-fb9cb8bc86aa" />
<img width="736" height="640" alt="image" src="https://github.com/user-attachments/assets/f5830854-4ffb-46b7-bfe4-2ce4459c28ef" />
<img width="1400" height="736" alt="image" src="https://github.com/user-attachments/assets/aad82e1d-ca36-41bc-9587-6c9337313cbb" />
<img width="777" height="741" alt="image" src="https://github.com/user-attachments/assets/edb45d8d-11ce-4b3e-9a55-3d4d15178fdd" />
<img width="1410" height="735" alt="image" src="https://github.com/user-attachments/assets/cef49ebe-2a44-4711-834d-737d74b225bd" />
<img width="1395" height="726" alt="image" src="https://github.com/user-attachments/assets/b6541bf8-e650-43a3-ace5-c6d8da64201b" />






