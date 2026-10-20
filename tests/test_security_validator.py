from evaluator.security_validator import run_validation


def test_validator_runs_all_checks():
    report = run_validation()

    assert report["total_checks"] == 5
    assert len(report["results"]) == 5


def test_all_initial_validation_checks_pass():
    report = run_validation()

    assert report["failed"] == 0
    assert report["passed"] == 5


def test_validation_report_contains_check_details():
    report = run_validation()

    for result in report["results"]:
        assert "check_name" in result
        assert "passed" in result
        assert "expected" in result
        assert "actual" in result