"""
Tests for the AI Model Evaluation harness (`evaluation/`).

These verify the *measuring instrument* for Test Plan Chapter 5 — the metric
maths, the DENTEX label conversions and the subset selection — using synthetic
data. They need neither the DENTEX dataset nor the ML stack, so the harness
can be trusted before anyone spends an hour running the real evaluation.

The evaluation of the model itself lives in tests/test_ai_model_evaluation.py.
"""
import pytest

from evaluation import dentex_gt, subset as subset_mod
from evaluation.metrics import (
    DISEASE_CLASSES,
    average_precision,
    compute_assignment_accuracy,
    compute_map,
    compute_precision_recall_f1,
    iou_xyxy,
    match_detections,
    summarise_tooth_masks,
)
from evaluation.run_evaluation import render_report, score


def box(x1, y1, x2, y2):
    return [x1, y1, x2, y2]


def gt(image_id, class_name, bbox, tooth_fdi=11):
    return {
        "image_id": image_id,
        "class": class_name,
        "bbox": bbox,
        "tooth_fdi": tooth_fdi,
    }


def pred(image_id, class_name, score_value, bbox, tooth_fdi=11):
    return {
        "image_id": image_id,
        "class": class_name,
        "score": score_value,
        "bbox": bbox,
        "tooth_fdi": tooth_fdi,
    }


# ===========================================================================
# Geometry
# ===========================================================================
class TestIoU:

    def test_identical_boxes_score_one(self):
        assert iou_xyxy(box(0, 0, 10, 10), box(0, 0, 10, 10)) == 1.0

    def test_disjoint_boxes_score_zero(self):
        assert iou_xyxy(box(0, 0, 10, 10), box(20, 20, 30, 30)) == 0.0

    def test_edge_touching_boxes_score_zero(self):
        assert iou_xyxy(box(0, 0, 10, 10), box(10, 0, 20, 10)) == 0.0

    def test_half_overlap(self):
        # 10x10 and 10x10 sharing a 5x10 strip -> 50 / (100 + 100 - 50)
        assert iou_xyxy(box(0, 0, 10, 10), box(5, 0, 15, 10)) == pytest.approx(50 / 150)

    def test_contained_box(self):
        assert iou_xyxy(box(0, 0, 10, 10), box(0, 0, 5, 10)) == pytest.approx(0.5)


# ===========================================================================
# Matching
# ===========================================================================
class TestMatchDetections:

    def test_one_gt_is_claimed_only_once(self):
        """A second overlapping detection is a false positive, not a 2nd TP."""
        predictions = [
            pred(1, "Caries", 0.9, box(0, 0, 10, 10)),
            pred(1, "Caries", 0.8, box(0, 0, 10, 10)),
        ]
        scored, matched = match_detections(predictions, [gt(1, "Caries", box(0, 0, 10, 10))], 0.5)

        assert [is_tp for _, is_tp in scored] == [True, False]
        assert matched == [0]

    def test_predictions_are_consumed_highest_confidence_first(self):
        predictions = [
            pred(1, "Caries", 0.4, box(0, 0, 10, 10)),
            pred(1, "Caries", 0.95, box(0, 0, 10, 10)),
        ]
        scored, _ = match_detections(predictions, [gt(1, "Caries", box(0, 0, 10, 10))], 0.5)

        assert scored[0][0] == 0.95 and scored[0][1] is True
        assert scored[1][0] == 0.4 and scored[1][1] is False

    def test_boxes_from_another_image_never_match(self):
        scored, matched = match_detections(
            [pred(2, "Caries", 0.9, box(0, 0, 10, 10))],
            [gt(1, "Caries", box(0, 0, 10, 10))],
            0.5,
        )
        assert scored == [(0.9, False)]
        assert matched == []

    def test_overlap_below_threshold_is_a_false_positive(self):
        scored, matched = match_detections(
            [pred(1, "Caries", 0.9, box(0, 0, 10, 10))],
            [gt(1, "Caries", box(8, 0, 18, 10))],
            0.5,
        )
        assert scored == [(0.9, False)]
        assert matched == []


# ===========================================================================
# Average precision
# ===========================================================================
class TestAveragePrecision:

    def test_perfect_detector_scores_one(self):
        assert average_precision([(0.9, True)], n_ground_truth=1) == pytest.approx(1.0)

    def test_class_with_no_ground_truth_is_undefined(self):
        assert average_precision([(0.9, False)], n_ground_truth=0) is None

    def test_no_predictions_scores_zero(self):
        assert average_precision([], n_ground_truth=5) == 0.0

    def test_false_positive_after_full_recall_does_not_hurt(self):
        scored = [(0.9, True), (0.4, False)]
        assert average_precision(scored, n_ground_truth=1) == pytest.approx(1.0)

    def test_half_recall_scores_about_half(self):
        # 1 of 2 ground truths found at precision 1.0 -> 51 of 101 recall points
        assert average_precision([(0.9, True)], n_ground_truth=2) == pytest.approx(
            51 / 101
        )


