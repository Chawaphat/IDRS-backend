import os
import uuid
from app.models.profile import Profile
import jwt

from jwt import PyJWKClient
from fastapi import HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from supabase_auth import Session

from app.core.database import get_session

security = HTTPBearer()

SUPABASE_JWKS_URL = os.getenv("SUPABASE_JWKS_URL")

jwks_client = PyJWKClient(SUPABASE_JWKS_URL)

def verify_token(
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    token = credentials.credentials

    try:
        signing_key = jwks_client.get_signing_key_from_jwt(token)

        payload = jwt.decode(
            token,
            signing_key.key,
            algorithms=["ES256"],
            audience="authenticated"
        )

        return payload

    except Exception:
        raise HTTPException(
            status_code=401,
            detail="Invalid or expired token"
        )
        
def get_current_profile(
    payload = Depends(verify_token),
    session: Session = Depends(get_session)
):
    user_id = payload["sub"]

    profile = session.get(Profile, user_id)

    if not profile:
        raise HTTPException(
            status_code=404,
            detail="Profile not found"
        )

    return profile

def require_admin(
    current_user: Profile = Depends(get_current_profile)
):
    if current_user.role != "admin":
        raise HTTPException(403,detail="Admin access required")

    return current_user

def require_profile_owner(
    profile_id: uuid.UUID,
    current_user: Profile = Depends(get_current_profile)
):
    if (
        current_user.id != profile_id
    ):
        raise HTTPException(
            status_code=403,
            detail="Not authorized"
        )

    return current_user

def require_dentist(
    current_user: Profile = Depends(get_current_profile)
):
    if current_user.role != "dentist":
        raise HTTPException(403,detail="Dentist access required")

    return current_user

def require_assistant(
    current_user: Profile = Depends(get_current_profile)
):
    if current_user.role != "assistant":
        raise HTTPException(403,detail="Assistant access required")

    return current_user

def require_chart_editor(
    current_user: Profile = Depends(get_current_profile)
):
    allowed_roles = ["dentist", "assistant", "admin"]

    if current_user.role not in allowed_roles:
        raise HTTPException(
            status_code=403,
            detail="Chart editing access required"
        )

    return current_user

def require_chart_owner(
    chart_id: uuid.UUID,
    session: Session = Depends(get_session),
    current_user: Profile = Depends(require_chart_editor)
):
    from app.models.dental_chart import DentalChart
    chart = session.get(DentalChart, chart_id)
    if not chart:
        raise HTTPException(status_code=404, detail="Dental chart not found")
        
    if current_user.role == "dentist" and chart.dentist_id != current_user.id:
        raise HTTPException(
            status_code=403, 
            detail="Not authorized. You are not the owner of this chart."
        )
        
    return current_user