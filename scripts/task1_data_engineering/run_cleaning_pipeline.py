#!/usr/bin/env python3
"""Run source normalization, cleaning, Silver and validated Gold in order."""
from __future__ import annotations

# Make shared task modules importable when running this file directly.
import sys as _task_sys
from pathlib import Path as _TaskPath
_task_scripts = _TaskPath(__file__).resolve().parents[1]
for _task_dir in ("task1_data_engineering", "task2_degradation_modeling", "task3_anomaly_detection", "task4_rul_estimation", "task5_pack_scaling", "task6_reporting"):
    _task_path = str(_task_scripts / _task_dir)
    if _task_path not in _task_sys.path:
        _task_sys.path.append(_task_path)


import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def run(script_name: str):
    script = Path(__file__).resolve().parent / script_name
    print(f"Running {script.name}...")
    subprocess.run([sys.executable, str(script)], cwd=ROOT, check=True)


def main():
    run("01_normalize_timestamps.py")
    run("01_clean_and_validate.py")
    run("02_silver_transform.py")
    run("03_build_cycle_features.py")
    print("Battery pipeline completed; see scripts/task1_data_engineering/outputs/03_gold_cycle_features/corrective_action_report.md for release limits.")


if __name__ == "__main__":
    main()
