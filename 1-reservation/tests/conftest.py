"""Pytest configuration: saves a JSON test report to results/ after each run."""
import json
import os
from datetime import datetime

# Path to the results directory (one level above tests/)
RESULTS_DIR = os.path.join(os.path.dirname(__file__), "..", "results")


def pytest_configure(config):  # pylint: disable=unused-argument
    """Create the results directory if it does not exist."""
    os.makedirs(RESULTS_DIR, exist_ok=True)


def pytest_runtest_logreport(report):
    """Collect individual test outcomes as they finish."""
    # Only record the call phase (not setup/teardown) to avoid duplicates
    if report.when != "call":
        return
    # Initialise the shared list on the config object on first use
    if not hasattr(pytest_runtest_logreport, "_results"):
        pytest_runtest_logreport._results = []  # pylint: disable=protected-access
    pytest_runtest_logreport._results.append(  # pylint: disable=protected-access
        {
            "test": report.nodeid,
            "outcome": report.outcome,
            # Include failure reason when the test did not pass
            "message": str(report.longrepr) if report.failed else None,
        }
    )


def pytest_sessionfinish(session, exitstatus):  # pylint: disable=unused-argument
    """Write the accumulated results to results/test_results.json."""
    results = getattr(pytest_runtest_logreport, "_results", [])
    # Reset for the next run in the same process
    pytest_runtest_logreport._results = []  # pylint: disable=protected-access

    # Tally outcomes
    passed = [r for r in results if r["outcome"] == "passed"]
    failed = [r for r in results if r["outcome"] == "failed"]
    errors = [r for r in results if r["outcome"] == "error"]

    report = {
        "timestamp": datetime.now().isoformat(),
        "summary": {
            "total": len(results),
            "passed": len(passed),
            "failed": len(failed),
            "errors": len(errors),
            "exit_status": int(exitstatus),
        },
        "tests": results,
    }

    out_path = os.path.join(RESULTS_DIR, "test_results.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)
