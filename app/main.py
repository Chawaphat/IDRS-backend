from fastapi import FastAPI

from app.core.database import create_db_and_tables
from app.routers import (
    ai_detection_results_router,
    dental_charts_router,
    dental_status_router,
    esthetic_evaluations_router,
    extraoral_exams_router,
    image_management_router,
    occlusal_analyses_router,
    occlusal_contacts_router,
    patients_router,
    profiles_router,
    teeth_router,
    tooth_surfaces_router,
    vdo_evaluations_router,
)

# Import all models so SQLModel metadata is fully registered before create_all.
from app import models as _models

app = FastAPI(title="IDRS Backend", version="1.0.0")


@app.on_event("startup")
def on_startup() -> None:
    create_db_and_tables()


app.include_router(profiles_router)
app.include_router(patients_router)
app.include_router(dental_charts_router)

app.include_router(
    extraoral_exams_router,
    prefix="/dental-charts/{chart_id}/extraoral-exams",
)

app.include_router(esthetic_evaluations_router)
app.include_router(vdo_evaluations_router)
app.include_router(dental_status_router)
app.include_router(teeth_router)
app.include_router(tooth_surfaces_router)
app.include_router(occlusal_analyses_router)
app.include_router(occlusal_contacts_router)
app.include_router(image_management_router)
app.include_router(ai_detection_results_router)
