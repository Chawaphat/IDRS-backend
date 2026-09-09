"""
AI Model Evaluation gates — Test Plan v0.2.0, Chapter 5 (AITC-01 .. AITC-04).

These assert the §5.3 targets against a completed evaluation run rather than
running the model themselves: scoring ~105 panoramic X-rays through YOLOv8x +
SEUNet takes far too long for a normal `pytest` invocation, and needs both the
DENTEX dataset and the model weights on disk.

So the workflow is two steps:

    python -m evaluation.run_evaluation --dataset-root ~/datasets/dentex
    pytest tests/test_ai_model_evaluation.py

Without `evaluation/results/results.json` every test here skips — it never
reports a false pass. Point `IDRS_EVAL_RESULTS` at another path to check a
different run.

The metric implementations themselves are covered by
tests/test_ai_evaluation_metrics.py, which needs no dataset.
"""
import json
import os

import pytest

from evaluation.run_evaluation import PER_CLASS_F1_TARGETS, TARGETS

RESULTS_PATH = os.environ.get(
    "IDRS_EVAL_RESULTS",
    os.path.join(os.path.dirname(__file__), "..", "evaluation", "results", "results.json"),
)


@pytest.fixture(scope="module")
def results():
    path = os.path.abspath(RESULTS_PATH)
    if not os.path.exists(path):
        pytest.skip(
            f"No evaluation results at {path}. Run "
            "`python -m evaluation.run_evaluation --dataset-root <DENTEX root>` first "
            "(see evaluation/README.md)."
        )
    with open(path) as handle:
        return json.load(handle)


def _section(results, name):
    section = results.get(name)
    if not section:
        pytest.skip(f"'{name}' was skipped in this evaluation run")
    return section


# ===========================================================================
# Provenance — a run on training data cannot validate anything
# ===========================================================================
class TestEvaluationProvenance:

    def test_subset_size_matches_the_test_plan(self, results):
        """§5.2 asks for a held-out sample of ~15% (100-110 images).

        When the original training split is supplied its real size wins — the
        images the model actually never saw matter more than hitting a count,
        and that split was 20% rather than 15%.
        """
        n_images = results["meta"]["n_images"]
        if results["meta"]["subset_provenance"]["method"] == "training_held_out":
            assert n_images >= 100
        else:
            assert 100 <= n_images <= 110

    def test_confidence_threshold_is_the_deployed_one(self, results):
        """§5.2: evaluated exactly as deployed, at conf=0.25."""
        assert results["meta"]["conf_threshold"] == 0.25

    def test_no_images_failed_during_inference(self, results):
        assert results["failures"] == [], f"inference failures: {results['failures']}"

    def test_subset_covers_all_four_disease_classes(self, results):
        distribution = results["meta"]["class_distribution"]
        missing = [name for name, counts in distribution.items() if counts["images"] == 0]
        assert not missing, f"evaluation subset has no images for: {missing}"

    def test_subset_is_genuinely_held_out_from_training(self, results):
        """A run over training data measures memorisation, not accuracy.

        The original split is `instances_val2017.json` from the training run;
        pass it with --held-out-json. Without it every disease metric below is
        an upper bound rather than a result.
        """
        assert results["meta"]["subset_provenance"]["leakage_risk"] == "none", (
            "evaluated on images that overlap the training set — re-run with "
            "--held-out-json <instances_val2017.json>"
        )


# ===========================================================================
# AITC-01 — disease detection accuracy (YOLOv8x)
# ===========================================================================
class TestAITC01DiseaseDetection:

    def test_map_50_meets_target(self, results):
        value = _section(results, "detection")["map_50"]["mAP"]
        assert value is not None
        assert value >= TARGETS["map_50"], f"mAP@0.5 = {value:.4f}, target ≥ 0.50"

    def test_map_50_95_meets_target(self, results):
        value = _section(results, "detection")["map_50_95"]["mAP"]
        assert value is not None
        assert value >= TARGETS["map_50_95"], f"mAP@0.5:0.95 = {value:.4f}, target ≥ 0.30"

    def test_map_is_scored_over_the_full_precision_recall_curve(self, results):
        """mAP at the deployed threshold is not comparable to a published mAP."""
        floor = _section(results, "detection").get("map_conf_threshold")
        assert floor is not None and floor <= 0.01, (
            f"mAP collected at conf ≥ {floor} — that truncates the curve; "
            "re-run without raising --map-conf"
        )

    def test_every_disease_class_meets_the_f1_target(self, results):
        per_class = _section(results, "detection")["prf1"]["per_class"]
        weak = {
            name: {"f1": round(stats["f1"], 4), "target": PER_CLASS_F1_TARGETS[name]}
            for name, stats in per_class.items()
            if stats["support"] > 0
            and name in PER_CLASS_F1_TARGETS
            and stats["f1"] < PER_CLASS_F1_TARGETS[name]
        }
        assert not weak, f"classes below their F1 target: {weak}"