# ===========================================================================
# AITC-01 — mAP and per-class F1
# ===========================================================================
class TestDetectionMetrics:

    def test_perfect_predictions_give_map_one(self):
        ground_truths = [gt(1, name, box(0, 0, 10, 10)) for name in DISEASE_CLASSES]
        predictions = [pred(1, name, 0.9, box(0, 0, 10, 10)) for name in DISEASE_CLASSES]

        result = compute_map(predictions, ground_truths, iou_thresholds=[0.5])

        assert result["mAP"] == pytest.approx(1.0)
        assert result["classes_scored"] == 4

    def test_class_absent_from_ground_truth_is_excluded_not_zeroed(self):
        ground_truths = [gt(1, "Caries", box(0, 0, 10, 10))]
        predictions = [pred(1, "Caries", 0.9, box(0, 0, 10, 10))]

        result = compute_map(predictions, ground_truths, iou_thresholds=[0.5])

        assert result["classes_scored"] == 1
        assert result["mAP"] == pytest.approx(1.0)
        assert result["per_class_ap"]["Impacted"] is None

    def test_map_50_95_is_stricter_than_map_50(self):
        # A slightly-offset box clears IoU 0.5 but fails the higher thresholds.
        ground_truths = [gt(1, "Caries", box(0, 0, 100, 100))]
        predictions = [pred(1, "Caries", 0.9, box(20, 0, 120, 100))]

        at_50 = compute_map(predictions, ground_truths, iou_thresholds=[0.5])
        sweep = compute_map(
            predictions, ground_truths, iou_thresholds=[0.5 + 0.05 * i for i in range(10)]
        )

        assert at_50["mAP"] == pytest.approx(1.0)
        assert sweep["mAP"] < at_50["mAP"]

    def test_precision_recall_f1_counts(self):
        ground_truths = [
            gt(1, "Caries", box(0, 0, 10, 10)),
            gt(2, "Caries", box(0, 0, 10, 10)),
        ]
        predictions = [
            pred(1, "Caries", 0.9, box(0, 0, 10, 10)),      # TP
            pred(1, "Caries", 0.8, box(50, 50, 60, 60)),    # FP
        ]

        stats = compute_precision_recall_f1(predictions, ground_truths)["per_class"]["Caries"]

        assert (stats["tp"], stats["fp"], stats["fn"]) == (1, 1, 1)
        assert stats["precision"] == pytest.approx(0.5)
        assert stats["recall"] == pytest.approx(0.5)
        assert stats["f1"] == pytest.approx(0.5)

    def test_macro_f1_ignores_classes_with_no_support(self):
        ground_truths = [gt(1, "Caries", box(0, 0, 10, 10))]
        predictions = [pred(1, "Caries", 0.9, box(0, 0, 10, 10))]

        result = compute_precision_recall_f1(predictions, ground_truths)

        assert result["macro_f1"] == pytest.approx(1.0)
        assert result["per_class"]["Impacted"]["support"] == 0


# ===========================================================================
# AITC-02 — tooth masks
# ===========================================================================
class TestToothMaskSummary:

    def test_mean_iou_and_enumeration_accuracy(self):
        per_tooth = [
            {"image_id": 1, "tooth_fdi": 11, "intersection": 90, "union": 100},  # 0.9
            {"image_id": 1, "tooth_fdi": 12, "intersection": 30, "union": 100},  # 0.3
        ]

        summary = summarise_tooth_masks(per_tooth)

        assert summary["mean_iou"] == pytest.approx(0.6)
        assert summary["enumeration_accuracy"] == pytest.approx(0.5)
        assert summary["teeth_evaluated"] == 2

    def test_missed_tooth_scores_zero_iou(self):
        summary = summarise_tooth_masks(
            [{"image_id": 1, "tooth_fdi": 48, "intersection": 0, "union": 500}]
        )

        assert summary["mean_iou"] == 0.0
        assert summary["enumeration_accuracy"] == 0.0

    def test_per_fdi_breakdown(self):
        per_tooth = [
            {"image_id": 1, "tooth_fdi": 11, "intersection": 80, "union": 100},
            {"image_id": 2, "tooth_fdi": 11, "intersection": 60, "union": 100},
        ]

        summary = summarise_tooth_masks(per_tooth)

        assert summary["per_fdi"][11]["count"] == 2
        assert summary["per_fdi"][11]["mean_iou"] == pytest.approx(0.7)

    def test_empty_input_is_undefined_not_zero(self):
        summary = summarise_tooth_masks([])

        assert summary["mean_iou"] is None
        assert summary["enumeration_accuracy"] is None


