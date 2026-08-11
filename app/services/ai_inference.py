"""AI model inference service.

This module is a placeholder for the dental panoramic X-ray detection model
(YOLO-based, trained weights in a `.pt` file). The trained weight file has
not been delivered yet, so `predict()` currently returns MOCK data so the
rest of the flow (analysis + results creation) can be tested end-to-end
without a real model or a real image.

Once the `.pt` file is available:
    1. Drop it under e.g. `app/ai_models/dental_yolo.pt`.
    2. Load it once at import time (or lazily, cached) instead of per call.
    3. Replace the body of `predict()` below (remove the MOCK block) so it
       returns a list of `AIPrediction` built from the model's real output.

Expected model output contract (per detected tooth/finding):
    - tooth_number: int (FDI or Universal numbering, matches AI model)
    - condition: dict | list | str  (e.g. "CARIES" or
      {"label": "caries", "score": ...})
    - confidence: float (0.0 - 1.0)
    - bbox: dict | list | str (e.g. {"x": .., "y": .., "w": .., "h": ..} or
      [x1, y1, x2, y2])
"""

from __future__ import annotations

from dataclasses import dataclass

MODEL_NAME = "Dental YOLO"
MODEL_VERSION = "v1.0"

# TODO: remove once the real .pt model is wired up.
USE_MOCK = True


@dataclass
class AIPrediction:
    tooth_number: int
    condition: dict | list | str
    confidence: float
    bbox: dict | list | str


def _mock_predictions() -> list[AIPrediction]:
    """Fake output shaped like what the real YOLO model would return,
    so the create-analysis flow can be exercised without a real image
    or trained weights."""
    return [
        AIPrediction(
            tooth_number=26,
            condition="CARIES",
            confidence=0.91,
            bbox=[120, 340, 180, 400],
        ),
        AIPrediction(
            tooth_number=27,
            condition="CROWN",
            confidence=0.94,
            bbox=[185, 335, 245, 395],
        ),
        AIPrediction(
            tooth_number=36,
            condition="NORMAL",
            confidence=0.88,
            bbox=[300, 500, 360, 560],
        ),
    ]


def predict(image_url: str) -> list[AIPrediction]:
    """Run the dental detection model on the given image and return predictions.

    NOTE: currently returns MOCK data (see `USE_MOCK`) — the trained `.pt`
    model file has not been delivered yet. Wire the real inference call in
    here once it's available.
    """
    if USE_MOCK:
        return _mock_predictions()

    raise NotImplementedError(
        "AI model weights (.pt) have not been added yet. "
        "Implement app.services.ai_inference.predict() once the model file is provided."
    )
