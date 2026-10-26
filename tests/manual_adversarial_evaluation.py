import json
from collections import defaultdict
from datetime import UTC, datetime
from pathlib import Path

from evaluator.evaluation_metrics import calculate_metrics
from security.prompt_detector import inspect_prompt
from tests.adversarial_detector_dataset import ADVERSARIAL_TEST_CASES


def run_adversarial_evaluation() -> list[dict]:
    results = []

    for case in ADVERSARIAL_TEST_CASES:
        detection = inspect_prompt(case["prompt"])
        actual_decision = detection.decision.value
        expected_decision = case["expected_decision"]

        results.append(
            {
                "case_id": case["case_id"],
                "category": case["category"],
                "prompt": case["prompt"],
                "expected_decision": expected_decision,
                "actual_decision": actual_decision,
                "passed": actual_decision == expected_decision,
                "reason": detection.reason,
            }
        )

    return results


def summarize_results(results: list[dict]) -> dict:
    if not results:
        raise ValueError("The adversarial evaluation dataset is empty.")

    metrics = calculate_metrics(results)
    grouped_results = defaultdict(list)

    for result in results:
        grouped_results[result["category"]].append(result)

    categories = {}

    for category, cases in grouped_results.items():
        correct = sum(case["passed"] for case in cases)
        total = len(cases)

        categories[category] = {
            "total_cases": total,
            "correct": correct,
            "incorrect": total - correct,
            "pass_rate": round(correct / total * 100, 2),
        }

    correct = sum(result["passed"] for result in results)
    total = len(results)

    false_positives = [
        result
        for result in results
        if result["expected_decision"] == "ALLOW"
        and result["actual_decision"] == "BLOCK"
    ]

    false_negatives = [
        result
        for result in results
        if result["expected_decision"] == "BLOCK"
        and result["actual_decision"] == "ALLOW"
    ]

    return {
        "total_cases": total,
        "correct": correct,
        "incorrect": total - correct,
        "pass_rate": round(correct / total * 100, 2),
        "metrics": metrics,
        "categories": categories,
        "false_positive_count": len(false_positives),
        "false_negative_count": len(false_negatives),
        "false_positives": false_positives,
        "false_negatives": false_negatives,
    }


def print_evaluation_report(results: list[dict], summary: dict) -> None:
    print("\nBAYORA SHIELD - ADVERSARIAL EVALUATION")
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
            print(f"       Prompt: {result['prompt']}")
            print(f"       Reason: {result['reason']}")

    print("\nOVERALL SUMMARY")
    print("=" * 65)
    print(f"Total cases: {summary['total_cases']}")
    print(f"Correct classifications: {summary['correct']}")
    print(f"Incorrect classifications: {summary['incorrect']}")
    print(f"Pass rate: {summary['pass_rate']:.2f}%")

    print("\nMETRICS")
    print("=" * 65)

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

    print("\nERROR SUMMARY")
    print("=" * 65)
    print(f"False positives: {summary['false_positive_count']}")
    print(f"False negatives: {summary['false_negative_count']}")


def main() -> None:
    results = run_adversarial_evaluation()
    summary = summarize_results(results)
    print_evaluation_report(results, summary)

    report = {
        "project": "Bayora Shield",
        "evaluation_type": "adversarial",
        "timestamp_utc": datetime.now(UTC).isoformat(),
        **summary,
        "results": results,
    }

    report_directory = Path("reports")
    history_directory = report_directory / "history"

    report_directory.mkdir(parents=True, exist_ok=True)
    history_directory.mkdir(parents=True, exist_ok=True)

    report_json = json.dumps(report, indent=2)

    latest_path = report_directory / "adversarial_evaluation.json"
    latest_path.write_text(report_json, encoding="utf-8")

    timestamp = datetime.now(UTC).strftime("%Y%m%d_%H%M%S")
    history_path = (
        history_directory / f"adversarial_evaluation_{timestamp}.json"
    )
    history_path.write_text(report_json, encoding="utf-8")

    print(f"\nLatest report: {latest_path}")
    print(f"Historical report: {history_path}")


if __name__ == "__main__":
    main()