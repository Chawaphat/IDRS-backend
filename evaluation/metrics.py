"""Metric implementations for the IDRS AI Model Evaluation (Test Plan §5.3).

Deliberately pure Python (no numpy / torch) so the metric maths can be unit
tested on any machine, including one without the ML stack installed. The
pixel-level work that genuinely needs numpy lives in `evaluation.masks`.

Metrics implemented, and the Test Plan target each one feeds:

    mAP@0.5              YOLOv8x (Disease)   >= 0.50    AITC-01
    mAP@0.5:0.95         YOLOv8x (Disease)   >= 0.30    AITC-01
    per-class F1         YOLOv8x (Disease)   >= 0.50    AITC-01
    Mean IoU             SEUNet (Tooth)      >= 0.70    AITC-02
    Enumeration Accuracy SEUNet (Tooth)      >= 0.90    AITC-02
    Assignment Accuracy  Post-processing     >= 0.85    AITC-03

Box convention throughout: ``[x1, y1, x2, y2]`` in absolute pixels on the
original image (the same convention `ai_inference` emits).
"""

from __future__ import annotations

from collections import defaultdict
from typing import Iterable, Sequence

# The 4 disease classes, in the order used by the DENTEX `category_id_3`
# labels and by `process_dataset.py` in the DentexSegAndDet repo.
DISEASE_CLASSES = ["Impacted", "Caries", "Periapical Lesion", "Deep Caries"]

# COCO-style 101-point interpolated average precision.
RECALL_POINTS = [i / 100.0 for i in range(101)]

# COCO mAP@0.5:0.95 sweep.
COCO_IOU_THRESHOLDS = [0.50 + 0.05 * i for i in range(10)]


# ---------------------------------------------------------------------------
# Geometry
# ---------------------------------------------------------------------------
def iou_xyxy(a: Sequence[float], b: Sequence[float]) -> float:
    """Intersection-over-union of two ``[x1, y1, x2, y2]`` boxes."""
    ix1, iy1 = max(a[0], b[0]), max(a[1], b[1])
    ix2, iy2 = min(a[2], b[2]), min(a[3], b[3])
    iw, ih = ix2 - ix1, iy2 - iy1
    if iw <= 0 or ih <= 0:
        return 0.0
    inter = iw * ih
    area_a = max(0.0, a[2] - a[0]) * max(0.0, a[3] - a[1])
    area_b = max(0.0, b[2] - b[0]) * max(0.0, b[3] - b[1])
    union = area_a + area_b - inter
    return inter / union if union > 0 else 0.0


# ---------------------------------------------------------------------------
# Detection matching
# ---------------------------------------------------------------------------
def match_detections(
    predictions: Iterable[dict],
    ground_truths: Sequence[dict],
    iou_threshold: float,
) -> tuple[list[tuple[float, bool]], list[int]]:
    """Greedily match predictions to ground truth boxes within each image.

    Predictions are consumed highest-confidence first; each ground truth box
    can only be claimed once (standard COCO / Pascal VOC protocol).

    Both sequences hold dicts with ``image_id`` and ``bbox``; predictions also
    carry ``score``. Callers are expected to have filtered both down to a
    single class already.

    Returns ``(scored, matched_gt_indices)`` where `scored` is one
    ``(score, is_true_positive)`` pair per prediction, ordered by descending
    score, and `matched_gt_indices` lists the ground truth indices that were
    successfully matched.
    """
    gt_by_image: dict = defaultdict(list)
    for index, gt in enumerate(ground_truths):
        gt_by_image[gt["image_id"]].append(index)

    claimed: set[int] = set()
    scored: list[tuple[float, bool]] = []

    for prediction in sorted(predictions, key=lambda p: -p["score"]):
        best_iou, best_index = 0.0, None
        for index in gt_by_image.get(prediction["image_id"], ()):
            if index in claimed:
                continue
            overlap = iou_xyxy(prediction["bbox"], ground_truths[index]["bbox"])
            if overlap > best_iou:
                best_iou, best_index = overlap, index

        if best_index is not None and best_iou >= iou_threshold:
            claimed.add(best_index)
            scored.append((prediction["score"], True))
        else:
            scored.append((prediction["score"], False))

    return scored, sorted(claimed)