# ===========================================================================
# AITC-03 — disease-to-tooth assignment
# ===========================================================================
class TestAssignmentAccuracy:

    def test_correct_and_incorrect_assignments(self):
        ground_truths = [
            gt(1, "Caries", box(0, 0, 10, 10), tooth_fdi=36),
            gt(2, "Caries", box(0, 0, 10, 10), tooth_fdi=47),
        ]
        predictions = [
            pred(1, "Caries", 0.9, box(0, 0, 10, 10), tooth_fdi=36),  # right
            pred(2, "Caries", 0.9, box(0, 0, 10, 10), tooth_fdi=46),  # wrong
        ]

        result = compute_assignment_accuracy(predictions, ground_truths)

        assert result["matched_detections"] == 2
        assert result["assignment_accuracy"] == pytest.approx(0.5)
        assert result["errors"][0]["expected_fdi"] == 47
        assert result["errors"][0]["actual_fdi"] == 46

    def test_unassigned_tooth_fdi_counts_as_wrong(self):
        result = compute_assignment_accuracy(
            [pred(1, "Caries", 0.9, box(0, 0, 10, 10), tooth_fdi=None)],
            [gt(1, "Caries", box(0, 0, 10, 10), tooth_fdi=36)],
        )

        assert result["unassigned"] == 1
        assert result["assignment_accuracy"] == 0.0

    def test_unmatched_detection_is_not_judged(self):
        """A YOLO miss belongs to AITC-01, not to the mapping metric."""
        result = compute_assignment_accuracy(
            [pred(1, "Caries", 0.9, box(90, 90, 100, 100), tooth_fdi=11)],
            [gt(1, "Caries", box(0, 0, 10, 10), tooth_fdi=36)],
        )

        assert result["matched_detections"] == 0
        assert result["assignment_accuracy"] is None

    def test_perfect_mapping(self):
        result = compute_assignment_accuracy(
            [pred(1, "Impacted", 0.9, box(0, 0, 10, 10), tooth_fdi=38)],
            [gt(1, "Impacted", box(0, 0, 10, 10), tooth_fdi=38)],
        )

        assert result["assignment_accuracy"] == pytest.approx(1.0)


# ===========================================================================
# DENTEX ground-truth conversions
# ===========================================================================
class TestDentexConversions:

    @pytest.mark.parametrize(
        "quadrant,enumeration,expected_fdi",
        [(0, 0, 11), (0, 7, 18), (1, 0, 21), (2, 5, 36), (3, 7, 48)],
    )
    def test_fdi_from_categories(self, quadrant, enumeration, expected_fdi):
        assert dentex_gt.fdi_from_categories(quadrant, enumeration) == expected_fdi

    def test_segmentation_label_round_trips_to_the_same_fdi(self):
        """GT mask labels must land in the same FDI space the model predicts."""
        from app.services.ai_inference import _label_to_fdi

        for quadrant in range(4):
            for enumeration in range(8):
                label = dentex_gt.segmentation_label(quadrant, enumeration)
                assert 1 <= label <= 32
                assert _label_to_fdi(label) == dentex_gt.fdi_from_categories(
                    quadrant, enumeration
                )

    def test_coco_bbox_becomes_xyxy(self):
        assert dentex_gt.xyxy_from_coco([10, 20, 30, 40]) == [10, 20, 40, 60]

    def test_polygons_accepts_flat_and_nested_forms(self):
        flat = [0, 0, 10, 0, 10, 10]
        assert dentex_gt.polygons(flat) == [flat]
        assert dentex_gt.polygons([flat]) == [flat]

    def test_polygons_rejects_degenerate_shapes(self):
        assert dentex_gt.polygons([]) == []
        assert dentex_gt.polygons([0, 0, 1, 1]) == []  # only 2 points


# ===========================================================================
# Reading a DENTEX dataset off disk
# ===========================================================================
def write_dentex_dataset(root, directory_name, json_name, with_disease):
    """Write a miniature DENTEX subset (annotations only — no image files)."""
    import json

    subset_dir = root / directory_name
    (subset_dir / "xrays").mkdir(parents=True)

    annotation = {
        "id": 1,
        "image_id": 7,
        "bbox": [100, 200, 50, 80],
        "segmentation": [100, 200, 150, 200, 150, 280, 100, 280],
        "category_id_1": 2,   # quadrant 3
        "category_id_2": 5,   # tooth 6  -> FDI 36
    }
    if with_disease:
        annotation["category_id_3"] = 1  # Caries

    (subset_dir / json_name).write_text(
        json.dumps(
            {
                "images": [
                    {"id": 7, "file_name": "train_7.png", "width": 2800, "height": 1300}
                ],
                "annotations": [annotation],
            }
        )
    )
    return subset_dir


