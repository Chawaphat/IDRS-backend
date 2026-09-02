"""Standalone AI Analysis endpoint — the "AI Analysis" tab in the main menu.

Unlike `ai_detection_results` (chart-scoped: persists a result against an
`image_management` row), this endpoint just runs the model on an uploaded
file and returns the raw detection payload. Nothing is written to the
database and no patient/chart association is required — it exists so a
dentist can try the model on any panoramic X-ray without first creating a
patient record.
"""
from __future__ import annotations

import os
import tempfile

from fastapi import APIRouter, File, Form, HTTPException, UploadFile

from app.services import ai_inference

router = APIRouter()

ALLOWED_CONTENT_TYPES = {"image/jpeg", "image/jpg", "image/png", "image/webp"}


@router.post("/detect")
async def detect_endpoint(
    file: UploadFile = File(...),
    conf: float = Form(ai_inference.DEFAULT_CONF_THRESHOLD),
) -> dict:
    if file.content_type not in ALLOWED_CONTENT_TYPES:
        raise HTTPException(status_code=400, detail="File must be a JPG, PNG, or WebP image")

    raw = await file.read()
    if not raw:
        raise HTTPException(status_code=400, detail="Uploaded file is empty")

    suffix = os.path.splitext(file.filename or "")[1] or ".png"
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        tmp.write(raw)
        tmp_path = tmp.name

    try:
        output = ai_inference.predict(tmp_path, conf_threshold=conf)
    except Exception as exc:  # model/IO failure — surface as a clean 500, not a stack trace
        raise HTTPException(status_code=500, detail=f"AI detection failed: {exc}") from exc
    finally:
        os.remove(tmp_path)

    # `raw` already has the shape the frontend needs: image_size, detections[], teeth[].
    # Drop the temp filesystem path — it's meaningless to the client.
    output.raw.pop("image", None)
    return output.raw
