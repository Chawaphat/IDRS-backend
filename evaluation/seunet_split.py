"""Reconstruct the held-out split SEUNet was trained against.

Unlike the YOLOv8x disease split — shuffled without a seed and only
recoverable from the training machine's `instances_val2017.json` — the tooth
segmentation split is reproducible from the public dataset alone.

`train_unet.py` in the DentexSegAndDet repo splits at runtime:

    train_size = int(len(dataset) * args.train_ratio)     # default 0.8
    train_dataset, val_dataset = torch.utils.data.random_split(
        dataset, [train_size, len(dataset) - train_size],
        generator=torch.Generator().manual_seed(args.seed),   # default 42
    )

and the dataset it indexes is `image_names.json`, which
`process_dataset.py::process_seg_enumeration32()` writes in exactly the order
`train_quadrant_enumeration.json` lists its images — no filtering, no sorting.

So given that JSON (which ships with the DENTEX download) plus the seed and
ratio, the split falls out of `torch.randperm`, which is what `random_split`
uses internally.

⚠ This is a *reconstruction*, not a recovered artefact. It is only the real
split if the training run used these arguments. `verify_split` exists because
that assumption has to be tested rather than trusted: a model scores visibly
better on data it trained on, so a reconstruction that is correct shows a
train/val gap and one that is wrong does not.
"""

from __future__ import annotations

import json
import os

from evaluation.dentex_gt import (
    ENUMERATION_DIR_CANDIDATES,
    ENUMERATION_JSON_NAMES,
    _find_dir,
    _find_json,
)

DEFAULT_SEED = 42
DEFAULT_TRAIN_RATIO = 0.8


def _image_names_in_dataset_order(dataset_root: str) -> list[str]:
    """The `image_names.json` order, rebuilt from the annotation JSON."""
    directory = _find_dir(dataset_root, ENUMERATION_DIR_CANDIDATES)
    if directory is None:
        raise FileNotFoundError(
            f"No '{ENUMERATION_DIR_CANDIDATES[0]}' directory under {dataset_root}"
        )
    annotation_path = _find_json(directory, ENUMERATION_JSON_NAMES)
    if annotation_path is None:
        raise FileNotFoundError(f"No annotation JSON in {directory}")

    with open(annotation_path) as handle:
        payload = json.load(handle)
    return [image["file_name"] for image in payload["images"]]


def reconstruct_val_split(
    dataset_root: str,
    seed: int = DEFAULT_SEED,
    train_ratio: float = DEFAULT_TRAIN_RATIO,
) -> dict:
    """Rebuild the SEUNet validation split from the public dataset."""
    import torch

    names = _image_names_in_dataset_order(dataset_root)
    total = len(names)
    train_size = int(total * train_ratio)

    order = torch.randperm(
        total, generator=torch.Generator().manual_seed(seed)
    ).tolist()

    return {
        "val_file_names": {names[index] for index in order[train_size:]},
        "train_file_names": {names[index] for index in order[:train_size]},
        "provenance": {
            "method": "reconstructed_from_seed",
            # Only an observed train/val gap upgrades this to "none".
            "leakage_risk": "unverified",
            "seed": seed,
            "train_ratio": train_ratio,
            "population": total,
            "train_size": train_size,
            "val_size": total - train_size,
            "assumption": (
                f"train_unet.py was run with --seed {seed} and --train_ratio "
                f"{train_ratio} (its defaults). A different value makes this "
                "split wrong, which verify_split is there to detect."
            ),
        },
    }


def verify_split(train_mean_iou: float | None, val_mean_iou: float | None) -> dict:
    """Judge a reconstruction by whether the model does better on its train half.

    A correct reconstruction separates seen from unseen images, so the model
    scores higher on the train half. No gap means the reconstruction probably
    does not correspond to the real split — the two halves are then just two
    arbitrary samples of the same (largely seen) data.
    """
    if train_mean_iou is None or val_mean_iou is None:
        return {"verified": None, "gap": None, "reason": "missing measurements"}

    gap = train_mean_iou - val_mean_iou
    verified = gap > 0
    return {
        "verified": verified,
        "gap": gap,
        "train_mean_iou": train_mean_iou,
        "val_mean_iou": val_mean_iou,
        "reason": (
            f"model scores {gap:+.4f} mean IoU higher on the reconstructed "
            "train half, consistent with it having trained on those images"
            if verified else
            f"no train/val gap ({gap:+.4f}) — the reconstruction likely does "
            "not match the split the training run actually used"
        ),
    }