class TestDatasetLoading:

    def test_loads_the_disease_subset(self, tmp_path):
        write_dentex_dataset(
            tmp_path,
            "quadrant_enumeration_disease",
            "train_quadrant_enumeration_disease.json",
            with_disease=True,
        )

        records = dentex_gt.load_disease_subset(str(tmp_path))

        assert len(records) == 1
        record = records[0]
        assert record.file_name == "train_7.png"
        assert record.path.endswith("xrays/train_7.png")
        assert record.diseases == [
            {
                "image_id": 7,
                "class": "Caries",
                "bbox": [100, 200, 150, 280],
                "tooth_fdi": 36,
            }
        ]
        assert record.teeth[0]["label"] == 22  # quadrant 2 * 8 + 5 + 1

    def test_accepts_hyphenated_directory_names(self, tmp_path):
        write_dentex_dataset(
            tmp_path,
            "quadrant-enumeration-disease",
            "train_quadrant-enumeration-disease.json",
            with_disease=True,
        )

        assert len(dentex_gt.load_disease_subset(str(tmp_path))) == 1

    def test_finds_a_subset_nested_under_training_data(self, tmp_path):
        write_dentex_dataset(
            tmp_path / "training_data",
            "quadrant_enumeration_disease",
            "train_quadrant_enumeration_disease.json",
            with_disease=True,
        )

        assert len(dentex_gt.load_disease_subset(str(tmp_path))) == 1

    def test_enumeration_subset_carries_teeth_but_no_diseases(self, tmp_path):
        write_dentex_dataset(
            tmp_path,
            "quadrant_enumeration",
            "train_quadrant_enumeration.json",
            with_disease=False,
        )

        records = dentex_gt.load_enumeration_subset(str(tmp_path))

        assert records[0].teeth[0]["tooth_fdi"] == 36
        assert records[0].diseases == []

    def test_missing_dataset_raises_a_pointed_error(self, tmp_path):
        with pytest.raises(FileNotFoundError, match="quadrant_enumeration_disease"):
            dentex_gt.load_disease_subset(str(tmp_path))

    def test_flatten_collects_every_finding(self, tmp_path):
        write_dentex_dataset(
            tmp_path,
            "quadrant_enumeration_disease",
            "train_quadrant_enumeration_disease.json",
            with_disease=True,
        )
        records = dentex_gt.load_disease_subset(str(tmp_path))

        assert dentex_gt.flatten_disease_ground_truth(records) == records[0].diseases


# ===========================================================================
# Mask rasterisation and comparison (needs numpy/PIL — skipped without them)
# ===========================================================================
class TestMaskComparison:

    @pytest.fixture(autouse=True)
    def _requires_numpy(self):
        pytest.importorskip("numpy", reason="mask comparison needs the ML stack")
        pytest.importorskip("PIL", reason="mask rasterisation needs pillow")

    def _record(self, label=22, square=(10, 10, 30, 30)):
        x1, y1, x2, y2 = square
        record = dentex_gt.ImageRecord(
            image_id=1, file_name="train_1.png", width=50, height=50,
            path="/tmp/train_1.png",
        )
        record.teeth.append(
            {
                "tooth_fdi": 36,
                "label": label,
                "bbox": [x1, y1, x2, y2],
                "polygons": [[x1, y1, x2, y1, x2, y2, x1, y2]],
            }
        )
        return record

    def test_polygon_is_rasterised_with_its_label(self):
        from evaluation.masks import rasterise_ground_truth

        mask = rasterise_ground_truth(self._record(label=22))

        assert mask.shape == (50, 50)
        assert mask[20, 20] == 22   # inside the polygon
        assert mask[5, 5] == 0      # background

    def test_identical_masks_score_full_overlap(self):
        from evaluation.masks import compare_masks, rasterise_ground_truth

        mask = rasterise_ground_truth(self._record())
        results = compare_masks(1, mask, mask)

        assert len(results) == 1
        assert results[0]["intersection"] == results[0]["union"]
        assert results[0]["tooth_fdi"] == 36  # label 22 -> quadrant 3, tooth 6

    def test_disjoint_masks_score_no_overlap(self):
        from evaluation.masks import compare_masks, rasterise_ground_truth

        truth = rasterise_ground_truth(self._record(square=(0, 0, 10, 10)))
        predicted = rasterise_ground_truth(self._record(square=(30, 30, 45, 45)))

        results = compare_masks(1, truth, predicted)

        assert results[0]["intersection"] == 0
        assert results[0]["union"] > 0

    def test_only_annotated_teeth_are_scored(self):
        """A tooth the model found but the GT never outlined is not an error."""
        from evaluation.masks import compare_masks, rasterise_ground_truth

        truth = rasterise_ground_truth(self._record(label=22))
        predicted = rasterise_ground_truth(self._record(label=22))
        predicted[40:48, 40:48] = 31  # an extra tooth the GT does not annotate

        results = compare_masks(1, truth, predicted)

        assert [entry["label"] for entry in results] == [22]

    def test_shape_mismatch_is_rejected_loudly(self):
        import numpy as np

        from evaluation.masks import compare_masks

        with pytest.raises(ValueError, match="shape mismatch"):
            compare_masks(1, np.zeros((10, 10)), np.zeros((20, 20)))


