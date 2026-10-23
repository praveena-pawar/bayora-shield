import json
import sys
from pathlib import Path    

def load_report(report_path: Path) -> dict:
    """Load an evaluation report from a JSON file."""

    if not report_path.is_file():
        raise FileNotFoundError(
            f"Evaluation report not found: {report_path}"
        )

    try:
        with report_path.open("r", encoding="utf-8") as file:
            report = json.load(file)
    except json.JSONDecodeError as exc:
        raise ValueError(
            f"Invalid JSON in evaluation report: {report_path}"
        ) from exc

    if not isinstance(report, dict):
        raise ValueError(
            f"Expected a JSON object in: {report_path}"
        )

    required_fields = {"total_cases", "metrics"}

    missing_fields = required_fields - report.keys()

    if missing_fields:
        raise ValueError(
            f"Report is missing required fields: "
            f"{', '.join(sorted(missing_fields))}"
        )

    if not isinstance(report["metrics"], dict):
        raise ValueError(
            f"'metrics' must be a JSON object in: {report_path}"
        )

    return report



def compare_reports(old_report: dict, new_report: dict) -> dict:
    """Compare metrics from two evaluation reports."""

    metric_names = [
        "precision",
        "recall",
        "false_positive_rate",
        "accuracy",
    ]

    old_metrics = old_report["metrics"]
    new_metrics = new_report["metrics"]

    comparison = {}

    for metric in metric_names:
        old_value = old_metrics.get(metric)
        new_value = new_metrics.get(metric)

        if not isinstance(old_value, (int, float)):
            raise ValueError(
                f"Missing or invalid '{metric}' in the older report."
            )

        if not isinstance(new_value, (int, float)):
            raise ValueError(
                f"Missing or invalid '{metric}' in the newer report."
            )

        comparison[metric] = {
            "old": old_value,
            "new": new_value,
            "change": round(new_value - old_value, 4),
        }

    count_names = [
        "true_positives",
        "false_positives",
        "true_negatives",
        "false_negatives",
    ]

    for count in count_names:
        old_value = old_metrics.get(count)
        new_value = new_metrics.get(count)

        if not isinstance(old_value, int) or not isinstance(new_value, int):
            raise ValueError(
                f"Missing or invalid '{count}' in one of the reports."
            )

        comparison[count] = {
            "old": old_value,
            "new": new_value,
            "change": new_value - old_value,
        }

    comparison["total_cases"] = {
        "old": old_report["total_cases"],
        "new": new_report["total_cases"],
        "change": new_report["total_cases"] - old_report["total_cases"],
    }

    return comparison



def print_comparison(comparison: dict) -> None:
    """Print a readable summary of evaluation differences."""

    print("\nBAYORA SHIELD — EVALUATION COMPARISON")
    print("=" * 65)

    print(f"{'Metric':<25}{'Old':>12}{'New':>12}{'Change':>14}")
    print("-" * 65)

    display_names = {
        "precision": "Precision",
        "recall": "Recall",
        "false_positive_rate": "False-positive rate",
        "accuracy": "Accuracy",
        "true_positives": "True positives",
        "false_positives": "False positives",
        "true_negatives": "True negatives",
        "false_negatives": "False negatives",
        "total_cases": "Total cases",
    }

    for key, label in display_names.items():
        values = comparison[key]
        old = values["old"]
        new = values["new"]
        change = values["change"]

        if key in {
            "precision",
            "recall",
            "false_positive_rate",
            "accuracy",
        }:
            print(
                f"{label:<25}{old:>12.4f}{new:>12.4f}{change:>+14.4f}"
            )
        else:
            print(
                f"{label:<25}{old:>12}{new:>12}{change:>+14}"
            )

    print("=" * 65)
    print("Interpretation:")
    print("- Higher precision, recall, and accuracy are generally desirable.")
    print("- Lower false-positive and false-negative counts are desirable.")
    print("- Compare results alongside test-set size and composition.")




def main() -> None:
    """Load and compare two evaluation reports."""

    if len(sys.argv) != 3:
        print(
            "Usage: python -m tests.manual_compare_evaluations "
            "<older_report.json> <newer_report.json>"
        )
        raise SystemExit(2)

    old_path = Path(sys.argv[1])
    new_path = Path(sys.argv[2])

    try:
        old_report = load_report(old_path)
        new_report = load_report(new_path)
        comparison = compare_reports(old_report, new_report)
    except (OSError, ValueError) as exc:
        print(f"Error: {exc}")
        raise SystemExit(1) from exc

    print_comparison(comparison)


if __name__ == "__main__":
    main()