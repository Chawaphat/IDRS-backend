from fastapi import FastAPI, Depends
from dotenv import load_dotenv

load_dotenv()

from app.core.database import create_db_and_tables
from app.core.authen import get_current_profile, require_admin, require_chart_editor
from app.routers import (
    auth_router,
    ai_detection_results_router,
    dental_charts_router,
    dental_status_router,
    medical_histories_router,
    medical_histories_admin_router,
    esthetic_evaluations_router,
    esthetic_evaluations_admin_router,
    extraoral_exams_router,
    extraoral_exams_admin_router,
    image_management_router,
    occlusal_analyses_router,
    occlusal_analyses_admin_router,
    occlusal_contacts_router,
    patients_router,
    profiles_router,
    vdo_evaluations_router,
    vdo_evaluations_admin_router,
    residual_ridge_assessments_router,
    residual_ridge_assessments_admin_router,
)

# Import all models so SQLModel metadata is fully registered before create_all.
from app import models as _models
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="IDRS Backend", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"], # Adjust to your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def on_startup() -> None:
    create_db_and_tables()


app.include_router(
    auth_router,
    prefix="/auth",
    tags=["auth"],
)

app.include_router(
    profiles_router,
    prefix="/profiles",
    tags=["profiles"],
    # Users handle their own auth inside the router
)

app.include_router(
    patients_router, 
    prefix="/patients", 
    tags=["patients"],
    dependencies=[Depends(require_chart_editor)]
)

app.include_router(
    dental_charts_router,
    prefix="/dental-charts", 
    tags=["dental-charts"],
    dependencies=[Depends(require_chart_editor)]
)

app.include_router(
    medical_histories_router,
    prefix="/dental-charts/{chart_id}/medical-history",
    tags=["medical-history"],
    dependencies=[Depends(require_chart_editor)]
)
app.include_router(
    medical_histories_admin_router,
    prefix="/medical-history",
    tags=["medical-history-admin"],
    dependencies=[Depends(require_admin)]
)

app.include_router(
    extraoral_exams_router,
    prefix="/dental-charts/{chart_id}/extraoral-exams",
    tags=["extraoral-exams"],
    dependencies=[Depends(require_chart_editor)]
)
app.include_router(
    extraoral_exams_admin_router,
    prefix="/extraoral-exams",
    tags=["extraoral-exams-admin"],
    dependencies=[Depends(require_admin)]
)

app.include_router(
    esthetic_evaluations_router,
    prefix="/dental-charts/{chart_id}/esthetic-evaluation",
    tags=["esthetic-evaluation"],
    dependencies=[Depends(require_chart_editor)]
)
app.include_router(
    esthetic_evaluations_admin_router,
    prefix="/esthetic-evaluation",
    tags=["esthetic-evaluation-admin"],
    dependencies=[Depends(require_admin)]
)

app.include_router(
    vdo_evaluations_router,
    prefix="/dental-charts/{chart_id}/vdo-evaluation",
    tags=["vdo-evaluation"],
    dependencies=[Depends(require_chart_editor)]
)
app.include_router(
    vdo_evaluations_admin_router,
    prefix="/vdo-evaluation",
    tags=["vdo-evaluation-admin"],
    dependencies=[Depends(require_admin)]
)
app.include_router(
    residual_ridge_assessments_router,
    prefix="/dental-charts/{chart_id}/residual-ridge-assessment",
    tags=["residual-ridge-assessment"],
    dependencies=[Depends(require_chart_editor)]
)
app.include_router(
    residual_ridge_assessments_admin_router,
    prefix="/residual-ridge-assessment",
    tags=["residual-ridge-assessment-admin"],
    dependencies=[Depends(require_admin)]
)

app.include_router(
    dental_status_router,
    prefix="/dental-charts/{chart_id}/dental-status",
    tags=["dental-status"],
    dependencies=[Depends(require_chart_editor)]
)

app.include_router(
    occlusal_analyses_router,
    prefix="/dental-charts/{chart_id}/occlusal-analysis",
    tags=["occlusal-analysis"],
    dependencies=[Depends(require_chart_editor)]
)

app.include_router(
    occlusal_analyses_admin_router,
    prefix="/occlusal-analysis",
    tags=["occlusal-analysis-admin"],
    dependencies=[Depends(require_admin)]
)

app.include_router(
    occlusal_contacts_router,
    prefix="/dental-charts/{chart_id}/occlusal-contacts",
    tags=["occlusal-contacts"],
    dependencies=[Depends(require_chart_editor)]
)

app.include_router(
    image_management_router,
    prefix="/dental-charts/{chart_id}/images",
    tags=["image-management"],
    dependencies=[Depends(require_chart_editor)]
)

app.include_router(
    ai_detection_results_router,
    prefix="/ai-detection-results",
    tags=["ai-detection-results"],
    dependencies=[Depends(require_chart_editor)]
)