# ===========================================================================
# Evaluation subset selection
# ===========================================================================
def make_record(index, classes):
    record = dentex_gt.ImageRecord(
        image_id=index,
        file_name=f"train_{index}.png",
        width=2800,
        height=1300,
        path=f"/tmp/train_{index}.png",
    )
    for class_name in classes:
        record.diseases.append(
            {
                "image_id": index,
                "class": class_name,
                "bbox": [0, 0, 10, 10],
                "tooth_fdi": 11,
            }
        )
    return record


@pytest.fixture
def population():
    """705 images shaped like DENTEX: Caries common, Periapical Lesion rare."""
    records = []
    for index in range(705):
        if index % 17 == 0:
            classes = ["Periapical Lesion"]
        elif index % 5 == 0:
            classes = ["Impacted", "Caries"]
        elif index % 3 == 0:
            classes = ["Deep Caries"]
        else:
            classes = ["Caries"]
        records.append(make_record(index, classes))
    return records


class TestSubsetSelection:

    def test_subset_size_lands_in_the_test_plan_window(self, population):
        selected = subset_mod.build_subset(population)["images"]

        assert subset_mod.MIN_IMAGES <= len(selected) <= subset_mod.MAX_IMAGES

    def test_all_four_disease_classes_are_covered(self, population):
        selection = subset_mod.build_subset(population)

        for class_name in DISEASE_CLASSES:
            assert selection["class_distribution"][class_name]["images"] > 0, class_name

    def test_selection_is_deterministic_for_a_given_seed(self, population):
        first = subset_mod.build_subset(population, seed=42)["images"]
        second = subset_mod.build_subset(population, seed=42)["images"]

        assert [r.file_name for r in first] == [r.file_name for r in second]

    def test_a_different_seed_selects_a_different_subset(self, population):
        first = subset_mod.build_subset(population, seed=1)["images"]
        second = subset_mod.build_subset(population, seed=2)["images"]

        assert [r.file_name for r in first] != [r.file_name for r in second]

    def test_resampled_subset_is_flagged_as_leaky(self, population):
        provenance = subset_mod.build_subset(population)["provenance"]

        assert provenance["method"] == "stratified_resample"
        assert provenance["leakage_risk"] == "high"

    def test_explicit_held_out_list_is_used_verbatim_and_trusted(self, population):
        names = {f"train_{i}.png" for i in range(20)}

        selection = subset_mod.build_subset(population, held_out_file_names=names)

        assert {r.file_name for r in selection["images"]} == names
        assert selection["provenance"]["method"] == "training_held_out"
        assert selection["provenance"]["leakage_risk"] == "none"


# ===========================================================================
# AITC verdicts
# ===========================================================================
class TestScoring:

    def _results(self, **overrides):
        base = {
            "detection": {
                "map_50": {"mAP": 0.62},
                "map_50_95": {"mAP": 0.41},
                "prf1": {
                    "per_class": {
                        # Each comfortably above that class's own F1 target.
                        "Impacted": {"support": 10, "f1": 0.85},
                        "Caries": {"support": 10, "f1": 0.50},
                        "Periapical Lesion": {"support": 10, "f1": 0.35},
                        "Deep Caries": {"support": 10, "f1": 0.55},
                    }
                },
            },
            "segmentation": {"mean_iou": 0.78, "enumeration_accuracy": 0.93},
            "assignment": {"assignment_accuracy": 0.88},
            "edge_cases": {"all_completed": True, "unfiltered_detections": 0},
        }
        base.update(overrides)
        return base

    def test_all_targets_met_passes_every_case(self):
        verdicts = score(self._results())

        assert [case["verdict"] for case in verdicts.values()] == ["PASS"] * 4

    def test_map_below_target_fails_aitc_01(self):
        results = self._results()
        results["detection"]["map_50"] = {"mAP": 0.42}

        assert score(results)["AITC-01"]["verdict"] == "FAIL"

    def test_one_weak_class_fails_the_per_class_f1_check(self):
        results = self._results()
        results["detection"]["prf1"]["per_class"]["Periapical Lesion"]["f1"] = 0.25

        verdicts = score(results)

        assert verdicts["AITC-01"]["verdict"] == "FAIL"
        assert verdicts["AITC-01"]["per_class_f1_pass"]["Periapical Lesion"] is False

    def test_f1_targets_are_per_class_not_flat(self):
        """0.55 clears Deep Caries' bar but not Impacted's."""
        from evaluation.run_evaluation import PER_CLASS_F1_TARGETS

        results = self._results()
        for name in ("Impacted", "Deep Caries"):
            results["detection"]["prf1"]["per_class"][name]["f1"] = 0.55

        passes = score(results)["AITC-01"]["per_class_f1_pass"]

        assert passes["Deep Caries"] is True
        assert passes["Impacted"] is False
        assert PER_CLASS_F1_TARGETS["Impacted"] > PER_CLASS_F1_TARGETS["Deep Caries"]

    def test_a_class_with_no_ground_truth_is_not_judged(self):
        results = self._results()
        results["detection"]["prf1"]["per_class"]["Periapical Lesion"] = {
            "support": 0, "f1": 0.0
        }

        verdicts = score(results)

        assert "Periapical Lesion" not in verdicts["AITC-01"]["per_class_f1_pass"]
        assert verdicts["AITC-01"]["verdict"] == "PASS"

    def test_low_mean_iou_fails_aitc_02(self):
        results = self._results()
        results["segmentation"]["mean_iou"] = 0.55

        assert score(results)["AITC-02"]["verdict"] == "FAIL"

    def test_a_crash_on_a_degraded_image_fails_aitc_04(self):
        results = self._results()
        results["edge_cases"]["all_completed"] = False

        assert score(results)["AITC-04"]["verdict"] == "FAIL"

    def test_skipped_section_reports_not_run_rather_than_pass(self):
        results = self._results(segmentation={})

        assert score(results)["AITC-02"]["verdict"] == "NOT RUN"


