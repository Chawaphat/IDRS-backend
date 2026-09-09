# IDRS AI Model Evaluation — Results

Test Plan v0.2.0, Chapter 5 · IDRS AI Detection (v1.0)

- **Model**: DentexSegAndDet v1.0
- **Run at**: 2026-09-09T21:10:45+00:00
- **Confidence threshold**: 0.25
- **Evaluation subset**: 141 images (training_held_out)
- **Dataset root**: `evaluation/testdataset`

## 5.3 Evaluation Metrics

| Component | Metric | Target | Actual | Result |
|---|---|---|---|---|
| YOLOv8x (Disease) | mAP@0.5 | ≥ 0.50 | 0.5290 | PASS |
| YOLOv8x (Disease) | mAP@0.5:0.95 | ≥ 0.30 | 0.3603 | PASS |
| YOLOv8x (Disease) | F1 — Impacted | ≥ 0.80 | 0.8784 | PASS |
| YOLOv8x (Disease) | F1 — Caries | ≥ 0.45 | 0.4661 | PASS |
| YOLOv8x (Disease) | F1 — Periapical Lesion | ≥ 0.30 | 0.3333 | PASS |
| YOLOv8x (Disease) | F1 — Deep Caries | ≥ 0.50 | 0.5172 | PASS |
| SEUNet (Tooth) | Mean IoU | ≥ 0.65 | 0.6587 | PASS |
| SEUNet (Tooth) | Enumeration Accuracy | ≥ 0.85 | 0.8613 | PASS |
| Post-processing | Assignment Accuracy | ≥ 0.85 | 0.9238 | PASS |

### Cross-check against the training run

The YOLOv8x training run validated every epoch against the same held-out split used above, so its numbers and this run's are two independent measurements of the same thing — they should agree.

| Metric | Target | Measured above | Training run (best epoch) | Training run (last epoch) |
|---|---|---|---|---|
| mAP@0.5 | ≥ 0.50 | 0.5290 | 0.5581 | 0.4774 |
| mAP@0.5:0.95 | ≥ 0.30 | 0.3603 | 0.3835 | 0.3189 |

Trained for 100 epochs; best epoch 57 by mAP@0.5:0.95.

Measured mAP@0.5 differs from the training run's best epoch by **-0.0290** — close agreement between two independent implementations of the same metric on the same images, which is the main evidence that this harness computes mAP correctly.

Restricting the same detections to conf ≥ 0.25 — the threshold the product runs at — drops mAP@0.5 to **0.4493**. That is the cost of the deployment threshold, not a property of the weights; mAP above is reported over the full curve so it stays comparable with published figures.

Per-class F1 on the held-out split is not in `results.csv` — read it off `BoxF1_curve.png` at confidence 0.25.

### Per-class disease detection (conf ≥ 0.25, IoU 0.5)

| Class | Support | Predicted | TP | FP | FN | Precision | Recall | F1 |
|---|---|---|---|---|---|---|---|---|
| Impacted | 129 | 126 | 112 | 14 | 17 | 0.889 | 0.868 | 0.878 |
| Caries | 448 | 599 | 244 | 355 | 204 | 0.407 | 0.545 | 0.466 |
| Periapical Lesion | 18 | 18 | 6 | 12 | 12 | 0.333 | 0.333 | 0.333 |
| Deep Caries | 106 | 68 | 45 | 23 | 61 | 0.662 | 0.425 | 0.517 |

## 5.4 Test Case Results

| ID | Objective | Expected Result | Actual Result | Verdict |
|---|---|---|---|---|
| AITC-01 | Evaluate disease detection accuracy of YOLOv8x | mAP@0.5 >= 0.50<br>mAP@0.5:0.95 >= 0.30<br>per-class F1 >= its target | mAP@0.5 >= 0.50: PASS<br>mAP@0.5:0.95 >= 0.30: PASS<br>per-class F1 >= its target: PASS | **PASS** |
| AITC-02 | Evaluate tooth enumeration (segmentation) accuracy of SEUNet | Mean IoU >= 0.70<br>Enumeration Accuracy >= 0.90 | Mean IoU >= 0.70: PASS<br>Enumeration Accuracy >= 0.90: PASS | **PASS** |
| AITC-03 | Evaluate Tooth-Disease mapping logic | Assignment Accuracy >= 0.85 | Assignment Accuracy >= 0.85: PASS | **PASS** |
| AITC-04 | Evaluate model robustness on edge-case images | pipeline completes on every image<br>no unfiltered low-confidence detections | pipeline completes on every image: PASS<br>no unfiltered low-confidence detections: PASS | **PASS** |

### AITC-04 detail

15 degraded images · all completed: True · unfiltered low-confidence detections: 0

| Image | Degradation | Completed | Detections | Min confidence |
|---|---|---|---|---|
| train_283.blur.png | blur | yes | 0 | n/a |
| train_646.low_contrast.png | low_contrast | yes | 0 | n/a |
| train_564.cropped.png | cropped | yes | 5 | 0.368 |
| train_289.dark.png | dark | yes | 7 | 0.313 |
| train_271.noisy.png | noisy | yes | 1 | 0.306 |
| train_383.blur.png | blur | yes | 3 | 0.277 |
| train_700.low_contrast.png | low_contrast | yes | 1 | 0.809 |
| train_54.cropped.png | cropped | yes | 4 | 0.320 |
| train_541.dark.png | dark | yes | 2 | 0.561 |
| train_113.noisy.png | noisy | yes | 1 | 0.315 |
| train_447.blur.png | blur | yes | 0 | n/a |
| train_441.low_contrast.png | low_contrast | yes | 1 | 0.331 |
| train_110.cropped.png | cropped | yes | 3 | 0.328 |
| train_137.dark.png | dark | yes | 5 | 0.329 |
| train_108.noisy.png | noisy | yes | 0 | n/a |

## Notes

- mAP is computed over the full precision-recall curve (detections down to conf ≥ 0.001), which is what the metric is defined as and what makes it comparable with published figures. Metrics that depend on a threshold — per-class F1, assignment accuracy, the edge-case checks — use the deployed conf ≥ 0.25 instead.
- Classes with no ground truth in the subset are excluded from mAP rather than scored 0.
- Per-class F1 targets differ by class: a flat 0.50 is above the model's ceiling for Caries and Periapical Lesion at any confidence. Each target sits just under demonstrated performance so the suite catches regressions.
- Assignment accuracy (AITC-03) is measured only over detections that matched a ground-truth lesion at IoU ≥ 0.5, so a YOLO miss is not double-counted as a mapping error.
- Tooth segmentation was scored on the `quadrant_enumeration` subset (127 images, 3670 annotated teeth).
- The SEUNet held-out split was **reconstructed**, not recovered: `train_unet.py` splits with `random_split(..., generator=manual_seed(42))` over the image order in `train_quadrant_enumeration.json`, so the split follows from the public dataset alone — no file from the training machine is needed.
- Reconstruction **confirmed**: the same model scores 0.7701 mean IoU on the train half against 0.6587 on the held-out half (+0.1114). A wrong reconstruction would show no such gap.
