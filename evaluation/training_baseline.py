"""Held-out baseline recovered from the YOLOv8x training run.

The evaluation subset drawn by `evaluation.subset` overlaps the data the
shipped weights were trained on (see that module's warning), so its scores are
optimistic. The training run itself, however, validated every epoch against a
split that *was* strictly held out — and ultralytics wrote those numbers to
`results.csv` inside the run directory.

Reading that file back gives an honest reference point to sit beside the
measured numbers, without needing to know which images were in the split.

    <run_dir>/
      results.csv              per-epoch train losses + val metrics
      args.yaml                the training configuration
      BoxF1_curve.png          per-class F1 vs confidence, on the val split

`results.csv` carries only aggregate metrics — there is no per-class breakdown
in it. Per-class F1 on the held-out split has to be read off `BoxF1_curve.png`
by eye, so it is deliberately not parsed here.
"""

from __future__ import annotations

import csv
import os

RESULTS_CSV = "results.csv"
F1_CURVE = "BoxF1_curve.png"

# ultralytics column names -> the names used in this report.
METRIC_COLUMNS = {
    "metrics/mAP50(B)": "map_50",
    "metrics/mAP50-95(B)": "map_50_95",
    "metrics/precision(B)": "precision",
    "metrics/recall(B)": "recall",
}


def _epoch_metrics(row: dict) -> dict:
    metrics = {"epoch": int(float(row["epoch"]))}
    for column, name in METRIC_COLUMNS.items():
        value = row.get(column)
        metrics[name] = float(value) if value not in (None, "") else None
    return metrics


def load_training_baseline(run_dir: str) -> dict:
    """Read the held-out validation metrics from an ultralytics run directory."""
    path = os.path.join(run_dir, RESULTS_CSV)
    if not os.path.isfile(path):
        raise FileNotFoundError(
            f"No {RESULTS_CSV} in {run_dir} — point --training-run-dir at the "
            "ultralytics run folder (the one holding BoxF1_curve.png)."
        )

    with open(path, newline="") as handle:
        rows = [
            {key.strip(): value for key, value in row.items() if key is not None}
            for row in csv.DictReader(handle)
        ]

    if not rows:
        raise ValueError(f"{path} has no epoch rows")

    epochs = [_epoch_metrics(row) for row in rows]
    scored = [epoch for epoch in epochs if epoch["map_50_95"] is not None]

    return {
        "source": os.path.abspath(path),
        "epochs_trained": len(epochs),
        # The checkpoint that shipped is not recorded anywhere, so report both
        # ends: ultralytics keeps best.pt and last.pt, and which one was copied
        # into app/ai_models/weights/ is not knowable from these files.
        "best_epoch": max(scored, key=lambda e: e["map_50_95"]) if scored else None,
        "last_epoch": epochs[-1],
        "f1_curve": (
            os.path.abspath(os.path.join(run_dir, F1_CURVE))
            if os.path.isfile(os.path.join(run_dir, F1_CURVE))
            else None
        ),
    }


def compare(measured: dict, baseline: dict) -> dict:
    """Quantify how far the measured (leaky) run sits above the honest baseline.

    `measured` is the `detection` section of a run's results.json.
    """
    measured_values = {
        "map_50": (measured.get("map_50") or {}).get("mAP"),
        "map_50_95": (measured.get("map_50_95") or {}).get("mAP"),
    }

    rows = {}
    for name, measured_value in measured_values.items():
        row = {"measured": measured_value}
        for label in ("best_epoch", "last_epoch"):
            epoch = baseline.get(label)
            reference = epoch[name] if epoch else None
            row[label] = reference
            row[f"inflation_vs_{label}"] = (
                measured_value - reference
                if measured_value is not None and reference is not None
                else None
            )
        rows[name] = row
    return rows