# ===========================================================================
# SEUNet held-out split reconstruction
# ===========================================================================
class TestSeunetSplit:

    @pytest.fixture(autouse=True)
    def _requires_torch(self):
        pytest.importorskip("torch", reason="split reconstruction uses torch.randperm")

    def _dataset(self, tmp_path, n=634):
        import json

        directory = tmp_path / "quadrant_enumeration"
        (directory / "xrays").mkdir(parents=True)
        (directory / "train_quadrant_enumeration.json").write_text(
            json.dumps(
                {
                    # Deliberately not in filename order — the real DENTEX JSON
                    # is not either, and the split depends on this order.
                    "images": [
                        {"id": i + 1, "file_name": f"train_{(i * 7) % n}.png",
                         "width": 2800, "height": 1300}
                        for i in range(n)
                    ],
                    "annotations": [],
                }
            )
        )
        return tmp_path

    def test_reconstruction_matches_torch_random_split(self, tmp_path):
        """The whole approach rests on this equivalence."""
        import torch
        from torch.utils.data import random_split

        from evaluation.seunet_split import reconstruct_val_split
        from evaluation.dentex_gt import load_enumeration_subset  # noqa: F401

        root = self._dataset(tmp_path)
        split = reconstruct_val_split(str(root), seed=42, train_ratio=0.8)

        import json
        names = [
            image["file_name"]
            for image in json.load(
                open(root / "quadrant_enumeration" / "train_quadrant_enumeration.json")
            )["images"]
        ]
        total = len(names)
        train_size = int(total * 0.8)

        class _Indices:
            def __len__(self): return total
            def __getitem__(self, i): return i

        _, val = random_split(
            _Indices(), [train_size, total - train_size],
            generator=torch.Generator().manual_seed(42),
        )
        assert split["val_file_names"] == {names[i] for i in val.indices}

    def test_split_sizes_follow_the_train_ratio(self, tmp_path):
        from evaluation.seunet_split import reconstruct_val_split

        split = reconstruct_val_split(str(self._dataset(tmp_path)), train_ratio=0.8)

        assert len(split["train_file_names"]) == 507
        assert len(split["val_file_names"]) == 127
        assert not (split["train_file_names"] & split["val_file_names"])

    def test_a_different_seed_gives_a_different_split(self, tmp_path):
        from evaluation.seunet_split import reconstruct_val_split

        root = str(self._dataset(tmp_path))
        first = reconstruct_val_split(root, seed=42)["val_file_names"]
        second = reconstruct_val_split(root, seed=7)["val_file_names"]

        assert first != second

    def test_reconstruction_starts_out_unverified(self, tmp_path):
        from evaluation.seunet_split import reconstruct_val_split

        provenance = reconstruct_val_split(str(self._dataset(tmp_path)))["provenance"]

        assert provenance["method"] == "reconstructed_from_seed"
        assert provenance["leakage_risk"] == "unverified"

    def test_a_train_val_gap_confirms_the_reconstruction(self):
        from evaluation.seunet_split import verify_split

        result = verify_split(train_mean_iou=0.81, val_mean_iou=0.74)

        assert result["verified"] is True
        assert result["gap"] == pytest.approx(0.07)

    def test_no_gap_means_the_reconstruction_is_wrong(self):
        from evaluation.seunet_split import verify_split

        result = verify_split(train_mean_iou=0.74, val_mean_iou=0.75)

        assert result["verified"] is False
        assert "does not match" in result["reason"]

    def test_missing_measurements_are_undecided_not_confirmed(self):
        from evaluation.seunet_split import verify_split

        assert verify_split(None, 0.74)["verified"] is None


