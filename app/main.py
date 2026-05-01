from fastapi import FastAPI

from app.core.database import create_db_and_tables
from app.routers import (
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
    teeth_router,
    tooth_surfaces_router,
    vdo_evaluations_router,
    vdo_evaluations_admin_router,
)

# Import all models so SQLModel metadata is fully registered before create_all.
from app import models as _models

app = FastAPI(title="IDRS Backend", version="1.0.0")


@app.on_event("startup")
def on_startup() -> None:
    create_db_and_tables()


app.include_router(
    profiles_router,
    prefix="/profiles",
    tags=["profiles"],
)

app.include_router(
    patients_router, 
    prefix="/patients", 
    tags=["patients"]
    )

app.include_router(
    dental_charts_router,
    prefix="/dental-charts", 
    tags=["dental-charts"]
    )

app.include_router(
    medical_histories_router,
    prefix="/dental-charts/{chart_id}/medical-history",
    tags=["medical-history"],
    )
app.include_router(
    medical_histories_admin_router,
    prefix="/medical-history",
    tags=["medical-history-admin"],
    )

app.include_router(
    extraoral_exams_router,
    prefix="/dental-charts/{chart_id}/extraoral-exams",
    tags=["extraoral-exams"],
    )
app.include_router(
    extraoral_exams_admin_router,
    prefix="/extraoral-exams",
    tags=["extraoral-exams-admin"],
    )

app.include_router(
    esthetic_evaluations_router,
    prefix="/dental-charts/{chart_id}/esthetic-evaluation",
    tags=["esthetic-evaluation"],
)
app.include_router(
    esthetic_evaluations_admin_router,
    prefix="/esthetic-evaluation",
    tags=["esthetic-evaluation-admin"],
)

app.include_router(
    vdo_evaluations_router,
    prefix="/dental-charts/{chart_id}/vdo-evaluation",
    tags=["vdo-evaluation"],
)
app.include_router(
    vdo_evaluations_admin_router,
    prefix="/vdo-evaluation",
    tags=["vdo-evaluation-admin"],
)
app.include_router(dental_status_router)
app.include_router(teeth_router)
app.include_router(tooth_surfaces_router)

app.include_router(
    occlusal_analyses_router,
    prefix="/dental-charts/{chart_id}/occlusal-analysis",
    tags=["occlusal-analysis"],)

app.include_router(
    occlusal_analyses_admin_router,
    prefix="/occlusal-analysis",
    tags=["occlusal-analysis-admin"],
)

app.include_router(
    occlusal_contacts_router,
    prefix="/dental-charts/{chart_id}/occlusal-contacts",
    tags=["occlusal-contacts"],
    )


app.include_router(
    image_management_router,
    prefix="/dental-charts/{chart_id}/images",
    tags=["image-management"],
    )


app.include_router(
    ai_detection_results_router,
    prefix="/ai-detection-results",
    tags=["ai-detection-results"],
    )
