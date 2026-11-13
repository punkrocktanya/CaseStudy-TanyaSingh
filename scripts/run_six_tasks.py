"""Run the six case-study tasks in dependency order from the project root."""
from __future__ import annotations
import argparse
import os
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parent.parent
TASKS = {
    1: ['run_cleaning_pipeline.py'],
    2: ['stage_04_fit_capacity_fade.py', '05_compare_capacity_models.py', '06_differential_voltage.py', 'task2_analysis_summary.py'],
    3: ['07_detect_battery_anomalies.py'],
    4: ['stage_08_individual_curve_rul.py', 'stage_09_estimate_rul_xgboost_shared.py', 'stage_10_estimate_rul_lstm_minimal.py', '11_build_common_checkpoint_comparison.py'],
    5: ['stage_13_scale_module_pack.py'],
    6: ['14_build_task6_visualizations.py', 'build_six_task_report.py'],
}

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--task', type=int, choices=TASKS, help='Run one task; prerequisites must already exist')
    args = parser.parse_args()
    env = dict(os.environ, PYTHONUTF8='1', MPLBACKEND='Agg')
    for task in ([args.task] if args.task else TASKS):
        for script in TASKS[task]:
            print(f'Task {task}: {script}', flush=True)
            subprocess.run([sys.executable, str(ROOT / 'scripts' / script)], cwd=ROOT, env=env, check=True)

if __name__ == '__main__':
    main()