# ===========================================================================
# Held-out baseline recovered from the training run
# ===========================================================================
CSV_HEADER = (
    "epoch,time,train/box_loss,train/cls_loss,train/dfl_loss,"
    "metrics/precision(B),metrics/recall(B),metrics/mAP50(B),metrics/mAP50-95(B)\n"
)


def write_training_run(directory, rows, with_curve=True):
    directory.mkdir(parents=True, exist_ok=True)
    lines = [CSV_HEADER]
    for epoch, precision, recall, map_50, map_50_95 in rows:
        lines.append(
            f"{epoch},100.0,0.5,0.4,0.9,{precision},{recall},{map_50},{map_50_95}\n"
        )
    (directory / "results.csv").write_text("".join(lines))
    if with_curve:
        (directory / "BoxF1_curve.png").write_bytes(b"\x89PNG\r\n")
    return directory


class TestTrainingBaseline:

    def _rows(self):
        # epoch 2 is the best by mAP50-95; epoch 3 is the last.
        return [
            (1, 0.50, 0.40, 0.40, 0.25),
            (2, 0.59, 0.52, 0.5581, 0.3835),
            (3, 0.61, 0.47, 0.4774, 0.3189),
        ]

    def test_reads_best_and_last_epoch(self, tmp_path):
        from evaluation.training_baseline import load_training_baseline

        run = write_training_run(tmp_path / "dentex_disease", self._rows())
        baseline = load_training_baseline(str(run))

        assert baseline["epochs_trained"] == 3
        assert baseline["best_epoch"]["epoch"] == 2
        assert baseline["best_epoch"]["map_50"] == pytest.approx(0.5581)
        assert baseline["last_epoch"]["epoch"] == 3
        assert baseline["last_epoch"]["map_50_95"] == pytest.approx(0.3189)

    def test_locates_the_f1_curve_when_present(self, tmp_path):
        from evaluation.training_baseline import load_training_baseline

        run = write_training_run(tmp_path / "run", self._rows())
        assert load_training_baseline(str(run))["f1_curve"].endswith("BoxF1_curve.png")

    def test_missing_f1_curve_is_reported_as_none(self, tmp_path):
        from evaluation.training_baseline import load_training_baseline

        run = write_training_run(tmp_path / "run", self._rows(), with_curve=False)
        assert load_training_baseline(str(run))["f1_curve"] is None

    def test_missing_results_csv_raises_a_pointed_error(self, tmp_path):
        from evaluation.training_baseline import load_training_baseline

        with pytest.raises(FileNotFoundError, match="results.csv"):
            load_training_baseline(str(tmp_path))

    def test_comparison_quantifies_the_inflation(self, tmp_path):
        from evaluation.training_baseline import compare, load_training_baseline

        run = write_training_run(tmp_path / "run", self._rows())
        baseline = load_training_baseline(str(run))
        measured = {"map_50": {"mAP": 0.6961}, "map_50_95": {"mAP": 0.5105}}

        comparison = compare(measured, baseline)

        assert comparison["map_50"]["measured"] == pytest.approx(0.6961)
        assert comparison["map_50"]["last_epoch"] == pytest.approx(0.4774)
        assert comparison["map_50"]["inflation_vs_last_epoch"] == pytest.approx(
            0.6961 - 0.4774
        )
        assert comparison["map_50_95"]["inflation_vs_best_epoch"] == pytest.approx(
            0.5105 - 0.3835
        )

    def test_comparison_tolerates_a_missing_measured_value(self, tmp_path):
        from evaluation.training_baseline import compare, load_training_baseline

        run = write_training_run(tmp_path / "run", self._rows())
        comparison = compare({}, load_training_baseline(str(run)))

        assert comparison["map_50"]["measured"] is None
        assert comparison["map_50"]["inflation_vs_last_epoch"] is None


