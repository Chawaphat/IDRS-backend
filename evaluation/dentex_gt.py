"""DENTEX 2023 ground-truth loading (Test Plan §5.2).

Reads the challenge's COCO-style annotation JSON and converts it into the
shapes `evaluation.metrics` expects, using exactly the label conventions the
DentexSegAndDet training code used (`process_dataset.py` in
github.com/xyzlancehe/DentexSegAndDet):

    enumeration32 label = category_id_1 * 8 + category_id_2      (0..31)
    segmentation mask   = that label + 1                         (1..32, 0 = bg)
    disease class       = DISEASE_CLASSES[category_id_3]

which is the inverse of `ai_inference._label_to_fdi`, so ground truth and
prediction land in the same FDI space.

Expected on-disk layout (as downloaded from the DENTEX Kaggle mirror):

    <root>/
      quadrant_enumeration_disease/
        xrays/*.png
        train_quadrant_enumeration_disease.json
      quadrant_enumeration/                     # optional, for AITC-02
        xrays/*.png
        train_quadrant_enumeration.json

Directory names are matched loosely (hyphen/underscore, nesting under a
`training_data/` folder) because the Kaggle mirrors are not consistent.
"""

from __future__ import annotations

import json
import os
from dataclasses import dataclass, field

from evaluation.metrics import DISEASE_CLASSES

DISEASE_DIR_CANDIDATES = [
    "quadrant_enumeration_disease",
    "quadrant-enumeration-disease",
]
ENUMERATION_DIR_CANDIDATES = [
    "quadrant_enumeration",
    "quadrant-enumeration",
]
DISEASE_JSON_NAMES = [
    "train_quadrant_enumeration_disease.json",
    "train_quadrant-enumeration-disease.json",
]
ENUMERATION_JSON_NAMES = [
    "train_quadrant_enumeration.json",
    "train_quadrant-enumeration.json",
]


def fdi_from_categories(category_id_1: int, category_id_2: int) -> int:
    """DENTEX (quadrant, enumeration) 0-based pair -> FDI tooth number."""
    return (category_id_1 + 1) * 10 + (category_id_2 + 1)


def segmentation_label(category_id_1: int, category_id_2: int) -> int:
    """DENTEX (quadrant, enumeration) 0-based pair -> SEUNet mask label 1..32."""
    return category_id_1 * 8 + category_id_2 + 1


def xyxy_from_coco(bbox: list[float]) -> list[float]:
    """COCO ``[x, y, w, h]`` -> ``[x1, y1, x2, y2]``."""
    x, y, width, height = bbox
    return [x, y, x + width, y + height]


def polygons(segmentation) -> list[list[float]]:
    """Normalise a DENTEX ``segmentation`` value into a list of flat polygons.

    DENTEX stores a single flat ``[x1, y1, x2, y2, ...]`` list, while stock
    COCO nests one list per polygon. Accept both.
    """
    if not segmentation:
        return []
    if isinstance(segmentation[0], (list, tuple)):
        return [list(polygon) for polygon in segmentation if len(polygon) >= 6]
    return [list(segmentation)] if len(segmentation) >= 6 else []


@dataclass
class ImageRecord:
    """One annotated panoramic X-ray."""

    image_id: int
    file_name: str
    width: int
    height: int
    path: str
    # Disease findings — present only for the disease subset.
    diseases: list[dict] = field(default_factory=list)
    # Tooth annotations (FDI + polygon) for every annotated tooth.
    teeth: list[dict] = field(default_factory=list)

    @property
    def disease_classes(self) -> set[str]:
        return {finding["class"] for finding in self.diseases}


def _find_dir(root: str, candidates: list[str]) -> str | None:
    """Locate a subset directory under `root`, tolerating layout differences."""
    for candidate in candidates:
        direct = os.path.join(root, candidate)
        if os.path.isdir(direct):
            return direct

    # Kaggle mirrors often nest everything one or two levels deeper.
    for current, directories, _ in os.walk(root):
        if current.count(os.sep) - root.count(os.sep) > 3:
            directories.clear()
            continue
        for directory in directories:
            if directory in candidates:
                return os.path.join(current, directory)
    return None


