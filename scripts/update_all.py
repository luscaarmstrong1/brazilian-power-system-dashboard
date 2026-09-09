from __future__ import annotations

import subprocess
import sys
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


STEPS = [
    ("ANEEL", "scripts/extract_aneel.py"),
    ("ONS", "scripts/extract_ons.py"),
    ("CCEE", "scripts/extract_ccee.py"),
    ("EPE", "scripts/extract_epe.py"),
    ("Model", "scripts/build_model.py"),
    ("Validation", "scripts/validate_data.py"),
    ("Mockups", "scripts/generate_mockups.py"),
    ("Insights", "src/analytics/generate_insights.py"),
]


def run_step(label: str, script: str) -> int:
    print(f"[INFO] Running {label}: {script}")
    env = os.environ.copy()
    env["PYTHONPATH"] = str(ROOT)
    result = subprocess.run([sys.executable, script], cwd=ROOT, text=True, env=env)
    if result.returncode == 0:
        print(f"[OK] {label}")
    else:
        print(f"[ERROR] {label} failed with exit code {result.returncode}")
    return result.returncode


def main() -> None:
    failures = []
    for label, script in STEPS:
        code = run_step(label, script)
        if code != 0 and label not in {"CCEE", "EPE"}:
            failures.append(label)
    if failures:
        raise SystemExit(f"Pipeline failed: {', '.join(failures)}")
    print("[OK] update_all completed")


if __name__ == "__main__":
    main()