# ===========================================================================
# Report rendering
# ===========================================================================
class TestReport:

    def _results(self, leakage_risk="high"):
        results = {
            "meta": {
                "model_name": "DentexSegAndDet",
                "model_version": "v1.0",
                "run_at": "2026-09-10T00:00:00+00:00",
                "conf_threshold": 0.25,
                "dataset_root": "/data/dentex",
                "n_images": 105,
                "subset_provenance": {
                    "method": "stratified_resample",
                    "leakage_risk": leakage_risk,
                    "note": "overlaps the training data",
                },
                "class_distribution": {
                    name: {"images": 10, "instances": 20} for name in DISEASE_CLASSES
                },
            },
            "failures": [],
            "detection": {
                "map_50": {"mAP": 0.61},
                "map_50_95": {"mAP": 0.38},
                "prf1": {
                    "per_class": {
                        name: {
                            "support": 20, "predicted": 22, "tp": 15, "fp": 7,
                            "fn": 5, "precision": 0.68, "recall": 0.75, "f1": 0.71,
                        }
                        for name in DISEASE_CLASSES
                    }
                },
            },
            "segmentation": {
                "mean_iou": 0.76,
                "enumeration_accuracy": 0.92,
                "source": "quadrant_enumeration",
                "n_images": 95,
                "teeth_evaluated": 2900,
            },
            "assignment": {
                "assignment_accuracy": 0.88,
                "matched_detections": 60,
                "correct": 53,
                "unassigned": 0,
                "errors": [],
            },
            "edge_cases": {
                "n_images": 15,
                "all_completed": True,
                "unfiltered_detections": 0,
                "cases": [
                    {
                        "image": "a.blur.png", "degradation": "blur",
                        "completed": True, "error": None, "n_detections": 3,
                        "min_confidence": 0.31, "below_threshold": 0,
                    }
                ],
            },
        }
        results["verdicts"] = score(results)
        return results

    def test_report_contains_the_table_11_metrics(self):
        report = render_report(self._results())

        for metric in ("mAP@0.5", "mAP@0.5:0.95", "Mean IoU",
                       "Enumeration Accuracy", "Assignment Accuracy"):
            assert metric in report

    def test_table_11_prints_the_configured_targets(self):
        """The Target column is pasted into the Test Plan — it must not drift."""
        from evaluation.run_evaluation import PER_CLASS_F1_TARGETS, TARGETS

        report = render_report(self._results())

        for key in ("map_50", "map_50_95", "mean_iou",
                    "enumeration_accuracy", "assignment_accuracy"):
            assert f"≥ {TARGETS[key]:.2f}" in report, key
        for name, target in PER_CLASS_F1_TARGETS.items():
            assert f"F1 — {name} | ≥ {target:.2f}" in report, name

    def test_report_contains_every_aitc_case(self):
        report = render_report(self._results())

        for case_id in ("AITC-01", "AITC-02", "AITC-03", "AITC-04"):
            assert case_id in report

    def test_leaky_subset_is_called_out_in_the_report(self):
        assert "Data-leakage warning" in render_report(self._results())

    def test_genuinely_held_out_subset_carries_no_warning(self):
        assert "Data-leakage warning" not in render_report(
            self._results(leakage_risk="none")
        )

    def test_held_out_baseline_section_shows_the_inflation(self, tmp_path):
        from evaluation.training_baseline import compare, load_training_baseline

        run = write_training_run(
            tmp_path / "run",
            [(1, 0.50, 0.40, 0.40, 0.25), (3, 0.61, 0.47, 0.4774, 0.3189)],
        )
        baseline = load_training_baseline(str(run))
        results = self._results()
        results["held_out_baseline"] = {
            **baseline,
            "comparison": compare(results["detection"], baseline),
        }

        report = render_report(results)

        assert "Held-out baseline" in report
        assert "0.4774" in report
        assert "BoxF1_curve.png" in report

    def test_report_omits_the_baseline_section_when_absent(self):
        assert "Held-out baseline" not in render_report(self._results())

    def test_held_out_run_reframes_the_baseline_as_a_cross_check(self, tmp_path):
        from evaluation.training_baseline import compare, load_training_baseline

        run = write_training_run(tmp_path / "run", [(1, 0.6, 0.47, 0.4774, 0.3189)])
        baseline = load_training_baseline(str(run))
        results = self._results(leakage_risk="none")
        results["meta"]["subset_provenance"]["method"] = "training_held_out"
        results["held_out_baseline"] = {
            **baseline,
            "comparison": compare(results["detection"], baseline),
        }

        report = render_report(results)

        assert "Cross-check against the training run" in report
        assert "data leakage inflates" not in report

    def test_leaky_segmentation_is_warned_about_on_its_own(self):
        """The disease split can be clean while the tooth split is not."""
        results = self._results(leakage_risk="none")
        results["segmentation"]["provenance"] = {
            "method": "stratified_resample",
            "leakage_risk": "high",
        }

        report = render_report(results)

        assert "Data-leakage warning (tooth segmentation)" in report
        assert "Data-leakage warning (disease metrics)" not in report

    def test_report_renders_when_sections_were_skipped(self):
        results = self._results()
        results["segmentation"] = {}
        results["edge_cases"] = {}
        results["verdicts"] = score(results)

        report = render_report(results)

        assert "NOT RUN" in report
        assert "n/a" in report
