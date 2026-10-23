from collections import defaultdict

import json
from datetime import datetime, timezone
from pathlib import Path

from evaluator.evaluation_metrics import calculate_metrics
from security.prompt_detector import inspect_prompt
from tests.holdout_detector_dataset import HOLDOUT_TEST_CASES


def run_holdout_evaluation() -> list[dict]:
    """Evaluate the detector against every holdout test case."""
    results = []

    for case in HOLDOUT_TEST_CASES:
        detection = inspect_prompt(case["prompt"])
        actual_decision = detection.decision.value
        expected_decision = case["expected_decision"]

        results.append(
            {
                "case_id": case["case_id"],
                "category": case["category"],
                "expected_decision": expected_decision,
                "actual_decision": actual_decision,
                "passed": actual_decision == expected_decision,
                "reason": detection.reason,
            }
        )

    return results


def summarize_results(results: list[dict]) -> dict:
    """Calculate overall and category-level evaluation metrics."""
    if not results:
        raise ValueError("The holdout evaluation dataset is empty.")

    metrics = calculate_metrics(results)

    grouped_results = defaultdict(list)

    for result in results:
        grouped_results[result["category"]].append(result)

    category_summary = {}

    for category, cases in grouped_results.items():
        correct = sum(case["passed"] for case in cases)
        total = len(cases)

        category_summary[category] = {
            "total_cases": total,
            "correct": correct,
            "incorrect": total - correct,
            "pass_rate": round(correct / total * 100, 2),
        }

    correct = sum(result["passed"] for result in results)
    total = len(results)

    return {
        "total_cases": total,
        "correct": correct,
        "incorrect": total - correct,
        "pass_rate": round(correct / total * 100, 2),
        "metrics": metrics,
        "categories": category_summary,
    }


def print_evaluation_report(results: list[dict], summary: dict) -> None:
    """Print individual classifications and evaluation metrics."""
    print("\nBAYORA SHIELD — HOLDOUT EVALUATION")
    print("=" * 65)

    for result in results:
        status = "PASS" if result["passed"] else "FAIL"

        print(
            f"{status} | {result['case_id']} | "
            f"category={result['category']} | "
            f"expected={result['expected_decision']} | "
            f"actual={result['actual_decision']}"
        )

        if not result["passed"]:
            print(f"       Reason: {result['reason']}")

    print("\nOVERALL SUMMARY")
    print("=" * 65)
    print(f"Total cases: {summary['total_cases']}")
    print(f"Correct classifications: {summary['correct']}")
    print(f"Incorrect classifications: {summary['incorrect']}")
    print(f"Pass rate: {summary['pass_rate']:.2f}%")

    for metric, value in summary["metrics"].items():
        print(f"{metric}: {value}")

    print("\nCATEGORY SUMMARY")
    print("=" * 65)

    for category, data in summary["categories"].items():
        print(
            f"{category}: "
            f"{data['correct']}/{data['total_cases']} correct "
            f"({data['pass_rate']:.2f}%)"
        )



def main() -> None:
    if not HOLDOUT_TEST_CASES:
        raise ValueError("The holdout dataset is empty.")

    results = run_holdout_evaluation()
    summary = summarize_results(results)

    print_evaluation_report(results, summary)

    report = {
        "project": "Bayora Shield",
        "evaluation_type": "holdout_candidate",
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "total_cases": summary["total_cases"],
        "correct_classifications": summary["correct"],
        "incorrect_classifications": summary["incorrect"],
        "pass_rate": summary["pass_rate"],
        "metrics": summary["metrics"],
        "categories": summary["categories"],
        "results": results,
    }

    report_directory = Path("reports")
    history_directory = report_directory / "history"

    report_directory.mkdir(parents=True, exist_ok=True)
    history_directory.mkdir(parents=True, exist_ok=True)

    report_json = json.dumps(report, indent=2)

    latest_report_path = report_directory / "holdout_evaluation.json"
    latest_report_path.write_text(report_json, encoding="utf-8")

    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    historical_report_path = (
        history_directory / f"holdout_evaluation_{timestamp}.json"
    )
    historical_report_path.write_text(report_json, encoding="utf-8")

    print(f"\nLatest report: {latest_report_path}")
    print(f"Historical report: {historical_report_path}")


if __name__ == "__main__":
    main()
