"""Run the cache simulator's existing automated checks and summarize results."""

from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent
BACKEND = ROOT / "backend"


def run_check(label: str, command: list[str], cwd: Path) -> bool:
    print(f"\n== {label} ==", flush=True)
    try:
        result = subprocess.run(command, cwd=cwd, check=False)
    except FileNotFoundError:
        print(f"Could not find required command: {command[0]}")
        return False
    status = "PASS" if result.returncode == 0 else f"FAIL (exit {result.returncode})"
    print(f"{label}: {status}")
    return result.returncode == 0


def main() -> int:
    python = sys.executable
    npm = shutil.which("npm")
    results = [
        run_check(
            "Backend unit tests",
            [python, "-m", "unittest", "discover", "-s", str(BACKEND / "tests")],
            BACKEND,
        )
    ]

    if not npm:
        print("\nFrontend checks: SKIPPED (npm was not found)")
        results.extend([False, False])
    else:
        results.append(run_check("Frontend lint", [npm, "run", "lint"], ROOT))
        results.append(run_check("Frontend production build", [npm, "run", "build"], ROOT))

    passed = sum(results)
    failed = len(results) - passed
    print(f"\nTester bot summary: {passed} passed, {failed} failed or skipped.")
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
