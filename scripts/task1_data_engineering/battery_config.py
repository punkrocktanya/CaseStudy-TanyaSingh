"""Shared processing conventions; provisional limits are not physical impossibilities."""

# Make shared task modules importable when running this file directly.
import sys as _task_sys
from pathlib import Path as _TaskPath
_task_scripts = _TaskPath(__file__).resolve().parents[1]
for _task_dir in ("task1_data_engineering", "task2_degradation_modeling", "task3_anomaly_detection", "task4_rul_estimation", "task5_pack_scaling", "task6_reporting"):
    _task_path = str(_task_scripts / _task_dir)
    if _task_path not in _task_sys.path:
        _task_sys.path.append(_task_path)

import hashlib
import json
from pathlib import Path

CONFIG_PATH = Path(__file__).resolve().parents[2] / 'battery_thresholds.json'
CONFIG = json.loads(CONFIG_PATH.read_text(encoding='utf-8'))
CONFIG_SHA256 = hashlib.sha256(CONFIG_PATH.read_bytes()).hexdigest()
