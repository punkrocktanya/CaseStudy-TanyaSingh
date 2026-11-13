"""Run the six case-study tasks in dependency order from the project root."""
from __future__ import annotations
import argparse
import os
from pathlib import Path
import shutil
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
TASK_FOLDERS = {
    1: 'task1_data_engineering', 2: 'task2_degradation_modeling',
    3: 'task3_anomaly_detection', 4: 'task4_rul_estimation',
    5: 'task5_pack_scaling', 6: 'task6_reporting',
}
OUTPUT_FOLDERS = {
    1: ['01_data_cleaning', '02_silver_phase_data', '03_gold_cycle_features'],
    2: ['04_capacity_fade', '05_capacity_model_comparison', '06_differential_voltage'],
    3: ['07_anomaly_detection'],
    4: ['08_rul_individual_curves', '09_rul_xgboost', '10_rul_lstm', '11_rul_model_comparison'],
    5: ['13_pack_scaling'], 6: ['14_reporting_visualization'],
}


def sync_outputs(task):
    """Copy reviewable results into the task folder; source outputs stay authoritative."""
    destination = ROOT / 'scripts' / TASK_FOLDERS[task] / 'outputs'
    for name in OUTPUT_FOLDERS[task]:
        source = ROOT / 'scripts' / 'outputs' / name
        if not source.is_dir():
            continue
        for file in source.rglob('*'):
            if (not file.is_file() or file.suffix.lower() == '.xlsx'
                    or file.name.endswith('_clean.parquet')
                    or file.name.startswith('interval_diagnostics_')):
                continue
            target = destination / name / file.relative_to(source)
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(file, target)
    if task == 6:
        report = ROOT / 'output' / 'pdf' / 'Technical_Report_Module_Outputs.pdf'
        if report.is_file():
            destination.mkdir(parents=True, exist_ok=True)
            shutil.copy2(report, destination / 'Technical_Report.pdf')
    print(f'Task {task} outputs copied to {destination}', flush=True)


def run_task(task):
    """Execute one task with the same settings used by the full pipeline."""
    env = dict(os.environ, PYTHONUTF8='1', MPLBACKEND='Agg')
    for script in TASKS[task]:
        print(f'Task {task}: {script}', flush=True)
        subprocess.run([sys.executable, str(ROOT / 'scripts' / TASK_FOLDERS[task] / script)], cwd=ROOT, env=env, check=True)
    sync_outputs(task)

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--task', type=int, choices=TASKS, help='Run one task; prerequisites must already exist')
    args = parser.parse_args()
    for task in ([args.task] if args.task else TASKS):
        run_task(task)

if __name__ == '__main__':
    main()
