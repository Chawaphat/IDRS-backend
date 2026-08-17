"""AI model inference service.

Runs the Dentex dental panoramic X-ray detection pipeline:
    1. U-Net (SEUNet) segments the 32 FDI teeth positions in the X-ray.
    2. YOLOv8 detects 4 disease classes (Impacted, Caries, Periapical Lesion,
       Deep Caries) as bounding boxes.
    3. Each disease box is matched to the tooth whose segmentation mask
       covers it the most, giving a `tooth_fdi` per finding.

Adapted from the standalone `deploy/detect.py` script. Model weights live in
`app/ai_models/weights/` (git-ignored — copy them in manually, see
`app/ai_models/README.md`) and the U-Net architecture is defined in
`app/ai_models/seunet_arch.py`.

Output shape (`AIInferenceOutput`):
    - predictions: one `AIPrediction` per detected finding — maps 1:1 onto a
      row in `ai_detection_results` (tooth_number, condition, confidence, bbox)
    - raw: the full payload (image path, image_size, per-tooth breakdown incl.
      healthy teeth) — stored as-is in `ai_detection_analysis.detection_data`
"""

from __future__ import annotations

import os
import tempfile
from dataclasses import dataclass, field
from functools import lru_cache
from urllib.parse import urlparse

import numpy as np
import requests
import torch
from PIL import Image

from app.ai_models.seunet_arch import SEUNet

MODEL_NAME = "DentexSegAndDet"
MODEL_VERSION = "v1.0"

MODEL_DIR = os.getenv("AI_MODEL_DIR", os.path.join(os.path.dirname(__file__), "..", "ai_models", "weights"))
YOLO_MODEL_PATH = os.path.join(MODEL_DIR, "dentex_disease_yolov8x.pt")
UNET_MODEL_PATH = os.path.join(MODEL_DIR, "dentex_enumeration32_seunet.pth")

DEFAULT_CONF_THRESHOLD = 0.25


@dataclass
class AIPrediction:
    """One row of `ai_detection_results` — a single detected finding."""

    tooth_number: int
    condition: str
    confidence: float
    bbox: list[int]


@dataclass
class AIInferenceOutput:
    """Full result of running the model on one image."""

    predictions: list[AIPrediction] = field(default_factory=list)
    # Full raw payload (image path, image_size, per-tooth breakdown incl.
    # healthy teeth) — stored as-is in ai_detection_analysis.detection_data.
    raw: dict = field(default_factory=dict)


def _label_to_fdi(label: int) -> int:
    """Convert a segmentation label (1~32) to an FDI tooth number (11~48)."""
    idx0 = label - 1
    quadrant = idx0 // 8
    position = idx0 % 8
    return (quadrant + 1) * 10 + (position + 1)


@lru_cache(maxsize=1)
def _device() -> torch.device:
    return torch.device("cuda" if torch.cuda.is_available() else "cpu")


@lru_cache(maxsize=1)
def _load_unet_model() -> SEUNet:
    model = SEUNet(in_channels=1, n_cls=33)  # 32 teeth + background
    device = _device()
    checkpoint = torch.load(UNET_MODEL_PATH, map_location=device, weights_only=False)
    model.load_state_dict(checkpoint["model_state_dict"])
    model.to(device)
    model.eval()
    return model


@lru_cache(maxsize=1)
def _load_yolo_model():
    from ultralytics import YOLO

    return YOLO(YOLO_MODEL_PATH)


def _get_tooth_mask(model: SEUNet, image: Image.Image) -> np.ndarray:
    """Run U-Net and return a mask the same size as the original image
    (0=background, 1~32=tooth)."""
    device = _device()
    orig_size = image.size  # (W, H)
    gray = image.convert("L").resize((256, 256), Image.BILINEAR)

    tensor = torch.from_numpy(np.array(gray)).float().unsqueeze(0).unsqueeze(0) / 255.0
    tensor = (tensor - 0.458) / 0.173
    tensor = tensor.to(device)

    with torch.no_grad():
        logits = model(tensor)
        mask_256 = logits.argmax(dim=1).squeeze(0).cpu().numpy().astype(np.uint8)

    mask_img = Image.fromarray(mask_256).resize(orig_size, Image.NEAREST)
    return np.array(mask_img)


