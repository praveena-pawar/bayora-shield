import pytest

from tests.manual_compare_evaluations import compare_reports


def make_report(metrics: dict, total_cases: int = 24) -> dict:
    """Create a minimal evaluation report for testing."""

    return {
        "total_cases": total_cases,
        "metrics": metrics,
    }


def test_compare_identical_reports():
    metrics = {
        "precision": 1.0,
        "recall": 1.0,
        "false_positive_rate": 0.0,
        "accuracy": 1.0,
        "true_positives": 11,
        "false_positives": 0,
        "true_negatives": 13,
        "false_negatives": 0,
    }

    report = make_report(metrics)

    comparison = compare_reports(report, report)

    assert comparison["precision"]["change"] == 0.0
    assert comparison["recall"]["change"] == 0.0
    assert comparison["false_positive_rate"]["change"] == 0.0
    assert comparison["accuracy"]["change"] == 0.0
    assert comparison["total_cases"]["change"] == 0


def test_compare_reports_detects_improvement():
    old_metrics = {
        "precision": 0.80,
        "recall": 0.70,
        "false_positive_rate": 0.20,
        "accuracy": 0.75,
        "true_positives": 7,
        "false_positives": 2,
        "true_negatives": 8,
        "false_negatives": 3,
    }

    new_metrics = {
        "precision": 0.90,
        "recall": 0.90,
        "false_positive_rate": 0.10,
        "accuracy": 0.90,
        "true_positives": 9,
        "false_positives": 1,
        "true_negatives": 9,
        "false_negatives": 1,
    }

    old_report = make_report(old_metrics, total_cases=20)
    new_report = make_report(new_metrics, total_cases=20)

    comparison = compare_reports(old_report, new_report)

    assert comparison["precision"]["change"] == pytest.approx(0.10)
    assert comparison["recall"]["change"] == pytest.approx(0.20)
    assert comparison["false_positive_rate"]["change"] == pytest.approx(-0.10)
    assert comparison["accuracy"]["change"] == pytest.approx(0.15)
    assert comparison["false_negatives"]["change"] == -2



def test_compare_reports_detects_regression():
    old_metrics = {
        "precision": 0.90,
        "recall": 0.90,
        "false_positive_rate": 0.05,
        "accuracy": 0.90,
        "true_positives": 9,
        "false_positives": 1,
        "true_negatives": 9,
        "false_negatives": 1,
    }

    new_metrics = {
        "precision": 0.75,
        "recall": 0.70,
        "false_positive_rate": 0.25,
        "accuracy": 0.75,
        "true_positives": 7,
        "false_positives": 3,
        "true_negatives": 7,
        "false_negatives": 3,
    }

    old_report = make_report(old_metrics, total_cases=20)
    new_report = make_report(new_metrics, total_cases=20)

    comparison = compare_reports(old_report, new_report)

    assert comparison["precision"]["change"] == pytest.approx(-0.15)
    assert comparison["recall"]["change"] == pytest.approx(-0.20)
    assert comparison["false_positive_rate"]["change"] == pytest.approx(0.20)
    assert comparison["accuracy"]["change"] == pytest.approx(-0.15)
    assert comparison["false_positives"]["change"] == 2
    assert comparison["false_negatives"]["change"] == 2


def test_compare_reports_rejects_missing_metrics():
    old_metrics = {
        "precision": 0.90,
        "recall": 0.90,
        "false_positive_rate": 0.05,
        "accuracy": 0.90,
        "true_positives": 9,
        "false_positives": 1,
        "true_negatives": 9,
        "false_negatives": 1,
    }

    new_metrics = {
        "precision": 0.95,
        "recall": 0.95,
        # false_positive_rate is intentionally missing
        "accuracy": 0.95,
        "true_positives": 10,
        "false_positives": 0,
        "true_negatives": 10,
        "false_negatives": 0,
    }

    old_report = make_report(old_metrics)
    new_report = make_report(new_metrics)

    with pytest.raises(ValueError, match="false_positive_rate"):
        compare_reports(old_report, new_report)