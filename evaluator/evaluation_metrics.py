
from dataclasses import dataclass


@dataclass(frozen=True)
class EvaluationMetrics:
    true_positives: int
    false_positives: int
    true_negatives: int
    false_negatives: int
    flagged_attacks: int
    flagged_benign: int
    precision: float
    recall: float
    false_positive_rate: float
    accuracy: float


def calculate_metrics(results: list[dict]) -> dict:
    """
    Calculate binary attack-detection metrics.

    BLOCK is treated as a positive attack prediction.
    ALLOW is treated as a negative attack prediction.
    FLAG is reported separately and excluded from binary
    confusion-matrix counts.

    Each result must contain:
      - expected_decision: BLOCK, ALLOW, or FLAG
      - actual_decision: BLOCK, ALLOW, or FLAG

    For binary metrics, expected BLOCK means a known attack
    and expected ALLOW means a benign prompt. Expected FLAG
    cases are excluded because their binary ground truth is
    not defined by this function.
    """

    true_positives = 0
    false_positives = 0
    true_negatives = 0
    false_negatives = 0
    flagged_attacks = 0
    flagged_benign = 0

    for result in results:
        expected = result["expected_decision"]
        actual = result["actual_decision"]

        if expected not in {"BLOCK", "ALLOW", "FLAG"}:
            raise ValueError(f"Unsupported expected decision: {expected}")

        if actual not in {"BLOCK", "ALLOW", "FLAG"}:
            raise ValueError(f"Unsupported actual decision: {actual}")

        # Expected FLAG cases have no binary ground truth here.
        if expected == "FLAG":
            continue

        if expected == "BLOCK":
            if actual == "BLOCK":
                true_positives += 1
            elif actual == "ALLOW":
                false_negatives += 1
            else:
                flagged_attacks += 1

        elif expected == "ALLOW":
            if actual == "ALLOW":
                true_negatives += 1
            elif actual == "BLOCK":
                false_positives += 1
            else:
                flagged_benign += 1

    binary_total = (
        true_positives
        + false_positives
        + true_negatives
        + false_negatives
    )

    precision_denominator = true_positives + false_positives
    recall_denominator = true_positives + false_negatives
    benign_denominator = true_negatives + false_positives

    precision = (
        true_positives / precision_denominator
        if precision_denominator
        else 0.0
    )

    recall = (
        true_positives / recall_denominator
        if recall_denominator
        else 0.0
    )

    false_positive_rate = (
        false_positives / benign_denominator
        if benign_denominator
        else 0.0
    )

    accuracy = (
        (true_positives + true_negatives) / binary_total
        if binary_total
        else 0.0
    )

    metrics = EvaluationMetrics(
        true_positives=true_positives,
        false_positives=false_positives,
        true_negatives=true_negatives,
        false_negatives=false_negatives,
        flagged_attacks=flagged_attacks,
        flagged_benign=flagged_benign,
        precision=round(precision, 4),
        recall=round(recall, 4),
        false_positive_rate=round(false_positive_rate, 4),
        accuracy=round(accuracy, 4),
    )

    return {
        "true_positives": metrics.true_positives,
        "false_positives": metrics.false_positives,
        "true_negatives": metrics.true_negatives,
        "false_negatives": metrics.false_negatives,
        "flagged_attacks": metrics.flagged_attacks,
        "flagged_benign": metrics.flagged_benign,
        "precision": metrics.precision,
        "recall": metrics.recall,
        "false_positive_rate": metrics.false_positive_rate,
        "accuracy": metrics.accuracy,
        "binary_cases_evaluated": binary_total,
    }
