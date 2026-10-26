import sys

from security.prompt_detector import inspect_prompt
from tests.independent_adversarial_probes import INDEPENDENT_PROBES


def main() -> None:
    print("\nBAYORA SHIELD - INDEPENDENT PROBE RESULTS")
    print("=" * 80)

    passed = 0
    failed = 0

    for case in INDEPENDENT_PROBES:
        result = inspect_prompt(case["prompt"])
        actual = result.decision.value
        expected = case["expected_decision"]

        status = "PASS" if actual == expected else "FAIL"

        if status == "PASS":
            passed += 1
        else:
            failed += 1

        print(
            f"{status} | {case['case_id']} | "
            f"expected={expected} | actual={actual}"
        )
        print(f"       Prompt: {case['prompt']}")
        print(f"       Reason: {result.reason}")

    print("\nSUMMARY")
    print("=" * 80)
    print(f"Total probes: {len(INDEPENDENT_PROBES)}")
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")

    if failed:
        sys.exit(1)


if __name__ == "__main__":
    main()