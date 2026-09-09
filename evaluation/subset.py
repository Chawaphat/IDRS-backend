"""Evaluation subset selection (Test Plan §5.2).

Builds the "stratified, held-out sample of ~15% (100-110 images)" the Test
Plan calls for, covering all 4 disease classes.

⚠ Data-leakage warning
----------------------
`process_dataset.py` in the DentexSegAndDet repo split train/val with a bare
``random.shuffle`` and **no seed**, so the exact set of images the shipped
YOLOv8x weights were trained on is not reproducible after the fact. A subset
drawn here will therefore overlap the training data, and the resulting numbers
are optimistic.

If the original ``instances_val2017.json`` from that training run still
exists, pass it via ``--held-out-json``: those images really were held out and
the scores are then honest. `build_subset` records which of the two happened
in `provenance` so the report can say so plainly.
"""

from __future__ import annotations

import json
import os
import random
from collections import Counter, defaultdict

from evaluation.dentex_gt import ImageRecord
from evaluation.metrics import DISEASE_CLASSES

DEFAULT_SEED = 42
DEFAULT_FRACTION = 0.15
MIN_IMAGES = 100
MAX_IMAGES = 110


def _stratum(record: ImageRecord, class_frequency: Counter) -> str:
    """Stratify each image by the rarest disease class it contains.

    Keying on the rarest class (rather than the full label set) keeps
    Periapical Lesion — by far the smallest class — proportionally represented
    instead of being swallowed by images that also contain Caries.
    """
    present = record.disease_classes
    if not present:
        return "__none__"
    return min(present, key=lambda name: (class_frequency[name], name))


def build_subset(
    records: list[ImageRecord],
    fraction: float = DEFAULT_FRACTION,
    seed: int = DEFAULT_SEED,
    min_images: int = MIN_IMAGES,
    max_images: int = MAX_IMAGES,
    held_out_file_names: set[str] | None = None,
) -> dict:
    """Select the evaluation subset and describe how it was chosen."""
    if held_out_file_names is not None:
        selected = [
            record for record in records if record.file_name in held_out_file_names
        ]
        return {
            "images": selected,
            "provenance": {
                "method": "training_held_out",
                "leakage_risk": "none",
                "note": (
                    "Images come from the original training run's validation "
                    "split, so they were never seen during training."
                ),
                "requested": len(held_out_file_names),
                "resolved": len(selected),
            },
            "class_distribution": _class_distribution(selected),
        }

    class_frequency = Counter(
        finding["class"] for record in records for finding in record.diseases
    )

    strata: dict[str, list[ImageRecord]] = defaultdict(list)
    for record in records:
        strata[_stratum(record, class_frequency)].append(record)

    rng = random.Random(seed)
    selected: list[ImageRecord] = []
    for key in sorted(strata):
        bucket = sorted(strata[key], key=lambda record: record.file_name)
        rng.shuffle(bucket)
        take = max(1, round(len(bucket) * fraction))
        selected.extend(bucket[:take])

    # Land inside the Test Plan's 100-110 window without dropping any class.
    selected.sort(key=lambda record: record.file_name)
    if len(selected) > max_images:
        selected = _trim_keeping_coverage(selected, max_images, rng)
    elif len(selected) < min_images:
        selected = _top_up(selected, records, min_images, rng)

    return {
        "images": selected,
        "provenance": {
            "method": "stratified_resample",
            "leakage_risk": "high",
            "note": (
                "The shipped weights' original train/val split used an unseeded "
                "random.shuffle and cannot be reconstructed, so these images "
                "likely overlap the training data. Treat the scores as an upper "
                "bound and re-run with --held-out-json if the original "
                "instances_val2017.json is available."
            ),
            "seed": seed,
            "fraction": fraction,
            "population": len(records),
        },
        "class_distribution": _class_distribution(selected),
    }


def _trim_keeping_coverage(
    selected: list[ImageRecord], limit: int, rng: random.Random
) -> list[ImageRecord]:
    """Drop images down to `limit`, never removing a class's last example."""
    keep: list[ImageRecord] = []
    seen_classes: set[str] = set()
    # Rarest-class-first so each class secures a representative early.
    order = sorted(
        selected, key=lambda record: (len(record.disease_classes), record.file_name)
    )
    for record in order:
        if not record.disease_classes.issubset(seen_classes):
            keep.append(record)
            seen_classes |= record.disease_classes

    kept_names = {record.file_name for record in keep}
    remainder = [record for record in selected if record.file_name not in kept_names]
    rng.shuffle(remainder)
    keep.extend(remainder[: max(0, limit - len(keep))])
    return sorted(keep[:limit], key=lambda record: record.file_name)


def _top_up(
    selected: list[ImageRecord],
    records: list[ImageRecord],
    target: int,
    rng: random.Random,
) -> list[ImageRecord]:
    chosen = {record.file_name for record in selected}
    remainder = [record for record in records if record.file_name not in chosen]
    rng.shuffle(remainder)
    selected = selected + remainder[: max(0, target - len(selected))]
    return sorted(selected, key=lambda record: record.file_name)


def _class_distribution(records: list[ImageRecord]) -> dict:
    images = Counter()
    instances = Counter()
    for record in records:
        for class_name in record.disease_classes:
            images[class_name] += 1
        for finding in record.diseases:
            instances[finding["class"]] += 1
    return {
        class_name: {
            "images": images.get(class_name, 0),
            "instances": instances.get(class_name, 0),
        }
        for class_name in DISEASE_CLASSES
    }


def load_held_out_file_names(path: str) -> set[str]:
    """Read held-out image names from a COCO JSON or a plain newline list."""
    if path.endswith(".json"):
        with open(path) as handle:
            payload = json.load(handle)
        return {image["file_name"] for image in payload.get("images", [])}
    with open(path) as handle:
        return {line.strip() for line in handle if line.strip()}


def save_subset(subset: dict, path: str) -> None:
    os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
    with open(path, "w") as handle:
        json.dump(
            {
                "images": [
                    {
                        "image_id": record.image_id,
                        "file_name": record.file_name,
                        "disease_classes": sorted(record.disease_classes),
                        "n_findings": len(record.diseases),
                    }
                    for record in subset["images"]
                ],
                "provenance": subset["provenance"],
                "class_distribution": subset["class_distribution"],
            },
            handle,
            indent=2,
        )
