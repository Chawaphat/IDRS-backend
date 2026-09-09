"""Tooth-mask rasterisation and comparison for AITC-02.

This is the only part of the evaluation that needs numpy/PIL, so it is
imported lazily by the runner and left out of `evaluation.metrics` — the
metric maths stays testable on a machine without the ML stack.

Ground-truth masks are rasterised from the DENTEX polygons exactly the way
`process_dataset.py` built the SEUNet training masks (label = quadrant * 8 +
enumeration + 1, background 0), so predicted and annotated labels line up
one-for-one.
"""

from __future__ import annotations

from evaluation.dentex_gt import ImageRecord


def rasterise_ground_truth(record: ImageRecord):
    """Render a ``(H, W)`` uint8 label mask (0 = background, 1..32 = tooth)."""
    import numpy as np
    from PIL import Image, ImageDraw

    mask = Image.new("L", (record.width, record.height), 0)
    draw = ImageDraw.Draw(mask)

    for tooth in record.teeth:
        for polygon in tooth["polygons"]:
            points = [
                (polygon[i], polygon[i + 1]) for i in range(0, len(polygon) - 1, 2)
            ]
            if len(points) >= 3:
                draw.polygon(points, fill=tooth["label"])

    return np.array(mask)


def compare_masks(image_id: int, ground_truth_mask, predicted_mask) -> list[dict]:
    """Per-tooth intersection/union counts for every FDI the GT annotates.

    Teeth the ground truth does not annotate are skipped rather than scored 0 —
    the disease subset only outlines diseased teeth, and counting the model's
    (correct) predictions for unannotated teeth as errors would be wrong.
    """
    import numpy as np

    if ground_truth_mask.shape != predicted_mask.shape:
        raise ValueError(
            f"mask shape mismatch: gt {ground_truth_mask.shape} vs "
            f"pred {predicted_mask.shape}"
        )

    from app.services.ai_inference import _label_to_fdi

    results = []
    for label in np.unique(ground_truth_mask):
        label = int(label)
        if label == 0:
            continue
        gt_pixels = ground_truth_mask == label
        pred_pixels = predicted_mask == label
        intersection = int(np.logical_and(gt_pixels, pred_pixels).sum())
        union = int(np.logical_or(gt_pixels, pred_pixels).sum())
        results.append(
            {
                "image_id": image_id,
                "tooth_fdi": _label_to_fdi(label),
                "label": label,
                "intersection": intersection,
                "union": union,
            }
        )
    return results
