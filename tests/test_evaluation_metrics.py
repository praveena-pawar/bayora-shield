
import pytest

from evaluator.evaluation_metrics import calculate_metrics


def test_confusion_matrix_and_metrics():
    results = [
        {"expected_decision": "BLOCK", "actual_decision": "BLOCK"},  # TP
        {"expected_decision": "BLOCK", "actual_decision": "ALLOW"},  # FN
        {"expected_decision": "ALLOW", "actual_decision": "BLOCK"},  # FP
        {"expected_decision": "ALLOW", "actual_decision": "ALLOW"},  # TN
    ]

    metrics = calculate_metrics(results)

    assert metrics["true_positives"] == 1
    assert metrics["false_positives"] == 1
    assert metrics["true_negatives"] == 1
    assert metrics["false_negatives"] == 1

    assert metrics["precision"] == 0.5
    assert metrics["recall"] == 0.5
    assert metrics["false_positive_rate"] == 0.5
    assert metrics["accuracy"] == 0.5
    assert metrics["binary_cases_evaluated"] == 4


def test_flagged_attacks_and_benign_prompts():
    results = [
        {"expected_decision": "BLOCK", "actual_decision": "FLAG"},
        {"expected_decision": "ALLOW", "actual_decision": "FLAG"},
        {"expected_decision": "BLOCK", "actual_decision": "BLOCK"},
        {"expected_decision": "ALLOW", "actual_decision": "ALLOW"},
    ]

    metrics = calculate_metrics(results)

    assert metrics["flagged_attacks"] == 1
    assert metrics["flagged_benign"] == 1
    assert metrics["true_positives"] == 1
    assert metrics["true_negatives"] == 1
    assert metrics["binary_cases_evaluated"] == 2
    assert metrics["accuracy"] == 1.0


def test_expected_flag_cases_are_excluded_from_binary_metrics():
    results = [
        {"expected_decision": "FLAG", "actual_decision": "FLAG"},
        {"expected_decision": "FLAG", "actual_decision": "BLOCK"},
        {"expected_decision": "BLOCK", "actual_decision": "BLOCK"},
    ]

    metrics = calculate_metrics(results)

    assert metrics["true_positives"] == 1
    assert metrics["binary_cases_evaluated"] == 1
    assert metrics["accuracy"] == 1.0


def test_empty_results_return_zero_metrics():
    metrics = calculate_metrics([])

    assert metrics["binary_cases_evaluated"] == 0
    assert metrics["precision"] == 0.0
    assert metrics["recall"] == 0.0
    assert metrics["false_positive_rate"] == 0.0
    assert metrics["accuracy"] == 0.0


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("expected_decision", "UNKNOWN"),
        ("actual_decision", "UNKNOWN"),
    ],
)
def test_unsupported_decisions_raise_value_error(field, value):
    result = {
        "expected_decision": "BLOCK",
        "actual_decision": "BLOCK",
    }
    result[field] = value

    with pytest.raises(ValueError, match="Unsupported"):
        calculate_metrics([result])


def test_missing_decision_field_raises_key_error():
    with pytest.raises(KeyError):
        calculate_metrics([{"expected_decision": "BLOCK"}])