def average_precision(scored: Sequence[tuple[float, bool]], n_ground_truth: int) -> float | None:
    """101-point interpolated AP from ``(score, is_tp)`` pairs.

    Returns ``None`` when the class has no ground truth at all — such a class
    is undefined rather than zero, and is excluded from the mAP average.
    """
    if n_ground_truth == 0:
        return None
    if not scored:
        return 0.0

    ordered = sorted(scored, key=lambda s: -s[0])

    true_positives = false_positives = 0
    precisions: list[float] = []
    recalls: list[float] = []
    for _, is_true_positive in ordered:
        if is_true_positive:
            true_positives += 1
        else:
            false_positives += 1
        precisions.append(true_positives / (true_positives + false_positives))
        recalls.append(true_positives / n_ground_truth)

    # Make precision monotonically non-increasing when read right-to-left, so
    # a later spike in precision lifts every earlier recall level too.
    for i in range(len(precisions) - 2, -1, -1):
        precisions[i] = max(precisions[i], precisions[i + 1])

    total = 0.0
    cursor = 0
    for recall_point in RECALL_POINTS:
        while cursor < len(recalls) and recalls[cursor] < recall_point:
            cursor += 1
        total += precisions[cursor] if cursor < len(precisions) else 0.0
    return total / len(RECALL_POINTS)


# ---------------------------------------------------------------------------
# AITC-01 — disease detection (YOLOv8x)
# ---------------------------------------------------------------------------
def _split_by_class(items: Iterable[dict], class_name: str) -> list[dict]:
    return [item for item in items if item["class"] == class_name]


def compute_map(
    predictions: Sequence[dict],
    ground_truths: Sequence[dict],
    classes: Sequence[str] = DISEASE_CLASSES,
    iou_thresholds: Sequence[float] = (0.5,),
) -> dict:
    """Mean average precision over `classes`, averaged over `iou_thresholds`.

    Classes absent from the ground truth are skipped rather than scored 0, so
    a subset that happens to miss a rare class does not silently drag mAP down.
    """
    per_class: dict[str, float | None] = {}

    for class_name in classes:
        class_predictions = _split_by_class(predictions, class_name)
        class_ground_truths = _split_by_class(ground_truths, class_name)

        threshold_scores: list[float] = []
        for iou_threshold in iou_thresholds:
            scored, _ = match_detections(class_predictions, class_ground_truths, iou_threshold)
            average = average_precision(scored, len(class_ground_truths))
            if average is not None:
                threshold_scores.append(average)

        per_class[class_name] = (
            sum(threshold_scores) / len(threshold_scores) if threshold_scores else None
        )

    scored_classes = [value for value in per_class.values() if value is not None]
    return {
        "per_class_ap": per_class,
        "mAP": sum(scored_classes) / len(scored_classes) if scored_classes else None,
        "iou_thresholds": list(iou_thresholds),
        "classes_scored": len(scored_classes),
    }


def compute_precision_recall_f1(
    predictions: Sequence[dict],
    ground_truths: Sequence[dict],
    classes: Sequence[str] = DISEASE_CLASSES,
    iou_threshold: float = 0.5,
) -> dict:
    """Per-class precision / recall / F1 at a fixed IoU threshold.

    The confidence threshold is whatever the caller already applied when
    running the model — the Test Plan fixes it at 0.25 (as deployed).
    """
    per_class: dict[str, dict] = {}

    for class_name in classes:
        class_predictions = _split_by_class(predictions, class_name)
        class_ground_truths = _split_by_class(ground_truths, class_name)

        scored, matched = match_detections(class_predictions, class_ground_truths, iou_threshold)
        true_positives = len(matched)
        false_positives = len(scored) - true_positives
        false_negatives = len(class_ground_truths) - true_positives

        precision = (
            true_positives / (true_positives + false_positives)
            if (true_positives + false_positives)
            else 0.0
        )
        recall = (
            true_positives / (true_positives + false_negatives)
            if (true_positives + false_negatives)
            else 0.0
        )
        f1 = 2 * precision * recall / (precision + recall) if (precision + recall) else 0.0

        per_class[class_name] = {
            "support": len(class_ground_truths),
            "predicted": len(scored),
            "tp": true_positives,
            "fp": false_positives,
            "fn": false_negatives,
            "precision": precision,
            "recall": recall,
            "f1": f1,
        }

    evaluated = [stats for stats in per_class.values() if stats["support"] > 0]
    return {
        "per_class": per_class,
        "macro_f1": (
            sum(stats["f1"] for stats in evaluated) / len(evaluated) if evaluated else None
        ),
        "iou_threshold": iou_threshold,
    }


