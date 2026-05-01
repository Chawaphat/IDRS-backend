from app.routers.ai_detection_results import router as ai_detection_results_router
from app.routers.dental_charts import router as dental_charts_router
from app.routers.dental_status import router as dental_status_router
from app.routers.esthetic_evaluations import (
	router as esthetic_evaluations_router,
	admin_router as esthetic_evaluations_admin_router,
)
from app.routers.extraoral_exams import (
    router as extraoral_exams_router,
    admin_router as extraoral_exams_admin_router,
)
from app.routers.image_management import router as image_management_router
from app.routers.occlusal_analyses import (
    router as occlusal_analyses_router,
    admin_router as occlusal_analyses_admin_router)

from app.routers.occlusal_contact import router as occlusal_contacts_router
from app.routers.patients import router as patients_router
from app.routers.profiles import router as profiles_router
from app.routers.teeth import router as teeth_router
from app.routers.tooth_surfaces import router as tooth_surfaces_router
from app.routers.vdo_evaluations import (
	router as vdo_evaluations_router,
	admin_router as vdo_evaluations_admin_router,
)
from app.routers.medical_histories import (
    router as medical_histories_router,
    admin_router as medical_histories_admin_router,
)


__all__ = [
	"ai_detection_results_router",
	"dental_charts_router",
	"dental_status_router",
	"medical_histories_router",
 	"medical_histories_admin_router",
	"esthetic_evaluations_router",
	"esthetic_evaluations_admin_router",
	"extraoral_exams_router",
	"extraoral_exams_admin_router",
	"image_management_router",
	"occlusal_analyses_router",
 	"occlusal_analyses_admin_router",
	"occlusal_contacts_router",
	"patients_router",
	"profiles_router",
	"teeth_router",
	"tooth_surfaces_router",
	"vdo_evaluations_router",
	"vdo_evaluations_admin_router",
	
]