# ===========================================================================
# AITC-02 — tooth enumeration / segmentation (SEUNet)
# ===========================================================================
class TestAITC02ToothEnumeration:

    def test_segmentation_subset_is_genuinely_held_out(self, results):
        provenance = _section(results, "segmentation").get("provenance") or {}
        assert provenance.get("leakage_risk") == "none", (
            "tooth metrics were measured on images not known to be held out "
            f"(provenance: {provenance.get('method')})"
        )

    def test_reconstructed_split_was_confirmed_by_the_control_pass(self, results):
        """A reconstruction is only trustworthy if it shows a train/val gap."""
        verification = _section(results, "segmentation").get("split_verification")
        if not verification:
            pytest.skip("no split reconstruction in this run")
        assert verification["verified"] is True, verification.get("reason")

    def test_mean_iou_meets_target(self, results):
        value = _section(results, "segmentation")["mean_iou"]
        assert value is not None
        assert value >= TARGETS["mean_iou"], (
            f"Mean IoU = {value:.4f}, target ≥ {TARGETS['mean_iou']}"
        )

    def test_enumeration_accuracy_meets_target(self, results):
        value = _section(results, "segmentation")["enumeration_accuracy"]
        assert value is not None
        assert value >= TARGETS["enumeration_accuracy"], (
            f"Enumeration accuracy = {value:.4f}, "
            f"target ≥ {TARGETS['enumeration_accuracy']}"
        )


# ===========================================================================
# AITC-03 — tooth-disease mapping (post-processing)
# ===========================================================================
class TestAITC03DiseaseToToothMapping:

    def test_assignment_accuracy_meets_target(self, results):
        assignment = _section(results, "assignment")
        value = assignment["assignment_accuracy"]
        assert value is not None, "no detection matched a ground-truth lesion"
        assert value >= TARGETS["assignment_accuracy"], (
            f"Assignment accuracy = {value:.4f} over "
            f"{assignment['matched_detections']} matched detections, target ≥ 0.85"
        )

    def test_every_matched_detection_was_assigned_to_some_tooth(self, results):
        """A null tooth_fdi means the mask never covered the lesion box."""
        assignment = _section(results, "assignment")
        assert assignment["unassigned"] == 0, (
            f"{assignment['unassigned']} of {assignment['matched_detections']} matched "
            "detections could not be mapped to a tooth"
        )


# ===========================================================================
# AITC-04 — robustness on degraded images
# ===========================================================================
class TestAITC04Robustness:

    def test_enough_edge_case_images_were_evaluated(self, results):
        """§5.4 asks for 10-15 poor quality images."""
        assert _section(results, "edge_cases")["n_images"] >= 10

    def test_pipeline_completes_on_every_degraded_image(self, results):
        edge_cases = _section(results, "edge_cases")
        crashed = [
            (case["image"], case["error"])
            for case in edge_cases["cases"]
            if not case["completed"]
        ]
        assert not crashed, f"pipeline crashed on: {crashed}"

    def test_no_detection_slips_below_the_confidence_threshold(self, results):
        edge_cases = _section(results, "edge_cases")
        assert edge_cases["unfiltered_detections"] == 0


# ===========================================================================
# Overall verdicts, as written into the report
# ===========================================================================
class TestOverallVerdicts:

    @pytest.mark.parametrize("case_id", ["AITC-01", "AITC-02", "AITC-03", "AITC-04"])
    def test_case_verdict_is_pass(self, results, case_id):
        case = results["verdicts"][case_id]
        if case["verdict"] == "NOT RUN":
            pytest.skip(f"{case_id} was not run in this evaluation")
        failed = [name for name, passed in case["checks"].items() if passed is False]
        assert case["verdict"] == "PASS", f"{case_id} failed: {failed}"