# ---------------------------------------------------------------------------
# AITC-02 — tooth segmentation / enumeration (SEUNet)
# ---------------------------------------------------------------------------
def summarise_tooth_masks(
    per_tooth: Sequence[dict],
    enumeration_iou_threshold: float = 0.5,
) -> dict:
    """Mean IoU and enumeration accuracy from per-(image, FDI) overlap counts.

    Each entry is ``{"image_id", "tooth_fdi", "intersection", "union"}`` and
    represents one tooth that the *ground truth* annotates. Entries are
    produced by `evaluation.masks.compare_masks`.

    - Mean IoU is averaged over every annotated tooth instance (the Test Plan's
      "Mean Intersection over Union of 32 FDI tooth masks").
    - Enumeration accuracy is the share of annotated teeth the model both found
      and labelled with the right FDI number, i.e. IoU >= 0.5 for that label.
    - `mean_iou_aggregated` pools pixels per FDI across the whole subset first;
      reported alongside because it is far less sensitive to small teeth.
    """
    if not per_tooth:
        return {
            "mean_iou": None,
            "mean_iou_aggregated": None,
            "enumeration_accuracy": None,
            "teeth_evaluated": 0,
            "per_fdi": {},
        }

    ious = []
    correct = 0
    pooled: dict[int, list[int]] = defaultdict(lambda: [0, 0])
    per_fdi_ious: dict[int, list[float]] = defaultdict(list)

    for entry in per_tooth:
        union = entry["union"]
        iou = entry["intersection"] / union if union else 0.0
        ious.append(iou)
        if iou >= enumeration_iou_threshold:
            correct += 1

        fdi = entry["tooth_fdi"]
        pooled[fdi][0] += entry["intersection"]
        pooled[fdi][1] += union
        per_fdi_ious[fdi].append(iou)

    aggregated = [
        intersection / union for intersection, union in pooled.values() if union
    ]

    return {
        "mean_iou": sum(ious) / len(ious),
        "mean_iou_aggregated": (
            sum(aggregated) / len(aggregated) if aggregated else None
        ),
        "enumeration_accuracy": correct / len(per_tooth),
        "teeth_evaluated": len(per_tooth),
        "per_fdi": {
            fdi: {
                "count": len(values),
                "mean_iou": sum(values) / len(values),
                "enumeration_accuracy": sum(
                    1 for value in values if value >= enumeration_iou_threshold
                )
                / len(values),
            }
            for fdi, values in sorted(per_fdi_ious.items())
        },
    }


# ---------------------------------------------------------------------------
# AITC-03 — disease-to-tooth assignment (post-processing)
# ---------------------------------------------------------------------------
def compute_assignment_accuracy(
    predictions: Sequence[dict],
    ground_truths: Sequence[dict],
    classes: Sequence[str] = DISEASE_CLASSES,
    iou_threshold: float = 0.5,
) -> dict:
    """Share of correctly assigned ``tooth_fdi`` among matched detections.

    Only detections that genuinely found their lesion are judged: a prediction
    must first match a ground truth box of the same class at IoU >= 0.5, and
    only then is its `tooth_fdi` compared against that box's annotated FDI
    number. Scoring unmatched detections here would conflate a YOLO miss
    (AITC-01) with a mapping error (AITC-03).

    Predictions carry ``tooth_fdi`` (``None`` when the segmentation mask did
    not cover the box — counted as unassigned, which is a failure).
    """
    total = correct = unassigned = 0
    errors: list[dict] = []

    for class_name in classes:
        class_predictions = sorted(
            _split_by_class(predictions, class_name), key=lambda p: -p["score"]
        )
        class_ground_truths = _split_by_class(ground_truths, class_name)

        gt_by_image: dict = defaultdict(list)
        for index, gt in enumerate(class_ground_truths):
            gt_by_image[gt["image_id"]].append(index)

        claimed: set[int] = set()
        for prediction in class_predictions:
            best_iou, best_index = 0.0, None
            for index in gt_by_image.get(prediction["image_id"], ()):
                if index in claimed:
                    continue
                overlap = iou_xyxy(prediction["bbox"], class_ground_truths[index]["bbox"])
                if overlap > best_iou:
                    best_iou, best_index = overlap, index

            if best_index is None or best_iou < iou_threshold:
                continue

            claimed.add(best_index)
            expected = class_ground_truths[best_index]["tooth_fdi"]
            actual = prediction.get("tooth_fdi")

            total += 1
            if actual is None:
                unassigned += 1
                errors.append(
                    {
                        "image_id": prediction["image_id"],
                        "class": class_name,
                        "expected_fdi": expected,
                        "actual_fdi": None,
                    }
                )
            elif actual == expected:
                correct += 1
            else:
                errors.append(
                    {
                        "image_id": prediction["image_id"],
                        "class": class_name,
                        "expected_fdi": expected,
                        "actual_fdi": actual,
                    }
                )

    return {
        "assignment_accuracy": correct / total if total else None,
        "matched_detections": total,
        "correct": correct,
        "unassigned": unassigned,
        "errors": errors,
    }
