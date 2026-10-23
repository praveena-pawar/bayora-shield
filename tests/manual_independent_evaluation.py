from collections import defaultdict

from evaluator.evaluation_metrics import calculate_metrics
from security.prompt_detector import inspect_prompt
from tests.independent_detector_dataset import INDEPENDENT_TEST_CASES


def run_independent_evaluation() -> list[dict]:
    """Evaluate the existing detector against the independent test cases."""

    results = []

    for case in INDEPENDENT_TEST_CASES:
        detection = inspect_prompt(case["prompt"])
        actual_decision = detection.decision.value
        expected_decision = case["expected_decision"]

        result = {
            "case_id": case["case_id"],
            "category": case["category"],
            "expected_decision": expected_decision,
            "actual_decision": actual_decision,
            "passed": actual_decision == expected_decision,
            "reason": detection.reason,
        }

        results.append(result)

    return results


def summarize_results(results: list[dict]) -> dict:
    """Calculate overall and per-category evaluation metrics."""

    metrics = calculate_metrics(results)

    category_results = defaultdict(list)

    for result in results:
        category_results[result["category"]].append(result)

    category_summary = {}

    for category, cases in category_results.items():
        category_metrics = calculate_metrics(cases)

        correct = sum(case["passed"] for case in cases)
        total = len(cases)

        category_summary[category] = {
            "total_cases": total,
            "correct": correct,
            "incorrect": total - correct,
            "pass_rate": round(correct / total * 100, 2) if total else 0.0,
            "metrics": category_metrics,
        }

    correct = sum(result["passed"] for result in results)
    total = len(results)

    return {
        "total_cases": total,
        "correct": correct,
        "incorrect": total - correct,
        "pass_rate": round(correct / total * 100, 2) if total else 0.0,
        "metrics": metrics,
        "categories": category_summary,
    }


def print_evaluation_report(
    results: list[dict],
    summary: dict,
) -> None:
    """Print the independent evaluation results."""

    print("\nBAYORA SHIELD — INDEPENDENT DETECTOR EVALUATION")
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

    metrics = summary["metrics"]
    print(f"Precision: {metrics['precision']:.4f}")
    print(f"Recall: {metrics['recall']:.4f}")
    print(f"False-positive rate: {metrics['false_positive_rate']:.4f}")
    print(f"Accuracy: {metrics['accuracy']:.4f}")

    print("\nCATEGORY SUMMARY")
    print("=" * 65)

    for category, category_data in summary["categories"].items():
        print(
            f"{category}: "
            f"{category_data['correct']}/{category_data['total_cases']} "
            f"correct ({category_data['pass_rate']:.2f}%)"
        )



def main() -> None:
    """Run and report the independent detector evaluation."""

    if not INDEPENDENT_TEST_CASES:
        raise ValueError("The independent evaluation dataset is empty.")

    results = run_independent_evaluation()
    summary = summarize_results(results)

    print_evaluation_report(results, summary)


if __name__ == "__main__":
    main()