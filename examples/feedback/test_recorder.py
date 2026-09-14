"""Collect exact pytest node ids and phase outcomes for an auditable local run."""

import json
import platform
import sys
from importlib.metadata import distributions, version
from pathlib import Path

import pytest


class Recorder:
    def __init__(self):
        self.collected = []
        self.phases = {}

    def pytest_collection_finish(self, session):
        self.collected = [item.nodeid for item in session.items]

    def pytest_runtest_logreport(self, report):
        self.phases.setdefault(report.nodeid, {})[report.when] = report.outcome


if __name__ == "__main__":
    output = Path(sys.argv[1])
    recorder = Recorder()
    args = sys.argv[2:]
    # Pytest prepends configured addopts to its input list; preserve the invocation.
    code = int(pytest.main(list(args), plugins=[recorder]))
    results = []
    for nodeid in recorder.collected:
        phases = recorder.phases.get(nodeid, {})
        results.append(
            {
                "nodeid": nodeid,
                "phases": phases,
                "outcome": (
                    "passed"
                    if phases == {"setup": "passed", "call": "passed", "teardown": "passed"}
                    else "not_passed"
                ),
            }
        )
    output.write_text(
        json.dumps(
            {
                "collected": recorder.collected,
                "results": results,
                "exit_code": code,
                "pytest_args": args,
                "environment": {
                    "python": platform.python_version(),
                    "pytest": pytest.__version__,
                    "jsonschema": version("jsonschema"),
                    "platform": platform.platform(),
                    "packages": sorted(
                        (item.metadata["Name"], item.version) for item in distributions()
                    ),
                },
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    sys.exit(code)