def _find_json(directory: str, names: list[str]) -> str | None:
    for name in names:
        path = os.path.join(directory, name)
        if os.path.isfile(path):
            return path
    for entry in sorted(os.listdir(directory)):
        if entry.endswith(".json"):
            return os.path.join(directory, entry)
    return None


def _xray_dir(directory: str) -> str:
    for name in ("xrays", "xray", "images"):
        candidate = os.path.join(directory, name)
        if os.path.isdir(candidate):
            return candidate
    return directory


def _load(annotation_path: str, xray_dir: str, with_disease: bool) -> list[ImageRecord]:
    with open(annotation_path) as handle:
        payload = json.load(handle)

    records: dict[int, ImageRecord] = {}
    for image in payload["images"]:
        records[image["id"]] = ImageRecord(
            image_id=image["id"],
            file_name=image["file_name"],
            width=image["width"],
            height=image["height"],
            path=os.path.join(xray_dir, image["file_name"]),
        )

    for annotation in payload["annotations"]:
        record = records.get(annotation["image_id"])
        if record is None:
            continue

        category_1 = annotation["category_id_1"]
        category_2 = annotation["category_id_2"]
        tooth_fdi = fdi_from_categories(category_1, category_2)
        box = xyxy_from_coco(annotation["bbox"])

        record.teeth.append(
            {
                "tooth_fdi": tooth_fdi,
                "label": segmentation_label(category_1, category_2),
                "bbox": box,
                "polygons": polygons(annotation.get("segmentation")),
            }
        )

        if with_disease:
            record.diseases.append(
                {
                    "image_id": annotation["image_id"],
                    "class": DISEASE_CLASSES[annotation["category_id_3"]],
                    "bbox": box,
                    "tooth_fdi": tooth_fdi,
                }
            )

    return [record for _, record in sorted(records.items())]


def load_disease_subset(root: str) -> list[ImageRecord]:
    """Load `quadrant_enumeration_disease` — the 705 fully-annotated images.

    Every annotation here is a *diseased tooth*: the box and polygon outline
    the tooth, `category_id_3` names its condition. This is what YOLOv8x was
    trained on, and it drives AITC-01 and AITC-03.
    """
    directory = _find_dir(root, DISEASE_DIR_CANDIDATES)
    if directory is None:
        raise FileNotFoundError(
            f"Could not find a '{DISEASE_DIR_CANDIDATES[0]}' directory under {root}. "
            "See evaluation/README.md for the expected dataset layout."
        )
    annotation_path = _find_json(directory, DISEASE_JSON_NAMES)
    if annotation_path is None:
        raise FileNotFoundError(f"No annotation JSON found in {directory}")
    return _load(annotation_path, _xray_dir(directory), with_disease=True)


def load_enumeration_subset(root: str) -> list[ImageRecord]:
    """Load `quadrant_enumeration` — 634 images with *every* tooth annotated.

    The disease subset only outlines diseased teeth, so tooth segmentation
    quality (AITC-02) has to be measured here to cover healthy teeth too.
    """
    directory = _find_dir(root, ENUMERATION_DIR_CANDIDATES)
    if directory is None:
        raise FileNotFoundError(
            f"Could not find a '{ENUMERATION_DIR_CANDIDATES[0]}' directory under {root}."
        )
    annotation_path = _find_json(directory, ENUMERATION_JSON_NAMES)
    if annotation_path is None:
        raise FileNotFoundError(f"No annotation JSON found in {directory}")
    return _load(annotation_path, _xray_dir(directory), with_disease=False)


def flatten_disease_ground_truth(records: list[ImageRecord]) -> list[dict]:
    """All disease annotations across `records`, ready for `evaluation.metrics`."""
    return [finding for record in records for finding in record.diseases]