def _get_teeth_boxes(tooth_mask: np.ndarray, min_pixels: int = 300) -> list[dict]:
    """Bounding box of every segmented tooth (label 1~32), not just diseased
    ones."""
    teeth = []
    for label in range(1, 33):
        ys, xs = np.where(tooth_mask == label)
        if len(xs) < min_pixels:
            continue
        teeth.append(
            {
                "tooth_fdi": _label_to_fdi(label),
                "bbox": [int(xs.min()), int(ys.min()), int(xs.max()), int(ys.max())],
            }
        )
    return teeth


def _resolve_image(source: str) -> Image.Image:
    """Load a PIL image from either an http(s) URL or a local file path."""
    parsed = urlparse(source)
    if parsed.scheme in ("http", "https"):
        response = requests.get(source, timeout=30)
        response.raise_for_status()
        with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(parsed.path)[1] or ".png") as tmp:
            tmp.write(response.content)
            tmp_path = tmp.name
        try:
            return Image.open(tmp_path).convert("RGB")
        finally:
            os.unlink(tmp_path)

    if not os.path.exists(source):
        raise FileNotFoundError(f"Image not found: {source}")
    return Image.open(source).convert("RGB")


def _detect(image_source: str, conf_threshold: float = DEFAULT_CONF_THRESHOLD) -> dict:
    image = _resolve_image(image_source)

    unet_model = _load_unet_model()
    tooth_mask = _get_tooth_mask(unet_model, image)
    teeth = _get_teeth_boxes(tooth_mask)

    yolo_model = _load_yolo_model()
    yolo_result = yolo_model.predict(source=image, conf=conf_threshold, verbose=False)[0]

    detections = []
    for box in yolo_result.boxes:
        disease = yolo_model.names[int(box.cls)]
        confidence = float(box.conf)
        x1, y1, x2, y2 = map(int, box.xyxy[0].tolist())

        crop = tooth_mask[y1:y2, x1:x2]
        values, counts = np.unique(crop[crop != 0], return_counts=True)

        tooth_fdi = None
        if len(values) > 0:
            best_label = int(values[np.argmax(counts)])
            tooth_fdi = _label_to_fdi(best_label)

        detections.append(
            {
                "disease": disease,
                "confidence": round(confidence, 4),
                "bbox": [x1, y1, x2, y2],
                "tooth_fdi": tooth_fdi,
            }
        )

    for tooth in teeth:
        tooth["diseases"] = [
            {"disease": d["disease"], "confidence": d["confidence"]}
            for d in detections
            if d["tooth_fdi"] == tooth["tooth_fdi"]
        ]
        tooth["is_healthy"] = len(tooth["diseases"]) == 0

    return {
        "image": image_source,
        "image_size": {"width": image.width, "height": image.height},
        "detections": detections,
        "teeth": teeth,
    }


def predict(image_url: str, conf_threshold: float = DEFAULT_CONF_THRESHOLD) -> AIInferenceOutput:
    """Run the dental detection model on the given image (URL or local path)
    and return its output."""
    raw = _detect(image_url, conf_threshold=conf_threshold)

    predictions = [
        AIPrediction(
            tooth_number=detection["tooth_fdi"],
            condition=detection["disease"],
            confidence=detection["confidence"],
            bbox=detection["bbox"],
        )
        for detection in raw["detections"]
        if detection["tooth_fdi"] is not None  # skip findings we couldn't assign to a tooth
    ]
    return AIInferenceOutput(predictions=predictions, raw=raw)
