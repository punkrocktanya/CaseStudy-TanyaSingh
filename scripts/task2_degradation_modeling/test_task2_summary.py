"""Checks for the Task 2 candidate-by-cycle summary."""

# Make shared task modules importable when running this file directly.
import sys as _task_sys
from pathlib import Path as _TaskPath
_task_scripts = _TaskPath(__file__).resolve().parents[1]
for _task_dir in ("task1_data_engineering", "task2_degradation_modeling", "task3_anomaly_detection", "task4_rul_estimation", "task5_pack_scaling", "task6_reporting"):
    _task_path = str(_task_scripts / _task_dir)
    if _task_path not in _task_sys.path:
        _task_sys.path.append(_task_path)

import unittest
import pandas as pd
from task2_analysis_summary import summarize_features


class CandidateSummaryTests(unittest.TestCase):
    def test_cycles_without_candidates_remain_visible_and_support_is_per_cycle(self):
        audit = pd.DataFrame([
            {'cell': '001_2', 'cycle': 2, 'capacity_Ah': 1.5, 'samples': 12, 'zero_dt': 0},
            {'cell': '001_2', 'cycle': 10, 'capacity_Ah': 1.3, 'samples': 11, 'zero_dt': 1},
        ])
        features = pd.DataFrame([
            {'cell': '001_2', 'cycle': 10, 'window': 21, 'stable': True, 'duplicate_affected': False},
            {'cell': '001_2', 'cycle': 10, 'window': 11, 'stable': False, 'duplicate_affected': True},
        ])
        physical = pd.DataFrame([
            {'cell': '001_2', 'cycle': 2, 'sampling_supported': True},
            {'cell': '001_2', 'cycle': 10, 'sampling_supported': False},
        ])
        result = summarize_features(features, audit, physical).set_index('cycle')
        self.assertEqual(result.loc[2, 'candidate_count'], 0)
        self.assertEqual(result.loc[10, 'candidate_count'], 1)
        self.assertEqual(result.loc[10, 'stable_count'], 1)
        self.assertFalse(result.loc[10, 'sampling_supported'])

if __name__ == '__main__':
    unittest.main()
